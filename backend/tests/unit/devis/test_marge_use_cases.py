"""Tests unitaires pour les Use Cases de gestion des marges.

DEV-06: Gestion marges et coefficients.
Regle de priorite: ligne > lot > type debourse > global.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.value_objects import TypeDebourse, StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.debourse_detail_repository import DebourseDetailRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.marge_use_cases import (
    AppliquerMargeGlobaleUseCase,
    AppliquerMargeLotUseCase,
    AppliquerMargeLigneUseCase,
    ConsulterMargesDevisUseCase,
)
from modules.devis.application.dtos.marge_dtos import (
    AppliquerMargeGlobaleDTO,
    AppliquerMargeLotDTO,
    AppliquerMargeLigneDTO,
    MargesDevisDTO,
)


def _make_devis(**kwargs):
    """Cree un devis valide."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "statut": StatutDevis.BROUILLON,
        "taux_marge_global": Decimal("15"),
        "date_creation": date(2026, 1, 15),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_lot(lot_id, devis_id=1, libelle="Test", **kwargs):
    """Cree un lot valide."""
    return LotDevis(
        id=lot_id, devis_id=devis_id,
        code_lot=f"LOT-{lot_id:03d}", libelle=libelle,
        **kwargs,
    )


def _make_ligne(ligne_id, lot_devis_id=1, libelle="Test", **kwargs):
    """Cree une ligne valide."""
    defaults = {
        "quantite": Decimal("1"),
        "prix_unitaire_ht": Decimal("0"),
    }
    defaults.update(kwargs)
    return LigneDevis(
        id=ligne_id, lot_devis_id=lot_devis_id,
        libelle=libelle, **defaults,
    )


class TestAppliquerMargeGlobaleUseCase:
    """Tests pour l'application de la marge globale."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = AppliquerMargeGlobaleUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_appliquer_marge_globale(self):
        """Test: modification de la marge globale."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = AppliquerMargeGlobaleDTO(
            devis_id=1,
            taux_marge_global=Decimal("20"),
        )

        result = self.use_case.execute(dto, updated_by=1)

        assert result["taux_marge_global"] == "20"
        self.mock_devis_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_appliquer_marge_globale_avec_types(self):
        """Test: modification des marges par type de debourse."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = AppliquerMargeGlobaleDTO(
            devis_id=1,
            taux_marge_global=Decimal("15"),
            taux_marge_moe=Decimal("20"),
            taux_marge_materiaux=Decimal("12"),
            taux_marge_sous_traitance=Decimal("8"),
        )

        result = self.use_case.execute(dto, updated_by=1)

        assert result["taux_marge_moe"] == "20"
        assert result["taux_marge_materiaux"] == "12"
        assert result["taux_marge_sous_traitance"] == "8"

    def test_appliquer_marge_globale_negative(self):
        """Test: erreur si marge globale negative."""
        dto = AppliquerMargeGlobaleDTO(
            devis_id=1,
            taux_marge_global=Decimal("-5"),
        )

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(dto, updated_by=1)
        assert "negatif" in str(exc_info.value).lower()

    def test_appliquer_marge_devis_inexistant(self):
        """Test: erreur si le devis n'existe pas."""
        self.mock_devis_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError

        dto = AppliquerMargeGlobaleDTO(
            devis_id=999,
            taux_marge_global=Decimal("15"),
        )

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(dto, updated_by=1)

    def test_appliquer_coefficient_frais_generaux(self):
        """Test: modification du coefficient de frais generaux."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = AppliquerMargeGlobaleDTO(
            devis_id=1,
            taux_marge_global=Decimal("15"),
            coefficient_frais_generaux=Decimal("12"),
        )

        result = self.use_case.execute(dto, updated_by=1)
        assert result["coefficient_frais_generaux"] == "12"


class TestAppliquerMargeLotUseCase:
    """Tests pour l'application de la marge lot."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = AppliquerMargeLotUseCase(
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_appliquer_marge_lot(self):
        """Test: definir une marge specifique sur un lot."""
        lot = _make_lot(1, libelle="Electricite")
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_lot_repo.save.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = AppliquerMargeLotDTO(lot_id=1, taux_marge_lot=Decimal("22"))

        result = self.use_case.execute(dto, updated_by=1)

        assert result["taux_marge_lot"] == "22"
        self.mock_lot_repo.save.assert_called_once()

    def test_supprimer_marge_lot(self):
        """Test: remettre la marge lot a None (heriter du parent)."""
        lot = _make_lot(1, libelle="Electricite", taux_marge_lot=Decimal("22"))
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_lot_repo.save.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = AppliquerMargeLotDTO(lot_id=1, taux_marge_lot=None)

        result = self.use_case.execute(dto, updated_by=1)

        assert result["taux_marge_lot"] is None

    def test_marge_lot_negative(self):
        """Test: erreur si marge lot negative."""
        lot = _make_lot(1)
        self.mock_lot_repo.find_by_id.return_value = lot

        dto = AppliquerMargeLotDTO(lot_id=1, taux_marge_lot=Decimal("-5"))

        with pytest.raises(ValueError):
            self.use_case.execute(dto, updated_by=1)

    def test_lot_inexistant(self):
        """Test: erreur si le lot n'existe pas."""
        self.mock_lot_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.lot_use_cases import LotDevisNotFoundError

        dto = AppliquerMargeLotDTO(lot_id=999, taux_marge_lot=Decimal("10"))

        with pytest.raises(LotDevisNotFoundError):
            self.use_case.execute(dto, updated_by=1)


