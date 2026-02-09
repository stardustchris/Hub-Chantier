"""Tests unitaires pour les Use Cases d'export comptable.

FIN-13: Export comptable - tests generation CSV/Excel, collecte
des achats factures, situations validees et factures client.
"""

import csv
import io
import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from modules.financier.domain.entities import Budget, LotBudgetaire, Fournisseur
from modules.financier.domain.repositories.budget_repository import BudgetRepository
from modules.financier.domain.repositories.achat_repository import AchatRepository
from modules.financier.domain.repositories.situation_repository import SituationRepository
from modules.financier.domain.repositories.facture_repository import FactureRepository
from modules.financier.domain.repositories.fournisseur_repository import FournisseurRepository
from modules.financier.domain.repositories.lot_budgetaire_repository import LotBudgetaireRepository
from modules.financier.domain.value_objects import StatutAchat
from modules.financier.application.dtos.export_dtos import (
    ExportComptableDTO,
    LigneExportComptableDTO,
)
from modules.financier.application.use_cases.export_comptable_use_cases import (
    ExportComptableUseCase,
    ExportComptableError,
)


class TestExportComptableUseCase:
    """Tests pour le use case d'export comptable."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_situation_repo = Mock(spec=SituationRepository)
        self.mock_facture_repo = Mock(spec=FactureRepository)
        self.mock_fournisseur_repo = Mock(spec=FournisseurRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)

        self.use_case = ExportComptableUseCase(
            budget_repo=self.mock_budget_repo,
            achat_repo=self.mock_achat_repo,
            situation_repo=self.mock_situation_repo,
            facture_repo=self.mock_facture_repo,
            fournisseur_repo=self.mock_fournisseur_repo,
            lot_repo=self.mock_lot_repo,
        )

    def _make_budget(self, chantier_id=1):
        """Helper pour creer un budget."""
        return Budget(
            id=10,
            chantier_id=chantier_id,
            montant_initial_ht=Decimal("100000"),
            montant_avenants_ht=Decimal("0"),
            created_at=datetime(2026, 1, 1),
        )

    def _make_achat(
        self,
        achat_id=1,
        quantite=Decimal("10"),
        prix_unitaire=Decimal("100"),
        taux_tva=Decimal("20"),
        fournisseur_id=1,
        lot_id=None,
        libelle="Achat test",
        date_commande=date(2026, 1, 15),
        numero_facture="FAC-001",
    ):
        """Helper pour creer un mock d'achat."""
        achat = Mock()
        achat.id = achat_id
        achat.quantite = quantite
        achat.prix_unitaire_ht = prix_unitaire
        achat.taux_tva = taux_tva
        achat.fournisseur_id = fournisseur_id
        achat.lot_budgetaire_id = lot_id
        achat.libelle = libelle
        achat.date_commande = date_commande
        achat.numero_facture = numero_facture
        achat.statut = StatutAchat.FACTURE
        return achat

    def _make_situation(
        self,
        numero="SIT-001",
        statut="validee",
        montant_periode_ht=Decimal("15000"),
        taux_tva=Decimal("20"),
        periode_fin=date(2026, 1, 31),
    ):
        """Helper pour creer un mock de situation."""
        situation = Mock()
        situation.numero = numero
        situation.statut = statut
        situation.montant_periode_ht = montant_periode_ht
        situation.taux_tva = taux_tva
        situation.periode_fin = periode_fin
        return situation

    def _make_facture(
        self,
        numero="FC-2026-001",
        statut="emise",
        montant_ht=Decimal("20000"),
        montant_tva=Decimal("4000"),
        montant_ttc=Decimal("24000"),
        type_facture="classique",
        date_emission=date(2026, 1, 20),
    ):
        """Helper pour creer un mock de facture."""
        facture = Mock()
        facture.numero_facture = numero
        facture.statut = statut
        facture.montant_ht = montant_ht
        facture.montant_tva = montant_tva
        facture.montant_ttc = montant_ttc
        facture.type_facture = type_facture
        facture.date_emission = date_emission
        return facture

    def test_execute_budget_not_found(self):
        """Test: ExportComptableError si pas de budget."""
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        with pytest.raises(ExportComptableError, match="Aucun budget"):
            self.use_case.execute(chantier_id=999)

    def test_execute_empty_chantier(self):
        """Test: export vide pour un chantier sans donnees."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_situation_repo.find_by_chantier_id.return_value = []
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert isinstance(result, ExportComptableDTO)
        assert result.chantier_id == 1
        assert len(result.lignes) == 0
        assert result.totaux["total_ht"] == "0.00"
        assert result.totaux["total_tva"] == "0.00"
        assert result.totaux["total_ttc"] == "0.00"

    def test_execute_with_achats(self):
        """Test: export avec des achats factures."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        achat = self._make_achat()
        self.mock_achat_repo.find_by_chantier.return_value = [achat]
        self.mock_situation_repo.find_by_chantier_id.return_value = []
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        fournisseur = Mock()
        fournisseur.raison_sociale = "Fournisseur Test"
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 1
        ligne = result.lignes[0]
        assert ligne.type_document == "achat"
        assert ligne.tiers == "Fournisseur Test"
        assert ligne.numero == "FAC-001"
        # montant_ht = 10 * 100 = 1000, arrondi à 2 décimales
        assert ligne.montant_ht == str(Decimal("1000.00"))

    def test_execute_with_situations_validees(self):
        """Test: export avec des situations validees."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        self.mock_achat_repo.find_by_chantier.return_value = []
        situation = self._make_situation(statut="validee")
        self.mock_situation_repo.find_by_chantier_id.return_value = [situation]
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 1
        ligne = result.lignes[0]
        assert ligne.type_document == "situation"
        assert ligne.tiers == "Greg Construction"
        assert ligne.montant_ht == str(Decimal("15000"))

    def test_execute_situations_brouillon_excluded(self):
        """Test: les situations en brouillon sont exclues."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        self.mock_achat_repo.find_by_chantier.return_value = []
        situation = self._make_situation(statut="brouillon")
        self.mock_situation_repo.find_by_chantier_id.return_value = [situation]
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 0

    def test_execute_situations_facturee_included(self):
        """Test: les situations facturees sont incluses."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        self.mock_achat_repo.find_by_chantier.return_value = []
        situation = self._make_situation(statut="facturee")
        self.mock_situation_repo.find_by_chantier_id.return_value = [situation]
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 1

    def test_execute_with_factures(self):
        """Test: export avec des factures client."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_situation_repo.find_by_chantier_id.return_value = []
        facture = self._make_facture()
        self.mock_facture_repo.find_by_chantier_id.return_value = [facture]

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 1
        ligne = result.lignes[0]
        assert ligne.type_document == "facture"
        assert ligne.numero == "FC-2026-001"
        assert ligne.montant_ht == str(Decimal("20000"))

    def test_execute_factures_brouillon_excluded(self):
        """Test: les factures en brouillon sont exclues."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_situation_repo.find_by_chantier_id.return_value = []
        facture = self._make_facture(statut="brouillon")
        self.mock_facture_repo.find_by_chantier_id.return_value = [facture]

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 0

    def test_execute_factures_annulee_excluded(self):
        """Test: les factures annulees sont exclues."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        self.mock_achat_repo.find_by_chantier.return_value = []
        self.mock_situation_repo.find_by_chantier_id.return_value = []
        facture = self._make_facture(statut="annulee")
        self.mock_facture_repo.find_by_chantier_id.return_value = [facture]

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 0

    def test_execute_totals_calculated_correctly(self):
        """Test: les totaux sont correctement calcules."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()

        # Achat: 10 * 100 = 1000 HT, TVA = 200, TTC = 1200
        achat = self._make_achat()
        self.mock_achat_repo.find_by_chantier.return_value = [achat]
        self.mock_fournisseur_repo.find_by_id.return_value = Mock(raison_sociale="F")

        # Situation: 15000 HT, TVA = 3000, TTC = 18000
        situation = self._make_situation()
        self.mock_situation_repo.find_by_chantier_id.return_value = [situation]

        # Facture: 20000 HT, 4000 TVA, 24000 TTC
        facture = self._make_facture()
        self.mock_facture_repo.find_by_chantier_id.return_value = [facture]

        result = self.use_case.execute(chantier_id=1)

        # Total HT = 1000 + 15000 + 20000 = 36000, arrondi à 2 décimales
        assert result.totaux["total_ht"] == "36000.00"

    def test_execute_sorted_by_date(self):
        """Test: les lignes sont triees par date."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()

        achat1 = self._make_achat(achat_id=1, date_commande=date(2026, 1, 20))
        achat2 = self._make_achat(achat_id=2, date_commande=date(2026, 1, 10))
        self.mock_achat_repo.find_by_chantier.return_value = [achat1, achat2]
        self.mock_fournisseur_repo.find_by_id.return_value = Mock(raison_sociale="F")

        self.mock_situation_repo.find_by_chantier_id.return_value = []
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert len(result.lignes) == 2
        assert result.lignes[0].date <= result.lignes[1].date

    def test_execute_achat_without_fournisseur(self):
        """Test: achat sans fournisseur -> tiers vide."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        achat = self._make_achat(fournisseur_id=None)
        self.mock_achat_repo.find_by_chantier.return_value = [achat]
        self.mock_situation_repo.find_by_chantier_id.return_value = []
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert result.lignes[0].tiers == ""

    def test_execute_achat_without_numero_facture(self):
        """Test: achat sans numero facture -> genere ACH-{id}."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        achat = self._make_achat(numero_facture=None)
        self.mock_achat_repo.find_by_chantier.return_value = [achat]
        self.mock_fournisseur_repo.find_by_id.return_value = Mock(raison_sociale="F")
        self.mock_situation_repo.find_by_chantier_id.return_value = []
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert result.lignes[0].numero == "ACH-1"

    def test_execute_achat_with_lot(self):
        """Test: achat avec lot -> code analytique inclut le lot."""
        self.mock_budget_repo.find_by_chantier_id.return_value = self._make_budget()
        achat = self._make_achat(lot_id=5)
        self.mock_achat_repo.find_by_chantier.return_value = [achat]
        self.mock_fournisseur_repo.find_by_id.return_value = Mock(raison_sociale="F")

        lot = Mock()
        lot.code_lot = "LOT01"
        self.mock_lot_repo.find_by_id.return_value = lot

        self.mock_situation_repo.find_by_chantier_id.return_value = []
        self.mock_facture_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=1)

        assert "LOT01" in result.lignes[0].code_analytique


