"""
Configuration pytest pour les tests unitaires.
Fixtures partagées entre tous les modules.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.auth.domain.entities.user import User
from modules.auth.domain.value_objects.password_hash import PasswordHash


@pytest.fixture
def mock_user():
    """Fixture: utilisateur de test."""
    return User(
        id=1,
        email="test@example.com",
        nom="Test",
        prenom="User",
        password_hash=PasswordHash("$2b$12$testhash"),
        role="employe",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_admin_user():
    """Fixture: administrateur de test."""
    return User(
        id=2,
        email="admin@example.com",
        nom="Admin",
        prenom="User",
        password_hash=PasswordHash("$2b$12$adminhash"),
        role="admin",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
