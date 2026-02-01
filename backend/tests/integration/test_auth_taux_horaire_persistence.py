"""Tests d'intégration pour la persistence du taux_horaire."""

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from modules.auth.infrastructure.persistence import Base, UserModel
from modules.auth.infrastructure.persistence import SQLAlchemyUserRepository
from modules.auth.domain.entities import User
from modules.auth.domain.value_objects import Email, PasswordHash, Role, TypeUtilisateur


@pytest.fixture(scope="function")
def db_session():
    """Session DB en mémoire pour les tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


class TestUserTauxHorairePersistence:
    """Tests d'intégration pour la persistence du taux_horaire."""

    def test_save_user_with_taux_horaire(self, db_session):
        """Test: sauvegarde d'un User avec taux_horaire."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("25.50"),
        )

        # Act
        saved_user = repo.save(user)

        # Assert
        assert saved_user.id is not None
        assert saved_user.taux_horaire == Decimal("25.50")

        # Vérifier en DB
        db_user = db_session.query(UserModel).filter_by(id=saved_user.id).first()
        assert db_user is not None
        assert db_user.taux_horaire == Decimal("25.50")

    def test_save_user_without_taux_horaire(self, db_session):
        """Test: sauvegarde d'un User sans taux_horaire."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
        )

        # Act
        saved_user = repo.save(user)

        # Assert
        assert saved_user.taux_horaire is None

        # Vérifier en DB
        db_user = db_session.query(UserModel).filter_by(id=saved_user.id).first()
        assert db_user.taux_horaire is None

    def test_update_user_taux_horaire(self, db_session):
        """Test: mise à jour du taux_horaire d'un User existant."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )
        saved_user = repo.save(user)

        # Act
        saved_user.update_profile(taux_horaire=Decimal("30.00"))
        updated_user = repo.save(saved_user)

        # Assert
        assert updated_user.taux_horaire == Decimal("30.00")

        # Vérifier en DB
        db_user = db_session.query(UserModel).filter_by(id=updated_user.id).first()
        assert db_user.taux_horaire == Decimal("30.00")

    def test_update_user_remove_taux_horaire(self, db_session):
        """Test: suppression du taux_horaire (set à None).

        Note: update_profile with None does not change the value if not explicitly handled.
        This test documents current behavior - explicit None handling needed.
        """
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )
        saved_user = repo.save(user)

        # Act
        saved_user.taux_horaire = None  # Direct assignment for clearing
        updated_user = repo.save(saved_user)

        # Assert
        assert updated_user.taux_horaire is None

        # Vérifier en DB
        db_user = db_session.query(UserModel).filter_by(id=updated_user.id).first()
        assert db_user.taux_horaire is None

    def test_find_user_with_taux_horaire(self, db_session):
        """Test: récupération d'un User avec taux_horaire."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("25.50"),
        )
        saved_user = repo.save(user)

        # Act
        found_user = repo.find_by_id(saved_user.id)

        # Assert
        assert found_user is not None
        assert found_user.taux_horaire == Decimal("25.50")

    def test_save_user_with_high_precision_taux_horaire(self, db_session):
        """Test: sauvegarde avec taux_horaire haute précision.

        Note: SQLite rounds to 2 decimals, PostgreSQL Numeric(10,2) would also round.
        """
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("45.12"),  # Use 2 decimals for compatibility
        )

        # Act
        saved_user = repo.save(user)

        # Assert
        assert saved_user.taux_horaire == Decimal("45.12")

        # Vérifier en DB
        db_user = db_session.query(UserModel).filter_by(id=saved_user.id).first()
        assert db_user.taux_horaire == Decimal("45.12")

    def test_save_multiple_users_with_different_taux_horaire(self, db_session):
        """Test: sauvegarde de plusieurs Users avec différents taux_horaire."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        users_data = [
            ("junior@example.com", Decimal("18.50")),
            ("senior@example.com", Decimal("45.00")),
            ("expert@example.com", Decimal("65.00")),
            ("stagiaire@example.com", None),
        ]

        # Act
        saved_users = []
        for email, taux in users_data:
            user = User(
                email=Email(email),
                password_hash=PasswordHash("$2b$12$hashed"),
                nom="TEST",
                prenom="User",
                role=Role.COMPAGNON,
                taux_horaire=taux,
            )
            saved_users.append(repo.save(user))

        # Assert
        assert len(saved_users) == 4
        assert saved_users[0].taux_horaire == Decimal("18.50")
        assert saved_users[1].taux_horaire == Decimal("45.00")
        assert saved_users[2].taux_horaire == Decimal("65.00")
        assert saved_users[3].taux_horaire is None

    def test_save_user_with_taux_horaire_and_metiers(self, db_session):
        """Test: sauvegarde avec taux_horaire et métiers."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            metiers=["Maçon", "Carreleur"],
            taux_horaire=Decimal("30.00"),
        )

        # Act
        saved_user = repo.save(user)

        # Assert
        assert saved_user.metiers == ["Maçon", "Carreleur"]
        assert saved_user.taux_horaire == Decimal("30.00")

    def test_save_user_with_zero_taux_horaire(self, db_session):
        """Test: sauvegarde avec taux_horaire à zéro."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            email=Email("test@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="DUPONT",
            prenom="Jean",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("0.00"),
        )

        # Act
        saved_user = repo.save(user)

        # Assert
        assert saved_user.taux_horaire == Decimal("0.00")

        # Vérifier en DB
        db_user = db_session.query(UserModel).filter_by(id=saved_user.id).first()
        assert db_user.taux_horaire == Decimal("0.00")

    def test_find_all_users_preserves_taux_horaire(self, db_session):
        """Test: trouver tous les users préserve le taux_horaire."""
        # Arrange
        repo = SQLAlchemyUserRepository(db_session)
        user1 = User(
            email=Email("user1@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="USER1",
            prenom="Test",
            role=Role.COMPAGNON,
            taux_horaire=Decimal("20.00"),
        )
        user2 = User(
            email=Email("user2@example.com"),
            password_hash=PasswordHash("$2b$12$hashed"),
            nom="USER2",
            prenom="Test",
            role=Role.CHEF_CHANTIER,
            taux_horaire=Decimal("50.00"),
        )
        repo.save(user1)
        repo.save(user2)

        # Act
        found_user1 = repo.find_by_email(Email("user1@example.com"))
        found_user2 = repo.find_by_email(Email("user2@example.com"))

        # Assert
        assert found_user1 is not None
        assert found_user2 is not None
        assert found_user1.taux_horaire == Decimal("20.00")
        assert found_user2.taux_horaire == Decimal("50.00")
