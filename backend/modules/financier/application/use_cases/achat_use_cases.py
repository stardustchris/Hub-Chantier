"""Use Cases pour la gestion des achats.

FIN-05: Saisie achat - Formulaire de saisie des achats.
FIN-06: Suivi achat - Workflow de validation et suivi.
FIN-07: Validation N+1 - Validation hiérarchique des achats.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from shared.domain.calcul_financier import arrondir_pct

logger = logging.getLogger(__name__)

from ..ports.event_bus import EventBus

from ...domain.entities import Achat
from ...domain.entities.achat import (
    AchatValidationError,
    TransitionStatutAchatInvalideError,
)
from ...domain.repositories import (
    AchatRepository,
    FournisseurRepository,
    BudgetRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.value_objects import StatutAchat, TypeAchat, TAUX_VALIDES
from ...domain.value_objects.statuts_financiers import STATUTS_ENGAGES
from ...domain.events import (
    AchatCreatedEvent,
    AchatValideEvent,
    AchatRefuseEvent,
    AchatCommandeEvent,
    AchatLivreEvent,
    AchatFactureEvent,
    DepassementBudgetEvent,
)
from ..dtos import (
    AchatCreateDTO,
    AchatUpdateDTO,
    AchatDTO,
    AchatListDTO,
)
from .fournisseur_use_cases import FournisseurNotFoundError


class AchatNotFoundError(Exception):
    """Erreur levée quand un achat n'est pas trouvé."""

    def __init__(self, achat_id: int):
        self.achat_id = achat_id
        super().__init__(f"Achat {achat_id} non trouvé")


class FournisseurInactifError(Exception):
    """Erreur levée quand on tente d'associer un fournisseur inactif."""

    def __init__(self, fournisseur_id: int):
        self.fournisseur_id = fournisseur_id
        super().__init__(
            f"Le fournisseur {fournisseur_id} est inactif et ne peut pas "
            f"être utilisé pour un achat"
        )


def _verifier_depassement_budget(
    budget_repository: BudgetRepository,
    achat_repository: AchatRepository,
    event_bus: EventBus,
    chantier_id: int,
) -> None:
    """Vérifie et émet un event si le seuil budgétaire est dépassé.

    FIN-12: Alertes dépassement budget.

    Args:
        budget_repository: Le repository des budgets.
        achat_repository: Le repository des achats.
        event_bus: Le bus d'événements.
        chantier_id: L'ID du chantier.
    """
    budget = budget_repository.find_by_chantier_id(chantier_id)
    if not budget or budget.montant_revise_ht <= Decimal("0"):
        return

    total_engage = achat_repository.somme_by_chantier(
        chantier_id, statuts=STATUTS_ENGAGES
    )
    pourcentage = arrondir_pct((total_engage / budget.montant_revise_ht) * Decimal("100"))

    if pourcentage >= budget.seuil_alerte_pct:
        event_bus.publish(
            DepassementBudgetEvent(
                chantier_id=chantier_id,
                budget_id=budget.id,
                montant_budget_ht=budget.montant_revise_ht,
                montant_engage_ht=total_engage,
                pourcentage_consomme=pourcentage,
                seuil_alerte_pct=budget.seuil_alerte_pct,
            )
        )


