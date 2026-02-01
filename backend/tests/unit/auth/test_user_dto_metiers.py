"""Tests unitaires pour UserDTO avec metiers array."""

import pytest
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur, Couleur
from modules.auth.application.dtos import UserDTO


class TestUserDTOMetiers:
    """Tests pour UserDTO.from_entity avec metiers array."""

    def test_user_dto_from_entity_with_single_metier(self):
        """Test: conversion User -> UserDTO avec un metier."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=["macon"],
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.metiers == ["macon"]
        assert len(dto.metiers) == 1

    def test_user_dto_from_entity_with_multiple_metiers(self):
        """Test: conversion User -> UserDTO avec plusieurs metiers."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=["macon", "coffreur", "ferrailleur"],
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.metiers == ["macon", "coffreur", "ferrailleur"]
        assert len(dto.metiers) == 3

    def test_user_dto_from_entity_with_no_metiers(self):
        """Test: conversion User -> UserDTO sans metiers (None)."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=None,
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.metiers is None

    def test_user_dto_from_entity_with_empty_metiers(self):
        """Test: conversion User -> UserDTO avec liste vide de metiers."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=[],
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.metiers == []

    def test_user_dto_metiers_are_strings(self):
        """Test: metiers dans le DTO sont des strings."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=["electricien", "plombier"],
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert isinstance(dto.metiers, list)
        assert all(isinstance(m, str) for m in dto.metiers)
        assert dto.metiers == ["electricien", "plombier"]

    def test_user_dto_is_frozen(self):
        """Test: UserDTO est immutable (frozen)."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=["macon"],
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert - Tentative de modification doit echouer
        with pytest.raises(Exception):  # FrozenInstanceError
            dto.metiers = ["autre"]

    def test_user_dto_metiers_order_preserved(self):
        """Test: l'ordre des metiers est preserve dans le DTO."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=["terrassier", "grutier", "charpentier"],
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.metiers[0] == "terrassier"
        assert dto.metiers[1] == "grutier"
        assert dto.metiers[2] == "charpentier"

    def test_user_dto_complete_with_metiers(self):
        """Test: DTO complet avec tous les champs incluant metiers."""
        # Arrange
        user = User(
            id=42,
            email=Email("complete@example.com"),
            password_hash=PasswordHash("hashed"),
            nom="MARTIN",
            prenom="Pierre",
            role=Role.CHEF_CHANTIER,
            type_utilisateur=TypeUtilisateur.EMPLOYE,
            couleur=Couleur("#E74C3C"),
            telephone="+33612345678",
            metiers=["electricien", "plombier"],
            code_utilisateur="MAR001",
            contact_urgence_nom="Marie MARTIN",
            contact_urgence_tel="+33611223344",
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.id == 42
        assert dto.email == "complete@example.com"
        assert dto.nom == "MARTIN"
        assert dto.prenom == "Pierre"
        assert dto.nom_complet == "Pierre MARTIN"
        assert dto.role == "chef_chantier"
        assert dto.type_utilisateur == "employe"
        assert dto.couleur == "#E74C3C"
        assert dto.telephone == "+33612345678"
        assert dto.metiers == ["electricien", "plombier"]
        assert dto.code_utilisateur == "MAR001"
        assert dto.contact_urgence_nom == "Marie MARTIN"
        assert dto.contact_urgence_tel == "+33611223344"

    def test_register_dto_with_metiers(self):
        """Test: RegisterDTO accepte metiers array."""
        from modules.auth.application.dtos import RegisterDTO

        # Arrange & Act
        dto = RegisterDTO(
            email="test@example.com",
            password="Password123!",
            nom="Dupont",
            prenom="Jean",
            metiers=["macon", "coffreur"],
        )

        # Assert
        assert dto.metiers == ["macon", "coffreur"]

    def test_update_dto_with_metiers(self):
        """Test: UpdateUserDTO accepte metiers array."""
        from modules.auth.application.dtos import UpdateUserDTO

        # Arrange & Act
        dto = UpdateUserDTO(metiers=["electricien", "plombier"])

        # Assert
        assert dto.metiers == ["electricien", "plombier"]

    def test_update_dto_metiers_optional(self):
        """Test: metiers est optionnel dans UpdateUserDTO."""
        from modules.auth.application.dtos import UpdateUserDTO

        # Arrange & Act
        dto = UpdateUserDTO(nom="MARTIN")

        # Assert
        assert dto.metiers is None
        assert dto.nom == "MARTIN"
