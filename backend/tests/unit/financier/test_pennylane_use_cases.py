"""Tests unitaires pour les Use Cases Pennylane du module Financier.

CONN-10: Tests pour SyncSupplierInvoicesUseCase.
CONN-11: Tests pour SyncCustomerInvoicesUseCase.
CONN-12: Tests pour SyncSuppliersUseCase.
CONN-14: Tests pour CreateMappingUseCase, GetMappingsUseCase, DeleteMappingUseCase.
CONN-15: Tests pour GetPendingReconciliationsUseCase, ResolveReconciliationUseCase.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch

from modules.financier.domain.entities import (
    Achat,
    PennylaneSyncLog,
    PennylaneMappingAnalytique,
    PennylanePendingReconciliation,
)
from modules.financier.application.dtos.pennylane_dtos import (
    CreateMappingDTO,
    ResolveReconciliationDTO,
)
from modules.financier.application.use_cases.pennylane_sync_use_cases import (
    SyncSupplierInvoicesUseCase,
    SyncCustomerInvoicesUseCase,
    SyncSuppliersUseCase,
    GetPendingReconciliationsUseCase,
    ResolveReconciliationUseCase,
    GetMappingsUseCase,
    CreateMappingUseCase,
    DeleteMappingUseCase,
    GetSyncHistoryUseCase,
    PennylaneSyncError,
    ReconciliationNotFoundError,
    ReconciliationAlreadyResolvedError,
    MappingCodeExistsError,
    MappingNotFoundError,
    AchatNotFoundError,
)
from shared.infrastructure.connectors.pennylane.sync_service import SyncResult


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures et helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _make_sync_result(**kwargs):
    """Cree un SyncResult avec des valeurs par defaut."""
    defaults = {
        "sync_type": "supplier_invoices",
        "records_processed": 100,
        "records_created": 20,
        "records_updated": 70,
        "records_pending": 10,
        "errors": [],
        "started_at": datetime(2026, 2, 1, 10, 0, 0),
        "completed_at": datetime(2026, 2, 1, 10, 1, 30),
    }
    defaults.update(kwargs)
    return SyncResult(**defaults)


def _make_sync_log(**kwargs):
    """Cree un PennylaneSyncLog avec des valeurs par defaut."""
    defaults = {
        "sync_type": "supplier_invoices",
        "started_at": datetime(2026, 2, 1, 10, 0, 0),
    }
    defaults.update(kwargs)
    log = PennylaneSyncLog(**defaults)
    log.id = kwargs.get("id", 1)
    return log


def _make_achat(**kwargs):
    """Cree un Achat avec des valeurs par defaut."""
    defaults = {
        "chantier_id": 100,
        "libelle": "Ciment CEM II 25kg",
        "quantite": Decimal("10"),
        "prix_unitaire_ht": Decimal("100"),
        "taux_tva": Decimal("20"),
    }
    defaults.update(kwargs)
    achat = Achat(**defaults)
    achat.id = kwargs.get("id", 1)
    return achat


def _make_pending(**kwargs):
    """Cree un PennylanePendingReconciliation avec des valeurs par defaut."""
    defaults = {
        "pennylane_invoice_id": "pl-inv-123",
        "supplier_name": "Materiaux du Sud",
        "amount_ht": Decimal("1500"),
        "code_analytique": "MONTMELIAN",
        "invoice_date": date(2026, 2, 1),
    }
    defaults.update(kwargs)
    pending = PennylanePendingReconciliation(**defaults)
    pending.id = kwargs.get("id", 1)
    return pending


def _make_mapping(**kwargs):
    """Cree un PennylaneMappingAnalytique avec des valeurs par defaut."""
    defaults = {
        "code_analytique": "MONTMELIAN",
        "chantier_id": 100,
        "created_at": datetime(2026, 2, 1),
        "created_by": 5,
    }
    defaults.update(kwargs)
    mapping = PennylaneMappingAnalytique(**defaults)
    mapping.id = kwargs.get("id", 1)
    return mapping


# ═══════════════════════════════════════════════════════════════════════════════
# Tests SyncSupplierInvoicesUseCase (CONN-10)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSyncSupplierInvoicesUseCase:
    """Tests pour le use case de sync factures fournisseurs."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sync_service = AsyncMock()
        self.mock_sync_log_repo = Mock()
        self.use_case = SyncSupplierInvoicesUseCase(
            sync_service=self.mock_sync_service,
            sync_log_repository=self.mock_sync_log_repo,
        )

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test: execution reussie de la synchronisation."""
        # Arrange
        sync_result = _make_sync_result()
        self.mock_sync_service.sync_supplier_invoices.return_value = sync_result

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect
        self.mock_sync_log_repo.find_last_successful.return_value = None

        # Act
        result = await self.use_case.execute()

        # Assert
        assert result.sync_id == 1
        assert result.sync_type == "supplier_invoices"
        assert result.records_processed == 100
        self.mock_sync_service.sync_supplier_invoices.assert_called_once()
        assert self.mock_sync_log_repo.save.call_count == 2  # Create + update

    @pytest.mark.asyncio
    async def test_execute_with_updated_since(self):
        """Test: execution avec date de derniere sync."""
        # Arrange
        sync_result = _make_sync_result()
        self.mock_sync_service.sync_supplier_invoices.return_value = sync_result

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect
        updated_since = datetime(2026, 1, 15, 0, 0, 0)

        # Act
        result = await self.use_case.execute(updated_since=updated_since)

        # Assert
        self.mock_sync_service.sync_supplier_invoices.assert_called_once_with(
            updated_since=updated_since
        )

    @pytest.mark.asyncio
    async def test_execute_uses_last_sync_date(self):
        """Test: utilise la date de derniere sync si pas specifiee."""
        # Arrange
        sync_result = _make_sync_result()
        self.mock_sync_service.sync_supplier_invoices.return_value = sync_result

        last_sync = _make_sync_log()
        last_sync.completed_at = datetime(2026, 1, 20, 12, 0, 0)
        self.mock_sync_log_repo.find_last_successful.return_value = last_sync

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect

        # Act
        await self.use_case.execute()

        # Assert
        self.mock_sync_service.sync_supplier_invoices.assert_called_once_with(
            updated_since=last_sync.completed_at
        )

    @pytest.mark.asyncio
    async def test_execute_with_errors(self):
        """Test: execution avec erreurs enregistre les erreurs."""
        # Arrange
        sync_result = _make_sync_result(
            errors=["Erreur 1", "Erreur 2"],
            records_pending=10,
        )
        self.mock_sync_service.sync_supplier_invoices.return_value = sync_result

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect
        self.mock_sync_log_repo.find_last_successful.return_value = None

        # Act
        result = await self.use_case.execute()

        # Assert
        assert result.records_pending == 10
        # Le log devrait avoir les erreurs
        saved_log = self.mock_sync_log_repo.save.call_args_list[-1][0][0]
        assert saved_log.error_message is not None

    @pytest.mark.asyncio
    async def test_execute_failure_marks_log_failed(self):
        """Test: echec de sync marque le log comme failed."""
        # Arrange
        self.mock_sync_service.sync_supplier_invoices.side_effect = Exception(
            "API Error"
        )

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect
        self.mock_sync_log_repo.find_last_successful.return_value = None

        # Act & Assert
        with pytest.raises(PennylaneSyncError) as exc_info:
            await self.use_case.execute()

        assert "factures fournisseurs" in exc_info.value.message
        saved_log = self.mock_sync_log_repo.save.call_args_list[-1][0][0]
        assert saved_log.status == "failed"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests SyncCustomerInvoicesUseCase (CONN-11)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSyncCustomerInvoicesUseCase:
    """Tests pour le use case de sync encaissements clients."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sync_service = AsyncMock()
        self.mock_sync_log_repo = Mock()
        self.use_case = SyncCustomerInvoicesUseCase(
            sync_service=self.mock_sync_service,
            sync_log_repository=self.mock_sync_log_repo,
        )

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test: execution reussie de la synchronisation."""
        # Arrange
        sync_result = _make_sync_result(sync_type="customer_invoices")
        self.mock_sync_service.sync_customer_invoices.return_value = sync_result

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect
        self.mock_sync_log_repo.find_last_successful.return_value = None

        # Act
        result = await self.use_case.execute()

        # Assert
        assert result.sync_type == "customer_invoices"
        self.mock_sync_service.sync_customer_invoices.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """Test: echec de sync leve une exception."""
        # Arrange
        self.mock_sync_service.sync_customer_invoices.side_effect = Exception(
            "Network Error"
        )

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect
        self.mock_sync_log_repo.find_last_successful.return_value = None

        # Act & Assert
        with pytest.raises(PennylaneSyncError) as exc_info:
            await self.use_case.execute()

        assert "encaissements" in exc_info.value.message


# ═══════════════════════════════════════════════════════════════════════════════
# Tests SyncSuppliersUseCase (CONN-12)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSyncSuppliersUseCase:
    """Tests pour le use case de sync fournisseurs."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sync_service = AsyncMock()
        self.mock_sync_log_repo = Mock()
        self.use_case = SyncSuppliersUseCase(
            sync_service=self.mock_sync_service,
            sync_log_repository=self.mock_sync_log_repo,
        )

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test: execution reussie de la synchronisation."""
        # Arrange
        sync_result = _make_sync_result(
            sync_type="suppliers",
            records_processed=50,
            records_created=10,
            records_updated=40,
            records_pending=0,
        )
        self.mock_sync_service.sync_suppliers.return_value = sync_result

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect

        # Act
        result = await self.use_case.execute()

        # Assert
        assert result.sync_type == "suppliers"
        assert result.records_created == 10
        assert result.records_updated == 40
        self.mock_sync_service.sync_suppliers.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """Test: echec de sync leve une exception."""
        # Arrange
        self.mock_sync_service.sync_suppliers.side_effect = Exception("API Error")

        def save_side_effect(log):
            log.id = 1
            return log

        self.mock_sync_log_repo.save.side_effect = save_side_effect

        # Act & Assert
        with pytest.raises(PennylaneSyncError) as exc_info:
            await self.use_case.execute()

        assert "fournisseurs" in exc_info.value.message


# ═══════════════════════════════════════════════════════════════════════════════
# Tests GetPendingReconciliationsUseCase (CONN-15)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetPendingReconciliationsUseCase:
    """Tests pour le use case de recuperation des reconciliations."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_pending_repo = Mock()
        self.mock_achat_repo = Mock()
        self.use_case = GetPendingReconciliationsUseCase(
            pending_repository=self.mock_pending_repo,
            achat_repository=self.mock_achat_repo,
        )

    def test_execute_all_pendings(self):
        """Test: recupere toutes les reconciliations."""
        # Arrange
        pendings = [_make_pending(id=1), _make_pending(id=2, pennylane_invoice_id="pl-inv-456")]
        self.mock_pending_repo.find_all.return_value = pendings
        self.mock_achat_repo.find_by_id.return_value = None

        # Act
        result = self.use_case.execute()

        # Assert
        assert len(result) == 2
        self.mock_pending_repo.find_all.assert_called_once_with(limit=50, offset=0)

    def test_execute_filter_by_status(self):
        """Test: filtre par statut."""
        # Arrange
        pendings = [_make_pending(id=1)]
        self.mock_pending_repo.find_by_status.return_value = pendings
        self.mock_achat_repo.find_by_id.return_value = None

        # Act
        result = self.use_case.execute(status="pending")

        # Assert
        assert len(result) == 1
        self.mock_pending_repo.find_by_status.assert_called_once_with(
            status="pending", limit=50, offset=0
        )

    def test_execute_with_suggested_achat(self):
        """Test: enrichit avec les infos de l'achat suggere."""
        # Arrange
        pending = _make_pending(id=1, suggested_achat_id=100)
        self.mock_pending_repo.find_all.return_value = [pending]

        achat = _make_achat(id=100, date_commande=date(2026, 1, 15))
        self.mock_achat_repo.find_by_id.return_value = achat

        # Act
        result = self.use_case.execute()

        # Assert
        assert len(result) == 1
        assert result[0].suggested_achat_info is not None
        assert result[0].suggested_achat_info["id"] == 100
        assert result[0].suggested_achat_info["libelle"] == "Ciment CEM II 25kg"

    def test_execute_pagination(self):
        """Test: pagination fonctionne."""
        # Arrange
        self.mock_pending_repo.find_all.return_value = []
        self.mock_achat_repo.find_by_id.return_value = None

        # Act
        self.use_case.execute(limit=20, offset=10)

        # Assert
        self.mock_pending_repo.find_all.assert_called_once_with(limit=20, offset=10)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests ResolveReconciliationUseCase (CONN-15)
