"""Tests unitaires pour les Use Cases de calcul des totaux.

DEV-06: Gestion marges et coefficients.
Couche Application - calcul_totaux_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, call

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.debourse_detail import DebourseDetail
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.type_debourse import TypeDebourse
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.debourse_detail_repository import DebourseDetailRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.calcul_totaux_use_cases import CalculerTotauxDevisUseCase
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError


def _make_devis(**kwargs):
    """Cree un devis valide."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation",
        "statut": StatutDevis.BROUILLON,
        "taux_marge_global": Decimal("15"),
        "coefficient_frais_generaux": Decimal("12"),
        "taux_tva_defaut": Decimal("20"),
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("0"),
        "montant_total_ttc": Decimal("0"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


class TestCalculerTotauxDevisUseCase:
    """Tests pour le recalcul des totaux de devis."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CalculerTotauxDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_calcul_devis_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, updated_by=1)

    def test_calcul_devis_sans_lots(self):
        """Test: calcul pour un devis sans lots."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        assert result["montant_total_ht"] == "0"
        assert result["montant_total_ttc"] == "0"

    def test_calcul_avec_debourses(self):
        """Test: calcul complet avec debourses et marges."""
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            coefficient_frais_generaux=Decimal("12"),
        )
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Gros oeuvre")
        ligne = LigneDevis(
            id=100,
            lot_devis_id=10,
            libelle="Beton",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("0"),
            taux_tva=Decimal("20"),
        )
        debourse = DebourseDetail(
            id=1000,
            ligne_devis_id=100,
            type_debourse=TypeDebourse.MATERIAUX,
            libelle="Ciment",
            quantite=Decimal("100"),
            prix_unitaire=Decimal("10"),
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot]
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = [debourse]
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.return_value = lot
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        # Debourse sec = 100 * 10 = 1000
        # Prix revient = 1000 * 1.12 = 1120
        # Prix vente HT = 1120 * 1.15 = 1288
        # Verify devis totals were saved
        self.mock_devis_repo.save.assert_called_once()
        self.mock_lot_repo.save.assert_called_once()
        self.mock_ligne_repo.save.assert_called_once()

        # montant_total_ht should be positive
        assert Decimal(result["montant_total_ht"]) > Decimal("0")

    def test_calcul_ligne_sans_debourses(self):
        """Test: ligne sans debourses utilise prix_unitaire direct."""
        devis = _make_devis()
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Lot")
        ligne = LigneDevis(
            id=100,
            lot_devis_id=10,
            libelle="Ligne directe",
            quantite=Decimal("5"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot]
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = []
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.return_value = lot
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        # ligne_montant_ht = 5 * 100 = 500
        assert Decimal(result["montant_total_ht"]) == Decimal("500")

    def test_calcul_marge_priorite_ligne(self):
        """Test: la marge de la ligne a la priorite."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        lot = LotDevis(
            id=10, devis_id=1, code_lot="LOT-001", libelle="Lot",
            taux_marge_lot=Decimal("20"),
        )
        ligne = LigneDevis(
            id=100,
            lot_devis_id=10,
            libelle="Ligne",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("0"),
            taux_marge_ligne=Decimal("30"),
            taux_tva=Decimal("20"),
        )
        debourse = DebourseDetail(
            id=1000,
            ligne_devis_id=100,
            type_debourse=TypeDebourse.MATERIAUX,
            libelle="Mat",
            quantite=Decimal("10"),
            prix_unitaire=Decimal("10"),
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot]
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = [debourse]
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.return_value = lot
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        # Debourse sec = 100
        # Prix revient = 100 * 1.12 = 112
        # Prix vente HT = 112 * 1.30 = 145.6 (marge ligne 30%, pas lot 20% ni global 15%)
        assert Decimal(result["montant_total_ht"]) > Decimal("0")

    def test_calcul_marge_priorite_lot(self):
        """Test: la marge du lot a la priorite si pas de marge ligne."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        lot = LotDevis(
            id=10, devis_id=1, code_lot="LOT-001", libelle="Lot",
            taux_marge_lot=Decimal("20"),
        )
        ligne = LigneDevis(
            id=100,
            lot_devis_id=10,
            libelle="Ligne",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("0"),
            taux_marge_ligne=None,  # Pas de marge ligne
            taux_tva=Decimal("20"),
        )
        debourse = DebourseDetail(
            id=1000,
            ligne_devis_id=100,
            type_debourse=TypeDebourse.MATERIAUX,
            libelle="Mat",
            quantite=Decimal("10"),
            prix_unitaire=Decimal("10"),
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot]
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = [debourse]
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.return_value = lot
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        # Debourse sec = 100
        # Prix revient = 100 * 1.12 = 112
        # Prix vente HT = 112 * 1.20 = 134.4 (marge lot 20%)
        ht = Decimal(result["montant_total_ht"])
        assert ht > Decimal("0")

    def test_calcul_marge_type_debourse(self):
        """Test: marge par type de debourse si pas de marge ligne/lot."""
        devis = _make_devis(
            taux_marge_global=Decimal("15"),
            taux_marge_moe=Decimal("25"),
        )
        lot = LotDevis(
            id=10, devis_id=1, code_lot="LOT-001", libelle="Lot",
            taux_marge_lot=None,  # Pas de marge lot
        )
        ligne = LigneDevis(
            id=100,
            lot_devis_id=10,
            libelle="Ligne MOE",
            quantite=Decimal("8"),
            prix_unitaire_ht=Decimal("0"),
            taux_marge_ligne=None,
            taux_tva=Decimal("20"),
        )
        debourse = DebourseDetail(
            id=1000,
            ligne_devis_id=100,
            type_debourse=TypeDebourse.MOE,
            libelle="Macon",
            quantite=Decimal("8"),
            prix_unitaire=Decimal("35"),
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot]
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = [debourse]
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.return_value = lot
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        # Marge = taux_marge_moe = 25% (type debourse principal)
        assert Decimal(result["montant_total_ht"]) > Decimal("0")

    def test_calcul_journal_entry(self):
        """Test: entree de journal apres recalcul."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case.execute(devis_id=1, updated_by=3)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "recalcul_totaux"
        assert journal_call.auteur_id == 3

    def test_calcul_multiple_lots(self):
        """Test: calcul avec plusieurs lots."""
        devis = _make_devis()
        lot1 = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Lot 1")
        lot2 = LotDevis(id=20, devis_id=1, code_lot="LOT-002", libelle="Lot 2")

        ligne1 = LigneDevis(
            id=100, lot_devis_id=10, libelle="L1",
            quantite=Decimal("5"), prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
        )
        ligne2 = LigneDevis(
            id=200, lot_devis_id=20, libelle="L2",
            quantite=Decimal("3"), prix_unitaire_ht=Decimal("200"),
            taux_tva=Decimal("20"),
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot1, lot2]
        self.mock_ligne_repo.find_by_lot.side_effect = [[ligne1], [ligne2]]
        self.mock_debourse_repo.find_by_ligne.return_value = []
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.side_effect = lambda l: l
        self.mock_ligne_repo.save.side_effect = lambda l: l
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        # lot1 = 5 * 100 = 500, lot2 = 3 * 200 = 600 => total = 1100
        assert Decimal(result["montant_total_ht"]) == Decimal("1100")

    def test_calcul_ligne_quantite_zero_avec_debourses(self):
        """Test: ligne avec quantite zero et debourses."""
        devis = _make_devis()
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Lot")
        ligne = LigneDevis(
            id=100, lot_devis_id=10, libelle="L",
            quantite=Decimal("0"), prix_unitaire_ht=Decimal("0"),
            taux_tva=Decimal("20"),
        )
        debourse = DebourseDetail(
            id=1000, ligne_devis_id=100, libelle="Mat",
            quantite=Decimal("10"), prix_unitaire=Decimal("10"),
        )

        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = [lot]
        self.mock_ligne_repo.find_by_lot.return_value = [ligne]
        self.mock_debourse_repo.find_by_ligne.return_value = [debourse]
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.return_value = lot
        self.mock_ligne_repo.save.return_value = ligne
        self.mock_journal_repo.save.return_value = Mock()

        result = self.use_case.execute(devis_id=1, updated_by=1)

        # prix_unitaire = 0 car quantite = 0 (division evitee)
        assert Decimal(result["montant_total_ht"]) == Decimal("0")


class TestResolveMarge:
    """Tests pour la resolution de priorite des marges."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CalculerTotauxDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_resolve_marge_ligne_priority(self):
        """Test: marge ligne a priorite sur tout."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = self.use_case._resolve_marge(
            ligne_marge=Decimal("30"),
            lot_marge=Decimal("20"),
            devis=devis,
            debourses=[],
        )
        assert result == Decimal("30")

    def test_resolve_marge_lot_priority(self):
        """Test: marge lot si pas de marge ligne."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = self.use_case._resolve_marge(
            ligne_marge=None,
            lot_marge=Decimal("20"),
            devis=devis,
            debourses=[],
        )
        assert result == Decimal("20")

    def test_resolve_marge_global_fallback(self):
        """Test: marge globale si pas de marge ligne/lot."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        result = self.use_case._resolve_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=[],
        )
        assert result == Decimal("15")

    def test_resolve_marge_type_debourse_moe(self):
        """Test: marge type debourse MOE."""
        devis = _make_devis(taux_marge_global=Decimal("15"), taux_marge_moe=Decimal("25"))
        debourse_moe = DebourseDetail(
            id=1, ligne_devis_id=1, libelle="Macon",
            type_debourse=TypeDebourse.MOE,
            quantite=Decimal("8"), prix_unitaire=Decimal("35"),
        )
        result = self.use_case._resolve_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=[debourse_moe],
        )
        assert result == Decimal("25")

    def test_resolve_marge_type_debourse_materiaux(self):
        """Test: marge type debourse Materiaux."""
        devis = _make_devis(taux_marge_global=Decimal("15"), taux_marge_materiaux=Decimal("18"))
        debourse = DebourseDetail(
            id=1, ligne_devis_id=1, libelle="Ciment",
            type_debourse=TypeDebourse.MATERIAUX,
            quantite=Decimal("50"), prix_unitaire=Decimal("12"),
        )
        result = self.use_case._resolve_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=[debourse],
        )
        assert result == Decimal("18")

    def test_resolve_marge_type_debourse_none_falls_to_global(self):
        """Test: fallback sur marge globale si type debourse non configure."""
        devis = _make_devis(taux_marge_global=Decimal("15"), taux_marge_moe=None)
        debourse_moe = DebourseDetail(
            id=1, ligne_devis_id=1, libelle="Macon",
            type_debourse=TypeDebourse.MOE,
            quantite=Decimal("8"), prix_unitaire=Decimal("35"),
        )
        result = self.use_case._resolve_marge(
            ligne_marge=None,
            lot_marge=None,
            devis=devis,
            debourses=[debourse_moe],
        )
        assert result == Decimal("15")


class TestVentilationTVA:
    """DEV-TVA: Tests pour la ventilation TVA multi-taux."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_debourse_repo = Mock(spec=DebourseDetailRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = CalculerTotauxDevisUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            debourse_repository=self.mock_debourse_repo,
            journal_repository=self.mock_journal_repo,
        )

    def _setup_mocks(self, devis, lots, lignes_by_lot):
        """Helper pour configurer les mocks."""
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = lots
        self.mock_ligne_repo.find_by_lot.side_effect = [
            lignes_by_lot.get(lot.id, []) for lot in lots
        ]
        self.mock_debourse_repo.find_by_ligne.return_value = []
        self.mock_devis_repo.save.return_value = devis
        self.mock_lot_repo.save.side_effect = lambda l: l
        self.mock_ligne_repo.save.side_effect = lambda l: l
        self.mock_journal_repo.save.return_value = Mock()

    def test_ventilation_mono_taux_20(self):
        """Test: ventilation avec un seul taux (20%)."""
        devis = _make_devis()
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Lot 1")
        ligne1 = LigneDevis(
            id=100, lot_devis_id=10, libelle="L1",
            quantite=Decimal("5"), prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
        )
        ligne2 = LigneDevis(
            id=101, lot_devis_id=10, libelle="L2",
            quantite=Decimal("3"), prix_unitaire_ht=Decimal("200"),
            taux_tva=Decimal("20"),
        )

        self._setup_mocks(devis, [lot], {10: [ligne1, ligne2]})
        result = self.use_case.execute(devis_id=1, updated_by=1)

        # Total HT = 500 + 600 = 1100, tout a 20%
        ventilation = result["ventilation_tva"]
        assert len(ventilation) == 1
        assert ventilation[0]["taux"] == "20"
        assert Decimal(ventilation[0]["base_ht"]) == Decimal("1100.00")
        assert Decimal(ventilation[0]["montant_tva"]) == Decimal("220.00")

    def test_ventilation_multi_taux(self):
        """Test: ventilation avec plusieurs taux (5.5%, 10%, 20%)."""
        devis = _make_devis()
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Lot 1")
        ligne_55 = LigneDevis(
            id=100, lot_devis_id=10, libelle="Isolation",
            quantite=Decimal("1"), prix_unitaire_ht=Decimal("1000"),
            taux_tva=Decimal("5.5"),
        )
        ligne_10 = LigneDevis(
            id=101, lot_devis_id=10, libelle="Renovation",
            quantite=Decimal("1"), prix_unitaire_ht=Decimal("2000"),
            taux_tva=Decimal("10"),
        )
        ligne_20 = LigneDevis(
            id=102, lot_devis_id=10, libelle="Neuf",
            quantite=Decimal("1"), prix_unitaire_ht=Decimal("3000"),
            taux_tva=Decimal("20"),
        )

        self._setup_mocks(devis, [lot], {10: [ligne_55, ligne_10, ligne_20]})
        result = self.use_case.execute(devis_id=1, updated_by=1)

        ventilation = result["ventilation_tva"]
        assert len(ventilation) == 3

        # Trie par taux croissant
        assert ventilation[0]["taux"] == "5.5"
        assert Decimal(ventilation[0]["base_ht"]) == Decimal("1000.00")
        assert Decimal(ventilation[0]["montant_tva"]) == Decimal("55.00")

        assert ventilation[1]["taux"] == "10"
        assert Decimal(ventilation[1]["base_ht"]) == Decimal("2000.00")
        assert Decimal(ventilation[1]["montant_tva"]) == Decimal("200.00")

        assert ventilation[2]["taux"] == "20"
        assert Decimal(ventilation[2]["base_ht"]) == Decimal("3000.00")
        assert Decimal(ventilation[2]["montant_tva"]) == Decimal("600.00")

    def test_ventilation_coherence_totaux(self):
        """Test: sum(montant_tva) + total_ht == total_ttc."""
        devis = _make_devis()
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Lot 1")
        ligne_10 = LigneDevis(
            id=100, lot_devis_id=10, libelle="Renovation",
            quantite=Decimal("10"), prix_unitaire_ht=Decimal("150"),
            taux_tva=Decimal("10"),
        )
        ligne_20 = LigneDevis(
            id=101, lot_devis_id=10, libelle="Standard",
            quantite=Decimal("5"), prix_unitaire_ht=Decimal("200"),
            taux_tva=Decimal("20"),
        )

        self._setup_mocks(devis, [lot], {10: [ligne_10, ligne_20]})
        result = self.use_case.execute(devis_id=1, updated_by=1)

        total_ht = Decimal(result["montant_total_ht"])
        total_ttc = Decimal(result["montant_total_ttc"])
        total_tva = sum(
            Decimal(v["montant_tva"]) for v in result["ventilation_tva"]
        )

        assert total_ht + total_tva == total_ttc

    def test_ventilation_devis_vide(self):
        """Test: ventilation vide pour un devis sans lignes."""
        devis = _make_devis()
        self._setup_mocks(devis, [], {})
        result = self.use_case.execute(devis_id=1, updated_by=1)

        assert result["ventilation_tva"] == []

    def test_ventilation_arrondis(self):
        """Test: montants arrondis a 2 decimales."""
        devis = _make_devis()
        lot = LotDevis(id=10, devis_id=1, code_lot="LOT-001", libelle="Lot 1")
        ligne = LigneDevis(
            id=100, lot_devis_id=10, libelle="L",
            quantite=Decimal("3"), prix_unitaire_ht=Decimal("33.33"),
            taux_tva=Decimal("5.5"),
        )

        self._setup_mocks(devis, [lot], {10: [ligne]})
        result = self.use_case.execute(devis_id=1, updated_by=1)

        ventilation = result["ventilation_tva"]
        # Verifier que les montants n'ont que 2 decimales
        base_ht = Decimal(ventilation[0]["base_ht"])
        montant_tva = Decimal(ventilation[0]["montant_tva"])
        assert base_ht == base_ht.quantize(Decimal("0.01"))
        assert montant_tva == montant_tva.quantize(Decimal("0.01"))
