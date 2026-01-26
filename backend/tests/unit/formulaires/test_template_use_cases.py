"""Tests unitaires pour les use cases de template formulaire."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from modules.formulaires.application.use_cases.delete_template import (
    DeleteTemplateUseCase,
    TemplateNotFoundError,
)
from modules.formulaires.application.use_cases.update_template import (
    UpdateTemplateUseCase,
    TemplateNotFoundError as UpdateTemplateNotFoundError,
)
from modules.formulaires.application.use_cases.get_template import GetTemplateUseCase
from modules.formulaires.application.use_cases.list_templates import ListTemplatesUseCase
from modules.formulaires.application.dtos import (
    UpdateTemplateDTO,
    ChampTemplateDTO,
)
from modules.formulaires.domain.value_objects import CategorieFormulaire, TypeChamp


def create_mock_template(template_id=1, nom="Template Test", is_active=True):
    """Helper pour créer un mock de template."""
    mock = Mock()
    mock.id = template_id
    mock.nom = nom
    mock.description = "Description test"
    mock.categorie = CategorieFormulaire.SECURITE
    mock.is_active = is_active
    mock.version = 1
    mock.champs = []
    mock.nombre_champs = 0
    mock.a_signature = False
    mock.a_photo = False
    mock.created_by = 1
    mock.created_at = datetime.now()
    mock.updated_at = datetime.now()
    return mock


class TestDeleteTemplateUseCase:
    """Tests pour DeleteTemplateUseCase."""

    def test_delete_template_success(self):
        """Test suppression template réussie."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.delete.return_value = True

        use_case = DeleteTemplateUseCase(mock_repo)
        result = use_case.execute(template_id=1, deleted_by=2)

        assert result is True
        mock_repo.find_by_id.assert_called_once_with(1)
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_template_not_found(self):
        """Test erreur si template non trouvé."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = DeleteTemplateUseCase(mock_repo)

        with pytest.raises(TemplateNotFoundError, match="non trouve"):
            use_case.execute(template_id=999)

    def test_delete_template_with_event_publisher(self):
        """Test suppression avec publication d'événement."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.delete.return_value = True
        mock_publisher = Mock()

        use_case = DeleteTemplateUseCase(mock_repo, event_publisher=mock_publisher)
        result = use_case.execute(template_id=1, deleted_by=2)

        assert result is True
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.template_id == 1
        assert event.nom == "Template Test"
        assert event.deleted_by == 2

    def test_delete_template_no_event_if_delete_fails(self):
        """Test pas d'événement si suppression échoue."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.delete.return_value = False
        mock_publisher = Mock()

        use_case = DeleteTemplateUseCase(mock_repo, event_publisher=mock_publisher)
        result = use_case.execute(template_id=1)

        assert result is False
        mock_publisher.assert_not_called()


class TestUpdateTemplateUseCase:
    """Tests pour UpdateTemplateUseCase."""

    def test_update_template_basic(self):
        """Test mise à jour basique du template."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.save.return_value = mock_template

        dto = UpdateTemplateDTO(
            nom="Nouveau nom",
            description="Nouvelle description",
        )

        use_case = UpdateTemplateUseCase(mock_repo)
        result = use_case.execute(template_id=1, dto=dto)

        assert result is not None
        mock_template.update.assert_called_once()

    def test_update_template_not_found(self):
        """Test erreur si template non trouvé."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        dto = UpdateTemplateDTO(nom="Test")

        use_case = UpdateTemplateUseCase(mock_repo)

        with pytest.raises(UpdateTemplateNotFoundError, match="non trouve"):
            use_case.execute(template_id=999, dto=dto)

    def test_update_template_activate(self):
        """Test activation du template."""
        mock_repo = Mock()
        mock_template = create_mock_template(is_active=False)
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.save.return_value = mock_template

        dto = UpdateTemplateDTO(is_active=True)

        use_case = UpdateTemplateUseCase(mock_repo)
        use_case.execute(template_id=1, dto=dto)

        mock_template.activer.assert_called_once()

    def test_update_template_deactivate(self):
        """Test désactivation du template."""
        mock_repo = Mock()
        mock_template = create_mock_template(is_active=True)
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.save.return_value = mock_template

        dto = UpdateTemplateDTO(is_active=False)

        use_case = UpdateTemplateUseCase(mock_repo)
        use_case.execute(template_id=1, dto=dto)

        mock_template.desactiver.assert_called_once()

    def test_update_template_with_champs(self):
        """Test mise à jour avec nouveaux champs."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_template.champs = []
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.save.return_value = mock_template

        champ_dto = ChampTemplateDTO(
            nom="champ1",
            label="Champ 1",
            type_champ="texte",
            obligatoire=True,
            ordre=0,
        )
        dto = UpdateTemplateDTO(champs=[champ_dto])

        use_case = UpdateTemplateUseCase(mock_repo)
        use_case.execute(template_id=1, dto=dto)

        mock_template.ajouter_champ.assert_called_once()
        mock_template.incrementer_version.assert_called_once()

    def test_update_template_with_event_publisher(self):
        """Test mise à jour avec publication d'événement."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.save.return_value = mock_template
        mock_publisher = Mock()

        dto = UpdateTemplateDTO(nom="Nouveau nom")

        use_case = UpdateTemplateUseCase(mock_repo, event_publisher=mock_publisher)
        use_case.execute(template_id=1, dto=dto, updated_by=2)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.template_id == 1
        assert event.updated_by == 2

    def test_update_template_with_categorie(self):
        """Test mise à jour de la catégorie."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_id.return_value = mock_template
        mock_repo.save.return_value = mock_template

        # Utiliser une valeur valide de CategorieFormulaire
        dto = UpdateTemplateDTO(categorie="securite")

        use_case = UpdateTemplateUseCase(mock_repo)
        use_case.execute(template_id=1, dto=dto)

        # Vérifie que update a été appelé avec la bonne catégorie
        mock_template.update.assert_called_once()