class TestExportComptableCodeAnalytique:
    """Tests pour la generation du code analytique."""

    def setup_method(self):
        """Configuration."""
        self.use_case = ExportComptableUseCase(
            budget_repo=Mock(),
            achat_repo=Mock(),
            situation_repo=Mock(),
            facture_repo=Mock(),
            fournisseur_repo=Mock(),
            lot_repo=Mock(),
        )

    def test_code_analytique_sans_lot(self):
        """Test: code analytique sans lot."""
        result = self.use_case._generer_code_analytique(1)
        assert result == "CHANT-001"

    def test_code_analytique_avec_lot(self):
        """Test: code analytique avec lot."""
        result = self.use_case._generer_code_analytique(1, "LOT01")
        assert result == "CHANT-001-LOT-LOT01"

    def test_code_analytique_padding(self):
        """Test: code analytique avec padding 3 chiffres."""
        result = self.use_case._generer_code_analytique(42)
        assert result == "CHANT-042"

    def test_code_analytique_large_id(self):
        """Test: code analytique avec grand ID."""
        result = self.use_case._generer_code_analytique(1234)
        assert result == "CHANT-1234"


class TestExportComptableHelpers:
    """Tests pour les methodes helpers."""

    def setup_method(self):
        """Configuration."""
        self.mock_fournisseur_repo = Mock(spec=FournisseurRepository)
        self.mock_lot_repo = Mock(spec=LotBudgetaireRepository)

        self.use_case = ExportComptableUseCase(
            budget_repo=Mock(),
            achat_repo=Mock(),
            situation_repo=Mock(),
            facture_repo=Mock(),
            fournisseur_repo=self.mock_fournisseur_repo,
            lot_repo=self.mock_lot_repo,
        )

    def test_get_fournisseur_nom_found(self):
        """Test: retourne le nom du fournisseur."""
        fournisseur = Mock()
        fournisseur.raison_sociale = "ABC Construction"
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        result = self.use_case._get_fournisseur_nom(1)

        assert result == "ABC Construction"

    def test_get_fournisseur_nom_not_found(self):
        """Test: retourne chaine vide si fournisseur non trouve."""
        self.mock_fournisseur_repo.find_by_id.return_value = None

        result = self.use_case._get_fournisseur_nom(999)

        assert result == ""

    def test_get_fournisseur_nom_none_id(self):
        """Test: retourne chaine vide si fournisseur_id est None."""
        result = self.use_case._get_fournisseur_nom(None)

        assert result == ""
        self.mock_fournisseur_repo.find_by_id.assert_not_called()

    def test_get_lot_code_found(self):
        """Test: retourne le code du lot."""
        lot = Mock()
        lot.code_lot = "LOT01"
        self.mock_lot_repo.find_by_id.return_value = lot

        result = self.use_case._get_lot_code(1)

        assert result == "LOT01"

    def test_get_lot_code_not_found(self):
        """Test: retourne None si lot non trouve."""
        self.mock_lot_repo.find_by_id.return_value = None

        result = self.use_case._get_lot_code(999)

        assert result is None

    def test_get_lot_code_none_id(self):
        """Test: retourne None si lot_id est None."""
        result = self.use_case._get_lot_code(None)

        assert result is None
        self.mock_lot_repo.find_by_id.assert_not_called()


