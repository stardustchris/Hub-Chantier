"""Tests unitaires pour les Use Cases Export Comptable du module Financier."""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from modules.financier.domain.repositories import ExportComptableRepository
from modules.financier.application.dtos.export_dtos import (
    ExportLigneComptableDTO,
    ExportComptableDTO,
)
from modules.financier.application.use_cases.export_comptable_use_cases import (
    GenerateExportComptableUseCase,
    ExportCSVUseCase,
    ExportExcelUseCase,
    COMPTES_ACHATS,
    COMPTE_VENTES,
    COMPTE_TVA_DEDUCTIBLE,
    COMPTE_TVA_COLLECTEE,
    COMPTE_FOURNISSEUR,
    COMPTE_CLIENT,
)


class TestGenerateExportComptableUseCase:
    """Tests pour le use case de generation d'export comptable."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_export_repo = Mock(spec=ExportComptableRepository)
        self.use_case = GenerateExportComptableUseCase(
            export_repository=self.mock_export_repo,
        )

    def test_export_achat_materiau(self):
        """Test: export comptable d'un achat de type materiau."""
        achat = {
            "type_achat": "materiau",
            "montant_ht": "10000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": "2026-01-15",
            "numero_facture": "FA-001",
            "libelle": "Ciment Portland",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
            chantier_id=5,
        )

        assert result.nombre_lignes == 3
        assert result.chantier_id == 5
        # Ligne 1: charge HT au debit (601000 pour materiau)
        assert result.lignes[0].compte_general == "601000"
        assert result.lignes[0].debit == "10000.00"
        assert result.lignes[0].credit == "0.00"
        assert result.lignes[0].code_journal == "HA"
        # Ligne 2: TVA deductible au debit
        assert result.lignes[1].compte_general == COMPTE_TVA_DEDUCTIBLE
        assert result.lignes[1].debit == "2000.00"
        assert result.lignes[1].credit == "0.00"
        # Ligne 3: fournisseur au credit TTC
        assert result.lignes[2].compte_general == COMPTE_FOURNISSEUR
        assert result.lignes[2].debit == "0.00"
        assert result.lignes[2].credit == "12000.00"

    def test_export_achat_sous_traitance(self):
        """Test: export comptable d'un achat de type sous_traitance."""
        achat = {
            "type_achat": "sous_traitance",
            "montant_ht": "5000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": "2026-01-20",
            "numero_facture": "FA-002",
            "libelle": "Sous-traitance electricite",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        # Compte 604000 pour sous_traitance
        assert result.lignes[0].compte_general == "604000"

    def test_export_achat_service(self):
        """Test: export comptable d'un achat de type service."""
        achat = {
            "type_achat": "service",
            "montant_ht": "3000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": "2026-01-20",
            "numero_facture": "FA-003",
            "libelle": "Etude geotechnique",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.lignes[0].compte_general == "615000"

    def test_export_achat_materiel(self):
        """Test: export comptable d'un achat de type materiel."""
        achat = {
            "type_achat": "materiel",
            "montant_ht": "8000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": "2026-01-20",
            "numero_facture": "FA-004",
            "libelle": "Location pelleteuse",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.lignes[0].compte_general == "606000"

    def test_export_achat_type_inconnu_default_601000(self):
        """Test: type d'achat inconnu utilise le compte par defaut 601000."""
        achat = {
            "type_achat": "inconnu",
            "montant_ht": "1000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": "2026-01-20",
            "numero_facture": "FA-005",
            "libelle": "Divers",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.lignes[0].compte_general == "601000"

    def test_export_achat_tva_zero(self):
        """Test: achat avec TVA a 0% ne genere pas de ligne TVA."""
        achat = {
            "type_achat": "materiau",
            "montant_ht": "10000",
            "taux_tva": "0",
            "chantier_id": 5,
            "date_facture": "2026-01-15",
            "numero_facture": "FA-006",
            "libelle": "Import hors TVA",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        # Pas de ligne TVA, seulement charge + fournisseur
        assert result.nombre_lignes == 2
        assert result.lignes[0].compte_general == "601000"
        assert result.lignes[1].compte_general == COMPTE_FOURNISSEUR

    def test_export_facture_client(self):
        """Test: export comptable d'une facture client emise."""
        facture = {
            "montant_ht": "20000",
            "montant_tva": "4000",
            "montant_ttc": "24000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_emission": "2026-01-25",
            "numero_facture": "FC-001",
        }
        self.mock_export_repo.get_achats_periode.return_value = []
        self.mock_export_repo.get_factures_periode.return_value = [facture]

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.nombre_lignes == 3
        # Ligne 1: Client au debit TTC
        assert result.lignes[0].compte_general == COMPTE_CLIENT
        assert result.lignes[0].debit == "24000.00"
        assert result.lignes[0].credit == "0.00"
        assert result.lignes[0].code_journal == "VE"
        # Ligne 2: Vente HT au credit
        assert result.lignes[1].compte_general == COMPTE_VENTES
        assert result.lignes[1].debit == "0.00"
        assert result.lignes[1].credit == "20000.00"
        # Ligne 3: TVA collectee au credit
        assert result.lignes[2].compte_general == COMPTE_TVA_COLLECTEE
        assert result.lignes[2].debit == "0.00"
        assert result.lignes[2].credit == "4000.00"

    def test_export_facture_sans_tva(self):
        """Test: facture client sans TVA ne genere pas de ligne TVA collectee."""
        facture = {
            "montant_ht": "20000",
            "montant_tva": "0",
            "montant_ttc": "20000",
            "taux_tva": "0",
            "chantier_id": 5,
            "date_emission": "2026-01-25",
            "numero_facture": "FC-002",
        }
        self.mock_export_repo.get_achats_periode.return_value = []
        self.mock_export_repo.get_factures_periode.return_value = [facture]

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        # Pas de ligne TVA collectee
        assert result.nombre_lignes == 2
        assert result.lignes[0].compte_general == COMPTE_CLIENT
        assert result.lignes[1].compte_general == COMPTE_VENTES

    def test_export_mixte_achats_et_factures(self):
        """Test: export comptable avec achats ET factures combinés."""
        achat = {
            "type_achat": "materiau",
            "montant_ht": "10000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": "2026-01-15",
            "numero_facture": "FA-001",
            "libelle": "Ciment",
        }
        facture = {
            "montant_ht": "20000",
            "montant_tva": "4000",
            "montant_ttc": "24000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_emission": "2026-01-25",
            "numero_facture": "FC-001",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = [facture]

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        # 3 lignes achat + 3 lignes facture = 6
        assert result.nombre_lignes == 6

    def test_export_periode_vide(self):
        """Test: export comptable sans achats ni factures."""
        self.mock_export_repo.get_achats_periode.return_value = []
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.nombre_lignes == 0
        assert result.total_debit == "0.00"
        assert result.total_credit == "0.00"
        assert len(result.lignes) == 0

    def test_export_totaux_equilibres(self):
        """Test: les totaux debit et credit sont equilibres."""
        achat = {
            "type_achat": "materiau",
            "montant_ht": "10000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": "2026-01-15",
            "numero_facture": "FA-001",
            "libelle": "Test equilibrage",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        # Pour un achat: debit = HT + TVA = 10000 + 2000 = 12000
        # credit = TTC = 12000
        assert result.total_debit == result.total_credit

    def test_export_chantier_id_none_tous_chantiers(self):
        """Test: chantier_id None signifie tous les chantiers."""
        self.mock_export_repo.get_achats_periode.return_value = []
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
            chantier_id=None,
        )

        assert result.chantier_id is None
        self.mock_export_repo.get_achats_periode.assert_called_once_with(
            None, date(2026, 1, 1), date(2026, 1, 31)
        )

    def test_export_dates_format(self):
        """Test: les dates sont formatees en ISO dans le DTO resultat."""
        self.mock_export_repo.get_achats_periode.return_value = []
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.date_debut == "2026-01-01"
        assert result.date_fin == "2026-01-31"

    def test_export_achat_date_objet(self):
        """Test: les dates d'achat sous forme d'objet date sont converties."""
        achat = {
            "type_achat": "materiau",
            "montant_ht": "1000",
            "taux_tva": "20",
            "chantier_id": 5,
            "date_facture": date(2026, 1, 15),
            "numero_facture": "FA-001",
            "libelle": "Test date objet",
        }
        self.mock_export_repo.get_achats_periode.return_value = [achat]
        self.mock_export_repo.get_factures_periode.return_value = []

        result = self.use_case.execute(
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.lignes[0].date == "2026-01-15"


class TestExportCSVUseCase:
    """Tests pour le use case d'export CSV."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.use_case = ExportCSVUseCase()

    def test_csv_header(self):
        """Test: le CSV contient l'en-tete correct."""
        export_dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=[],
            total_debit="0.00",
            total_credit="0.00",
            nombre_lignes=0,
        )

        csv_content = self.use_case.execute(export_dto)

        lines = csv_content.strip().split("\n")
        header = lines[0]
        assert "Date" in header
        assert "Code Journal" in header
        assert "Numero Piece" in header
        assert "Code Analytique" in header
        assert "Libelle" in header
        assert "Compte General" in header
        assert "Debit" in header
        assert "Credit" in header
        assert "Code TVA" in header

    def test_csv_with_lignes(self):
        """Test: le CSV contient les lignes d'ecritures."""
        lignes = [
            ExportLigneComptableDTO(
                date="2026-01-15",
                code_journal="HA",
                numero_piece="FA-001",
                code_analytique="5",
                libelle="Ciment Portland",
                compte_general="601000",
                debit="10000.00",
                credit="0.00",
                tva_code="20",
            ),
            ExportLigneComptableDTO(
                date="2026-01-15",
                code_journal="HA",
                numero_piece="FA-001",
                code_analytique="5",
                libelle="TVA deductible - Ciment Portland",
                compte_general="445660",
                debit="2000.00",
                credit="0.00",
                tva_code="20",
            ),
        ]
        export_dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=lignes,
            total_debit="12000.00",
            total_credit="0.00",
            nombre_lignes=2,
        )

        csv_content = self.use_case.execute(export_dto)

        assert "601000" in csv_content
        assert "445660" in csv_content
        assert "10000.00" in csv_content
        assert "2000.00" in csv_content

    def test_csv_separator_semicolon(self):
        """Test: le CSV utilise le point-virgule comme separateur."""
        export_dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=[
                ExportLigneComptableDTO(
                    date="2026-01-15",
                    code_journal="HA",
                    numero_piece="FA-001",
                    code_analytique="5",
                    libelle="Test",
                    compte_general="601000",
                    debit="1000.00",
                    credit="0.00",
                    tva_code="20",
                ),
            ],
            total_debit="1000.00",
            total_credit="0.00",
            nombre_lignes=1,
        )

        csv_content = self.use_case.execute(export_dto)

        lines = csv_content.strip().split("\n")
        # L'en-tete contient des point-virgules
        assert ";" in lines[0]

    def test_csv_totaux_en_fin(self):
        """Test: le CSV contient les totaux en fin de fichier."""
        export_dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=[],
            total_debit="12000.00",
            total_credit="12000.00",
            nombre_lignes=0,
        )

        csv_content = self.use_case.execute(export_dto)

        assert "TOTAUX" in csv_content
        assert "12000.00" in csv_content

    def test_csv_empty_export(self):
        """Test: le CSV vide contient quand meme l'en-tete et les totaux."""
        export_dto = ExportComptableDTO(
            chantier_id=None,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=[],
            total_debit="0.00",
            total_credit="0.00",
            nombre_lignes=0,
        )

        csv_content = self.use_case.execute(export_dto)

        assert "Date" in csv_content
        assert "TOTAUX" in csv_content


class TestExportExcelUseCase:
    """Tests pour le use case d'export Excel."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.use_case = ExportExcelUseCase()

    def test_excel_returns_bytes(self):
        """Test: l'export Excel retourne des bytes."""
        export_dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=[],
            total_debit="0.00",
            total_credit="0.00",
            nombre_lignes=0,
        )

        result = self.use_case.execute(export_dto)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_excel_with_lignes(self):
        """Test: l'export Excel avec des lignes produit des bytes valides."""
        lignes = [
            ExportLigneComptableDTO(
                date="2026-01-15",
                code_journal="HA",
                numero_piece="FA-001",
                code_analytique="5",
                libelle="Ciment Portland",
                compte_general="601000",
                debit="10000.00",
                credit="0.00",
                tva_code="20",
            ),
        ]
        export_dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=lignes,
            total_debit="10000.00",
            total_credit="0.00",
            nombre_lignes=1,
        )

        result = self.use_case.execute(export_dto)

        assert isinstance(result, bytes)
        # Signature XLSX (ZIP)
        assert result[:2] == b"PK"

    def test_excel_without_chantier_id(self):
        """Test: l'export Excel fonctionne sans chantier_id."""
        export_dto = ExportComptableDTO(
            chantier_id=None,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=[],
            total_debit="0.00",
            total_credit="0.00",
            nombre_lignes=0,
        )

        result = self.use_case.execute(export_dto)

        assert isinstance(result, bytes)
        assert len(result) > 0


class TestConstantesComptables:
    """Tests pour les constantes comptables."""

    def test_comptes_achats_materiau(self):
        """Test: compte achats materiaux est 601000."""
        assert COMPTES_ACHATS["materiau"] == "601000"

    def test_comptes_achats_sous_traitance(self):
        """Test: compte sous-traitance est 604000."""
        assert COMPTES_ACHATS["sous_traitance"] == "604000"

    def test_comptes_achats_service(self):
        """Test: compte services est 615000."""
        assert COMPTES_ACHATS["service"] == "615000"

    def test_comptes_achats_materiel(self):
        """Test: compte materiel est 606000."""
        assert COMPTES_ACHATS["materiel"] == "606000"

    def test_compte_ventes(self):
        """Test: compte ventes est 706000."""
        assert COMPTE_VENTES == "706000"

    def test_compte_tva_deductible(self):
        """Test: compte TVA deductible est 445660."""
        assert COMPTE_TVA_DEDUCTIBLE == "445660"

    def test_compte_tva_collectee(self):
        """Test: compte TVA collectee est 445710."""
        assert COMPTE_TVA_COLLECTEE == "445710"

    def test_compte_fournisseur(self):
        """Test: compte fournisseur est 401000."""
        assert COMPTE_FOURNISSEUR == "401000"

    def test_compte_client(self):
        """Test: compte client est 411000."""
        assert COMPTE_CLIENT == "411000"