class CreateAchatUseCase:
    """Use case pour créer un achat.

    FIN-05: Saisie achat.
    FIN-07: Auto-validation si montant < seuil.
    """

    def __init__(
        self,
        achat_repository: AchatRepository,
        fournisseur_repository: FournisseurRepository,
        budget_repository: BudgetRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._achat_repository = achat_repository
        self._fournisseur_repository = fournisseur_repository
        self._budget_repository = budget_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: AchatCreateDTO, demandeur_id: int) -> AchatDTO:
        """Crée un nouvel achat.

        Args:
            dto: Les données de l'achat à créer.
            demandeur_id: L'ID de l'utilisateur demandeur.

        Returns:
            Le DTO de l'achat créé.

        Raises:
            FournisseurNotFoundError: Si le fournisseur n'existe pas.
            FournisseurInactifError: Si le fournisseur est inactif.
        """
        fournisseur_nom = None
        taux_tva = dto.taux_tva
        type_achat = dto.type_achat

        # Vérifier le fournisseur si renseigné
        if dto.fournisseur_id:
            fournisseur = self._fournisseur_repository.find_by_id(dto.fournisseur_id)
            if not fournisseur:
                raise FournisseurNotFoundError(dto.fournisseur_id)
            if not fournisseur.actif:
                raise FournisseurInactifError(dto.fournisseur_id)
            fournisseur_nom = fournisseur.raison_sociale

            # CGI art. 283-2 nonies : autoliquidation TVA sous-traitance BTP
            # Le sous-traitant facture HT, le donneur d'ordre autoliquide la TVA
            if fournisseur.est_sous_traitant:
                type_achat = TypeAchat.SOUS_TRAITANCE
                if taux_tva > Decimal("0"):
                    logger.warning(
                        "Autoliquidation TVA (CGI art. 283-2 nonies) : taux forcé "
                        "à 0%% pour le sous-traitant '%s' (id=%d) - taux original: %s%%",
                        fournisseur.raison_sociale, fournisseur.id, taux_tva,
                    )
                    taux_tva = Decimal("0")

        # Créer l'entité
        achat = Achat(
            chantier_id=dto.chantier_id,
            fournisseur_id=dto.fournisseur_id,
            lot_budgetaire_id=dto.lot_budgetaire_id,
            type_achat=type_achat,
            libelle=dto.libelle,
            quantite=dto.quantite,
            unite=dto.unite,
            prix_unitaire_ht=dto.prix_unitaire_ht,
            taux_tva=taux_tva,
            date_commande=dto.date_commande,
            date_livraison_prevue=dto.date_livraison_prevue,
            commentaire=dto.commentaire,
            statut=StatutAchat.DEMANDE,
            demandeur_id=demandeur_id,
            created_at=datetime.utcnow(),
            created_by=demandeur_id,
        )

        # FIN-07: Auto-validation si montant < seuil
        budget = self._budget_repository.find_by_chantier_id(dto.chantier_id)
        if budget and not budget.necessite_validation_achat(achat.total_ht):
            achat.valider(demandeur_id)

        # Persister
        achat = self._achat_repository.save(achat)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="achat",
                entite_id=achat.id,
                chantier_id=achat.chantier_id,
                action="creation",
                details=(
                    f"Création de l'achat '{achat.libelle}' "
                    f"- {achat.total_ht} EUR HT"
                ),
                auteur_id=demandeur_id,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            AchatCreatedEvent(
                achat_id=achat.id,
                chantier_id=achat.chantier_id,
                fournisseur_id=achat.fournisseur_id,
                type_achat=achat.type_achat.value,
                libelle=achat.libelle,
                total_ht=achat.total_ht,
                demandeur_id=demandeur_id,
            )
        )

        # Vérifier dépassement budget
        _verifier_depassement_budget(
            self._budget_repository,
            self._achat_repository,
            self._event_bus,
            achat.chantier_id,
        )

        return AchatDTO.from_entity(achat, fournisseur_nom=fournisseur_nom)