class TestExportComptableCSV:
    """Tests pour la generation CSV."""

    def setup_method(self):
        """Configuration."""
        self.use_case = ExportComptableUseCase(
            budget_repo=Mock(),
            achat_repo=Mock(),
            situation_repo=Mock(),
            facture_repo=Mock(),
            fournisseur_repo=Mock(),
            lot_repo=Mock(),
        )

    def test_to_csv_empty(self):
        """Test: CSV avec 0 lignes."""
        dto = ExportComptableDTO(
            chantier_id=1,
            nom_chantier="Test",
            date_export="2026-02-01T00:00:00",
            lignes=[],
            totaux={"total_ht": "0", "total_tva": "0", "total_ttc": "0"},
        )

        result = self.use_case.to_csv(dto)

        # BOM + headers + empty line + totaux
        assert result.startswith("\ufeff")
        assert "Date" in result
        assert "TOTAUX" in result

    def test_to_csv_with_data(self):
        """Test: CSV avec des lignes."""
        ligne = LigneExportComptableDTO(
            date="2026-01-15",
            type_document="achat",
            numero="FAC-001",
            tiers="Fournisseur",
            montant_ht="1000",
            montant_tva="200",
            montant_ttc="1200",
            code_analytique="CHANT-001",
            libelle="Achat materiel",
            reference_chantier="CHANT-001",
            statut="facture",
        )
        dto = ExportComptableDTO(
            chantier_id=1,
            nom_chantier="Test",
            date_export="2026-02-01T00:00:00",
            lignes=[ligne],
            totaux={"total_ht": "1000", "total_tva": "200", "total_ttc": "1200"},
        )

        result = self.use_case.to_csv(dto)

        assert "FAC-001" in result
        assert "Fournisseur" in result
        assert "1000" in result
        assert ";" in result  # separateur point-virgule

    def test_to_csv_delimiter_semicolon(self):
        """Test: le separateur est bien le point-virgule."""
        dto = ExportComptableDTO(
            chantier_id=1,
            nom_chantier="Test",
            date_export="2026-02-01T00:00:00",
            lignes=[],
            totaux={"total_ht": "0", "total_tva": "0", "total_ttc": "0"},
        )

        result = self.use_case.to_csv(dto)

        # Header line should use semicolons
        lines = result.split("\n")
        # First line after BOM
        header_line = lines[0].replace("\ufeff", "")
        assert ";" in header_line

    def test_to_csv_bom_utf8(self):
        """Test: le BOM UTF-8 est present pour Excel."""
        dto = ExportComptableDTO(
            chantier_id=1,
            nom_chantier="Test",
            date_export="2026-02-01T00:00:00",
            lignes=[],
            totaux={"total_ht": "0", "total_tva": "0", "total_ttc": "0"},
        )

        result = self.use_case.to_csv(dto)

        assert result[0] == "\ufeff"


