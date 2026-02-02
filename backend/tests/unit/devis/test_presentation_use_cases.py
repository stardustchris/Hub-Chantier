"""Tests unitaires pour les Use Cases de presentation de devis.

DEV-11: Personnalisation presentation - Modeles de mise en page configurables.
Couche Application - presentation_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.value_objects.options_presentation import (
    OptionsPresentation,
    OptionsPresentationInvalideError,
    TEMPLATES_PRESENTATION,
)
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import DevisNotFoundError
from modules.devis.application.use_cases.presentation_use_cases import (
    UpdateOptionsPresentationUseCase,
    GetOptionsPresentationUseCase,
    ListTemplatesPresentationUseCase,
)
from modules.devis.application.dtos.options_presentation_dtos import (
    OptionsPresentationDTO,
    UpdateOptionsPresentationDTO,
    ListeTemplatesPresentationDTO,
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
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Tests UpdateOptionsPresentationUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestUpdateOptionsPresentationUseCase:
    """Tests pour la mise a jour des options de presentation."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = UpdateOptionsPresentationUseCase(
            devis_repo=self.mock_devis_repo,
            journal_repo=self.mock_journal_repo,
        )

    def test_update_options_success(self):
        """Test: mise a jour des options de presentation reussie."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = UpdateOptionsPresentationDTO(
            afficher_composants=True,
            afficher_tva_detaillee=False,
        )
        result = self.use_case.execute(devis_id=1, dto=dto, user_id=1)

        assert isinstance(result, OptionsPresentationDTO)
        assert result.afficher_composants is True
        assert result.afficher_tva_detaillee is False
        self.mock_devis_repo.save.assert_called_once()
        self.mock_journal_repo.save.assert_called_once()

    def test_update_options_with_template(self):
        """Test: application d'un template puis surcharge."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = UpdateOptionsPresentationDTO(
            template_nom="minimaliste",
            afficher_quantites=True,  # surcharge du template
        )
        result = self.use_case.execute(devis_id=1, dto=dto, user_id=1)

        assert isinstance(result, OptionsPresentationDTO)
        # minimaliste a afficher_quantites=False, mais on surcharge a True
        assert result.afficher_quantites is True
        # minimaliste: afficher_prix_unitaires=False
        assert result.afficher_prix_unitaires is False

    def test_update_options_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        dto = UpdateOptionsPresentationDTO(afficher_composants=True)
        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999, dto=dto, user_id=1)

    def test_update_options_template_invalide(self):
        """Test: erreur si template invalide."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        dto = UpdateOptionsPresentationDTO(template_nom="inexistant")
        with pytest.raises(OptionsPresentationInvalideError):
            self.use_case.execute(devis_id=1, dto=dto, user_id=1)

    def test_update_options_debourses_toujours_false(self):
        """Test: les debourses sont toujours False (regle metier)."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = UpdateOptionsPresentationDTO(afficher_debourses=True)
        result = self.use_case.execute(devis_id=1, dto=dto, user_id=1)

        # Meme si on passe True, la regle metier force a False
        assert result.afficher_debourses is False


# ─────────────────────────────────────────────────────────────────────────────
# Tests GetOptionsPresentationUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestGetOptionsPresentationUseCase:
    """Tests pour la recuperation des options de presentation."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.use_case = GetOptionsPresentationUseCase(
            devis_repo=self.mock_devis_repo,
        )

    def test_get_options_success(self):
        """Test: recuperation des options par defaut."""
        devis = _make_devis()
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert isinstance(result, OptionsPresentationDTO)
        assert result.template_nom == "standard"

    def test_get_options_not_found(self):
        """Test: erreur si devis non trouve."""
        self.mock_devis_repo.find_by_id.return_value = None

        with pytest.raises(DevisNotFoundError):
            self.use_case.execute(devis_id=999)

    def test_get_options_custom(self):
        """Test: recuperation d'options personnalisees."""
        devis = _make_devis(
            options_presentation_json={
                "afficher_debourses": False,
                "afficher_composants": True,
                "afficher_quantites": True,
                "afficher_prix_unitaires": True,
                "afficher_tva_detaillee": False,
                "afficher_conditions_generales": True,
                "afficher_logo": True,
                "afficher_coordonnees_entreprise": True,
                "afficher_retenue_garantie": True,
                "afficher_frais_chantier_detail": False,
                "template_nom": "detaille",
            }
        )
        self.mock_devis_repo.find_by_id.return_value = devis

        result = self.use_case.execute(devis_id=1)

        assert result.afficher_composants is True
        assert result.afficher_tva_detaillee is False
        assert result.template_nom == "detaille"


# ─────────────────────────────────────────────────────────────────────────────
# Tests ListTemplatesPresentationUseCase
# ─────────────────────────────────────────────────────────────────────────────

class TestListTemplatesPresentationUseCase:
    """Tests pour le listage des templates de presentation."""

    def setup_method(self):
        self.use_case = ListTemplatesPresentationUseCase()

    def test_list_templates(self):
        """Test: retourne tous les templates disponibles."""
        result = self.use_case.execute()

        assert isinstance(result, ListeTemplatesPresentationDTO)
        assert len(result.templates) == len(TEMPLATES_PRESENTATION)

    def test_list_templates_contenu(self):
        """Test: chaque template a un nom, description et options."""
        result = self.use_case.execute()

        for template in result.templates:
            assert template.nom
            assert template.description
            assert isinstance(template.options, dict)

    def test_list_templates_noms_connus(self):
        """Test: les noms de templates connus sont presents."""
        result = self.use_case.execute()
        noms = [t.nom for t in result.templates]

        assert "standard" in noms
        assert "simplifie" in noms
        assert "detaille" in noms
        assert "minimaliste" in noms
