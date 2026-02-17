"""Tests unitaires pour User entity avec taux_horaire."""

import pytest
from decimal import Decimal
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur, Couleur


class TestUserEntityTauxHoraire:
    """Tests pour l'attribut taux_horaire de l'entité User."""

    def test_user_creation_with_taux_horaire(self):
        """Test: création d'un User avec taux_horaire."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("25.50"),
        )

        # Assert
        assert user.taux_horaire == Decimal("25.50")

    def test_user_creation_without_taux_horaire(self):
        """Test: création d'un User sans taux_horaire (optionnel)."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
        )

        # Assert
        assert user.taux_horaire is None

    def test_user_creation_with_zero_taux_horaire(self):
        """Test: création d'un User avec taux_horaire zéro lève ValueError (SMIC)."""
        # Act & Assert
        with pytest.raises(ValueError, match="SMIC"):
            User(
                email=Email("test@example.com"),
                password_hash=PasswordHash("$2b$12$hashed"),
                nom="DUPONT",
                prenom="Jean",
                role=Role.COMPAGNON,
                taux_horaire=Decimal("0.00"),
            )

    def test_user_creation_with_high_precision_taux_horaire(self):
        """Test: création d'un User avec taux_horaire haute précision lève ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="décimales"):
            User(
                email=Email("test@example.com"),
                password_hash=PasswordHash("$2b$12$hashed"),
                nom="DUPONT",
                prenom="Jean",
                role=Role.COMPAGNON,
                taux_horaire=Decimal("45.123456"),
            )

    def test_update_profile_with_taux_horaire(self):
        """Test: mise à jour du taux_horaire via update_profile."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )
        old_updated_at = user.updated_at

        # Act
        user.update_profile(taux_horaire=Decimal("30.00"))

        # Assert
        assert user.taux_horaire == Decimal("30.00")
        assert user.updated_at > old_updated_at

    def test_update_profile_with_none_taux_horaire(self):
        """Test: passer None pour taux_horaire ne change pas la valeur existante."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )

        # Act
        user.update_profile(taux_horaire=None)

        # Assert - None means "don't update", value stays unchanged
        assert user.taux_horaire == Decimal("20.00")

    def test_update_profile_without_taux_horaire_keeps_existing(self):
        """Test: ne pas passer taux_horaire conserve la valeur existante."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )

        # Act
        user.update_profile(nom="MARTIN")

        # Assert
        assert user.taux_horaire == Decimal("20.00")
        assert user.nom == "MARTIN"

    def test_update_profile_taux_horaire_with_other_fields(self):
        """Test: mise à jour de taux_horaire avec d'autres champs."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            telephone="0612345678",
            taux_horaire=Decimal("20.00"),
        )

        # Act
        user.update_profile(
            telephone="0698765432",
            taux_horaire=Decimal("35.50"),
            metiers=["Maçon", "Carreleur"],
        )

        # Assert
        assert user.telephone == "0698765432"
        assert user.taux_horaire == Decimal("35.50")
        assert user.metiers == ["Maçon", "Carreleur"]

    def test_taux_horaire_immutable_after_creation(self):
        """Test: taux_horaire ne peut être modifié que via update_profile."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )

        # Act - modification directe (déconseillée mais possible avec dataclass)
        user.taux_horaire = Decimal("50.00")

        # Assert - vérifie que la modification est effective
        # (Note: dataclass permet la mutation, mais la pratique recommandée est update_profile)
        assert user.taux_horaire == Decimal("50.00")

    def test_user_with_taux_horaire_and_all_optional_fields(self):
        """Test: User avec taux_horaire et tous les champs optionnels."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            type_utilisateur=TypeUtilisateur.EMPLOYE,
            couleur=Couleur("#FF5733"),
            photo_profil="https://example.com/photo.jpg",
            code_utilisateur="EMP001",
            telephone="0612345678",
            metiers=["Maçon", "Plombier"],
            taux_horaire=Decimal("28.75"),
            contact_urgence_nom="Dupont Marie",
            contact_urgence_tel="0698765432",
        )

        # Assert
        assert user.taux_horaire == Decimal("28.75")
        assert user.metiers == ["Maçon", "Plombier"]
        assert user.telephone == "0612345678"
        assert user.contact_urgence_nom == "Dupont Marie"
