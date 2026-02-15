"""Tests unitaires pour l'import DPGF automatique.

DEV-21: Import fichier DPGF Excel/CSV.
Couche Application - import_dpgf_use_case.py
"""

import csv
import io
import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, call, patch

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.lot_devis import LotDevis
from modules.devis.domain.entities.ligne_devis import LigneDevis
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.unite_article import UniteArticle
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.lot_devis_repository import LotDevisRepository
from modules.devis.domain.repositories.ligne_devis_repository import LigneDevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.import_dpgf_use_case import (
    ImportDPGFUseCase,
    DPGFFormatError,
    DevisNonImportableError,
    _parse_unite,
    _parse_decimal,
)
from modules.devis.application.dtos.dpgf_dtos import DPGFColumnMappingDTO


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation bureau",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "taux_tva_defaut": Decimal("20"),
        "montant_total_ht": Decimal("0"),
        "montant_total_ttc": Decimal("0"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


def _make_csv_content(rows, delimiter=";"):
    """Cree un contenu CSV binaire a partir de lignes."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter)
    for row in rows:
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


class TestParseUnite:
    """Tests du parsing des unites DPGF."""

    def test_parse_u(self):
        assert _parse_unite("U") == UniteArticle.U

    def test_parse_m2(self):
        assert _parse_unite("m2") == UniteArticle.M2

    def test_parse_m2_unicode(self):
        assert _parse_unite("m\u00b2") == UniteArticle.M2

    def test_parse_ml(self):
        assert _parse_unite("ml") == UniteArticle.ML

    def test_parse_m3(self):
        assert _parse_unite("m3") == UniteArticle.M3

    def test_parse_kg(self):
        assert _parse_unite("kg") == UniteArticle.KG

    def test_parse_heure(self):
        assert _parse_unite("h") == UniteArticle.HEURE

    def test_parse_jour(self):
        assert _parse_unite("jour") == UniteArticle.JOUR

    def test_parse_forfait(self):
        assert _parse_unite("fft") == UniteArticle.FORFAIT

    def test_parse_inconnu_defaut_u(self):
        assert _parse_unite("boite") == UniteArticle.U

    def test_parse_vide_defaut_u(self):
        assert _parse_unite("") == UniteArticle.U

    def test_parse_case_insensitive(self):
        assert _parse_unite("M2") == UniteArticle.M2
        assert _parse_unite("Kg") == UniteArticle.KG


class TestParseDecimal:
    """Tests du parsing des valeurs decimales DPGF."""

    def test_parse_entier(self):
        val, err = _parse_decimal("42", "test", 1)
        assert val == Decimal("42")
        assert err is None

    def test_parse_decimal_point(self):
        val, err = _parse_decimal("15.50", "test", 1)
        assert val == Decimal("15.50")

    def test_parse_decimal_virgule(self):
        """Les fichiers CSV FR utilisent la virgule."""
        val, err = _parse_decimal("15,50", "test", 1)
        assert val == Decimal("15.50")

    def test_parse_vide_retourne_zero(self):
        val, err = _parse_decimal("", "test", 1)
        assert val == Decimal("0")
        assert err is None

    def test_parse_tiret_retourne_zero(self):
        val, err = _parse_decimal("-", "test", 1)
        assert val == Decimal("0")
        assert err is None

    def test_parse_invalide_retourne_zero_avec_erreur(self):
        val, err = _parse_decimal("abc", "test", 5)
        assert val == Decimal("0")
        assert err is not None
        assert "Ligne 5" in err

    def test_parse_negatif_retourne_zero_avec_erreur(self):
        val, err = _parse_decimal("-10", "test", 3)
        assert val == Decimal("0")
        assert err is not None

    def test_parse_espaces(self):
        """Les montants avec separateurs de milliers."""
        val, err = _parse_decimal("1 234.56", "test", 1)
        assert val == Decimal("1234.56")


class TestImportDPGFUseCase:
    """Tests du use case d'import DPGF."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)

        # Configurer les mocks pour retourner des entites avec ID
        self._lot_id_counter = 0
        self._ligne_id_counter = 0

        def _save_lot(lot):
            self._lot_id_counter += 1
            lot.id = self._lot_id_counter
            return lot

        def _save_ligne(ligne):
            self._ligne_id_counter += 1
            ligne.id = self._ligne_id_counter
            return ligne

        self.mock_lot_repo.save.side_effect = _save_lot
        self.mock_ligne_repo.save.side_effect = _save_ligne
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case = ImportDPGFUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_import_csv_simple(self):
        """Test: import CSV basique avec 2 lots et 3 lignes."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],  # Header
            ["01", "Demolition mur", "m2", "25", "30"],
            ["01", "Evacuation gravats", "m3", "10", "50"],
            ["02", "Dalle beton", "m2", "50", "80"],
        ])

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        assert result.lots_crees == 2
        assert result.lignes_creees == 3
        assert result.lignes_ignorees == 0
        assert len(result.lots) == 2

    def test_import_csv_lot_par_defaut(self):
        """Test: les lignes sans lot sont groupees sous 'DIVERS'."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
            ["", "Travaux divers", "u", "1", "100"],
        ])

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        assert result.lots_crees == 1
        lot_call = self.mock_lot_repo.save.call_args[0][0]
        assert lot_call.code_lot == "DIVERS"

    def test_import_devis_non_trouve(self):
        """Test: erreur si devis n'existe pas."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(
                devis_id=999,
                file_content=b"",
                filename="dpgf.csv",
                imported_by=5,
            )

    def test_import_devis_non_modifiable(self):
        """Test: erreur si devis en statut non modifiable."""
        devis = _make_devis(statut=StatutDevis.ENVOYE)
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DevisNonImportableError) as exc_info:
            self.use_case.execute(
                devis_id=1,
                file_content=b"data",
                filename="dpgf.csv",
                imported_by=5,
            )
        assert "Envoye" in exc_info.value.message

    def test_import_devis_en_negociation_ok(self):
        """Test: import autorise quand le devis est en negociation."""
        devis = _make_devis(statut=StatutDevis.EN_NEGOCIATION)
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
            ["01", "Ligne test", "u", "1", "100"],
        ])

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        assert result.lignes_creees == 1

    def test_import_format_non_supporte(self):
        """Test: erreur si format de fichier non supporte."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        with pytest.raises(DPGFFormatError) as exc_info:
            self.use_case.execute(
                devis_id=1,
                file_content=b"data",
                filename="dpgf.pdf",
                imported_by=5,
            )
        assert "non supporte" in exc_info.value.message

    def test_import_csv_vide(self):
        """Test: erreur si fichier CSV sans donnees."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
        ])

        with pytest.raises(DPGFFormatError) as exc_info:
            self.use_case.execute(
                devis_id=1,
                file_content=csv_content,
                filename="dpgf.csv",
                imported_by=5,
            )
        assert "Aucune ligne" in exc_info.value.message

    def test_import_csv_virgule_delimiteur(self):
        """Test: detection automatique du delimiteur virgule."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content(
            [
                ["lot", "description", "unite", "quantite", "pu"],
                ["01", "Ligne 1", "m2", "10", "25"],
            ],
            delimiter=",",
        )

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        assert result.lignes_creees == 1

    def test_import_csv_custom_mapping(self):
        """Test: import avec mapping de colonnes personnalise."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        # Format non standard: description en col 0, lot en col 1, etc.
        csv_content = _make_csv_content([
            ["desc", "lot", "qty", "pu", "unite"],
            ["Demolition", "A", "10", "25", "m2"],
        ])

        mapping = DPGFColumnMappingDTO(
            col_lot=1,
            col_description=0,
            col_unite=4,
            col_quantite=2,
            col_prix_unitaire=3,
        )

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
            mapping=mapping,
        )

        assert result.lignes_creees == 1
        ligne_call = self.mock_ligne_repo.save.call_args[0][0]
        assert ligne_call.libelle == "Demolition"
        assert ligne_call.quantite == Decimal("10")
        assert ligne_call.prix_unitaire_ht == Decimal("25")

    def test_import_csv_lignes_vides_ignorees(self):
        """Test: les lignes sans description sont ignorees."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
            ["01", "Ligne valide", "u", "1", "100"],
            ["01", "", "u", "1", "50"],  # Description vide -> ignoree
            ["01", "Autre ligne", "u", "2", "75"],
        ])

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        assert result.lignes_creees == 2

    def test_import_journal_entry(self):
        """Test: une entree journal est creee apres import."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
            ["01", "Ligne 1", "u", "1", "100"],
        ])

        self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf_projet_x.csv",
            imported_by=5,
        )

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "import_dpgf"
        assert journal_call.auteur_id == 5
        assert "dpgf_projet_x.csv" in journal_call.details_json["message"]
        assert journal_call.details_json["type_modification"] == "import_dpgf"

    def test_import_respecte_ordre_lots_existants(self):
        """Test: les nouveaux lots commencent apres les lots existants."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        # 2 lots existants
        existing_lot1 = LotDevis(id=10, devis_id=1, code_lot="01", libelle="Lot 1", ordre=1)
        existing_lot2 = LotDevis(id=11, devis_id=1, code_lot="02", libelle="Lot 2", ordre=2)
        self.mock_lot_repo.find_by_devis.return_value = [existing_lot1, existing_lot2]

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
            ["03", "Nouveau lot", "u", "1", "100"],
        ])

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        # Le nouveau lot doit avoir ordre = 3 (max(1,2) + 1)
        lot_call = self.mock_lot_repo.save.call_args[0][0]
        assert lot_call.ordre == 3

    def test_import_tva_defaut_du_devis(self):
        """Test: les lignes importees utilisent le taux TVA par defaut du devis."""
        devis = _make_devis(taux_tva_defaut=Decimal("10"))
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
            ["01", "Ligne", "u", "1", "100"],
        ])

        self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        ligne_call = self.mock_ligne_repo.save.call_args[0][0]
        assert ligne_call.taux_tva == Decimal("10")

    def test_import_result_contains_details(self):
        """Test: le resultat contient les details des lots et lignes crees."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_lot_repo.find_by_devis.return_value = []

        csv_content = _make_csv_content([
            ["lot", "description", "unite", "quantite", "pu"],
            ["01", "Demolition", "m2", "25", "30"],
        ])

        result = self.use_case.execute(
            devis_id=1,
            file_content=csv_content,
            filename="dpgf.csv",
            imported_by=5,
        )

        result_dict = result.to_dict()
        assert result_dict["devis_id"] == 1
        assert result_dict["lots_crees"] == 1
        assert result_dict["lignes_creees"] == 1
        assert len(result_dict["lots"]) == 1
        assert result_dict["lots"][0]["code_lot"] == "01"
        assert result_dict["lots"][0]["nb_lignes"] == 1


class TestImportDPGFExcel:
    """Tests specifiques pour l'import Excel."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_lot_repo = Mock(spec=LotDevisRepository)
        self.mock_ligne_repo = Mock(spec=LigneDevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)

        self.mock_lot_repo.save.side_effect = lambda l: setattr(l, 'id', 1) or l
        self.mock_ligne_repo.save.side_effect = lambda l: setattr(l, 'id', 1) or l
        self.mock_journal_repo.save.return_value = Mock()

        self.use_case = ImportDPGFUseCase(
            devis_repository=self.mock_devis_repo,
            lot_repository=self.mock_lot_repo,
            ligne_repository=self.mock_ligne_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_import_xlsx_format_accepted(self):
        """Test: les fichiers .xlsx sont acceptes (si openpyxl installe)."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        # Creer un vrai fichier Excel minimal avec openpyxl
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl non installe")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["lot", "description", "unite", "quantite", "pu"])
        ws.append(["01", "Demolition", "m2", "25", "30"])

        excel_bytes = io.BytesIO()
        wb.save(excel_bytes)
        excel_content = excel_bytes.getvalue()

        self.mock_lot_repo.find_by_devis.return_value = []

        result = self.use_case.execute(
            devis_id=1,
            file_content=excel_content,
            filename="dpgf.xlsx",
            imported_by=5,
        )

        assert result.lots_crees == 1
        assert result.lignes_creees == 1
