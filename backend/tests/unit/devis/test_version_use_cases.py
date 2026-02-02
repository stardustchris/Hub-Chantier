"""Tests unitaires pour les Use Cases de versioning de devis.

DEV-08: Variantes et revisions.
Couche Application - version_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from modules.devis.domain.entities.devis import Devis, DevisValidationError
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.comparatif_devis import ComparatifDevis
from modules.devis.domain.entities.comparatif_ligne import ComparatifLigne
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.type_version import TypeVersion
from modules.devis.domain.value_objects.type_ecart import TypeEcart
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.debourse_detail_repository import DebourseDetailRepository
from modules.devis.domain.repositories.comparatif_repository import ComparatifRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.version_use_cases import (
    CreerRevisionUseCase,
    CreerVarianteUseCase,
    ListerVersionsUseCase,
    GenererComparatifUseCase,
    GetComparatifUseCase,
    FigerVersionUseCase,
    VersionFigeeError,
)
from modules.devis.application.dtos.version_dtos import (
    CreerRevisionDTO,
    CreerVarianteDTO,
    FigerVersionDTO,
    VersionDTO,
    ComparatifDTO,
)


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation bureau",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("10000"),
        "montant_total_ttc": Decimal("12000"),
        "taux_marge_global": Decimal("15"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests CreerRevisionUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestCreerRevisionUseCase:
    """Tests pour le use case de creation de revision."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreerRevisionUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_creer_revision_success(self):
        """Test: creation de revision reussie."""
        devis_source = _make_devis(id=1, version_figee=False)
        nouveau_devis = _make_devis(
            id=2, numero="DEV-2026-001-R2", devis_parent_id=1,
            numero_version=2, type_version=TypeVersion.REVISION,
        )

        self.mock_devis_repo.find_by_id.return_value = devis_source
        self.mock_devis_repo.get_next_version_number.return_value = 2
        self.mock_devis_repo.save.return_value = nouveau_devis
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreerRevisionDTO(commentaire="Revision apres negociation")
        result = self.use_case.execute(devis_id=1, dto=dto, created_by=1)

        assert isinstance(result, VersionDTO)
        assert self.mock_devis_repo.save.called
        assert self.mock_journal_repo.save.called

    def test_creer_revision_not_found(self):
        """Test: erreur si devis source non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = CreerRevisionDTO()
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto, created_by=1)

    def test_creer_revision_fige_version_precedente(self):
        """Test: la version precedente est figee automatiquement."""
        devis_source = _make_devis(id=1, version_figee=False)
        nouveau_devis = _make_devis(
            id=2, numero="DEV-2026-001-R2", devis_parent_id=1,
            numero_version=2, type_version=TypeVersion.REVISION,
        )

        self.mock_devis_repo.find_by_id.return_value = devis_source
        self.mock_devis_repo.get_next_version_number.return_value = 2
        self.mock_devis_repo.save.return_value = nouveau_devis
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreerRevisionDTO()
        self.use_case.execute(devis_id=1, dto=dto, created_by=1)

        # La version source devrait avoir ete figee
        assert devis_source.version_figee is True


# ─────────────────────────────────────────────────────────────────────────────
# Tests CreerVarianteUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestCreerVarianteUseCase:
    """Tests pour le use case de creation de variante."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CreerVarianteUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_creer_variante_eco_success(self):
        """Test: creation variante ECO reussie."""
        devis_source = _make_devis(id=1)
        nouveau_devis = _make_devis(
            id=2, numero="DEV-2026-001-ECO", devis_parent_id=1,
            type_version=TypeVersion.VARIANTE, label_variante="ECO",
        )

        self.mock_devis_repo.find_by_id.return_value = devis_source
        self.mock_devis_repo.get_next_version_number.return_value = 2
        self.mock_devis_repo.save.return_value = nouveau_devis
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreerVarianteDTO(label_variante="ECO", commentaire="Version economique")
        result = self.use_case.execute(devis_id=1, dto=dto, created_by=1)

        assert isinstance(result, VersionDTO)

    def test_creer_variante_label_vide(self):
        """Test: erreur si label variante vide."""
        dto = CreerVarianteDTO(label_variante="")
        with pytest.raises(ValueError, match="label.*obligatoire"):
            self.use_case.execute(devis_id=1, dto=dto, created_by=1)

    def test_creer_variante_label_invalide(self):
        """Test: erreur si label variante non autorise."""
        dto = CreerVarianteDTO(label_variante="ULTRA")
        with pytest.raises(ValueError, match="invalide"):
            self.use_case.execute(devis_id=1, dto=dto, created_by=1)

    def test_creer_variante_not_found(self):
        """Test: erreur si devis source non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = CreerVarianteDTO(label_variante="STD")
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto, created_by=1)

    def test_creer_variante_labels_valides(self):
        """Test: tous les labels valides sont acceptes."""
        for label in ["ECO", "STD", "PREM", "ALT"]:
            devis_source = _make_devis(id=1)
            nouveau_devis = _make_devis(
                id=2, numero=f"DEV-2026-001-{label}",
                devis_parent_id=1, type_version=TypeVersion.VARIANTE,
                label_variante=label,
            )

            self.mock_devis_repo.find_by_id.return_value = devis_source
            self.mock_devis_repo.get_next_version_number.return_value = 2
            self.mock_devis_repo.save.return_value = nouveau_devis
            self.mock_lot_repo.find_by_devis.return_value = []
            self.mock_journal_repo.save.return_value = Mock()

            dto = CreerVarianteDTO(label_variante=label)
            result = self.use_case.execute(devis_id=1, dto=dto, created_by=1)
            assert isinstance(result, VersionDTO)

    def test_creer_variante_label_case_insensitive(self):
        """Test: le label est normalise en majuscules."""
        devis_source = _make_devis(id=1)
        nouveau_devis = _make_devis(
            id=2, numero="DEV-2026-001-ECO", devis_parent_id=1,
            type_version=TypeVersion.VARIANTE, label_variante="ECO",
        )

        self.mock_devis_repo.find_by_id.return_value = devis_source
        self.mock_devis_repo.get_next_version_number.return_value = 2
        self.mock_devis_repo.save.return_value = nouveau_devis
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_journal_repo.save.return_value = Mock()

        dto = CreerVarianteDTO(label_variante="eco")
        result = self.use_case.execute(devis_id=1, dto=dto, created_by=1)
        assert isinstance(result, VersionDTO)


# ─────────────────────────────────────────────────────────────────────────────
# Tests ListerVersionsUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestListerVersionsUseCase:
    """Tests pour le use case de listage des versions."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.use_case = ListerVersionsUseCase(
            devis_repository=self.mock_devis_repo,
        )

    def test_lister_versions_success(self):
        """Test: listage des versions reussi."""
        devis_original = _make_devis(id=1)
        devis_rev = _make_devis(
            id=2, numero="DEV-2026-001-R2", devis_parent_id=1,
            type_version=TypeVersion.REVISION, numero_version=2,
        )

        self.mock_devis_repo.find_by_id.return_value = devis_original
        self.mock_devis_repo.find_versions.return_value = [devis_original, devis_rev]

        result = self.use_case.execute(devis_id=1)

        assert len(result) == 2
        assert all(isinstance(v, VersionDTO) for v in result)

    def test_lister_versions_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_lister_versions_devis_seul(self):
        """Test: un seul devis sans versions."""
        devis = _make_devis(id=1)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.find_versions.return_value = [devis]

        result = self.use_case.execute(devis_id=1)

        assert len(result) == 1


