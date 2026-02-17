"""Tests unitaires pour UserDTO avec taux_horaire."""

import pytest
from decimal import Decimal
from datetime import datetime

from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur, Couleur
from modules.auth.application.dtos import UserDTO, RegisterDTO, UpdateUserDTO


class TestUserDTOTauxHoraire:
    """Tests pour UserDTO avec l'attribut taux_horaire."""

    def test_user_dto_from_entity_with_taux_horaire(self):
        """Test: conversion User -> UserDTO avec taux_horaire."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("25.50"),
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.taux_horaire == Decimal("25.50")
        assert dto.id == 1
        assert dto.nom == "DUPONT"
        assert dto.prenom == "Jean"

    def test_user_dto_from_entity_without_taux_horaire(self):
        """Test: conversion User -> UserDTO sans taux_horaire (None)."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=None,
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.taux_horaire is None

    def test_user_dto_from_entity_zero_taux_horaire(self):
        """Test: création User avec taux_horaire zéro lève ValueError (SMIC)."""
        # Act & Assert
        with pytest.raises(ValueError, match="SMIC"):
            User(
                id=1,
                email=Email("test@example.com"),
                password_hash=PasswordHash("$2b$12$hashed"),
                nom="DUPONT",
                prenom="Jean",
                role=Role.COMPAGNON,
                taux_horaire=Decimal("0.00"),
            )

    def test_user_dto_from_entity_high_precision_taux_horaire(self):
        """Test: création User avec taux_horaire haute précision lève ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="décimales"):
            User(
                id=1,
                email=Email("test@example.com"),
                password_hash=PasswordHash("$2b$12$hashed"),
                nom="DUPONT",
                prenom="Jean",
                role=Role.COMPAGNON,
                taux_horaire=Decimal("45.123456"),
            )

    def test_user_dto_from_entity_all_fields_with_taux_horaire(self):
        """Test: conversion User -> UserDTO avec tous les champs."""
        # Arrange
        user = User(
            id=1,
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
            taux_horaire=Decimal("35.75"),
            contact_urgence_nom="Dupont Marie",
            contact_urgence_tel="0698765432",
        )

        # Act
        dto = UserDTO.from_entity(user)

        # Assert
        assert dto.taux_horaire == Decimal("35.75")
        assert dto.metiers == ["Maçon", "Plombier"]
        assert dto.telephone == "0612345678"
        assert dto.code_utilisateur == "EMP001"
        assert dto.contact_urgence_nom == "Dupont Marie"
        assert dto.contact_urgence_tel == "0698765432"

    def test_register_dto_with_taux_horaire(self):
        """Test: RegisterDTO avec taux_horaire."""
        # Arrange & Act
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            taux_horaire=Decimal("28.50"),
        )

        # Assert
        assert dto.taux_horaire == Decimal("28.50")
        assert dto.email == "test@example.com"
        assert dto.nom == "Dupont"

    def test_register_dto_without_taux_horaire(self):
        """Test: RegisterDTO sans taux_horaire (None par défaut)."""
        # Arrange & Act
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
        )

        # Assert
        assert dto.taux_horaire is None

    def test_register_dto_all_fields_with_taux_horaire(self):
        """Test: RegisterDTO avec tous les champs y compris taux_horaire."""
        # Arrange & Act
        dto = RegisterDTO(
            email="test@example.com",
            password="SecurePass123!",
            nom="Dupont",
            prenom="Jean",
            type_utilisateur="employe",
            telephone="0612345678",
            metiers=["Maçon", "Carreleur"],
            taux_horaire=Decimal("42.00"),
            code_utilisateur="EMP001",
            couleur="#FF5733",
        )

        # Assert
        assert dto.taux_horaire == Decimal("42.00")
        assert dto.metiers == ["Maçon", "Carreleur"]
        assert dto.telephone == "0612345678"
        assert dto.code_utilisateur == "EMP001"

    def test_update_user_dto_with_taux_horaire(self):
        """Test: UpdateUserDTO avec taux_horaire."""
        # Arrange & Act
        dto = UpdateUserDTO(taux_horaire=Decimal("35.00"))

        # Assert
        assert dto.taux_horaire == Decimal("35.00")

    def test_update_user_dto_without_taux_horaire(self):
        """Test: UpdateUserDTO sans taux_horaire (None par défaut)."""
        # Arrange & Act
        dto = UpdateUserDTO(nom="MARTIN")

        # Assert
        assert dto.taux_horaire is None
        assert dto.nom == "MARTIN"

    def test_update_user_dto_set_taux_horaire_to_none(self):
        """Test: UpdateUserDTO avec taux_horaire explicitement None."""
        # Arrange & Act
        dto = UpdateUserDTO(taux_horaire=None)

        # Assert
        assert dto.taux_horaire is None

    def test_update_user_dto_all_fields_with_taux_horaire(self):
        """Test: UpdateUserDTO avec tous les champs y compris taux_horaire."""
        # Arrange & Act
        dto = UpdateUserDTO(
            nom="MARTIN",
            prenom="Pierre",
            telephone="0698765432",
            metiers=["Électricien"],
            taux_horaire=Decimal("55.00"),
            couleur="#FF0000",
            photo_profil="https://example.com/new.jpg",
            contact_urgence_nom="Martin Sophie",
            contact_urgence_tel="0611223344",
            role="conducteur",
            type_utilisateur="employe",
            code_utilisateur="EMP999",
        )

        # Assert
        assert dto.taux_horaire == Decimal("55.00")
        assert dto.nom == "MARTIN"
        assert dto.metiers == ["Électricien"]
        assert dto.role == "conducteur"

    def test_user_dto_immutability(self):
        """Test: UserDTO est immutable (frozen=True)."""
        # Arrange
        user = User(
            id=1,
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("25.50"),
        )
        dto = UserDTO.from_entity(user)

        # Act & Assert
        with pytest.raises(Exception):  # FrozenInstanceError
            dto.taux_horaire = Decimal("30.00")
