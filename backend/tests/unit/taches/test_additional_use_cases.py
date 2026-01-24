"""Tests unitaires supplémentaires pour les Use Cases du module taches."""

import pytest
from datetime import date
from unittest.mock import Mock

# Imports directs pour éviter le chargement de l'infrastructure via __init__.py
from modules.taches.domain.entities.tache import Tache
from modules.taches.domain.value_objects.statut_tache import StatutTache
from modules.taches.domain.value_objects.unite_mesure import UniteMesure
from modules.taches.domain.repositories.tache_repository import TacheRepository
from modules.taches.application.use_cases.delete_tache import DeleteTacheUseCase
from modules.taches.application.use_cases.update_tache import UpdateTacheUseCase
from modules.taches.application.use_cases.get_tache import TacheNotFoundError
from modules.taches.application.dtos.tache_dto import UpdateTacheDTO


class TestDeleteTacheUseCase:
    """Tests pour DeleteTacheUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.tache_repo = Mock(spec=TacheRepository)
        self.use_case = DeleteTacheUseCase(tache_repo=self.tache_repo)

        self.test_tache = Tache(
            id=1,
            chantier_id=10,
            titre="Tâche test",
            statut=StatutTache.A_FAIRE,
            ordre=1,
        )

    def test_delete_success(self):
        """Test suppression réussie."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.delete.return_value = True

        result = self.use_case.execute(1)

        assert result is True
        self.tache_repo.delete.assert_called_once_with(1)

    def test_delete_not_found(self):
        """Test échec si tâche non trouvée."""
        self.tache_repo.find_by_id.return_value = None

        with pytest.raises(TacheNotFoundError):
            self.use_case.execute(999)

    def test_delete_publishes_event(self):
        """Test publication d'un event après suppression."""
        mock_publisher = Mock()
        use_case = DeleteTacheUseCase(
            tache_repo=self.tache_repo,
            event_publisher=mock_publisher,
        )

        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.delete.return_value = True

        use_case.execute(1)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.tache_id == 1
        assert event.chantier_id == 10


class TestUpdateTacheUseCase:
    """Tests pour UpdateTacheUseCase."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.tache_repo = Mock(spec=TacheRepository)
        self.use_case = UpdateTacheUseCase(tache_repo=self.tache_repo)

        self.test_tache = Tache(
            id=1,
            chantier_id=10,
            titre="Tâche test",
            statut=StatutTache.A_FAIRE,
            ordre=1,
        )

    def test_update_titre_success(self):
        """Test mise à jour du titre."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(titre="Nouveau titre")

        result = self.use_case.execute(1, dto)

        assert result.id == 1
        self.tache_repo.save.assert_called_once()

    def test_update_not_found(self):
        """Test échec si tâche non trouvée."""
        self.tache_repo.find_by_id.return_value = None

        dto = UpdateTacheDTO(titre="Test")

        with pytest.raises(TacheNotFoundError):
            self.use_case.execute(999, dto)

    def test_update_description(self):
        """Test mise à jour de la description."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(description="Nouvelle description")

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_date_echeance(self):
        """Test mise à jour de la date d'échéance."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(date_echeance="2026-02-15")

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_unite_mesure(self):
        """Test mise à jour de l'unité de mesure."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(unite_mesure="m2")

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_quantite_estimee(self):
        """Test mise à jour de la quantité estimée."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(quantite_estimee=100.5)

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_heures_estimees(self):
        """Test mise à jour des heures estimées."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(heures_estimees=40.0)

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_statut_termine(self):
        """Test mise à jour du statut vers terminé."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(statut="termine")

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_statut_reopen(self):
        """Test réouverture d'une tâche terminée."""
        tache_terminee = Tache(
            id=1,
            chantier_id=10,
            titre="Tâche terminée",
            statut=StatutTache.TERMINE,
            ordre=1,
        )
        self.tache_repo.find_by_id.return_value = tache_terminee
        self.tache_repo.save.return_value = tache_terminee

        dto = UpdateTacheDTO(statut="a_faire")

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_ordre(self):
        """Test mise à jour de l'ordre."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(ordre=5)

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()

    def test_update_publishes_event(self):
        """Test publication d'un event après mise à jour."""
        mock_publisher = Mock()
        use_case = UpdateTacheUseCase(
            tache_repo=self.tache_repo,
            event_publisher=mock_publisher,
        )

        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(titre="Nouveau titre")

        use_case.execute(1, dto)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.tache_id == 1
        assert "titre" in event.updated_fields

    def test_update_multiple_fields(self):
        """Test mise à jour de plusieurs champs."""
        self.tache_repo.find_by_id.return_value = self.test_tache
        self.tache_repo.save.return_value = self.test_tache

        dto = UpdateTacheDTO(
            titre="Nouveau titre",
            description="Nouvelle description",
            heures_estimees=20.0,
        )

        result = self.use_case.execute(1, dto)

        self.tache_repo.save.assert_called_once()
