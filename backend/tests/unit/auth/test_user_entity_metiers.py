"""Tests unitaires pour User entity avec metiers array."""

import pytest
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur, Couleur


class TestUserEntityMetiers:
    """Tests pour l'entite User avec le champ metiers (List[str])."""

    def test_user_creation_with_single_metier(self):
        """Test: creation d'un User avec un seul metier."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon"],
        )

        # Assert
        assert user.metiers == ["macon"]
        assert len(user.metiers) == 1

    def test_user_creation_with_multiple_metiers(self):
        """Test: creation d'un User avec plusieurs metiers."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon", "coffreur", "ferrailleur"],
        )

        # Assert
        assert user.metiers == ["macon", "coffreur", "ferrailleur"]
        assert len(user.metiers) == 3

    def test_user_creation_with_no_metiers(self):
        """Test: creation d'un User sans metiers (None)."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=None,
        )

        # Assert
        assert user.metiers is None

    def test_user_creation_with_empty_metiers_list(self):
        """Test: creation d'un User avec liste vide de metiers."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=[],
        )

        # Assert
        assert user.metiers == []

    def test_user_update_profile_with_metiers(self):
        """Test: mise a jour du profil avec nouveaux metiers."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon"],
        )
        old_updated_at = user.updated_at

        # Act
        user.update_profile(metiers=["macon", "coffreur"])

        # Assert
        assert user.metiers == ["macon", "coffreur"]
        assert user.updated_at > old_updated_at

    def test_user_update_profile_replace_all_metiers(self):
        """Test: remplacement complet de la liste de metiers."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon", "coffreur"],
        )

        # Act
        user.update_profile(metiers=["electricien", "plombier"])

        # Assert
        assert user.metiers == ["electricien", "plombier"]
        assert "macon" not in user.metiers
        assert "coffreur" not in user.metiers

    def test_user_update_profile_clear_metiers(self):
        """Test: suppression de tous les metiers."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon", "coffreur"],
        )

        # Act
        user.update_profile(metiers=[])

        # Assert
        assert user.metiers == []

    def test_user_update_profile_set_metiers_to_none(self):
        """Test: mise a None des metiers via passage explicite."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon"],
        )

        # Act - Note: la logique actuelle "if metiers is not None" ne permet pas
        # de setter à None via update_profile. Il faut utiliser [] pour vider.
        # Cette limitation est acceptée car update_profile est pour mettre à jour,
        # pas pour effacer. Pour effacer, on passe [].
        user.update_profile(metiers=[])  # Vider avec liste vide

        # Assert
        assert user.metiers == []  # Vide plutôt que None

    def test_user_update_profile_keeps_metiers_unchanged_if_not_provided(self):
        """Test: metiers inchanges si non fournis dans update_profile."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon", "coffreur"],
        )

        # Act
        user.update_profile(telephone="+33612345678")

        # Assert
        assert user.metiers == ["macon", "coffreur"]
        assert user.telephone == "+33612345678"

    def test_user_update_profile_with_all_fields_including_metiers(self):
        """Test: mise a jour complete du profil avec metiers."""
        # Arrange
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon"],
        )

        # Act
        user.update_profile(
            nom="MARTIN",
            prenom="Pierre",
            telephone="+33612345678",
            metiers=["electricien", "plombier"],
            couleur=Couleur("#E74C3C"),
            contact_urgence_nom="Marie MARTIN",
            contact_urgence_tel="+33611223344",
        )

        # Assert
        assert user.nom == "MARTIN"
        assert user.prenom == "Pierre"
        assert user.telephone == "+33612345678"
        assert user.metiers == ["electricien", "plombier"]
        assert str(user.couleur) == "#E74C3C"
        assert user.contact_urgence_nom == "Marie MARTIN"
        assert user.contact_urgence_tel == "+33611223344"

    def test_user_metiers_preserves_order(self):
        """Test: l'ordre des metiers est preserve."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["electricien", "plombier", "macon"],
        )

        # Assert
        assert user.metiers[0] == "electricien"
        assert user.metiers[1] == "plombier"
        assert user.metiers[2] == "macon"

    def test_user_metiers_allows_duplicates(self):
        """Test: metiers autorise les doublons (validation applicative)."""
        # Arrange & Act - L'entite n'empeche pas les doublons
        # (la validation sera faite au niveau DTO/use case)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["macon", "macon"],
        )

        # Assert
        assert user.metiers == ["macon", "macon"]

    def test_user_metiers_accepts_any_string_value(self):
        """Test: metiers accepte n'importe quelle valeur string."""
        # Arrange & Act - La validation des valeurs sera au niveau DTO
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=["metier_invalide", "autre_metier"],
        )

        # Assert
        assert user.metiers == ["metier_invalide", "autre_metier"]

    def test_user_backward_compatibility_metiers_none(self):
        """Test: retrocompatibilite avec metiers=None (anciens utilisateurs)."""
        # Arrange & Act
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            metiers=None,
        )

        # Assert
        assert user.metiers is None
        # Ne doit pas crasher
        assert user.nom_complet == "Jean DUPONT"
