"""Tests unitaires pour ChangeStatutUseCase."""

import pytest
from unittest.mock import Mock

from modules.chantiers.domain.entities import Chantier
from modules.chantiers.domain.value_objects import CodeChantier, StatutChantier
from modules.chantiers.domain.repositories import ChantierRepository
from modules.chantiers.application.use_cases import (
    ChangeStatutUseCase,
    ChantierNotFoundError,
    TransitionNonAutoriseeError,
)
from modules.chantiers.application.dtos import ChangeStatutDTO


class TestChangeStatutUseCase:
    """Tests pour le use case de changement de statut."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ChantierRepository)
        self.use_case = ChangeStatutUseCase(chantier_repo=self.mock_repo)

    def _create_chantier(
        self, chantier_id: int = 1, statut: str = "ouvert"
    ) -> Chantier:
        """Crée un chantier de test."""
        return Chantier(
            id=chantier_id,
            code=CodeChantier("A001"),
            nom="Chantier Test",
            adresse="Adresse Test",
            statut=StatutChantier.from_string(statut),
        )

    def test_transition_ouvert_to_en_cours(self):
        """Test: Ouvert → En cours (autorisé)."""
        # Arrange
        chantier = self._create_chantier(statut="ouvert")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act
        result = self.use_case.execute(1, dto)

        # Assert
        assert result.statut == "en_cours"

    def test_transition_en_cours_to_receptionne(self):
        """Test: En cours → Réceptionné (autorisé)."""
        # Arrange
        chantier = self._create_chantier(statut="en_cours")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act
        result = self.use_case.execute(1, dto)

        # Assert
        assert result.statut == "receptionne"

    def test_transition_receptionne_to_ferme(self):
        """Test: Réceptionné → Fermé (autorisé)."""
        # Arrange
        chantier = self._create_chantier(statut="receptionne")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="ferme")

        # Act
        result = self.use_case.execute(1, dto)

        # Assert
        assert result.statut == "ferme"

    def test_transition_receptionne_to_en_cours(self):
        """Test: Réceptionné → En cours (autorisé - réouverture)."""
        # Arrange
        chantier = self._create_chantier(statut="receptionne")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act
        result = self.use_case.execute(1, dto)

        # Assert
        assert result.statut == "en_cours"

    def test_transition_ferme_not_allowed(self):
        """Test: Fermé → X (non autorisé - aucune transition depuis fermé)."""
        # Arrange
        chantier = self._create_chantier(statut="ferme")
        self.mock_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act & Assert
        with pytest.raises(TransitionNonAutoriseeError) as exc_info:
            self.use_case.execute(1, dto)
        assert "ferme" in str(exc_info.value)

    def test_transition_ouvert_to_receptionne_not_allowed(self):
        """Test: Ouvert → Réceptionné (non autorisé - doit passer par En cours)."""
        # Arrange
        chantier = self._create_chantier(statut="ouvert")
        self.mock_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="receptionne")

        # Act & Assert
        with pytest.raises(TransitionNonAutoriseeError) as exc_info:
            self.use_case.execute(1, dto)
        assert "ouvert" in str(exc_info.value)
        assert "receptionne" in str(exc_info.value)

    def test_chantier_not_found(self):
        """Test: échec si chantier non trouvé."""
        # Arrange
        self.mock_repo.find_by_id.return_value = None

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act & Assert
        with pytest.raises(ChantierNotFoundError):
            self.use_case.execute(999, dto)

    def test_invalid_statut_value(self):
        """Test: échec si valeur de statut invalide."""
        # Arrange
        chantier = self._create_chantier(statut="ouvert")
        self.mock_repo.find_by_id.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="invalide")

        # Act & Assert
        with pytest.raises(ValueError):
            self.use_case.execute(1, dto)

    def test_demarrer_shortcut(self):
        """Test: méthode raccourci demarrer()."""
        # Arrange
        chantier = self._create_chantier(statut="ouvert")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        # Act
        result = self.use_case.demarrer(1)

        # Assert
        assert result.statut == "en_cours"

    def test_receptionner_shortcut(self):
        """Test: méthode raccourci receptionner()."""
        # Arrange
        chantier = self._create_chantier(statut="en_cours")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        # Act
        result = self.use_case.receptionner(1)

        # Assert
        assert result.statut == "receptionne"

    def test_fermer_shortcut(self):
        """Test: méthode raccourci fermer()."""
        # Arrange
        chantier = self._create_chantier(statut="en_cours")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        # Act
        result = self.use_case.fermer(1)

        # Assert
        assert result.statut == "ferme"

    def test_change_statut_publishes_event(self):
        """Test: publication d'un event après changement de statut."""
        # Arrange
        mock_publisher = Mock()
        use_case_with_events = ChangeStatutUseCase(
            chantier_repo=self.mock_repo,
            event_publisher=mock_publisher,
        )

        chantier = self._create_chantier(statut="ouvert")
        self.mock_repo.find_by_id.return_value = chantier
        self.mock_repo.save.return_value = chantier

        dto = ChangeStatutDTO(nouveau_statut="en_cours")

        # Act
        use_case_with_events.execute(1, dto)

        # Assert
        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.chantier_id == 1
        assert event.ancien_statut == "ouvert"
        assert event.nouveau_statut == "en_cours"
