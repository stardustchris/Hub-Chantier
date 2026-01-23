"""Tests unitaires pour CreateSignalementUseCase."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite, StatutSignalement
from modules.signalements.domain.repositories import SignalementRepository
from modules.signalements.application.dtos import SignalementCreateDTO
from modules.signalements.application.use_cases import CreateSignalementUseCase


class TestCreateSignalementUseCase:
    """Tests pour le use case de création de signalement (SIG-01)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=SignalementRepository)
        self.use_case = CreateSignalementUseCase(
            signalement_repository=self.mock_repo,
        )

    def _create_saved_signalement(self, signalement: Signalement) -> Signalement:
        """Simule la sauvegarde en ajoutant un ID."""
        signalement.id = 1
        return signalement

    def test_create_signalement_success_basic(self):
        """Test: création réussie avec données minimales."""
        self.mock_repo.save.side_effect = self._create_saved_signalement

        dto = SignalementCreateDTO(
            chantier_id=1,
            titre="Fuite d'eau",
            description="Fuite détectée au niveau du sous-sol",
            cree_par=10,
        )

        result = self.use_case.execute(dto)

        assert result.id == 1
        assert result.chantier_id == 1
        assert result.titre == "Fuite d'eau"
        assert result.description == "Fuite détectée au niveau du sous-sol"
        assert result.cree_par == 10
        assert result.priorite == "moyenne"  # Défaut
        assert result.statut == "ouvert"  # Défaut
        self.mock_repo.save.assert_called_once()

    def test_create_signalement_with_priorite_critique(self):
        """Test: création avec priorité critique."""
        self.mock_repo.save.side_effect = self._create_saved_signalement

        dto = SignalementCreateDTO(
            chantier_id=1,
            titre="Urgence sécurité",
            description="Danger immédiat",
            cree_par=10,
            priorite="critique",
        )

        result = self.use_case.execute(dto)

        assert result.priorite == "critique"
        assert result.priorite_label == "Critique (4h)"
        assert result.priorite_couleur == "red"

    def test_create_signalement_with_all_fields(self):
        """Test: création avec tous les champs optionnels."""
        self.mock_repo.save.side_effect = self._create_saved_signalement
        date_resolution = datetime(2026, 1, 25, 18, 0, 0)

        dto = SignalementCreateDTO(
            chantier_id=1,
            titre="Problème électrique",
            description="Court-circuit au niveau du tableau",
            cree_par=10,
            priorite="haute",
            assigne_a=5,
            date_resolution_souhaitee=date_resolution,
            photo_url="https://example.com/photo.jpg",
            localisation="Bâtiment A, Étage 2",
        )

        result = self.use_case.execute(dto)

        assert result.priorite == "haute"
        assert result.assigne_a == 5
        assert result.date_resolution_souhaitee == date_resolution
        assert result.photo_url == "https://example.com/photo.jpg"
        assert result.localisation == "Bâtiment A, Étage 2"

    def test_create_signalement_with_user_name_resolver(self):
        """Test: création avec résolution des noms d'utilisateurs."""
        self.mock_repo.save.side_effect = self._create_saved_signalement

        def get_user_name(user_id: int) -> str:
            names = {10: "Jean Dupont", 5: "Marie Martin"}
            return names.get(user_id, f"User #{user_id}")

        use_case = CreateSignalementUseCase(
            signalement_repository=self.mock_repo,
            get_user_name=get_user_name,
        )

        dto = SignalementCreateDTO(
            chantier_id=1,
            titre="Test",
            description="Description",
            cree_par=10,
            assigne_a=5,
        )

        result = use_case.execute(dto)

        assert result.cree_par_nom == "Jean Dupont"
        assert result.assigne_a_nom == "Marie Martin"

    def test_create_signalement_invalid_priorite(self):
        """Test: erreur si priorité invalide."""
        dto = SignalementCreateDTO(
            chantier_id=1,
            titre="Test",
            description="Description",
            cree_par=10,
            priorite="invalide",
        )

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(dto)
        assert "Priorité invalide" in str(exc_info.value)

    def test_create_signalement_repository_called_with_correct_entity(self):
        """Test: le repository est appelé avec l'entité correcte."""
        self.mock_repo.save.side_effect = self._create_saved_signalement

        dto = SignalementCreateDTO(
            chantier_id=1,
            titre="Test création",
            description="Description test",
            cree_par=10,
            priorite="haute",
        )

        self.use_case.execute(dto)

        call_args = self.mock_repo.save.call_args[0][0]
        assert isinstance(call_args, Signalement)
        assert call_args.chantier_id == 1
        assert call_args.titre == "Test création"
        assert call_args.priorite == Priorite.HAUTE


class TestCreateSignalementDTO:
    """Tests pour les DTO de création."""

    def test_dto_defaults(self):
        """Test: valeurs par défaut du DTO."""
        dto = SignalementCreateDTO(
            chantier_id=1,
            titre="Test",
            description="Description",
            cree_par=10,
        )

        assert dto.priorite == "moyenne"
        assert dto.assigne_a is None
        assert dto.date_resolution_souhaitee is None
        assert dto.photo_url is None
        assert dto.localisation is None