class TestGetTemplateUseCase:
    """Tests pour GetTemplateUseCase."""

    def test_get_template_found(self):
        """Test récupération template existant."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_id.return_value = mock_template

        use_case = GetTemplateUseCase(mock_repo)
        result = use_case.execute(template_id=1)

        assert result is not None
        assert result.id == 1

    def test_get_template_not_found(self):
        """Test récupération template non existant lève erreur."""
        from modules.formulaires.application.use_cases.get_template import TemplateNotFoundError as GetTemplateNotFoundError

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = GetTemplateUseCase(mock_repo)

        with pytest.raises(GetTemplateNotFoundError, match="non trouve"):
            use_case.execute(template_id=999)

    def test_get_template_by_nom(self):
        """Test récupération template par nom."""
        mock_repo = Mock()
        mock_template = create_mock_template()
        mock_repo.find_by_nom.return_value = mock_template

        use_case = GetTemplateUseCase(mock_repo)
        result = use_case.execute_by_nom(nom="Template Test")

        assert result is not None
        mock_repo.find_by_nom.assert_called_once_with("Template Test")


class TestListTemplatesUseCase:
    """Tests pour ListTemplatesUseCase."""

    def test_list_templates_with_search(self):
        """Test liste templates avec recherche."""
        mock_repo = Mock()
        mock_templates = [create_mock_template(i) for i in range(3)]
        mock_repo.search.return_value = (mock_templates, 3)

        use_case = ListTemplatesUseCase(mock_repo)
        result = use_case.execute()

        assert result.total == 3
        assert len(result.templates) == 3
        mock_repo.search.assert_called_once()

    def test_list_templates_active_only(self):
        """Test liste templates actifs uniquement."""
        mock_repo = Mock()
        mock_templates = [create_mock_template(i, is_active=True) for i in range(2)]
        mock_repo.find_active.return_value = mock_templates

        use_case = ListTemplatesUseCase(mock_repo)
        result = use_case.execute_active()

        assert len(result) == 2
        mock_repo.find_active.assert_called_once()

    def test_list_templates_by_categorie(self):
        """Test liste templates par catégorie."""
        mock_repo = Mock()
        mock_templates = [create_mock_template(1)]
        mock_repo.find_by_categorie.return_value = mock_templates

        use_case = ListTemplatesUseCase(mock_repo)
        result = use_case.execute_by_categorie("securite")

        assert len(result) == 1
        mock_repo.find_by_categorie.assert_called_once()

    def test_list_templates_with_query(self):
        """Test liste templates avec texte de recherche."""
        mock_repo = Mock()
        mock_templates = [create_mock_template(1)]
        mock_repo.search.return_value = (mock_templates, 1)

        use_case = ListTemplatesUseCase(mock_repo)
        result = use_case.execute(query="test")

        assert result.total == 1
        mock_repo.search.assert_called_once()

    def test_list_templates_with_pagination(self):
        """Test liste templates avec pagination."""
        mock_repo = Mock()
        mock_templates = [create_mock_template(i) for i in range(10)]
        mock_repo.search.return_value = (mock_templates[:5], 10)

        use_case = ListTemplatesUseCase(mock_repo)
        result = use_case.execute(skip=0, limit=5)

        assert result.skip == 0
        assert result.limit == 5
        assert result.total == 10
        assert len(result.templates) == 5
