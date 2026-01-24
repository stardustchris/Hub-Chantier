"""Tests unitaires pour ListChantiersUseCase."""

from unittest.mock import Mock

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases.list_chantiers import ListChantiersUseCase


class TestListChantiersUseCase:
    """Tests pour le use case de liste des chantiers."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_chantier_repo = Mock(spec=ChantierRepository)
        self.use_case = ListChantiersUseCase(chantier_repo=self.mock_chantier_repo)

        self.chantiers = [
            Chantier(
                id=1,
                nom="Chantier A",
                code=CodeChantier("A001"),
                adresse="1 Rue Test",
                statut=StatutChantier.ouvert(),
            ),
            Chantier(
                id=2,
                nom="Chantier B",
                code=CodeChantier("A002"),
                adresse="2 Rue Test",
                statut=StatutChantier.en_cours(),
            ),
        ]

    def test_list_chantiers_all(self):
        """Test: liste de tous les chantiers."""
        self.mock_chantier_repo.find_all.return_value = self.chantiers
        self.mock_chantier_repo.count.return_value = 2

        result = self.use_case.execute()

        assert len(result.chantiers) == 2
        assert result.total == 2
        self.mock_chantier_repo.find_all.assert_called_once()

    def test_list_chantiers_with_statut_filter(self):
        """Test: filtre par statut."""
        self.mock_chantier_repo.find_by_statut.return_value = [self.chantiers[1]]

        result = self.use_case.execute(statut="en_cours")

        assert len(result.chantiers) == 1
        self.mock_chantier_repo.find_by_statut.assert_called_once()

    def test_list_chantiers_actifs_uniquement(self):
        """Test: filtre actifs uniquement."""
        self.mock_chantier_repo.find_active.return_value = self.chantiers

        self.use_case.execute(actifs_uniquement=True)

        self.mock_chantier_repo.find_active.assert_called_once()

    def test_list_chantiers_by_conducteur(self):
        """Test: filtre par conducteur."""
        self.mock_chantier_repo.find_by_conducteur.return_value = [self.chantiers[0]]

        self.use_case.execute(conducteur_id=10)

        self.mock_chantier_repo.find_by_conducteur.assert_called_once()
        call_kwargs = self.mock_chantier_repo.find_by_conducteur.call_args[1]
        assert call_kwargs["conducteur_id"] == 10

    def test_list_chantiers_by_chef_chantier(self):
        """Test: filtre par chef de chantier."""
        self.mock_chantier_repo.find_by_chef_chantier.return_value = [self.chantiers[0]]

        self.use_case.execute(chef_chantier_id=20)

        self.mock_chantier_repo.find_by_chef_chantier.assert_called_once()

    def test_list_chantiers_by_responsable(self):
        """Test: filtre par responsable (conducteur OU chef)."""
        self.mock_chantier_repo.find_by_responsable.return_value = self.chantiers

        self.use_case.execute(responsable_id=5)

        self.mock_chantier_repo.find_by_responsable.assert_called_once()

    def test_list_chantiers_with_search(self):
        """Test: recherche textuelle."""
        self.mock_chantier_repo.search.return_value = [self.chantiers[0]]

        self.use_case.execute(search="Chantier A")

        self.mock_chantier_repo.search.assert_called_once()
        call_kwargs = self.mock_chantier_repo.search.call_args[1]
        assert call_kwargs["query"] == "Chantier A"

    def test_list_chantiers_pagination(self):
        """Test: pagination."""
        self.mock_chantier_repo.find_all.return_value = self.chantiers
        self.mock_chantier_repo.count.return_value = 100

        result = self.use_case.execute(skip=20, limit=10)

        assert result.skip == 20
        assert result.limit == 10
