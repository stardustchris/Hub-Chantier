"""Use Cases pour la gestion des situations de travaux.

FIN-07: Situations de travaux - creation, mise a jour, workflow de validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..ports.event_bus import EventBus

from ...domain.entities.situation_travaux import SituationTravaux
from ...domain.entities.ligne_situation import LigneSituation
from ...domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.repositories.situation_repository import (
    SituationRepository,
    LigneSituationRepository,
)
from ...domain.events import (
    SituationCreatedEvent,
    SituationEmiseEvent,
    SituationValideeEvent,
    SituationFactureeEvent,
)
from ..dtos.situation_dtos import (
    SituationCreateDTO,
    SituationUpdateDTO,
    SituationDTO,
    LigneSituationCreateDTO,
)


class SituationNotFoundError(Exception):
    """Erreur levee quand une situation n'est pas trouvee."""

    def __init__(self, situation_id: int):
        self.situation_id = situation_id
        super().__init__(f"Situation {situation_id} non trouvee")


class SituationWorkflowError(Exception):
    """Erreur levee lors d'une transition de workflow invalide."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CreateSituationUseCase:
    """Use case pour creer une situation de travaux.

    FIN-07: Numerotation automatique SIT-YYYY-NN.
    Cree les lignes automatiquement a partir des lots budgetaires.
    """

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
        budget_repository: BudgetRepository,
        lot_repository: LotBudgetaireRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository
        self._budget_repository = budget_repository
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: SituationCreateDTO, created_by: int) -> SituationDTO:
        """Cree une nouvelle situation de travaux.

        Args:
            dto: Les donnees de la situation a creer.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de la situation creee avec ses lignes.

        Raises:
            ValueError: Si le budget n'existe pas.
        """
        # Verifier que le budget existe
        budget = self._budget_repository.find_by_id(dto.budget_id)
        if not budget:
            raise ValueError(f"Budget {dto.budget_id} non trouve")

        # Recuperer la derniere situation VALIDEE pour le montant cumule precedent.
        # find_derniere_situation() filtre deja sur statuts emise/validee/facturee
        # (exclut brouillons et en_validation) conformement au contrat du repository.
        derniere_situation = self._situation_repository.find_derniere_situation(
            dto.chantier_id
        )
        montant_cumule_precedent_ht = Decimal("0")
        if derniere_situation:
            montant_cumule_precedent_ht = derniere_situation.montant_cumule_ht

        # Generer le numero automatiquement: SIT-YYYY-NN
        count = self._situation_repository.count_by_chantier_id(dto.chantier_id)
        year = datetime.utcnow().year
        numero = f"SIT-{year}-{count + 1:02d}"

        # Creer l'entite situation
        situation = SituationTravaux(
            chantier_id=dto.chantier_id,
            budget_id=dto.budget_id,
            numero=numero,
            periode_debut=dto.periode_debut,
            periode_fin=dto.periode_fin,
            montant_cumule_precedent_ht=montant_cumule_precedent_ht,
            retenue_garantie_pct=dto.retenue_garantie_pct,
            taux_tva=dto.taux_tva,
            notes=dto.notes,
            statut="brouillon",
            created_by=created_by,
            created_at=datetime.utcnow(),
        )

        # Persister la situation
        situation = self._situation_repository.save(situation)

        # Recuperer les lots budgetaires du budget
        lots = self._lot_repository.find_by_budget_id(dto.budget_id)

        # Recuperer les lignes de la derniere situation pour le cumule precedent par lot
        lignes_precedentes = {}
        if derniere_situation:
            lignes_prec = self._ligne_repository.find_by_situation_id(
                derniere_situation.id
            )
            for lp in lignes_prec:
                lignes_precedentes[lp.lot_budgetaire_id] = lp

        # Construire un index des avancements fournis par l'utilisateur
        avancements_dto = {}
        for ligne_dto in dto.lignes:
            avancements_dto[ligne_dto.lot_budgetaire_id] = ligne_dto.pourcentage_avancement

        # Creer les lignes de situation a partir des lots
        lignes = []
        montant_cumule_total = Decimal("0")
        montant_periode_total = Decimal("0")

        for lot in lots:
            if lot.est_supprime:
                continue

            montant_marche_ht = lot.total_prevu_ht
            cumule_precedent = Decimal("0")
            if lot.id in lignes_precedentes:
                cumule_precedent = lignes_precedentes[lot.id].montant_cumule_ht

            # Avancement: utiliser celui fourni ou reprendre le precedent
            avancement = avancements_dto.get(lot.id, Decimal("0"))

            ligne = LigneSituation(
                situation_id=situation.id,
                lot_budgetaire_id=lot.id,
                pourcentage_avancement=avancement,
                montant_marche_ht=montant_marche_ht,
                montant_cumule_precedent_ht=cumule_precedent,
            )
            ligne.calculer_montants()

            lignes.append(ligne)
            montant_cumule_total += ligne.montant_cumule_ht
            montant_periode_total += ligne.montant_periode_ht

        # Persister les lignes
        lignes = self._ligne_repository.save_all(lignes)

        # Mettre a jour les totaux de la situation
        situation.montant_cumule_ht = montant_cumule_total
        situation.montant_periode_ht = montant_periode_total
        situation = self._situation_repository.save(situation)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="situation",
                entite_id=situation.id,
                chantier_id=situation.chantier_id,
                action="creation",
                details=(
                    f"Creation de la situation {situation.numero} - "
                    f"Periode: {situation.periode_debut} au {situation.periode_fin} - "
                    f"Montant cumule HT: {situation.montant_cumule_ht} EUR"
                ),
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            SituationCreatedEvent(
                situation_id=situation.id,
                chantier_id=situation.chantier_id,
                budget_id=situation.budget_id,
                numero=situation.numero,
                montant_cumule_ht=situation.montant_cumule_ht,
                created_by=created_by,
            )
        )

        return SituationDTO.from_entity(situation, lignes)


class UpdateSituationUseCase:
    """Use case pour mettre a jour une situation de travaux.

    Seules les situations en statut 'brouillon' peuvent etre modifiees.
    """

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
        lot_repository: LotBudgetaireRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository

    def execute(
        self, situation_id: int, dto: SituationUpdateDTO, updated_by: int
    ) -> SituationDTO:
        """Met a jour une situation de travaux.

        Args:
            situation_id: L'ID de la situation a mettre a jour.
            dto: Les donnees a mettre a jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO de la situation mise a jour.

        Raises:
            SituationNotFoundError: Si la situation n'existe pas.
            SituationWorkflowError: Si la situation n'est pas en brouillon.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise SituationNotFoundError(situation_id)

        if situation.statut != "brouillon":
            raise SituationWorkflowError(
                f"Impossible de modifier une situation en statut '{situation.statut}'. "
                "Seul le statut 'brouillon' est accepte."
            )

        modifications = []

        # Appliquer les modifications de la situation
        if dto.periode_debut is not None:
            situation.periode_debut = dto.periode_debut
            modifications.append("periode_debut")
        if dto.periode_fin is not None:
            situation.periode_fin = dto.periode_fin
            modifications.append("periode_fin")
        if dto.retenue_garantie_pct is not None:
            situation.retenue_garantie_pct = dto.retenue_garantie_pct
            modifications.append("retenue_garantie_pct")
        if dto.taux_tva is not None:
            situation.taux_tva = dto.taux_tva
            modifications.append("taux_tva")
        if dto.notes is not None:
            situation.notes = dto.notes
            modifications.append("notes")

        # Mettre a jour les lignes si fournies
        lignes = self._ligne_repository.find_by_situation_id(situation_id)

        if dto.lignes is not None:
            # Construire un index des avancements fournis
            avancements_dto = {}
            for ligne_dto in dto.lignes:
                avancements_dto[ligne_dto.lot_budgetaire_id] = ligne_dto.pourcentage_avancement

            montant_cumule_total = Decimal("0")
            montant_periode_total = Decimal("0")

            for ligne in lignes:
                if ligne.lot_budgetaire_id in avancements_dto:
                    ligne.pourcentage_avancement = avancements_dto[ligne.lot_budgetaire_id]
                    ligne.calculer_montants()
                    ligne.updated_at = datetime.utcnow()

                montant_cumule_total += ligne.montant_cumule_ht
                montant_periode_total += ligne.montant_periode_ht

            # Persister les lignes mises a jour
            lignes = self._ligne_repository.save_all(lignes)

            # Mettre a jour les totaux
            situation.montant_cumule_ht = montant_cumule_total
            situation.montant_periode_ht = montant_periode_total
            modifications.append("lignes_avancement")

        situation.updated_at = datetime.utcnow()

        # Persister la situation
        situation = self._situation_repository.save(situation)

        # Journal
        for champ in modifications:
            self._journal_repository.save(
                JournalEntry(
                    entite_type="situation",
                    entite_id=situation.id,
                    chantier_id=situation.chantier_id,
                    action="modification",
                    details=f"Modification du champ '{champ}'",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        return SituationDTO.from_entity(situation, lignes)


class SoumettreSituationUseCase:
    """Use case pour soumettre une situation en validation.

    Transition: brouillon -> en_validation.
    """

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository
        self._journal_repository = journal_repository

    def execute(self, situation_id: int, submitted_by: int) -> SituationDTO:
        """Soumet une situation pour validation.

        Args:
            situation_id: L'ID de la situation.
            submitted_by: L'ID de l'utilisateur qui soumet.

        Returns:
            Le DTO de la situation soumise.

        Raises:
            SituationNotFoundError: Si la situation n'existe pas.
            SituationWorkflowError: Si la transition est invalide.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise SituationNotFoundError(situation_id)

        try:
            situation.soumettre_validation()
        except ValueError as e:
            raise SituationWorkflowError(str(e))

        situation = self._situation_repository.save(situation)

        lignes = self._ligne_repository.find_by_situation_id(situation_id)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="situation",
                entite_id=situation.id,
                chantier_id=situation.chantier_id,
                action="validation",
                details=(
                    f"Soumission de la situation {situation.numero} "
                    f"pour validation"
                ),
                auteur_id=submitted_by,
                created_at=datetime.utcnow(),
            )
        )

        return SituationDTO.from_entity(situation, lignes)


class ValiderSituationUseCase:
    """Use case pour valider une situation de travaux.

    Transition: en_validation -> emise.
    """

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, situation_id: int, validated_by: int) -> SituationDTO:
        """Valide une situation de travaux.

        Args:
            situation_id: L'ID de la situation a valider.
            validated_by: L'ID de l'utilisateur valideur.

        Returns:
            Le DTO de la situation validee.

        Raises:
            SituationNotFoundError: Si la situation n'existe pas.
            SituationWorkflowError: Si la transition est invalide.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise SituationNotFoundError(situation_id)

        try:
            situation.valider(validated_by)
        except ValueError as e:
            raise SituationWorkflowError(str(e))

        situation = self._situation_repository.save(situation)

        lignes = self._ligne_repository.find_by_situation_id(situation_id)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="situation",
                entite_id=situation.id,
                chantier_id=situation.chantier_id,
                action="emission",
                details=(
                    f"Validation et emission de la situation {situation.numero} - "
                    f"Montant cumule HT: {situation.montant_cumule_ht} EUR"
                ),
                auteur_id=validated_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            SituationEmiseEvent(
                situation_id=situation.id,
                chantier_id=situation.chantier_id,
                numero=situation.numero,
                montant_cumule_ht=situation.montant_cumule_ht,
                validated_by=validated_by,
            )
        )

        return SituationDTO.from_entity(situation, lignes)


class MarquerValideeClientUseCase:
    """Use case pour marquer une situation comme validee par le client.

    Transition: emise -> validee.
    """

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, situation_id: int, marked_by: int) -> SituationDTO:
        """Marque une situation comme validee par le client.

        Args:
            situation_id: L'ID de la situation.
            marked_by: L'ID de l'utilisateur qui marque.

        Returns:
            Le DTO de la situation validee client.

        Raises:
            SituationNotFoundError: Si la situation n'existe pas.
            SituationWorkflowError: Si la transition est invalide.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise SituationNotFoundError(situation_id)

        try:
            situation.marquer_validee_client()
        except ValueError as e:
            raise SituationWorkflowError(str(e))

        situation = self._situation_repository.save(situation)

        lignes = self._ligne_repository.find_by_situation_id(situation_id)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="situation",
                entite_id=situation.id,
                chantier_id=situation.chantier_id,
                action="validation",
                details=(
                    f"Validation client de la situation {situation.numero}"
                ),
                auteur_id=marked_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            SituationValideeEvent(
                situation_id=situation.id,
                chantier_id=situation.chantier_id,
                numero=situation.numero,
                montant_cumule_ht=situation.montant_cumule_ht,
            )
        )

        return SituationDTO.from_entity(situation, lignes)


class MarquerFactureeSituationUseCase:
    """Use case pour marquer une situation comme facturee.

    Transition: validee -> facturee.
    """

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(
        self,
        situation_id: int,
        marked_by: int,
        facturee_at: Optional[datetime] = None,
    ) -> SituationDTO:
        """Marque une situation comme facturee.

        Args:
            situation_id: L'ID de la situation.
            marked_by: L'ID de l'utilisateur qui marque.
            facturee_at: Date de facturation (defaut: maintenant).

        Returns:
            Le DTO de la situation facturee.

        Raises:
            SituationNotFoundError: Si la situation n'existe pas.
            SituationWorkflowError: Si la transition est invalide.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise SituationNotFoundError(situation_id)

        try:
            situation.marquer_facturee(facturee_at)
        except ValueError as e:
            raise SituationWorkflowError(str(e))

        situation = self._situation_repository.save(situation)

        lignes = self._ligne_repository.find_by_situation_id(situation_id)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="situation",
                entite_id=situation.id,
                chantier_id=situation.chantier_id,
                action="facturation",
                details=(
                    f"Facturation de la situation {situation.numero} - "
                    f"Montant cumule HT: {situation.montant_cumule_ht} EUR"
                ),
                auteur_id=marked_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            SituationFactureeEvent(
                situation_id=situation.id,
                chantier_id=situation.chantier_id,
                numero=situation.numero,
                montant_cumule_ht=situation.montant_cumule_ht,
            )
        )

        return SituationDTO.from_entity(situation, lignes)


