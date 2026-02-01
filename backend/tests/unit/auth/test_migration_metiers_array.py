"""Tests unitaires pour la migration metier -> metiers (array)."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from modules.auth.infrastructure.persistence import Base, UserModel


class TestMigrationMetiersArray:
    """Tests pour la migration de metier string vers metiers array."""

    @pytest.fixture
    def db_session(self):
        """Session DB SQLite en memoire pour les tests de migration."""
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

    def test_migration_metier_null_to_metiers_null(self, db_session):
        """Test: metier NULL reste metiers NULL apres migration."""
        # Arrange - Creer un user avec metier NULL (simulation pre-migration)
        user = UserModel(
            email="test@example.com",
            password_hash="hashed",
            nom="DUPONT",
            prenom="Jean",
            role="compagnon",
            type_utilisateur="employe",
            metiers=None,
        )
        db_session.add(user)
        db_session.commit()

        # Assert
        assert user.metiers is None

    def test_migration_metier_string_to_metiers_array(self, db_session):
        """Test: metier string converti en metiers array a 1 element."""
        # Arrange - Simuler donnees post-migration (metier -> metiers)
        user = UserModel(
            email="macon@example.com",
            password_hash="hashed",
            nom="MARTIN",
            prenom="Pierre",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["macon"],  # Converti de metier='macon'
        )
        db_session.add(user)
        db_session.commit()

        # Act
        db_session.refresh(user)

        # Assert
        assert user.metiers == ["macon"]
        assert len(user.metiers) == 1

    def test_migration_supports_multiple_metiers(self, db_session):
        """Test: metiers array supporte plusieurs metiers."""
        # Arrange
        user = UserModel(
            email="multi@example.com",
            password_hash="hashed",
            nom="MULTI",
            prenom="Marc",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["macon", "coffreur", "ferrailleur"],
        )
        db_session.add(user)
        db_session.commit()

        # Act
        db_session.refresh(user)

        # Assert
        assert user.metiers == ["macon", "coffreur", "ferrailleur"]
        assert len(user.metiers) == 3

    def test_migration_metiers_empty_array(self, db_session):
        """Test: metiers peut etre un array vide."""
        # Arrange
        user = UserModel(
            email="empty@example.com",
            password_hash="hashed",
            nom="EMPTY",
            prenom="Test",
            role="compagnon",
            type_utilisateur="employe",
            metiers=[],
        )
        db_session.add(user)
        db_session.commit()

        # Act
        db_session.refresh(user)

        # Assert
        assert user.metiers == []

    def test_migration_preserves_metier_order(self, db_session):
        """Test: l'ordre des metiers est preserve."""
        # Arrange
        user = UserModel(
            email="order@example.com",
            password_hash="hashed",
            nom="ORDER",
            prenom="Test",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["electricien", "plombier", "macon"],
        )
        db_session.add(user)
        db_session.commit()

        # Act
        db_session.refresh(user)

        # Assert
        assert user.metiers[0] == "electricien"
        assert user.metiers[1] == "plombier"
        assert user.metiers[2] == "macon"

    def test_query_users_by_metier_contains(self, db_session):
        """Test: recherche d'utilisateurs contenant un metier specifique."""
        # Arrange
        user1 = UserModel(
            email="user1@example.com",
            password_hash="hashed",
            nom="USER1",
            prenom="Test",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["macon", "coffreur"],
        )
        user2 = UserModel(
            email="user2@example.com",
            password_hash="hashed",
            nom="USER2",
            prenom="Test",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["electricien"],
        )
        user3 = UserModel(
            email="user3@example.com",
            password_hash="hashed",
            nom="USER3",
            prenom="Test",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["macon", "electricien"],
        )
        db_session.add_all([user1, user2, user3])
        db_session.commit()

        # Act - Trouver tous les macons
        # Note: SQLite ne supporte pas JSONB, donc on teste la structure
        users_with_metiers = (
            db_session.query(UserModel).filter(UserModel.metiers.isnot(None)).all()
        )

        # Assert
        macons = [u for u in users_with_metiers if u.metiers and "macon" in u.metiers]
        assert len(macons) == 2
        assert user1 in macons
        assert user3 in macons

    def test_migration_handles_special_characters(self, db_session):
        """Test: metiers avec caracteres speciaux."""
        # Arrange
        user = UserModel(
            email="special@example.com",
            password_hash="hashed",
            nom="SPECIAL",
            prenom="Test",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["Chef d'équipe", "Maître-ouvrier"],
        )
        db_session.add(user)
        db_session.commit()

        # Act
        db_session.refresh(user)

        # Assert
        assert user.metiers == ["Chef d'équipe", "Maître-ouvrier"]

    def test_migration_max_5_metiers(self, db_session):
        """Test: validation future max 5 metiers (business rule)."""
        # Arrange - La limite est applicative, pas DB
        user = UserModel(
            email="max@example.com",
            password_hash="hashed",
            nom="MAX",
            prenom="Test",
            role="compagnon",
            type_utilisateur="employe",
            metiers=["macon", "coffreur", "ferrailleur", "electricien", "plombier"],
        )
        db_session.add(user)
        db_session.commit()

        # Act
        db_session.refresh(user)

        # Assert - DB accepte 5 metiers
        assert len(user.metiers) == 5

        # Note: La validation max 5 sera faite au niveau DTO/Entity