# ═══════════════════════════════════════════════════════════════════════════════

class TestResolveReconciliationUseCase:
    """Tests pour le use case de resolution des reconciliations."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_pending_repo = Mock()
        self.mock_achat_repo = Mock()
        self.use_case = ResolveReconciliationUseCase(
            pending_repository=self.mock_pending_repo,
            achat_repository=self.mock_achat_repo,
        )

    def test_execute_match_success(self):
        """Test: match reussi met a jour l'achat."""
        # Arrange
        pending = _make_pending(id=1, amount_ht=Decimal("1500"))
        achat = _make_achat(id=100)

        self.mock_pending_repo.find_by_id.return_value = pending
        self.mock_achat_repo.find_by_id.return_value = achat
        self.mock_pending_repo.save.return_value = pending
        self.mock_achat_repo.save.return_value = achat

        dto = ResolveReconciliationDTO(
            reconciliation_id=1,
            action="match",
            achat_id=100,
        )

        # Act
        result = self.use_case.execute(dto, user_id=5)

        # Assert
        assert result.status == "matched"
        self.mock_achat_repo.save.assert_called_once()
        # Verifier que l'achat a ete mis a jour avec les donnees Pennylane
        saved_achat = self.mock_achat_repo.save.call_args[0][0]
        assert saved_achat.montant_ht_reel == Decimal("1500")
        assert saved_achat.pennylane_invoice_id == "pl-inv-123"

    def test_execute_match_pending_not_found(self):
        """Test: erreur si reconciliation non trouvee."""
        # Arrange
        self.mock_pending_repo.find_by_id.return_value = None

        dto = ResolveReconciliationDTO(
            reconciliation_id=999,
            action="match",
            achat_id=100,
        )

        # Act & Assert
        with pytest.raises(ReconciliationNotFoundError):
            self.use_case.execute(dto, user_id=5)

    def test_execute_match_already_resolved(self):
        """Test: erreur si reconciliation deja resolue."""
        # Arrange
        pending = _make_pending(id=1)
        pending.valider_match(resolved_by=5, achat_id=100)

        self.mock_pending_repo.find_by_id.return_value = pending

        dto = ResolveReconciliationDTO(
            reconciliation_id=1,
            action="match",
            achat_id=200,
        )

        # Act & Assert
        with pytest.raises(ReconciliationAlreadyResolvedError):
            self.use_case.execute(dto, user_id=6)

    def test_execute_match_achat_not_found(self):
        """Test: erreur si achat non trouve."""
        # Arrange
        pending = _make_pending(id=1)
        self.mock_pending_repo.find_by_id.return_value = pending
        self.mock_achat_repo.find_by_id.return_value = None

        dto = ResolveReconciliationDTO(
            reconciliation_id=1,
            action="match",
            achat_id=999,
        )

        # Act & Assert
        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(dto, user_id=5)

    def test_execute_match_no_achat_id(self):
        """Test: erreur si action match sans achat_id."""
        # Arrange
        pending = _make_pending(id=1)
        self.mock_pending_repo.find_by_id.return_value = pending

        dto = ResolveReconciliationDTO(
            reconciliation_id=1,
            action="match",
            achat_id=None,
        )

        # Act & Assert
        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(dto, user_id=5)

    def test_execute_reject_success(self):
        """Test: reject reussi."""
        # Arrange
        pending = _make_pending(id=1)
        self.mock_pending_repo.find_by_id.return_value = pending
        self.mock_pending_repo.save.return_value = pending

        dto = ResolveReconciliationDTO(
            reconciliation_id=1,
            action="reject",
        )

        # Act
        result = self.use_case.execute(dto, user_id=5)

        # Assert
        assert result.status == "rejected"
        self.mock_pending_repo.save.assert_called_once()

    def test_execute_manual_success(self):
        """Test: manual reussi."""
        # Arrange
        pending = _make_pending(id=1)
        self.mock_pending_repo.find_by_id.return_value = pending
        self.mock_pending_repo.save.return_value = pending

        dto = ResolveReconciliationDTO(
            reconciliation_id=1,
            action="manual",
        )

        # Act
        result = self.use_case.execute(dto, user_id=5)

        # Assert
        assert result.status == "manual"
        self.mock_pending_repo.save.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# Tests GetMappingsUseCase (CONN-14)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetMappingsUseCase:
    """Tests pour le use case de recuperation des mappings."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_mapping_repo = Mock()
        self.mock_chantier_repo = Mock()
        self.use_case = GetMappingsUseCase(
            mapping_repository=self.mock_mapping_repo,
            chantier_repository=self.mock_chantier_repo,
        )

    def test_execute_returns_all_mappings(self):
        """Test: retourne tous les mappings."""
        # Arrange
        mappings = [
            _make_mapping(id=1, code_analytique="MONTMELIAN", chantier_id=100),
            _make_mapping(id=2, code_analytique="CHAMBERY", chantier_id=200),
        ]
        self.mock_mapping_repo.find_all.return_value = mappings
        self.mock_chantier_repo.find_by_id.return_value = None

        # Act
        result = self.use_case.execute()

        # Assert
        assert len(result) == 2
        assert result[0].code_analytique == "MONTMELIAN"
        assert result[1].code_analytique == "CHAMBERY"

    def test_execute_enriches_with_chantier_name(self):
        """Test: enrichit avec le nom du chantier."""
        # Arrange
        mapping = _make_mapping(id=1, code_analytique="MONTMELIAN", chantier_id=100)
        self.mock_mapping_repo.find_all.return_value = [mapping]

        # Mock chantier
        mock_chantier = Mock()
        mock_chantier.nom = "Residence Montmelian"
        self.mock_chantier_repo.find_by_id.return_value = mock_chantier

        # Act
        result = self.use_case.execute()

        # Assert
        assert len(result) == 1
        assert result[0].chantier_nom == "Residence Montmelian"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests CreateMappingUseCase (CONN-14)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreateMappingUseCase:
    """Tests pour le use case de creation de mapping."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_mapping_repo = Mock()
        self.mock_chantier_repo = Mock()
        self.use_case = CreateMappingUseCase(
            mapping_repository=self.mock_mapping_repo,
            chantier_repository=self.mock_chantier_repo,
        )

    def test_execute_success(self):
        """Test: creation reussie d'un mapping."""
        # Arrange
        self.mock_mapping_repo.find_by_code_analytique.return_value = None

        def save_side_effect(mapping):
            mapping.id = 1
            return mapping

        self.mock_mapping_repo.save.side_effect = save_side_effect
        self.mock_chantier_repo.find_by_id.return_value = None

        dto = CreateMappingDTO(
            code_analytique="MONTMELIAN",
            chantier_id=100,
        )

        # Act
        result = self.use_case.execute(dto, user_id=5)

        # Assert
        assert result.id == 1
        assert result.code_analytique == "MONTMELIAN"
        assert result.chantier_id == 100
        self.mock_mapping_repo.save.assert_called_once()

    def test_execute_code_already_exists(self):
        """Test: erreur si code analytique deja existe."""
        # Arrange
        existing = _make_mapping(id=1, code_analytique="MONTMELIAN")
        self.mock_mapping_repo.find_by_code_analytique.return_value = existing

        dto = CreateMappingDTO(
            code_analytique="MONTMELIAN",
            chantier_id=100,
        )

        # Act & Assert
        with pytest.raises(MappingCodeExistsError):
            self.use_case.execute(dto, user_id=5)

    def test_execute_enriches_with_chantier_name(self):
        """Test: enrichit avec le nom du chantier."""
        # Arrange
        self.mock_mapping_repo.find_by_code_analytique.return_value = None

        def save_side_effect(mapping):
            mapping.id = 1
            return mapping

        self.mock_mapping_repo.save.side_effect = save_side_effect

        mock_chantier = Mock()
        mock_chantier.nom = "Residence Montmelian"
        self.mock_chantier_repo.find_by_id.return_value = mock_chantier

        dto = CreateMappingDTO(
            code_analytique="MONTMELIAN",
            chantier_id=100,
        )

        # Act
        result = self.use_case.execute(dto, user_id=5)

        # Assert
        assert result.chantier_nom == "Residence Montmelian"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests DeleteMappingUseCase (CONN-14)
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeleteMappingUseCase:
    """Tests pour le use case de suppression de mapping."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_mapping_repo = Mock()
        self.use_case = DeleteMappingUseCase(
            mapping_repository=self.mock_mapping_repo,
        )

    def test_execute_success(self):
        """Test: suppression reussie d'un mapping."""
        # Arrange
        mapping = _make_mapping(id=1)
        self.mock_mapping_repo.find_by_id.return_value = mapping

        # Act
        result = self.use_case.execute(mapping_id=1)

        # Assert
        assert result is True
        self.mock_mapping_repo.delete.assert_called_once_with(1)

    def test_execute_not_found(self):
        """Test: erreur si mapping non trouve."""
        # Arrange
        self.mock_mapping_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(MappingNotFoundError):
            self.use_case.execute(mapping_id=999)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests GetSyncHistoryUseCase
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetSyncHistoryUseCase:
    """Tests pour le use case de recuperation de l'historique des syncs."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_sync_log_repo = Mock()
        self.use_case = GetSyncHistoryUseCase(
            sync_log_repository=self.mock_sync_log_repo,
        )

    def test_execute_all_logs(self):
        """Test: recupere tous les logs."""
        # Arrange
        logs = [
            _make_sync_log(id=1, sync_type="supplier_invoices"),
            _make_sync_log(id=2, sync_type="customer_invoices"),
        ]
        for log in logs:
            log.marquer_complete(records_processed=100)
        self.mock_sync_log_repo.find_all.return_value = logs

        # Act
        result = self.use_case.execute()

        # Assert
        assert len(result) == 2
        self.mock_sync_log_repo.find_all.assert_called_once_with(limit=20, offset=0)

    def test_execute_filter_by_type(self):
        """Test: filtre par type de sync."""
        # Arrange
        logs = [_make_sync_log(id=1, sync_type="supplier_invoices")]
        logs[0].marquer_complete(records_processed=100)
        self.mock_sync_log_repo.find_by_type.return_value = logs

        # Act
        result = self.use_case.execute(sync_type="supplier_invoices")

        # Assert
        assert len(result) == 1
        self.mock_sync_log_repo.find_by_type.assert_called_once_with(
            sync_type="supplier_invoices", limit=20, offset=0
        )

    def test_execute_pagination(self):
        """Test: pagination fonctionne."""
        # Arrange
        self.mock_sync_log_repo.find_all.return_value = []

        # Act
        self.use_case.execute(limit=10, offset=5)

        # Assert
        self.mock_sync_log_repo.find_all.assert_called_once_with(limit=10, offset=5)