class TestExportComptableError:
    """Tests pour l'exception ExportComptableError."""

    def test_default_message(self):
        """Test: message par defaut."""
        err = ExportComptableError()
        assert err.message == "Erreur lors de l'export comptable"

    def test_custom_message(self):
        """Test: message personnalise."""
        err = ExportComptableError("Budget introuvable")
        assert err.message == "Budget introuvable"

    def test_inherits_exception(self):
        """Test: herite de Exception."""
        err = ExportComptableError()
        assert isinstance(err, Exception)


class TestExportComptableDTOs:
    """Tests pour les DTOs d'export."""

    def test_ligne_export_to_dict(self):
        """Test: to_dict pour LigneExportComptableDTO."""
        ligne = LigneExportComptableDTO(
            date="2026-01-15",
            type_document="achat",
            numero="FAC-001",
            tiers="Fournisseur",
            montant_ht="1000",
            montant_tva="200",
            montant_ttc="1200",
            code_analytique="CHANT-001",
            libelle="Test",
            reference_chantier="CHANT-001",
            statut="facture",
        )
        d = ligne.to_dict()
        assert d["date"] == "2026-01-15"
        assert d["type_document"] == "achat"
        assert d["montant_ht"] == "1000"

    def test_export_dto_to_dict(self):
        """Test: to_dict pour ExportComptableDTO."""
        dto = ExportComptableDTO(
            chantier_id=1,
            nom_chantier="Test",
            date_export="2026-02-01",
            lignes=[],
            totaux={"total_ht": "0"},
        )
        d = dto.to_dict()
        assert d["chantier_id"] == 1
        assert d["nombre_lignes"] == 0
        assert d["totaux"]["total_ht"] == "0"

    def test_export_dto_to_dict_with_lignes(self):
        """Test: to_dict inclut les lignes serialisees."""
        ligne = LigneExportComptableDTO(
            date="2026-01-15",
            type_document="achat",
            numero="FAC-001",
            tiers="F",
            montant_ht="1000",
            montant_tva="200",
            montant_ttc="1200",
            code_analytique="CHANT-001",
            libelle="T",
            reference_chantier="CHANT-001",
            statut="facture",
        )
        dto = ExportComptableDTO(
            chantier_id=1,
            nom_chantier="Test",
            date_export="2026-02-01",
            lignes=[ligne],
            totaux={},
        )
        d = dto.to_dict()
        assert d["nombre_lignes"] == 1
        assert d["lignes"][0]["numero"] == "FAC-001"