class UpdateAchatUseCase:
    """Use case pour mettre à jour un achat.

    Seulement modifiable si le statut est 'demande'.
    """

    def __init__(
        self,
        achat_repository: AchatRepository,
        fournisseur_repository: FournisseurRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._achat_repository = achat_repository
        self._fournisseur_repository = fournisseur_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(
        self, achat_id: int, dto: AchatUpdateDTO, updated_by: int
    ) -> AchatDTO:
        """Met à jour un achat.

        Args:
            achat_id: L'ID de l'achat à mettre à jour.
            dto: Les données à mettre à jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO de l'achat mis à jour.

        Raises:
            AchatNotFoundError: Si l'achat n'existe pas.
            ValueError: Si le statut n'est pas 'demande'.
        """
        achat = self._achat_repository.find_by_id(achat_id)
        if not achat:
            raise AchatNotFoundError(achat_id)

        if achat.statut != StatutAchat.DEMANDE:
            raise ValueError(
                "Seuls les achats en statut 'demande' peuvent être modifiés"
            )

        modifications = []

        # Appliquer les modifications
        if dto.fournisseur_id is not None:
            achat.fournisseur_id = dto.fournisseur_id
            modifications.append("fournisseur_id")
        if dto.lot_budgetaire_id is not None:
            achat.lot_budgetaire_id = dto.lot_budgetaire_id
            modifications.append("lot_budgetaire_id")
        if dto.type_achat is not None:
            achat.type_achat = dto.type_achat
            modifications.append("type_achat")
        if dto.libelle is not None:
            achat.libelle = dto.libelle
            modifications.append("libelle")
        if dto.quantite is not None:
            achat.quantite = dto.quantite
            modifications.append("quantite")
        if dto.unite is not None:
            achat.unite = dto.unite
            modifications.append("unite")
        if dto.prix_unitaire_ht is not None:
            achat.prix_unitaire_ht = dto.prix_unitaire_ht
            modifications.append("prix_unitaire_ht")
        if dto.taux_tva is not None:
            if dto.taux_tva not in TAUX_VALIDES:
                raise ValueError(
                    f"Taux TVA invalide: {dto.taux_tva}. "
                    f"Taux autorisés: {', '.join(str(t) for t in TAUX_VALIDES)}"
                )
            achat.taux_tva = dto.taux_tva
            modifications.append("taux_tva")
        if dto.date_commande is not None:
            achat.date_commande = dto.date_commande
            modifications.append("date_commande")
        if dto.date_livraison_prevue is not None:
            achat.date_livraison_prevue = dto.date_livraison_prevue
            modifications.append("date_livraison_prevue")
        if dto.commentaire is not None:
            achat.commentaire = dto.commentaire
            modifications.append("commentaire")

        # CGI art. 283-2 nonies : autoliquidation TVA sous-traitance BTP
        # Vérifier après toutes les modifications (fournisseur et/ou taux_tva
        # ont pu changer) si le fournisseur est un sous-traitant
        if achat.fournisseur_id:
            fournisseur = self._fournisseur_repository.find_by_id(
                achat.fournisseur_id
            )
            if (
                fournisseur
                and fournisseur.est_sous_traitant
                and achat.taux_tva > Decimal("0")
            ):
                logger.warning(
                    "Autoliquidation TVA (CGI art. 283-2 nonies) : taux forcé "
                    "à 0%% pour le sous-traitant '%s' (id=%d) - taux original: %s%%",
                    fournisseur.raison_sociale, fournisseur.id, achat.taux_tva,
                )
                achat.taux_tva = Decimal("0")
                if "taux_tva" not in modifications:
                    modifications.append("taux_tva")

        achat.updated_at = datetime.utcnow()

        # Persister
        achat = self._achat_repository.save(achat)

        # Journal
        for champ in modifications:
            self._journal_repository.save(
                JournalEntry(
                    entite_type="achat",
                    entite_id=achat.id,
                    chantier_id=achat.chantier_id,
                    action="modification",
                    details=f"Modification du champ '{champ}'",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        return AchatDTO.from_entity(achat)


class ValiderAchatUseCase:
    """Use case pour valider un achat.

    FIN-07: Validation N+1 - Le chef/conducteur valide l'achat.
    """

    def __init__(
        self,
        achat_repository: AchatRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._achat_repository = achat_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, achat_id: int, valideur_id: int) -> AchatDTO:
        """Valide un achat (demande -> validé).

        Args:
            achat_id: L'ID de l'achat à valider.
            valideur_id: L'ID de l'utilisateur valideur.

        Returns:
            Le DTO de l'achat validé.

        Raises:
            AchatNotFoundError: Si l'achat n'existe pas.
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        achat = self._achat_repository.find_by_id(achat_id)
        if not achat:
            raise AchatNotFoundError(achat_id)

        # Effectuer la validation (lève une exception si invalide)
        achat.valider(valideur_id)

        achat = self._achat_repository.save(achat)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="achat",
                entite_id=achat.id,
                chantier_id=achat.chantier_id,
                action="validation",
                details=f"Validation de l'achat '{achat.libelle}'",
                auteur_id=valideur_id,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            AchatValideEvent(
                achat_id=achat.id,
                chantier_id=achat.chantier_id,
                total_ht=achat.total_ht,
                valideur_id=valideur_id,
            )
        )

        return AchatDTO.from_entity(achat)


class RefuserAchatUseCase:
    """Use case pour refuser un achat."""

    def __init__(
        self,
        achat_repository: AchatRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._achat_repository = achat_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(
        self, achat_id: int, valideur_id: int, motif: str
    ) -> AchatDTO:
        """Refuse un achat (demande -> refusé).

        Args:
            achat_id: L'ID de l'achat à refuser.
            valideur_id: L'ID de l'utilisateur valideur.
            motif: Le motif de refus.

        Returns:
            Le DTO de l'achat refusé.

        Raises:
            AchatNotFoundError: Si l'achat n'existe pas.
            AchatValidationError: Si le motif est vide.
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        achat = self._achat_repository.find_by_id(achat_id)
        if not achat:
            raise AchatNotFoundError(achat_id)

        # Effectuer le refus (lève une exception si invalide)
        achat.refuser(valideur_id, motif)

        achat = self._achat_repository.save(achat)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="achat",
                entite_id=achat.id,
                chantier_id=achat.chantier_id,
                action="refus",
                details=(
                    f"Refus de l'achat '{achat.libelle}' - Motif: {motif}"
                ),
                auteur_id=valideur_id,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            AchatRefuseEvent(
                achat_id=achat.id,
                chantier_id=achat.chantier_id,
                valideur_id=valideur_id,
                motif=motif,
            )
        )

        return AchatDTO.from_entity(achat)


class PasserCommandeAchatUseCase:
    """Use case pour passer un achat en commande.

    FIN-06: Workflow validé -> commandé.
    """

    def __init__(
        self,
        achat_repository: AchatRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._achat_repository = achat_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, achat_id: int, user_id: int) -> AchatDTO:
        """Passe un achat en commande (validé -> commandé).

        Args:
            achat_id: L'ID de l'achat.
            user_id: L'ID de l'utilisateur.

        Returns:
            Le DTO de l'achat commandé.

        Raises:
            AchatNotFoundError: Si l'achat n'existe pas.
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        achat = self._achat_repository.find_by_id(achat_id)
        if not achat:
            raise AchatNotFoundError(achat_id)

        achat.passer_commande()

        achat = self._achat_repository.save(achat)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="achat",
                entite_id=achat.id,
                chantier_id=achat.chantier_id,
                action="commande",
                details=f"Passage en commande de l'achat '{achat.libelle}'",
                auteur_id=user_id,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            AchatCommandeEvent(
                achat_id=achat.id,
                chantier_id=achat.chantier_id,
                fournisseur_id=achat.fournisseur_id,
                total_ht=achat.total_ht,
            )
        )

        return AchatDTO.from_entity(achat)


class MarquerLivreAchatUseCase:
    """Use case pour marquer un achat comme livré.

    FIN-06: Workflow commandé -> livré.
    """

    def __init__(
        self,
        achat_repository: AchatRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._achat_repository = achat_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, achat_id: int, user_id: int) -> AchatDTO:
        """Marque un achat comme livré (commandé -> livré).

        Args:
            achat_id: L'ID de l'achat.
            user_id: L'ID de l'utilisateur.

        Returns:
            Le DTO de l'achat livré.

        Raises:
            AchatNotFoundError: Si l'achat n'existe pas.
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        achat = self._achat_repository.find_by_id(achat_id)
        if not achat:
            raise AchatNotFoundError(achat_id)

        achat.marquer_livre()

        achat = self._achat_repository.save(achat)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="achat",
                entite_id=achat.id,
                chantier_id=achat.chantier_id,
                action="livraison",
                details=f"Réception de l'achat '{achat.libelle}'",
                auteur_id=user_id,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            AchatLivreEvent(
                achat_id=achat.id,
                chantier_id=achat.chantier_id,
            )
        )

        return AchatDTO.from_entity(achat)


class MarquerFactureAchatUseCase:
    """Use case pour marquer un achat comme facturé.

    FIN-06: Workflow livré -> facturé.
    """

    def __init__(
        self,
        achat_repository: AchatRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._achat_repository = achat_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(
        self, achat_id: int, numero_facture: str, user_id: int
    ) -> AchatDTO:
        """Marque un achat comme facturé (livré -> facturé).

        Args:
            achat_id: L'ID de l'achat.
            numero_facture: Le numéro de facture.
            user_id: L'ID de l'utilisateur.

        Returns:
            Le DTO de l'achat facturé.

        Raises:
            AchatNotFoundError: Si l'achat n'existe pas.
            AchatValidationError: Si le numéro de facture est vide.
            TransitionStatutAchatInvalideError: Si la transition est interdite.
        """
        achat = self._achat_repository.find_by_id(achat_id)
        if not achat:
            raise AchatNotFoundError(achat_id)

        achat.marquer_facture(numero_facture)

        achat = self._achat_repository.save(achat)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="achat",
                entite_id=achat.id,
                chantier_id=achat.chantier_id,
                action="facturation",
                details=(
                    f"Facturation de l'achat '{achat.libelle}' "
                    f"- Facture n°{numero_facture} "
                    f"- {achat.total_ttc} EUR TTC"
                ),
                auteur_id=user_id,
                created_at=datetime.utcnow(),
            )
        )

        # Event
        self._event_bus.publish(
            AchatFactureEvent(
                achat_id=achat.id,
                chantier_id=achat.chantier_id,
                numero_facture=numero_facture,
                total_ttc=achat.total_ttc,
            )
        )

        return AchatDTO.from_entity(achat)


