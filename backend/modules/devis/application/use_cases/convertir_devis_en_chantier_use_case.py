"""Use Case ConvertirDevisEnChantier - Conversion devis accepte en chantier.

DEV-16: Conversion en chantier avec budget et lots budgetaires.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Callable

from ...domain.entities.devis import (
    Devis,
    DevisValidationError,
    TransitionStatutDevisInvalideError,
)
from ...domain.entities.lot_devis import LotDevis
from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ...domain.repositories.signature_devis_repository import SignatureDevisRepository
from ...domain.value_objects import StatutDevis

# Import du port shared (pas de dependance cross-module)
from shared.application.ports.chantier_creation_port import (
    ChantierCreationPort,
    ChantierCreationData,
    BudgetCreationData,
    LotBudgetaireCreationData,
)

from ..dtos.convertir_devis_dto import ConvertirDevisOptionsDTO, ConvertirDevisResultDTO

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions metier
# ─────────────────────────────────────────────────────────────────────────────


class DevisNonConvertibleError(Exception):
    """Le devis ne remplit pas les conditions pour etre converti."""

    def __init__(self, message: str = "Le devis ne peut pas etre converti"):
        self.message = message
        super().__init__(self.message)


class DevisDejaConvertiError(Exception):
    """Le devis a deja ete converti en chantier."""

    def __init__(
        self,
        devis_id: int,
        chantier_ref: str,
        message: str = "Ce devis a deja ete converti",
    ):
        self.devis_id = devis_id
        self.chantier_ref = chantier_ref
        self.message = message
        super().__init__(self.message)


class ConversionError(Exception):
    """Erreur technique lors de la conversion."""

    def __init__(self, message: str = "Erreur lors de la conversion"):
        self.message = message
        super().__init__(self.message)


# ─────────────────────────────────────────────────────────────────────────────
# Use Case
# ─────────────────────────────────────────────────────────────────────────────


class ConvertirDevisEnChantierUseCase:
    """Cas d'utilisation : Convertir un devis accepte en chantier operationnel.

    Ce use case orchestre la creation d'un chantier, d'un budget et des lots
    budgetaires a partir d'un devis accepte. L'operation est atomique :
    si une etape echoue, rien n'est persiste (rollback gere par la route).

    Attributes:
        _devis_repo: Repository pour acceder aux devis.
        _lot_devis_repo: Repository pour acceder aux lots du devis.
        _journal_repo: Repository pour le journal d'audit.
        _chantier_creation_port: Port pour creer le chantier/budget/lots.
        _signature_repo: Repository pour verifier la signature du devis.
    """

    def __init__(
        self,
        devis_repo: DevisRepository,
        lot_devis_repo: LotDevisRepository,
        journal_repo: JournalDevisRepository,
        chantier_creation_port: ChantierCreationPort,
        signature_repo: SignatureDevisRepository,
        event_publisher: Optional[Callable] = None,
    ) -> None:
        """Initialise le use case.

        Args:
            devis_repo: Repository devis (interface).
            lot_devis_repo: Repository lots devis (interface).
            journal_repo: Repository journal d'audit (interface).
            chantier_creation_port: Port pour la creation chantier (interface).
            signature_repo: Repository signatures (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self._devis_repo = devis_repo
        self._lot_devis_repo = lot_devis_repo
        self._journal_repo = journal_repo
        self._chantier_creation_port = chantier_creation_port
        self._signature_repo = signature_repo
        self._event_publisher = event_publisher

    def execute(
        self,
        devis_id: int,
        current_user_id: int,
        options: Optional[ConvertirDevisOptionsDTO] = None,
    ) -> ConvertirDevisResultDTO:
        """Execute la conversion du devis en chantier.

        Args:
            devis_id: ID du devis a convertir.
            current_user_id: ID de l'utilisateur effectuant la conversion.
            options: Options de conversion (notifications, etc.).

        Returns:
            ConvertirDevisResultDTO contenant les identifiants crees.

        Raises:
            DevisNonConvertibleError: Si le devis n'est pas en statut accepte.
            DevisDejaConvertiError: Si le devis a deja ete converti.
            ConversionError: Si une erreur technique survient.
        """
        if options is None:
            options = ConvertirDevisOptionsDTO()

        logger.info(
            "Conversion devis en chantier demarre",
            extra={
                "event": "devis.conversion.started",
                "use_case": "ConvertirDevisEnChantierUseCase",
                "devis_id": devis_id,
                "user_id": current_user_id,
            },
        )

        try:
            # 1. Recuperer le devis
            devis = self._get_devis(devis_id)

            # 2. Valider les prerequis
            self._validate_prerequisites(devis)

            # 3. Recuperer les lots du devis
            lots_devis = self._get_lots_devis(devis_id)

            # 4. Preparer les donnees de creation
            chantier_data = self._build_chantier_data(devis)
            budget_data = self._build_budget_data(devis)
            lots_data = self._build_lots_data(lots_devis)

            # 5. Deleguer la creation au port
            result = self._chantier_creation_port.create_chantier_from_devis(
                chantier_data=chantier_data,
                budget_data=budget_data,
                lots_data=lots_data,
            )

            # 6. Marquer le devis comme converti
            devis.convertir(str(result.chantier_id))
            self._devis_repo.save(devis)

            # 7. Enregistrer l'entree journal d'audit (DEFAUT 2)
            self._log_conversion(devis, result, current_user_id)

            logger.info(
                "Conversion devis en chantier reussie",
                extra={
                    "event": "devis.conversion.succeeded",
                    "use_case": "ConvertirDevisEnChantierUseCase",
                    "devis_id": devis_id,
                    "chantier_id": result.chantier_id,
                    "chantier_code": result.code_chantier,
                    "budget_id": result.budget_id,
                    "nb_lots": result.nb_lots_transferes,
                },
            )

            return ConvertirDevisResultDTO(
                chantier_id=result.chantier_id,
                code_chantier=result.code_chantier,
                budget_id=result.budget_id,
                nb_lots_transferes=result.nb_lots_transferes,
                montant_total_ht=budget_data.montant_initial_ht,
                devis_id=devis.id,
                devis_numero=devis.numero,
            )

        except (DevisNonConvertibleError, DevisDejaConvertiError):
            raise
        except Exception as e:
            logger.error(
                "Conversion devis en chantier echouee",
                extra={
                    "event": "devis.conversion.failed",
                    "use_case": "ConvertirDevisEnChantierUseCase",
                    "devis_id": devis_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
            raise ConversionError(
                f"Erreur lors de la conversion du devis {devis_id}: {str(e)}"
            ) from e

    # ─────────────────────────────────────────────────────────────────────────
    # Methodes privees
    # ─────────────────────────────────────────────────────────────────────────

    def _get_devis(self, devis_id: int) -> Devis:
        """Recupere le devis par ID.

        Args:
            devis_id: ID du devis.

        Returns:
            L'entite Devis.

        Raises:
            DevisNonConvertibleError: Si le devis n'existe pas.
        """
        devis = self._devis_repo.find_by_id(devis_id)
        if devis is None:
            raise DevisNonConvertibleError(
                f"Le devis {devis_id} n'existe pas"
            )
        return devis

    def _validate_prerequisites(self, devis: Devis) -> None:
        """Valide que le devis peut etre converti.

        Args:
            devis: Le devis a valider.

        Raises:
            DevisDejaConvertiError: Si le devis est deja converti.
            DevisNonConvertibleError: Si le statut n'est pas ACCEPTE.
        """
        # Verifier si deja converti (statut CONVERTI ou chantier_ref deja renseigne)
        if devis.statut == StatutDevis.CONVERTI:
            raise DevisDejaConvertiError(
                devis_id=devis.id,
                chantier_ref=devis.chantier_ref or "",
                message="Ce devis a deja ete converti en chantier",
            )
        if devis.chantier_ref is not None:
            raise DevisDejaConvertiError(
                devis_id=devis.id,
                chantier_ref=devis.chantier_ref,
                message=f"Ce devis est deja lie au chantier {devis.chantier_ref}",
            )

        # Verifier que le statut est ACCEPTE
        if devis.statut != StatutDevis.ACCEPTE:
            raise DevisNonConvertibleError(
                f"Le devis doit etre accepte pour etre converti "
                f"(statut actuel: {devis.statut.label})"
            )

        # Verifier que le devis est signe (regle metier obligatoire)
        signature = self._signature_repo.find_by_devis_id(devis.id)
        if signature is None:
            raise DevisNonConvertibleError(
                "Le devis doit etre signe avant conversion en chantier"
            )

        # Verifier que le montant est positif
        if devis.montant_total_ht <= Decimal("0"):
            raise DevisNonConvertibleError(
                "Le montant du devis doit etre superieur a 0"
            )

    def _get_lots_devis(self, devis_id: int) -> list[LotDevis]:
        """Recupere les lots du devis.

        Args:
            devis_id: ID du devis.

        Returns:
            Liste des lots du devis.

        Raises:
            DevisNonConvertibleError: Si le devis n'a aucun lot.
        """
        lots = self._lot_devis_repo.find_by_devis(devis_id)
        # Filtrer les lots supprimes
        lots = [lot for lot in lots if not lot.est_supprime]
        if not lots:
            raise DevisNonConvertibleError(
                "Le devis doit contenir au moins un lot pour etre converti"
            )
        return lots

    def _build_chantier_data(self, devis: Devis) -> ChantierCreationData:
        """Construit les donnees de creation du chantier.

        Args:
            devis: Le devis source.

        Returns:
            ChantierCreationData avec les donnees mappees.
        """
        nom = devis.objet or f"Chantier {devis.client_nom}"
        adresse = devis.client_adresse or "Adresse a definir"
        conducteur_ids = [devis.conducteur_id] if devis.conducteur_id else []

        return ChantierCreationData(
            nom=nom,
            adresse=adresse,
            description=f"Chantier cree depuis le devis {devis.numero}",
            conducteur_ids=conducteur_ids,
        )

    def _build_budget_data(self, devis: Devis) -> BudgetCreationData:
        """Construit les donnees de creation du budget.

        Args:
            devis: Le devis source.

        Returns:
            BudgetCreationData avec les montants du devis.
        """
        return BudgetCreationData(
            montant_initial_ht=devis.montant_total_ht,
            retenue_garantie_pct=devis.retenue_garantie_pct,
            seuil_alerte_pct=Decimal("80"),
            seuil_validation_achat=Decimal("5000"),
            devis_id=devis.id,
        )

    def _build_lots_data(
        self, lots_devis: list[LotDevis]
    ) -> list[LotBudgetaireCreationData]:
        """Construit les donnees de creation des lots budgetaires.

        Transfere les montants reels du devis pour permettre le suivi
        des ecarts debourse/vente dans le budget operationnel.

        - prix_unitaire_ht : cout reel (debourse) du lot, utilise pour
          le suivi budgetaire des depenses.
        - prix_vente_ht : montant de vente au client, utilise pour
          calculer la marge previsionnelle.

        Si le montant de debourse n'est pas renseigne (None ou 0),
        le montant de vente est utilise en fallback pour eviter
        toute regression.

        Args:
            lots_devis: Les lots du devis source.

        Returns:
            Liste de LotBudgetaireCreationData.
        """
        return [
            LotBudgetaireCreationData(
                code_lot=lot.code_lot,
                libelle=lot.libelle,
                unite="forfait",
                quantite_prevue=Decimal("1"),
                prix_unitaire_ht=(
                    lot.montant_debourse_ht
                    if lot.montant_debourse_ht
                    else lot.montant_vente_ht or Decimal("0")
                ),
                ordre=lot.ordre,
                prix_vente_ht=lot.montant_vente_ht or Decimal("0"),
            )
            for lot in lots_devis
        ]

    def _log_conversion(
        self,
        devis: Devis,
        result: "ConversionChantierResult",
        current_user_id: int,
    ) -> None:
        """Enregistre l'entree journal d'audit pour la conversion.

        Args:
            devis: Le devis converti.
            result: Le resultat de la conversion.
            current_user_id: ID de l'utilisateur effectuant la conversion.
        """
        journal_entry = JournalDevis(
            devis_id=devis.id,
            action="conversion",
            auteur_id=current_user_id,
            details_json={
                "chantier_id": result.chantier_id,
                "code_chantier": result.code_chantier,
                "budget_id": result.budget_id,
                "nb_lots_transferes": result.nb_lots_transferes,
                "montant_total_ht": str(devis.montant_total_ht),
            },
            created_at=datetime.now(timezone.utc),
        )
        self._journal_repo.save(journal_entry)
