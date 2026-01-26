"""Tests unitaires supplémentaires pour les use cases formulaires."""

import pytest
from unittest.mock import Mock
from datetime import date, datetime

from modules.formulaires.application.use_cases.get_formulaire import (
    GetFormulaireUseCase,
    FormulaireNotFoundError,
)
from modules.formulaires.application.use_cases.list_formulaires import (
    ListFormulairesUseCase,
)
from modules.formulaires.application.use_cases.get_formulaire_history import (
    GetFormulaireHistoryUseCase,
)
from modules.formulaires.domain.value_objects import StatutFormulaire


def create_mock_formulaire(formulaire_id=1):
    """Crée un mock formulaire complet avec tous les attributs requis."""
    mock_form = Mock()
    mock_form.id = formulaire_id
    mock_form.template_id = 10
    mock_form.chantier_id = 5
    mock_form.user_id = 3
    mock_form.statut = StatutFormulaire.BROUILLON
    mock_form.champs = []  # Liste de ChampRempli
    mock_form.photos = []  # Liste de PhotoFormulaire
    mock_form.est_signe = False
    mock_form.signature_nom = None
    mock_form.signature_timestamp = None
    mock_form.est_geolocalise = False
    mock_form.localisation_latitude = None
    mock_form.localisation_longitude = None
    mock_form.soumis_at = None
    mock_form.valide_by = None
    mock_form.valide_at = None
    mock_form.version = 1
    mock_form.parent_id = None
    mock_form.created_at = datetime.now()
    mock_form.updated_at = datetime.now()
    return mock_form


class TestGetFormulaireUseCase:
    """Tests de GetFormulaireUseCase."""

    def test_get_formulaire_success(self):
        """Test récupération formulaire trouvé."""
        mock_repo = Mock()
        mock_formulaire = create_mock_formulaire(1)
        mock_repo.find_by_id.return_value = mock_formulaire

        use_case = GetFormulaireUseCase(formulaire_repo=mock_repo)
        result = use_case.execute(formulaire_id=1)

        assert result.id == 1
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_get_formulaire_not_found(self):
        """Test récupération formulaire non trouvé."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = GetFormulaireUseCase(formulaire_repo=mock_repo)

        with pytest.raises(FormulaireNotFoundError, match="non trouve"):
            use_case.execute(formulaire_id=999)


class TestListFormulairesUseCase:
    """Tests de ListFormulairesUseCase."""

    def test_list_formulaires_basic(self):
        """Test liste basique."""
        mock_repo = Mock()
        mock_repo.search.return_value = ([], 0)

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        result = use_case.execute()

        assert result.total == 0
        assert result.formulaires == []
        assert result.skip == 0
        assert result.limit == 100

    def test_list_formulaires_with_filters(self):
        """Test liste avec filtres."""
        mock_repo = Mock()
        mock_repo.search.return_value = ([], 0)

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        use_case.execute(
            chantier_id=5,
            template_id=10,
            user_id=3,
            statut="brouillon",
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
            skip=10,
            limit=20,
        )

        mock_repo.search.assert_called_once()
        call_kwargs = mock_repo.search.call_args.kwargs
        assert call_kwargs["chantier_id"] == 5
        assert call_kwargs["template_id"] == 10
        assert call_kwargs["user_id"] == 3
        assert call_kwargs["statut"] == StatutFormulaire.BROUILLON
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 20

    def test_list_formulaires_with_results(self):
        """Test liste avec résultats."""
        mock_repo = Mock()
        mock_form = create_mock_formulaire(1)
        mock_repo.search.return_value = ([mock_form], 1)

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        result = use_case.execute()

        assert result.total == 1
        assert len(result.formulaires) == 1
        assert result.formulaires[0].id == 1

    def test_execute_by_chantier(self):
        """Test liste par chantier."""
        mock_repo = Mock()
        mock_repo.find_by_chantier.return_value = []

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        result = use_case.execute_by_chantier(chantier_id=5, skip=0, limit=50)

        assert result == []
        mock_repo.find_by_chantier.assert_called_once_with(5, 0, 50)

    def test_execute_by_chantier_with_results(self):
        """Test liste par chantier avec résultats."""
        mock_repo = Mock()
        mock_form = create_mock_formulaire(1)
        mock_repo.find_by_chantier.return_value = [mock_form]

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        result = use_case.execute_by_chantier(chantier_id=5)

        assert len(result) == 1
        assert result[0].id == 1

    def test_execute_by_user(self):
        """Test liste par utilisateur."""
        mock_repo = Mock()
        mock_repo.find_by_user.return_value = []

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        result = use_case.execute_by_user(user_id=3, skip=5, limit=25)

        assert result == []
        mock_repo.find_by_user.assert_called_once_with(3, 5, 25)

    def test_execute_by_user_with_results(self):
        """Test liste par utilisateur avec résultats."""
        mock_repo = Mock()
        mock_form = create_mock_formulaire(1)
        mock_repo.find_by_user.return_value = [mock_form]

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        result = use_case.execute_by_user(user_id=3)

        assert len(result) == 1

    def test_count_by_chantier(self):
        """Test comptage par chantier."""
        mock_repo = Mock()
        mock_repo.count_by_chantier.return_value = 42

        use_case = ListFormulairesUseCase(formulaire_repo=mock_repo)
        result = use_case.count_by_chantier(chantier_id=5)

        assert result == 42
        mock_repo.count_by_chantier.assert_called_once_with(5)


class TestGetFormulaireHistoryUseCase:
    """Tests de GetFormulaireHistoryUseCase."""

    def test_get_history_success(self):
        """Test récupération historique."""
        mock_repo = Mock()
        mock_form = create_mock_formulaire(1)
        mock_repo.find_by_id.return_value = mock_form
        mock_repo.find_history.return_value = [mock_form]

        use_case = GetFormulaireHistoryUseCase(formulaire_repo=mock_repo)
        result = use_case.execute(formulaire_id=1)

        assert len(result) == 1
        mock_repo.find_by_id.assert_called_once_with(1)
        mock_repo.find_history.assert_called_once_with(1)

    def test_get_history_multiple_versions(self):
        """Test récupération historique avec plusieurs versions."""
        mock_repo = Mock()
        mock_form1 = create_mock_formulaire(1)
        mock_form1.version = 2
        mock_form2 = create_mock_formulaire(1)
        mock_form2.version = 1

        mock_repo.find_by_id.return_value = mock_form1
        mock_repo.find_history.return_value = [mock_form1, mock_form2]

        use_case = GetFormulaireHistoryUseCase(formulaire_repo=mock_repo)
        result = use_case.execute(formulaire_id=1)

        assert len(result) == 2

    def test_get_history_not_found(self):
        """Test historique formulaire non trouvé."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = GetFormulaireHistoryUseCase(formulaire_repo=mock_repo)

        with pytest.raises(Exception):  # FormulaireNotFoundError
            use_case.execute(formulaire_id=999)