class GetAchatUseCase:
    """Use case pour récupérer un achat avec enrichissement."""

    def __init__(self, achat_repository: AchatRepository):
        self._achat_repository = achat_repository

    def execute(self, achat_id: int) -> AchatDTO:
        """Récupère un achat par son ID.

        Args:
            achat_id: L'ID de l'achat.

        Returns:
            Le DTO de l'achat.

        Raises:
            AchatNotFoundError: Si l'achat n'existe pas.
        """
        achat = self._achat_repository.find_by_id(achat_id)
        if not achat:
            raise AchatNotFoundError(achat_id)

        return AchatDTO.from_entity(achat)


class ListAchatsUseCase:
    """Use case pour lister les achats avec filtres."""

    def __init__(self, achat_repository: AchatRepository):
        self._achat_repository = achat_repository

    def execute(
        self,
        chantier_id: Optional[int] = None,
        statut: Optional[StatutAchat] = None,
        fournisseur_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> AchatListDTO:
        """Liste les achats avec filtres optionnels.

        Args:
            chantier_id: Filtrer par chantier.
            statut: Filtrer par statut.
            fournisseur_id: Filtrer par fournisseur.
            limit: Nombre max de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste paginée d'achats.
        """
        if chantier_id:
            achats = self._achat_repository.find_by_chantier(
                chantier_id=chantier_id,
                statut=statut,
                limit=limit,
                offset=offset,
            )
            total = self._achat_repository.count_by_chantier(
                chantier_id=chantier_id,
                statuts=[statut] if statut else None,
            )
        elif fournisseur_id:
            achats = self._achat_repository.find_by_fournisseur(
                fournisseur_id=fournisseur_id,
                limit=limit,
                offset=offset,
            )
            # Approximation pour le total avec filtre fournisseur
            total = len(achats) if len(achats) < limit else limit + 1
        else:
            # Sans filtre, liste par chantier 0 (tous)
            achats = self._achat_repository.find_by_chantier(
                chantier_id=0,
                statut=statut,
                limit=limit,
                offset=offset,
            )
            total = len(achats)

        return AchatListDTO(
            items=[AchatDTO.from_entity(a) for a in achats],
            total=total,
            limit=limit,
            offset=offset,
        )


class ListAchatsEnAttenteUseCase:
    """Use case pour lister les achats en attente de validation.

    FIN-07: Validation N+1 - Liste des achats à valider.
    """

    def __init__(self, achat_repository: AchatRepository):
        self._achat_repository = achat_repository

    def execute(self, limit: int = 100, offset: int = 0) -> AchatListDTO:
        """Liste les achats en attente de validation.

        Args:
            limit: Nombre max de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste paginée des achats en attente.
        """
        achats = self._achat_repository.find_en_attente_validation(
            limit=limit,
            offset=offset,
        )
        total = len(achats) if len(achats) < limit else limit + 1

        return AchatListDTO(
            items=[AchatDTO.from_entity(a) for a in achats],
            total=total,
            limit=limit,
            offset=offset,
        )