class GetSituationUseCase:
    """Use case pour recuperer une situation de travaux."""

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository

    def execute(self, situation_id: int) -> SituationDTO:
        """Recupere une situation par son ID.

        Args:
            situation_id: L'ID de la situation.

        Returns:
            Le DTO de la situation avec ses lignes.

        Raises:
            SituationNotFoundError: Si la situation n'existe pas.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise SituationNotFoundError(situation_id)

        lignes = self._ligne_repository.find_by_situation_id(situation_id)

        return SituationDTO.from_entity(situation, lignes)


class ListSituationsUseCase:
    """Use case pour lister les situations d'un chantier."""

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository

    def execute(self, chantier_id: int) -> List[SituationDTO]:
        """Liste les situations d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des DTOs de situations avec leurs lignes.
        """
        situations = self._situation_repository.find_by_chantier_id(chantier_id)
        result = []
        for situation in situations:
            lignes = self._ligne_repository.find_by_situation_id(situation.id)
            result.append(SituationDTO.from_entity(situation, lignes))
        return result


class DeleteSituationUseCase:
    """Use case pour supprimer une situation de travaux."""

    def __init__(
        self,
        situation_repository: SituationRepository,
        ligne_repository: LigneSituationRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._situation_repository = situation_repository
        self._ligne_repository = ligne_repository
        self._journal_repository = journal_repository

    def execute(self, situation_id: int, deleted_by: int) -> None:
        """Supprime une situation de travaux (soft delete).

        Seules les situations en statut 'brouillon' peuvent etre supprimees.

        Args:
            situation_id: L'ID de la situation a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Raises:
            SituationNotFoundError: Si la situation n'existe pas.
            SituationWorkflowError: Si la situation n'est pas en brouillon.
        """
        situation = self._situation_repository.find_by_id(situation_id)
        if not situation:
            raise SituationNotFoundError(situation_id)

        if situation.statut != "brouillon":
            raise SituationWorkflowError(
                f"Impossible de supprimer une situation en statut '{situation.statut}'. "
                "Seul le statut 'brouillon' est accepte."
            )

        # Supprimer les lignes
        self._ligne_repository.delete_by_situation_id(situation_id)

        # Supprimer la situation (soft delete)
        self._situation_repository.delete(situation_id, deleted_by)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="situation",
                entite_id=situation.id,
                chantier_id=situation.chantier_id,
                action="suppression",
                details=(
                    f"Suppression de la situation {situation.numero} - "
                    f"Montant cumule HT: {situation.montant_cumule_ht} EUR"
                ),
                auteur_id=deleted_by,
                created_at=datetime.utcnow(),
            )
        )