# ─────────────────────────────────────────────────────────────────────────────
# Tests GenererComparatifUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGenererComparatifUseCase:
    """Tests pour le use case de generation de comparatif."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_comparatif_repo = Mock(spec=ComparatifRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = GenererComparatifUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            comparatif_repository=self.mock_comparatif_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_generer_comparatif_success(self):
        """Test: generation de comparatif reussie (devis sans lignes)."""
        devis_source = _make_devis(id=1, montant_total_ht=Decimal("10000"))
        devis_cible = _make_devis(
            id=2, numero="DEV-2026-001-R2",
            montant_total_ht=Decimal("12000"),
            montant_total_ttc=Decimal("14400"),
        )
        comparatif = ComparatifDevis(
            id=1,
            devis_source_id=1,
            devis_cible_id=2,
            ecart_montant_ht=Decimal("2000"),
            ecart_montant_ttc=Decimal("2400"),
            ecart_marge_pct=Decimal("0"),
            ecart_debourse_total=Decimal("0"),
            nb_lignes_ajoutees=0,
            nb_lignes_supprimees=0,
            nb_lignes_modifiees=0,
            nb_lignes_identiques=0,
            created_at=datetime.utcnow(),
        )

        self.mock_devis_repo.find_by_id.side_effect = lambda did: (
            devis_source if did == 1 else devis_cible
        )
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_comparatif_repo.save.return_value = comparatif
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(
            devis_source_id=1, devis_cible_id=2, genere_par=1
        )

        assert isinstance(result, ComparatifDTO)
        self.mock_comparatif_repo.save.assert_called_once()
        # Journal pour les deux devis
        assert self.mock_journal_repo.save.call_count == 2

    def test_generer_comparatif_meme_devis(self):
        """Test: erreur si meme devis source et cible."""
        with pytest.raises(ValueError, match="differents"):
            self.use_case.execute(
                devis_source_id=1, devis_cible_id=1, genere_par=1
            )

    def test_generer_comparatif_source_not_found(self):
        """Test: erreur si devis source non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(
                devis_source_id=999, devis_cible_id=2, genere_par=1
            )

    def test_generer_comparatif_cible_not_found(self):
        """Test: erreur si devis cible non trouve."""
        devis_source = _make_devis(id=1)
        self.mock_devis_repo.find_by_id.side_effect = lambda did: (
            devis_source if did == 1 else None
        )

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(
                devis_source_id=1, devis_cible_id=999, genere_par=1
            )


