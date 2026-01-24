"""Tests des Use Cases du module Formulaires."""

import pytest
from unittest.mock import Mock

from modules.formulaires.domain.entities import (
    TemplateFormulaire,
    ChampTemplate,
    FormulaireRempli,
)
from modules.formulaires.domain.value_objects import (
    TypeChamp,
    StatutFormulaire,
    CategorieFormulaire,
)
from modules.formulaires.application.use_cases import (
    CreateTemplateUseCase,
    GetTemplateUseCase,
    ListTemplatesUseCase,
    CreateFormulaireUseCase,
    UpdateFormulaireUseCase,
    SubmitFormulaireUseCase,
)
from modules.formulaires.application.dtos import (
    CreateTemplateDTO,
    ChampTemplateDTO,
    CreateFormulaireDTO,
    UpdateFormulaireDTO,
    SubmitFormulaireDTO,
)
from modules.formulaires.application.use_cases.create_template import TemplateAlreadyExistsError
from modules.formulaires.application.use_cases.get_template import TemplateNotFoundError


class TestCreateTemplateUseCase:
    """Tests pour CreateTemplateUseCase."""

    def test_create_template_success(self):
        """Creation de template reussie."""
        # Setup
        mock_repo = Mock()
        mock_repo.exists_by_nom.return_value = False

        saved_template = TemplateFormulaire(
            id=1,
            nom="Rapport d'intervention",
            categorie=CategorieFormulaire.INTERVENTION,
        )
        mock_repo.save.return_value = saved_template

        use_case = CreateTemplateUseCase(template_repo=mock_repo)

        dto = CreateTemplateDTO(
            nom="Rapport d'intervention",
            categorie="intervention",
        )

        # Execute
        result = use_case.execute(dto)

        # Assert
        assert result.id == 1
        assert result.nom == "Rapport d'intervention"
        assert result.categorie == "intervention"
        mock_repo.save.assert_called_once()

    def test_create_template_already_exists(self):
        """Erreur si template existe deja."""
        mock_repo = Mock()
        mock_repo.exists_by_nom.return_value = True

        use_case = CreateTemplateUseCase(template_repo=mock_repo)

        dto = CreateTemplateDTO(
            nom="Rapport d'intervention",
            categorie="intervention",
        )

        with pytest.raises(TemplateAlreadyExistsError):
            use_case.execute(dto)

    def test_create_template_with_champs(self):
        """Creation de template avec champs."""
        mock_repo = Mock()
        mock_repo.exists_by_nom.return_value = False

        saved_template = TemplateFormulaire(
            id=1,
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )
        champ = ChampTemplate(nom="titre", label="Titre", type_champ=TypeChamp.TEXTE, id=1)
        saved_template.ajouter_champ(champ)
        mock_repo.save.return_value = saved_template

        use_case = CreateTemplateUseCase(template_repo=mock_repo)

        dto = CreateTemplateDTO(
            nom="Test",
            categorie="autre",
            champs=[
                ChampTemplateDTO(
                    nom="titre",
                    label="Titre",
                    type_champ="texte",
                )
            ],
        )

        result = use_case.execute(dto)

        assert result.nombre_champs == 1
        assert result.champs[0].nom == "titre"

    def test_create_template_publishes_event(self):
        """Verifie la publication d'evenement."""
        mock_repo = Mock()
        mock_repo.exists_by_nom.return_value = False
        mock_repo.save.return_value = TemplateFormulaire(
            id=1,
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )

        mock_publisher = Mock()
        use_case = CreateTemplateUseCase(
            template_repo=mock_repo,
            event_publisher=mock_publisher,
        )

        dto = CreateTemplateDTO(nom="Test", categorie="autre")
        use_case.execute(dto)

        mock_publisher.assert_called_once()


