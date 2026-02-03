"""Use Cases pour la synchronisation Pennylane.

CONN-10: Sync factures fournisseurs.
CONN-11: Sync encaissements clients.
CONN-12: Import fournisseurs.
CONN-14: Gestion mappings analytiques.
CONN-15: Dashboard reconciliation.
"""

import logging
from datetime import datetime
from typing import List, Optional

from ..dtos.pennylane_dtos import (
    PennylaneSyncResultDTO,
    PennylanePendingReconciliationDTO,
    PennylaneMappingDTO,
    PennylaneSyncHistoryDTO,
    CreateMappingDTO,
    ResolveReconciliationDTO,
)
from ...domain.entities import (
    PennylaneSyncLog,
    PennylaneMappingAnalytique,
    PennylanePendingReconciliation,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class PennylaneSyncError(Exception):
    """Erreur lors de la synchronisation Pennylane."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ReconciliationNotFoundError(Exception):
    """Reconciliation non trouvee."""

    def __init__(self, reconciliation_id: int):
        self.reconciliation_id = reconciliation_id
        super().__init__(f"Reconciliation {reconciliation_id} non trouvee")


class ReconciliationAlreadyResolvedError(Exception):
    """Reconciliation deja resolue."""

    def __init__(self, reconciliation_id: int, status: str):
        self.reconciliation_id = reconciliation_id
        self.status = status
        super().__init__(
            f"Reconciliation {reconciliation_id} deja resolue (status: {status})"
        )


class MappingCodeExistsError(Exception):
    """Code analytique deja mappe."""

    def __init__(self, code_analytique: str):
        self.code_analytique = code_analytique
        super().__init__(f"Code analytique '{code_analytique}' deja mappe")


class MappingNotFoundError(Exception):
    """Mapping non trouve."""

    def __init__(self, mapping_id: int):
        self.mapping_id = mapping_id
        super().__init__(f"Mapping {mapping_id} non trouve")


class AchatNotFoundError(Exception):
    """Achat non trouve pour reconciliation."""

    def __init__(self, achat_id: int):
        self.achat_id = achat_id
        super().__init__(f"Achat {achat_id} non trouve")


# ─────────────────────────────────────────────────────────────────────────────
# CONN-10: Sync factures fournisseurs
# ─────────────────────────────────────────────────────────────────────────────

class SyncSupplierInvoicesUseCase:
    """Use Case: Synchroniser les factures fournisseurs depuis Pennylane.

    CONN-10: Import des factures fournisseurs payees pour calcul
    de la rentabilite reelle.
    """

    def __init__(
        self,
        sync_service,  # PennylaneSyncService
        sync_log_repository,  # PennylaneSyncLogRepository
    ):
        """Initialise le use case.

        Args:
            sync_service: Service de synchronisation Pennylane.
            sync_log_repository: Repository pour les logs de sync.
        """
        self.sync_service = sync_service
        self.sync_log_repo = sync_log_repository

    async def execute(
        self,
        updated_since: Optional[datetime] = None,
    ) -> PennylaneSyncResultDTO:
        """Execute la synchronisation des factures fournisseurs.

        Args:
            updated_since: Date depuis laquelle synchroniser (optionnel).
                          Si None, utilise la date de derniere sync.

        Returns:
            Resultat de la synchronisation.

        Raises:
            PennylaneSyncError: En cas d'erreur de synchronisation.
        """
        # Creer le log de sync
        sync_log = PennylaneSyncLog(
            sync_type="supplier_invoices",
            started_at=datetime.utcnow(),
        )
        sync_log = self.sync_log_repo.save(sync_log)

        try:
            # Si pas de date specifiee, recuperer la derniere sync
            if updated_since is None:
                last_sync = self.sync_log_repo.find_last_successful(
                    sync_type="supplier_invoices"
                )
                if last_sync:
                    updated_since = last_sync.completed_at

            # Lancer la synchronisation
            result = await self.sync_service.sync_supplier_invoices(
                updated_since=updated_since,
            )

            # Mettre a jour le log
            sync_log.marquer_complete(
                records_processed=result.records_processed,
                records_created=result.records_created,
                records_updated=result.records_updated,
                records_pending=result.records_pending,
            )

            if result.has_errors:
                sync_log.error_message = "; ".join(result.errors[:5])  # Max 5 erreurs
                if result.records_pending > 0:
                    sync_log.status = "partial"

            self.sync_log_repo.save(sync_log)

            logger.info(
                f"Sync factures fournisseurs terminee: "
                f"{result.records_processed} traites, "
                f"{result.records_updated} mis a jour, "
                f"{result.records_pending} en attente"
            )

            return PennylaneSyncResultDTO.from_result(result, sync_log.id)

        except Exception as e:
            sync_log.marquer_echec(str(e))
            self.sync_log_repo.save(sync_log)
            logger.error(f"Erreur sync factures fournisseurs: {e}")
            raise PennylaneSyncError(
                "Erreur lors de la synchronisation des factures fournisseurs",
                details=str(e),
            )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-11: Sync encaissements clients
# ─────────────────────────────────────────────────────────────────────────────

class SyncCustomerInvoicesUseCase:
    """Use Case: Synchroniser les encaissements clients depuis Pennylane.

    CONN-11: Import des paiements clients pour suivi DSO.
    """

    def __init__(
        self,
        sync_service,
        sync_log_repository,
    ):
        self.sync_service = sync_service
        self.sync_log_repo = sync_log_repository

    async def execute(
        self,
        updated_since: Optional[datetime] = None,
    ) -> PennylaneSyncResultDTO:
        """Execute la synchronisation des encaissements clients."""
        sync_log = PennylaneSyncLog(
            sync_type="customer_invoices",
            started_at=datetime.utcnow(),
        )
        sync_log = self.sync_log_repo.save(sync_log)

        try:
            if updated_since is None:
                last_sync = self.sync_log_repo.find_last_successful(
                    sync_type="customer_invoices"
                )
                if last_sync:
                    updated_since = last_sync.completed_at

            result = await self.sync_service.sync_customer_invoices(
                updated_since=updated_since,
            )

            sync_log.marquer_complete(
                records_processed=result.records_processed,
                records_created=result.records_created,
                records_updated=result.records_updated,
                records_pending=result.records_pending,
            )

            if result.has_errors:
                sync_log.error_message = "; ".join(result.errors[:5])

            self.sync_log_repo.save(sync_log)

            logger.info(
                f"Sync encaissements clients terminee: "
                f"{result.records_processed} traites, "
                f"{result.records_updated} mis a jour"
            )

            return PennylaneSyncResultDTO.from_result(result, sync_log.id)

        except Exception as e:
            sync_log.marquer_echec(str(e))
            self.sync_log_repo.save(sync_log)
            logger.error(f"Erreur sync encaissements clients: {e}")
            raise PennylaneSyncError(
                "Erreur lors de la synchronisation des encaissements",
                details=str(e),
            )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-12: Import fournisseurs
# ─────────────────────────────────────────────────────────────────────────────

class SyncSuppliersUseCase:
    """Use Case: Synchroniser les fournisseurs depuis Pennylane.

    CONN-12: Import/mise a jour des fiches fournisseurs.
    """

    def __init__(
        self,
        sync_service,
        sync_log_repository,
    ):
        self.sync_service = sync_service
        self.sync_log_repo = sync_log_repository

    async def execute(self) -> PennylaneSyncResultDTO:
        """Execute la synchronisation des fournisseurs."""
        sync_log = PennylaneSyncLog(
            sync_type="suppliers",
            started_at=datetime.utcnow(),
        )
        sync_log = self.sync_log_repo.save(sync_log)

        try:
            result = await self.sync_service.sync_suppliers()

            sync_log.marquer_complete(
                records_processed=result.records_processed,
                records_created=result.records_created,
                records_updated=result.records_updated,
                records_pending=result.records_pending,
            )

            if result.has_errors:
                sync_log.error_message = "; ".join(result.errors[:5])

            self.sync_log_repo.save(sync_log)

            logger.info(
                f"Sync fournisseurs terminee: "
                f"{result.records_processed} traites, "
                f"{result.records_created} crees, "
                f"{result.records_updated} mis a jour"
            )

            return PennylaneSyncResultDTO.from_result(result, sync_log.id)

        except Exception as e:
            sync_log.marquer_echec(str(e))
            self.sync_log_repo.save(sync_log)
            logger.error(f"Erreur sync fournisseurs: {e}")
            raise PennylaneSyncError(
                "Erreur lors de la synchronisation des fournisseurs",
                details=str(e),
            )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-15: Reconciliations en attente
# ─────────────────────────────────────────────────────────────────────────────

class GetPendingReconciliationsUseCase:
    """Use Case: Recuperer les reconciliations en attente.

    CONN-15: Dashboard de reconciliation manuelle.
    """

    def __init__(
        self,
        pending_repository,
        achat_repository,
    ):
        self.pending_repo = pending_repository
        self.achat_repo = achat_repository

    def execute(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PennylanePendingReconciliationDTO]:
        """Recupere les reconciliations en attente.

        Args:
            status: Filtrer par statut (pending, matched, rejected, manual).
            limit: Nombre max de resultats.
            offset: Offset pour pagination.

        Returns:
            Liste des reconciliations.
        """
        if status:
            pendings = self.pending_repo.find_by_status(
                status=status,
                limit=limit,
                offset=offset,
            )
        else:
            pendings = self.pending_repo.find_all(
                limit=limit,
                offset=offset,
            )

        # Enrichir avec les infos des achats suggeres
        dtos = []
        for pending in pendings:
            achat_info = None
            if pending.suggested_achat_id:
                achat = self.achat_repo.find_by_id(pending.suggested_achat_id)
                if achat:
                    achat_info = {
                        "id": achat.id,
                        "libelle": achat.libelle,
                        "montant_ht": str(achat.total_ht),
                        "date_commande": achat.date_commande.isoformat()
                        if achat.date_commande
                        else None,
                    }

            dtos.append(
                PennylanePendingReconciliationDTO.from_entity(
                    pending,
                    suggested_achat_info=achat_info,
                )
            )

        return dtos


class ResolveReconciliationUseCase:
    """Use Case: Resoudre une reconciliation en attente.

    CONN-15: Validation manuelle du matching facture -> achat.
    """

    def __init__(
        self,
        pending_repository,
        achat_repository,
    ):
        self.pending_repo = pending_repository
        self.achat_repo = achat_repository

    def execute(
        self,
        dto: ResolveReconciliationDTO,
        user_id: int,
    ) -> PennylanePendingReconciliationDTO:
        """Resout une reconciliation.

        Args:
            dto: Donnees de resolution.
            user_id: ID de l'utilisateur qui resout.

        Returns:
            La reconciliation mise a jour.

        Raises:
            ReconciliationNotFoundError: Si reconciliation non trouvee.
            ReconciliationAlreadyResolvedError: Si deja resolue.
            AchatNotFoundError: Si l'achat cible n'existe pas.
        """
        pending = self.pending_repo.find_by_id(dto.reconciliation_id)
        if not pending:
            raise ReconciliationNotFoundError(dto.reconciliation_id)

        if pending.est_resolue:
            raise ReconciliationAlreadyResolvedError(
                dto.reconciliation_id,
                pending.status,
            )

        if dto.action == "match":
            # Valider le match
            if not dto.achat_id:
                raise AchatNotFoundError(0)

            achat = self.achat_repo.find_by_id(dto.achat_id)
            if not achat:
                raise AchatNotFoundError(dto.achat_id)

            pending.valider_match(user_id, dto.achat_id)

            # Mettre a jour l'achat avec les donnees Pennylane
            achat.montant_ht_reel = pending.amount_ht
            achat.date_facture_reelle = pending.invoice_date
            achat.pennylane_invoice_id = pending.pennylane_invoice_id
            self.achat_repo.save(achat)

            logger.info(
                f"Reconciliation {dto.reconciliation_id} matchee avec achat {dto.achat_id}"
            )

        elif dto.action == "reject":
            pending.rejeter(user_id)
            logger.info(f"Reconciliation {dto.reconciliation_id} rejetee")

        elif dto.action == "manual":
            pending.creer_achat_manuel(user_id)
            logger.info(
                f"Reconciliation {dto.reconciliation_id} marquee pour creation manuelle"
            )

        self.pending_repo.save(pending)

        return PennylanePendingReconciliationDTO.from_entity(pending)


# ─────────────────────────────────────────────────────────────────────────────
# CONN-14: Gestion mappings analytiques
# ─────────────────────────────────────────────────────────────────────────────

class GetMappingsUseCase:
    """Use Case: Recuperer les mappings analytiques."""

    def __init__(self, mapping_repository, chantier_repository=None):
        self.mapping_repo = mapping_repository
        self.chantier_repo = chantier_repository

    def execute(self) -> List[PennylaneMappingDTO]:
        """Recupere tous les mappings analytiques."""
        mappings = self.mapping_repo.find_all()

        dtos = []
        for mapping in mappings:
            chantier_nom = None
            if self.chantier_repo and mapping.chantier_id:
                chantier = self.chantier_repo.find_by_id(mapping.chantier_id)
                if chantier:
                    chantier_nom = chantier.nom

            dtos.append(
                PennylaneMappingDTO.from_entity(mapping, chantier_nom=chantier_nom)
            )

        return dtos


class CreateMappingUseCase:
    """Use Case: Creer un mapping analytique."""

    def __init__(self, mapping_repository, chantier_repository=None):
        self.mapping_repo = mapping_repository
        self.chantier_repo = chantier_repository

    def execute(
        self,
        dto: CreateMappingDTO,
        user_id: int,
    ) -> PennylaneMappingDTO:
        """Cree un nouveau mapping analytique.

        Args:
            dto: Donnees du mapping.
            user_id: ID de l'utilisateur createur.

        Returns:
            Le mapping cree.

        Raises:
            MappingCodeExistsError: Si le code analytique existe deja.
        """
        # Verifier unicite du code
        existing = self.mapping_repo.find_by_code_analytique(dto.code_analytique)
        if existing:
            raise MappingCodeExistsError(dto.code_analytique)

        mapping = PennylaneMappingAnalytique(
            code_analytique=dto.code_analytique,
            chantier_id=dto.chantier_id,
            created_at=datetime.utcnow(),
            created_by=user_id,
        )

        mapping = self.mapping_repo.save(mapping)

        chantier_nom = None
        if self.chantier_repo:
            chantier = self.chantier_repo.find_by_id(dto.chantier_id)
            if chantier:
                chantier_nom = chantier.nom

        logger.info(
            f"Mapping analytique cree: {dto.code_analytique} -> chantier {dto.chantier_id}"
        )

        return PennylaneMappingDTO.from_entity(mapping, chantier_nom=chantier_nom)


class DeleteMappingUseCase:
    """Use Case: Supprimer un mapping analytique."""

    def __init__(self, mapping_repository):
        self.mapping_repo = mapping_repository

    def execute(self, mapping_id: int) -> bool:
        """Supprime un mapping analytique.

        Args:
            mapping_id: ID du mapping a supprimer.

        Returns:
            True si supprime.

        Raises:
            MappingNotFoundError: Si le mapping n'existe pas.
        """
        mapping = self.mapping_repo.find_by_id(mapping_id)
        if not mapping:
            raise MappingNotFoundError(mapping_id)

        self.mapping_repo.delete(mapping_id)
        logger.info(f"Mapping analytique {mapping_id} supprime")

        return True


# ─────────────────────────────────────────────────────────────────────────────
# Historique des synchronisations
# ─────────────────────────────────────────────────────────────────────────────

class GetSyncHistoryUseCase:
    """Use Case: Recuperer l'historique des synchronisations."""

    def __init__(self, sync_log_repository):
        self.sync_log_repo = sync_log_repository

    def execute(
        self,
        sync_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[PennylaneSyncHistoryDTO]:
        """Recupere l'historique des synchronisations.

        Args:
            sync_type: Filtrer par type (supplier_invoices, customer_invoices, suppliers).
            limit: Nombre max de resultats.
            offset: Offset pour pagination.

        Returns:
            Liste des logs de synchronisation.
        """
        if sync_type:
            logs = self.sync_log_repo.find_by_type(
                sync_type=sync_type,
                limit=limit,
                offset=offset,
            )
        else:
            logs = self.sync_log_repo.find_all(
                limit=limit,
                offset=offset,
            )

        return [PennylaneSyncHistoryDTO.from_entity(log) for log in logs]
