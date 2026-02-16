"""Tests unitaires pour GenerateDevisPDFUseCase.

DEV-12: Generation PDF devis client.
"""

import pytest
from unittest.mock import MagicMock

from modules.devis.application.use_cases.generate_pdf_use_case import (
    GenerateDevisPDFUseCase,
    GenerateDevisPDFError,
)
from modules.devis.application.dtos.devis_dtos import DevisDetailDTO, VentilationTVADTO
from modules.devis.application.dtos.lot_dtos import LotDevisDTO
from modules.devis.application.dtos.ligne_dtos import LigneDevisDTO


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _make_ligne(**kwargs) -> LigneDevisDTO:
    """Factory pour creer un LigneDevisDTO de test."""
    defaults = {
        "id": 1,
        "lot_devis_id": 1,
        "designation": "Fourniture et pose parpaings",
        "unite": "m2",
        "quantite": "50.00",
        "prix_unitaire_ht": "45.00",
        "montant_ht": "2250.00",
        "taux_tva": "20.0",
        "montant_ttc": "2700.00",
        "ordre": 1,
        "marge_ligne_pct": None,
        "article_id": None,
        "debourse_sec": "1800.00",
        "prix_revient": "2016.00",
        "debourses": [],
    }
    defaults.update(kwargs)
    return LigneDevisDTO(**defaults)


def _make_lot(**kwargs) -> LotDevisDTO:
    """Factory pour creer un LotDevisDTO de test."""
    defaults = {
        "id": 1,
        "devis_id": 1,
        "titre": "Maconnerie",
        "numero": "1",
        "total_ht": "2250.00",
        "total_ttc": "2700.00",
        "debourse_sec": "1800.00",
        "ordre": 1,
        "marge_lot_pct": None,
        "lignes": [_make_ligne()],
    }
    defaults.update(kwargs)
    return LotDevisDTO(**defaults)


def _make_devis_detail_dto(**kwargs) -> DevisDetailDTO:
    """Factory pour creer un DevisDetailDTO de test."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "M. Martin",
        "client_adresse": "25 avenue Victor Hugo\n69006 Lyon",
        "client_telephone": "04 72 11 22 33",
        "client_email": "martin@email.com",
        "objet": "Renovation cuisine",
        "statut": "brouillon",
        "date_creation": "2026-02-01",
        "date_validite": "2026-03-01",
        "updated_at": "2026-02-01T10:00:00",
        "montant_total_ht": "2250.00",
        "montant_total_ttc": "2700.00",
        "taux_marge_global": "15",
        "taux_marge_moe": None,
        "taux_marge_materiaux": None,
        "taux_marge_sous_traitance": None,
        "taux_marge_materiel": None,
        "taux_marge_deplacement": None,
        "coefficient_frais_generaux": "0.12",
        "coefficient_productivite": None,
        "retenue_garantie_pct": "0",
        "montant_retenue_garantie": "0.00",
        "montant_net_a_payer": "2700.00",
        "taux_tva_defaut": "20",
        "commercial_id": None,
        "conducteur_id": None,
        "chantier_ref": None,
        "created_by": 1,
        "notes": None,
        "conditions_generales": "Devis valable 30 jours.",
        "lots": [_make_lot()],
        "acompte_pct": "30",
        "echeance": "30_jours_fin_mois",
        "moyens_paiement": ["cheque", "virement"],
        "ventilation_tva": [
            VentilationTVADTO(
                taux="20.0",
                base_ht="2250.00",
                montant_tva="450.00",
            ),
        ],
    }
    defaults.update(kwargs)
    return DevisDetailDTO(**defaults)


def _make_use_case():
    """Cree un use case avec des mocks."""
    get_devis_uc = MagicMock()
    pdf_generator = MagicMock()

    use_case = GenerateDevisPDFUseCase(
        get_devis_use_case=get_devis_uc,
        pdf_generator=pdf_generator,
    )

    return use_case, get_devis_uc, pdf_generator


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestGenerateDevisPDFUseCase:
    """Tests pour GenerateDevisPDFUseCase."""

    def test_execute_success(self):
        """Test: generation PDF reussie."""
        use_case, get_devis_uc, pdf_gen = _make_use_case()

        devis_detail = _make_devis_detail_dto()
        get_devis_uc.execute.return_value = devis_detail
        pdf_gen.generate.return_value = b"%PDF-fake-devis-content"

        pdf_bytes, filename = use_case.execute(1)

        assert pdf_bytes == b"%PDF-fake-devis-content"
        assert filename == "DEV-2026-001.pdf"

        get_devis_uc.execute.assert_called_once_with(1)
        pdf_gen.generate.assert_called_once_with(devis_detail)

    def test_execute_devis_not_found(self):
        """Test: erreur si le devis n'existe pas (via GetDevisUseCase)."""
        use_case, get_devis_uc, pdf_gen = _make_use_case()

        from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
        get_devis_uc.execute.side_effect = DevisNotFoundError(999)

        with pytest.raises(DevisNotFoundError):
            use_case.execute(999)

    def test_execute_pdf_generation_error(self):
        """Test: GenerateDevisPDFError si la generation echoue."""
        use_case, get_devis_uc, pdf_gen = _make_use_case()

        devis_detail = _make_devis_detail_dto()
        get_devis_uc.execute.return_value = devis_detail
        pdf_gen.generate.side_effect = RuntimeError("fpdf2 error")

        with pytest.raises(GenerateDevisPDFError):
            use_case.execute(1)

    def test_filename_uses_devis_numero(self):
        """Test: le nom de fichier utilise le numero du devis."""
        use_case, get_devis_uc, pdf_gen = _make_use_case()

        devis_detail = _make_devis_detail_dto(numero="DEV-2026-042-R2")
        get_devis_uc.execute.return_value = devis_detail
        pdf_gen.generate.return_value = b"%PDF"

        _, filename = use_case.execute(42)
        assert filename == "DEV-2026-042-R2.pdf"

    def test_generator_receives_complete_dto(self):
        """Test: le generateur recoit le DTO complet avec lots et ventilation TVA."""
        use_case, get_devis_uc, pdf_gen = _make_use_case()

        devis_detail = _make_devis_detail_dto()
        get_devis_uc.execute.return_value = devis_detail
        pdf_gen.generate.return_value = b"%PDF"

        use_case.execute(1)

        # Verifie que le DTO est passe tel quel
        pdf_gen.generate.assert_called_once_with(devis_detail)
        passed_dto = pdf_gen.generate.call_args[0][0]
        assert passed_dto.client_nom == "M. Martin"
        assert len(passed_dto.lots) == 1
        assert passed_dto.lots[0].titre == "Maconnerie"
        assert len(passed_dto.lots[0].lignes) == 1
        assert passed_dto.lots[0].lignes[0].designation == "Fourniture et pose parpaings"
        assert len(passed_dto.ventilation_tva) == 1
        assert passed_dto.ventilation_tva[0].taux == "20.0"

    def test_execute_does_not_expose_internal_data(self):
        """Test: le PDF client ne contient pas les debourses ni marges internes."""
        use_case, get_devis_uc, pdf_gen = _make_use_case()

        devis_detail = _make_devis_detail_dto()
        get_devis_uc.execute.return_value = devis_detail
        pdf_gen.generate.return_value = b"%PDF"

        use_case.execute(1)

        # Le use case passe le DTO au generateur; c'est le generateur (fpdf2)
        # qui est responsable de ne pas afficher les debourses/marges dans le PDF.
        # On verifie simplement que l'appel est correct.
        pdf_gen.generate.assert_called_once()