class TestGetTemplateUseCase:
    """Tests pour GetTemplateUseCase."""

    def test_get_template_success(self):
        """Recuperation reussie."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = TemplateFormulaire(
            id=1,
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
        )

        use_case = GetTemplateUseCase(template_repo=mock_repo)
        result = use_case.execute(1)

        assert result.id == 1
        assert result.nom == "Test"

    def test_get_template_not_found(self):
        """Erreur si template non trouve."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = GetTemplateUseCase(template_repo=mock_repo)

        with pytest.raises(TemplateNotFoundError):
            use_case.execute(999)


class TestListTemplatesUseCase:
    """Tests pour ListTemplatesUseCase."""

    def test_list_templates_success(self):
        """Liste des templates reussie."""
        mock_repo = Mock()
        templates = [
            TemplateFormulaire(id=1, nom="Template 1", categorie=CategorieFormulaire.INTERVENTION),
            TemplateFormulaire(id=2, nom="Template 2", categorie=CategorieFormulaire.SECURITE),
        ]
        mock_repo.search.return_value = (templates, 2)

        use_case = ListTemplatesUseCase(template_repo=mock_repo)
        result = use_case.execute()

        assert len(result.templates) == 2
        assert result.total == 2

    def test_list_templates_with_filters(self):
        """Liste avec filtres."""
        mock_repo = Mock()
        templates = [
            TemplateFormulaire(id=1, nom="Securite 1", categorie=CategorieFormulaire.SECURITE),
        ]
        mock_repo.search.return_value = (templates, 1)

        use_case = ListTemplatesUseCase(template_repo=mock_repo)
        result = use_case.execute(categorie="securite", active_only=True)

        assert len(result.templates) == 1
        mock_repo.search.assert_called_once()


class TestCreateFormulaireUseCase:
    """Tests pour CreateFormulaireUseCase."""

    def test_create_formulaire_success(self):
        """Creation de formulaire reussie."""
        mock_formulaire_repo = Mock()
        mock_template_repo = Mock()

        template = TemplateFormulaire(
            id=1,
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
            is_active=True,
        )
        mock_template_repo.find_by_id.return_value = template

        saved_formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
        )
        mock_formulaire_repo.save.return_value = saved_formulaire

        use_case = CreateFormulaireUseCase(
            formulaire_repo=mock_formulaire_repo,
            template_repo=mock_template_repo,
        )

        dto = CreateFormulaireDTO(
            template_id=1,
            chantier_id=1,
            user_id=1,
        )

        result = use_case.execute(dto)

        assert result.id == 1
        assert result.statut == "brouillon"

    def test_create_formulaire_template_not_found(self):
        """Erreur si template non trouve."""
        mock_formulaire_repo = Mock()
        mock_template_repo = Mock()
        mock_template_repo.find_by_id.return_value = None

        use_case = CreateFormulaireUseCase(
            formulaire_repo=mock_formulaire_repo,
            template_repo=mock_template_repo,
        )

        dto = CreateFormulaireDTO(template_id=999, chantier_id=1, user_id=1)

        from modules.formulaires.application.use_cases.create_formulaire import TemplateNotFoundError
        with pytest.raises(TemplateNotFoundError):
            use_case.execute(dto)

    def test_create_formulaire_template_inactive(self):
        """Erreur si template inactif."""
        mock_formulaire_repo = Mock()
        mock_template_repo = Mock()

        template = TemplateFormulaire(
            id=1,
            nom="Test",
            categorie=CategorieFormulaire.AUTRE,
            is_active=False,
        )
        mock_template_repo.find_by_id.return_value = template

        use_case = CreateFormulaireUseCase(
            formulaire_repo=mock_formulaire_repo,
            template_repo=mock_template_repo,
        )

        dto = CreateFormulaireDTO(template_id=1, chantier_id=1, user_id=1)

        from modules.formulaires.application.use_cases.create_formulaire import TemplateInactiveError
        with pytest.raises(TemplateInactiveError):
            use_case.execute(dto)