class TestAppliquerMargeLigneUseCase:
    """Tests pour l'application de la marge ligne."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = AppliquerMargeLigneUseCase(
            ligne_repository=self.mock_ligne_repo,
            lot_repository=self.mock_lot_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_appliquer_marge_ligne(self):
        """Test: definir une marge specifique sur une ligne."""
        ligne = _make_ligne(100)
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_ligne_repo.save.return_value = ligne
        lot = _make_lot(1)
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = AppliquerMargeLigneDTO(ligne_id=100, taux_marge_ligne=Decimal("10"))

        result = self.use_case.execute(dto, updated_by=1)

        assert result["taux_marge_ligne"] == "10"
        self.mock_ligne_repo.save.assert_called_once()

    def test_supprimer_marge_ligne(self):
        """Test: remettre la marge ligne a None."""
        ligne = _make_ligne(100, taux_marge_ligne=Decimal("10"))
        self.mock_ligne_repo.find_by_id.return_value = ligne
        self.mock_ligne_repo.save.return_value = ligne
        lot = _make_lot(1)
        self.mock_lot_repo.find_by_id.return_value = lot
        self.mock_journal_repo.save.return_value = Mock()

        dto = AppliquerMargeLigneDTO(ligne_id=100, taux_marge_ligne=None)

        result = self.use_case.execute(dto, updated_by=1)

        assert result["taux_marge_ligne"] is None

    def test_marge_ligne_negative(self):
        """Test: erreur si marge ligne negative."""
        ligne = _make_ligne(100)
        self.mock_ligne_repo.find_by_id.return_value = ligne

        dto = AppliquerMargeLigneDTO(ligne_id=100, taux_marge_ligne=Decimal("-5"))

        with pytest.raises(ValueError):
            self.use_case.execute(dto, updated_by=1)


class TestConsulterMargesDevisUseCase:
    """Tests pour la consultation des marges resolues."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.use_case = ConsulterMargesDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
        )

    def test_consulter_marges_resolues(self):
        """Test: consultation des marges avec resolution de priorite."""
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            taux_marge_moe=Decimal("20"),
        )
        self.mock_devis_repo.find_by_id.return_value = devis

        lot = _make_lot(1, taux_marge_lot=Decimal("18"))
        self.mock_lot_repo.find_by_devis.return_value = [lot]

        # Ligne 1: marge ligne definie -> utilise marge ligne
        ligne1 = _make_ligne(100, taux_marge_ligne=Decimal("25"))
        # Ligne 2: pas de marge ligne -> utilise marge lot
        ligne2 = _make_ligne(200)
        self.mock_ligne_repo.find_by_lot.return_value = [ligne1, ligne2]

        # Debourses pour les lignes
        deb1 = DebourseDetail(
            id=1, ligne_devis_id=100, type_debourse=TypeDebourse.MOE,
            libelle="Macon", quantite=Decimal("10"), prix_unitaire=Decimal("42"),
            total=Decimal("420"), metier="macon", taux_horaire=Decimal("42"),
        )
        deb2 = DebourseDetail(
            id=2, ligne_devis_id=200, type_debourse=TypeDebourse.MATERIAUX,
            libelle="Parpaings", quantite=Decimal("100"), prix_unitaire=Decimal("3.50"),
            total=Decimal("350"),
        )

        def find_by_ligne(ligne_id):
            if ligne_id == 100:
                return [deb1]
            elif ligne_id == 200:
                return [deb2]
            return []
        self.mock_debourse_repo.find_by_ligne.side_effect = find_by_ligne

        result = self.use_case.execute(1)

        assert isinstance(result, MargesDevisDTO)
        assert result.devis_id == 1
        assert result.taux_marge_global == "15"
        assert len(result.lignes) == 2

        # Ligne 1: marge ligne = 25%
        assert result.lignes[0].taux_marge == "25"
        assert result.lignes[0].niveau == "ligne"

        # Ligne 2: pas de marge ligne, lot marge = 18%
        assert result.lignes[1].taux_marge == "18"
        assert result.lignes[1].niveau == "lot"

    def test_consulter_marges_devis_inexistant(self):
        """Test: erreur si le devis n'existe pas."""
        self.mock_devis_repo.find_by_id.return_value = None

        from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(999)

    def test_consulter_marges_devis_vide(self):
        """Test: devis sans lots retourne des totaux a zero."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        result = self.use_case.execute(1)

        assert result.total_debourse_sec == "0"
        assert result.total_prix_revient == "0"
        assert result.total_prix_vente_ht == "0"
        assert result.marge_globale_montant == "0"
        assert len(result.lignes) == 0

    def test_consulter_marges_serialisation(self):
        """Test: le DTO se serialise correctement."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        result = self.use_case.execute(1)
        d = result.to_dict()

        assert d["devis_id"] == 1
        assert d["taux_marge_global"] == "15"
        assert isinstance(d["lignes"], list)

    def test_consulter_marges_exemple_spec_maconnerie(self):
        """Test: exemple de la spec - Lot maconnerie.

        Debourse sec = 8010 EUR
        Frais generaux (19%) -> Quote-part = 1521.90 -> Prix de revient = 9531.90
        Marge globale (15%) -> Prix vente = 9531.90 * 1.15 = 10961.685 -> arrondi 10961.69
        """
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            coefficient_frais_generaux=Decimal("19"),
        )
        self.mock_devis_repo.find_by_id.return_value = devis

        lot = _make_lot(1)
        self.mock_lot_repo.find_by_devis.return_value = [lot]

        ligne = _make_ligne(100)
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]

        debourses = [
            DebourseDetail(
                id=1, ligne_devis_id=100, type_debourse=TypeDebourse.MOE,
                libelle="Macon", quantite=Decimal("120"), prix_unitaire=Decimal("42"),
                total=Decimal("5040"), metier="macon", taux_horaire=Decimal("42"),
            ),
            DebourseDetail(
                id=2, ligne_devis_id=100, type_debourse=TypeDebourse.MATERIAUX,
                libelle="Parpaings", quantite=Decimal("800"), prix_unitaire=Decimal("3.50"),
                total=Decimal("2800"),
            ),
            DebourseDetail(
                id=3, ligne_devis_id=100, type_debourse=TypeDebourse.MATERIAUX,
                libelle="Mortier", quantite=Decimal("2"), prix_unitaire=Decimal("85"),
                total=Decimal("170"),
            ),
        ]
        self.mock_debourse_repo.find_by_ligne.return_value = debourses

        result = self.use_case.execute(1)

        assert Decimal(result.total_debourse_sec) == Decimal("8010")
        # Prix de revient = 8010 * (1 + 19/100) = 8010 * 1.19 = 9531.90
        assert Decimal(result.total_prix_revient) == Decimal("9531.90")
        # Prix de vente = 9531.90 * (1 + 15/100) = 9531.90 * 1.15 = 10961.685 -> arrondi 10961.69
        assert Decimal(result.total_prix_vente_ht) == Decimal("10961.69")
        # Marge montant = 10961.69 - 9531.90 = 1429.79
        assert Decimal(result.marge_globale_montant) == Decimal("1429.79")
        # Verification du niveau: pas de marge ligne, pas de marge lot, pas de type -> global
        assert result.lignes[0].niveau == "global"
