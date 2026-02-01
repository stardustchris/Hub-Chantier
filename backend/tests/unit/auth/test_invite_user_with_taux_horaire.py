"""Tests unitaires pour InviteUserUseCase avec taux_horaire."""

import pytest
from unittest.mock import Mock
from decimal import Decimal

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, Role, TypeUtilisateur
from modules.auth.domain.repositories import UserRepository
from modules.auth.domain.exceptions import EmailAlreadyExistsError, CodeAlreadyExistsError
from modules.auth.application.use_cases.invite_user import InviteUserUseCase


class TestInviteUserWithTauxHoraire:
    """Tests pour le use case d'invitation avec taux_horaire."""

    def setup_method(self):
        """Configuration avant chaque test."""
        # Mock
        self.mock_user_repo = Mock(spec=UserRepository)

        # Use case à tester
        self.use_case = InviteUserUseCase(user_repository=self.mock_user_repo)

        # Configurer les mocks par défaut
        self.mock_user_repo.exists_by_email.return_value = False
        self.mock_user_repo.exists_by_code.return_value = False

    def _create_saved_user(self, user: User) -> User:
        """Simule la sauvegarde en ajoutant un ID."""
        user.id = 1
        return user

    def test_invite_user_with_taux_horaire_success(self):
        """Test: invitation réussie avec taux_horaire."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="new@example.com",
            nom="Dupont",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("25.50"),
        )

        # Assert
        assert user.id == 1
        assert user.email == Email("new@example.com")
        assert user.nom == "DUPONT"
        assert user.prenom == "Jean"
        assert user.role == Role.COMPAGNON
        assert user.taux_horaire == Decimal("25.50")
        assert user.is_active is False  # Inactif jusqu'à acceptation
        assert user.invitation_token is not None
        assert user.invitation_expires_at is not None

    def test_invite_user_with_high_taux_horaire(self):
        """Test: invitation avec taux_horaire élevé."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="expert@example.com",
            nom="Expert",
            prenom="Senior",
            role=Role.CHEF_CHANTIER,
            taux_horaire=Decimal("65.00"),
        )

        # Assert
        assert user.taux_horaire == Decimal("65.00")
        assert user.role == Role.CHEF_CHANTIER

    def test_invite_user_without_taux_horaire(self):
        """Test: invitation sans taux_horaire (optionnel)."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="new@example.com",
            nom="Dupont",
            prenom="Jean",
            role=Role.COMPAGNON,
        )

        # Assert
        assert user.taux_horaire is None

    def test_invite_user_with_taux_horaire_zero(self):
        """Test: invitation avec taux_horaire à zéro."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="stagiaire@example.com",
            nom="Stagiaire",
            prenom="Test",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("0.00"),
        )

        # Assert
        assert user.taux_horaire == Decimal("0.00")

    def test_invite_user_with_taux_horaire_and_metiers(self):
        """Test: invitation avec taux_horaire et métiers."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user
        metiers = ["Maçon", "Carreleur"]

        # Act
        user = self.use_case.execute(
            email="polyvalent@example.com",
            nom="Polyvalent",
            prenom="Multi",
            role=Role.COMPAGNON,
            metiers=metiers,
            taux_horaire=Decimal("30.00"),
        )

        # Assert
        assert user.metiers == metiers
        assert user.taux_horaire == Decimal("30.00")

    def test_invite_user_with_taux_horaire_high_precision(self):
        """Test: invitation avec taux_horaire haute précision."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="precise@example.com",
            nom="Precise",
            prenom="Test",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("28.756"),
        )

        # Assert
        assert user.taux_horaire == Decimal("28.756")

    def test_invite_user_email_already_exists(self):
        """Test: échec si email déjà utilisé."""
        # Arrange
        self.mock_user_repo.exists_by_email.return_value = True

        # Act & Assert
        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(
                email="existing@example.com",
                nom="Dupont",
                prenom="Jean",
                role=Role.COMPAGNON,
                taux_horaire=Decimal("25.00"),
            )

    def test_invite_user_code_already_exists(self):
        """Test: échec si code utilisateur déjà utilisé."""
        # Arrange
        self.mock_user_repo.exists_by_code.return_value = True

        # Act & Assert
        with pytest.raises(CodeAlreadyExistsError):
            self.use_case.execute(
                email="new@example.com",
                nom="Dupont",
                prenom="Jean",
                role=Role.COMPAGNON,
                code_utilisateur="DUP001",
                taux_horaire=Decimal("25.00"),
            )

    def test_invite_admin_with_taux_horaire(self):
        """Test: invitation d'un admin avec taux_horaire."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="admin@example.com",
            nom="Admin",
            prenom="Super",
            role=Role.ADMIN,
            taux_horaire=Decimal("75.00"),
        )

        # Assert
        assert user.role == Role.ADMIN
        assert user.taux_horaire == Decimal("75.00")

    def test_invite_conducteur_with_taux_horaire(self):
        """Test: invitation d'un conducteur avec taux_horaire."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="conducteur@example.com",
            nom="Conducteur",
            prenom="Travaux",
            role=Role.CONDUCTEUR,
            taux_horaire=Decimal("55.00"),
        )

        # Assert
        assert user.role == Role.CONDUCTEUR
        assert user.taux_horaire == Decimal("55.00")

    def test_invite_sous_traitant_with_taux_horaire(self):
        """Test: invitation d'un sous-traitant avec taux_horaire."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="soustraitant@example.com",
            nom="Entreprise",
            prenom="Contact",
            role=Role.COMPAGNON,
            type_utilisateur=TypeUtilisateur.SOUS_TRAITANT,
            taux_horaire=Decimal("35.00"),
        )

        # Assert
        assert user.type_utilisateur == TypeUtilisateur.SOUS_TRAITANT
        assert user.taux_horaire == Decimal("35.00")

    def test_invite_user_with_all_fields_including_taux_horaire(self):
        """Test: invitation avec tous les champs CDC incluant taux_horaire."""
        # Arrange
        self.mock_user_repo.save.side_effect = self._create_saved_user

        # Act
        user = self.use_case.execute(
            email="complet@example.com",
            nom="Complet",
            prenom="Test",
            role=Role.CHEF_CHANTIER,
            type_utilisateur=TypeUtilisateur.EMPLOYE,
            code_utilisateur="COM001",
            metiers=["Maçon", "Chef d'équipe"],
            taux_horaire=Decimal("45.50"),
        )

        # Assert
        assert user.email == Email("complet@example.com")
        assert user.role == Role.CHEF_CHANTIER
        assert user.type_utilisateur == TypeUtilisateur.EMPLOYE
        assert user.code_utilisateur == "COM001"
        assert user.metiers == ["Maçon", "Chef d'équipe"]
        assert user.taux_horaire == Decimal("45.50")
        assert user.is_active is False
        assert user.invitation_token is not None