class TestSubmitFormulaireUseCase:
    """Tests pour SubmitFormulaireUseCase."""

    def test_submit_formulaire_success(self):
        """Soumission reussie."""
        mock_repo = Mock()

        formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
        )
        mock_repo.find_by_id.return_value = formulaire

        # Le formulaire sera modifie par soumettre() et renvoye par save()
        def save_side_effect(f):
            return f

        mock_repo.save.side_effect = save_side_effect

        use_case = SubmitFormulaireUseCase(formulaire_repo=mock_repo)

        dto = SubmitFormulaireDTO(formulaire_id=1)

        result = use_case.execute(dto)

        assert result.statut == "soumis"
        assert result.soumis_at is not None

    def test_submit_formulaire_with_signature(self):
        """Soumission avec signature."""
        mock_repo = Mock()

        formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
        )
        mock_repo.find_by_id.return_value = formulaire
        mock_repo.save.side_effect = lambda f: f

        use_case = SubmitFormulaireUseCase(formulaire_repo=mock_repo)

        dto = SubmitFormulaireDTO(
            formulaire_id=1,
            signature_url="https://example.com/sig.png",
            signature_nom="Jean Dupont",
        )

        result = use_case.execute(dto)

        assert result.est_signe is True
        assert result.signature_nom == "Jean Dupont"

    def test_submit_formulaire_already_submitted(self):
        """Erreur si deja soumis."""
        mock_repo = Mock()

        formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
            statut=StatutFormulaire.SOUMIS,
        )
        mock_repo.find_by_id.return_value = formulaire

        use_case = SubmitFormulaireUseCase(formulaire_repo=mock_repo)

        dto = SubmitFormulaireDTO(formulaire_id=1)

        from modules.formulaires.application.use_cases.submit_formulaire import FormulaireNotSubmittableError
        with pytest.raises(FormulaireNotSubmittableError):
            use_case.execute(dto)


class TestUpdateFormulaireUseCase:
    """Tests pour UpdateFormulaireUseCase."""

    def test_update_champs_success(self):
        """Mise a jour des champs reussie."""
        mock_repo = Mock()

        formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
        )
        mock_repo.find_by_id.return_value = formulaire
        mock_repo.save.side_effect = lambda f: f

        use_case = UpdateFormulaireUseCase(formulaire_repo=mock_repo)

        dto = UpdateFormulaireDTO(
            champs=[
                {"nom": "titre", "valeur": "Mon titre", "type_champ": "texte"},
            ]
        )

        result = use_case.execute(1, dto)

        assert len(result.champs) == 1

    def test_update_formulaire_not_modifiable(self):
        """Erreur si formulaire non modifiable."""
        mock_repo = Mock()

        formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
            statut=StatutFormulaire.SOUMIS,
        )
        mock_repo.find_by_id.return_value = formulaire

        use_case = UpdateFormulaireUseCase(formulaire_repo=mock_repo)

        dto = UpdateFormulaireDTO(champs=[{"nom": "test", "valeur": "test", "type_champ": "texte"}])

        from modules.formulaires.application.use_cases.update_formulaire import FormulaireNotModifiableError
        with pytest.raises(FormulaireNotModifiableError):
            use_case.execute(1, dto)

    def test_add_photo_success(self):
        """Ajout de photo reussi."""
        mock_repo = Mock()

        formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
        )
        mock_repo.find_by_id.return_value = formulaire
        mock_repo.save.side_effect = lambda f: f

        use_case = UpdateFormulaireUseCase(formulaire_repo=mock_repo)

        result = use_case.add_photo(
            formulaire_id=1,
            url="https://example.com/photo.jpg",
            nom_fichier="photo.jpg",
            champ_nom="photo_avant",
        )

        assert len(result.photos) == 1

    def test_add_signature_success(self):
        """Ajout de signature reussi."""
        mock_repo = Mock()

        formulaire = FormulaireRempli(
            id=1,
            template_id=1,
            chantier_id=1,
            user_id=1,
        )
        mock_repo.find_by_id.return_value = formulaire
        mock_repo.save.side_effect = lambda f: f

        use_case = UpdateFormulaireUseCase(formulaire_repo=mock_repo)

        result = use_case.add_signature(
            formulaire_id=1,
            signature_url="https://example.com/sig.png",
            signature_nom="Jean Dupont",
        )

        assert result.est_signe is True