# ─────────────────────────────────────────────────────────────────────────────
# Tests GetComparatifUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGetComparatifUseCase:
    """Tests pour le use case de recuperation de comparatif."""

    def setup_method(self):
        self.mock_comparatif_repo = Mock(spec=ComparatifRepository)
        self.use_case = GetComparatifUseCase(
            comparatif_repository=self.mock_comparatif_repo,
        )

    def test_get_comparatif_success(self):
        """Test: recuperation reussie."""
        comparatif = ComparatifDevis(
            id=1, devis_source_id=1, devis_cible_id=2,
            created_at=datetime.utcnow(),
        )
        self.mock_comparatif_repo.find_by_id.return_value = comparatif

        result = self.use_case.execute(comparatif_id=1)

        assert isinstance(result, ComparatifDTO)
        self.mock_comparatif_repo.find_by_id.assert_called_once_with(1)

    def test_get_comparatif_not_found(self):
        """Test: erreur si comparatif non trouve."""
        self.mock_comparatif_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="non trouve"):
            self.use_case.execute(comparatif_id=999)


# ─────────────────────────────────────────────────────────────────────────────
# Tests FigerVersionUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestFigerVersionUseCase:
    """Tests pour le use case de gel de version."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = FigerVersionUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_figer_version_success(self):
        """Test: gel de version reussi."""
        devis = _make_devis(id=1, version_figee=False)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = FigerVersionDTO(commentaire="Version finale")
        result = self.use_case.execute(devis_id=1, dto=dto, fige_par=1)

        assert isinstance(result, VersionDTO)
        assert devis.version_figee is True
        self.mock_devis_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_figer_version_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = FigerVersionDTO()
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto, fige_par=1)

    def test_figer_version_deja_figee(self):
        """Test: erreur si version deja figee."""
        devis = _make_devis(id=1, version_figee=True)
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = FigerVersionDTO()
        with pytest.raises(DevisValidationError, match="deja fige"):
            self.use_case.execute(devis_id=1, dto=dto, fige_par=1)

    def test_figer_version_avec_commentaire(self):
        """Test: le commentaire est applique a la version."""
        devis = _make_devis(id=1, version_figee=False)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = FigerVersionDTO(commentaire="Version client validee")
        self.use_case.execute(devis_id=1, dto=dto, fige_par=1)

        assert devis.version_commentaire == "Version client validee"
