"""Tests unitaires pour SQLAlchemyUserRepository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from modules.auth.infrastructure.persistence.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from modules.auth.domain.value_objects import Email, Role, TypeUtilisateur


class TestFindById:
    """Tests de find_by_id."""

    def test_find_by_id_returns_entity_when_found(self):
        """Test retourne l'entité quand trouvée."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.email = "test@test.com"
        mock_model.password_hash = "hashed"
        mock_model.nom = "Dupont"
        mock_model.prenom = "Jean"
        mock_model.role = "compagnon"
        mock_model.type_utilisateur = "employe"
        mock_model.is_active = True
        mock_model.couleur = "#3498DB"
        mock_model.photo_profil = None
        mock_model.code_utilisateur = "JD001"
        mock_model.telephone = None
        mock_model.metier = None
        mock_model.contact_urgence_nom = None
        mock_model.contact_urgence_tel = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert str(result.email) == "test@test.com"

    def test_find_by_id_returns_none_when_not_found(self):
        """Test retourne None quand non trouvé."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.find_by_id(999)

        assert result is None


class TestFindByEmail:
    """Tests de find_by_email."""

    def test_find_by_email_returns_entity_when_found(self):
        """Test trouve par email."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.email = "test@test.com"
        mock_model.password_hash = "hashed"
        mock_model.nom = "Dupont"
        mock_model.prenom = "Jean"
        mock_model.role = "compagnon"
        mock_model.type_utilisateur = "employe"
        mock_model.is_active = True
        mock_model.couleur = "#3498DB"
        mock_model.photo_profil = None
        mock_model.code_utilisateur = None
        mock_model.telephone = None
        mock_model.metier = None
        mock_model.contact_urgence_nom = None
        mock_model.contact_urgence_tel = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.find_by_email(Email("test@test.com"))

        assert result is not None
        assert str(result.email) == "test@test.com"


class TestFindByCode:
    """Tests de find_by_code."""

    def test_find_by_code_returns_entity_when_found(self):
        """Test trouve par code utilisateur."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.id = 1
        mock_model.email = "test@test.com"
        mock_model.password_hash = "hashed"
        mock_model.nom = "Dupont"
        mock_model.prenom = "Jean"
        mock_model.role = "compagnon"
        mock_model.type_utilisateur = "employe"
        mock_model.is_active = True
        mock_model.couleur = "#3498DB"
        mock_model.photo_profil = None
        mock_model.code_utilisateur = "JD001"
        mock_model.telephone = None
        mock_model.metier = None
        mock_model.contact_urgence_nom = None
        mock_model.contact_urgence_tel = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.find_by_code("JD001")

        assert result is not None
        assert result.code_utilisateur == "JD001"

    def test_find_by_code_returns_none_when_not_found(self):
        """Test retourne None si code non trouvé."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.find_by_code("INVALID")

        assert result is None


class TestSave:
    """Tests de save."""

    def test_save_new_user(self):
        """Test sauvegarde nouvel utilisateur."""
        mock_session = Mock()
        mock_user = Mock()
        mock_user.id = None
        mock_user.email = Mock()
        mock_user.email.__str__ = Mock(return_value="new@test.com")
        mock_user.password_hash = Mock()
        mock_user.password_hash.value = "hashed"
        mock_user.nom = "New"
        mock_user.prenom = "User"
        mock_user.role = Mock()
        mock_user.role.value = "compagnon"
        mock_user.type_utilisateur = Mock()
        mock_user.type_utilisateur.value = "employe"
        mock_user.is_active = True
        mock_user.couleur = None
        mock_user.photo_profil = None
        mock_user.code_utilisateur = None
        mock_user.telephone = None
        mock_user.metier = None
        mock_user.contact_urgence_nom = None
        mock_user.contact_urgence_tel = None
        mock_user.created_at = datetime.now()
        mock_user.updated_at = datetime.now()

        # Mock le modèle retourné après save
        mock_model = Mock()
        mock_model.id = 1
        mock_model.email = "new@test.com"
        mock_model.password_hash = "hashed"
        mock_model.nom = "New"
        mock_model.prenom = "User"
        mock_model.role = "compagnon"
        mock_model.type_utilisateur = "employe"
        mock_model.is_active = True
        mock_model.couleur = "#3498DB"
        mock_model.photo_profil = None
        mock_model.code_utilisateur = None
        mock_model.telephone = None
        mock_model.metier = None
        mock_model.contact_urgence_nom = None
        mock_model.contact_urgence_tel = None
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()

        def refresh_side_effect(m):
            m.id = 1

        mock_session.refresh.side_effect = refresh_side_effect

        with patch(
            "modules.auth.infrastructure.persistence.sqlalchemy_user_repository.UserModel"
        ) as MockUserModel:
            MockUserModel.return_value = mock_model

            repo = SQLAlchemyUserRepository(mock_session)
            result = repo.save(mock_user)

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()


class TestDelete:
    """Tests de delete (soft delete)."""

    def test_delete_existing_user(self):
        """Test suppression utilisateur existant."""
        mock_session = Mock()
        mock_model = Mock()
        mock_model.deleted_at = None

        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.delete(1)

        assert result is True
        assert mock_model.deleted_at is not None
        mock_session.commit.assert_called_once()

    def test_delete_non_existing_user(self):
        """Test suppression utilisateur inexistant."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.delete(999)

        assert result is False


class TestFindAll:
    """Tests de find_all."""

    def test_find_all_with_pagination(self):
        """Test find_all avec pagination."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyUserRepository(mock_session)
        repo.find_all(skip=10, limit=5)

        mock_query.offset.assert_called_with(10)
        mock_query.limit.assert_called_with(5)


class TestCount:
    """Tests de count."""

    def test_count_returns_total(self):
        """Test count retourne le total."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 42

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.count()

        assert result == 42


class TestFindByRole:
    """Tests de find_by_role."""

    def test_find_by_role(self):
        """Test trouve par rôle."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyUserRepository(mock_session)
        repo.find_by_role(Role.ADMIN)

        # Vérifie que les filtres sont appliqués
        assert mock_query.filter.call_count == 2  # role + not_deleted


class TestFindByType:
    """Tests de find_by_type."""

    def test_find_by_type(self):
        """Test trouve par type utilisateur."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyUserRepository(mock_session)
        repo.find_by_type(TypeUtilisateur.EMPLOYE)

        assert mock_query.filter.call_count == 2


class TestFindActive:
    """Tests de find_active."""

    def test_find_active(self):
        """Test trouve utilisateurs actifs."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        repo = SQLAlchemyUserRepository(mock_session)
        repo.find_active()

        assert mock_query.filter.call_count == 2  # is_active + not_deleted


class TestExistsByEmail:
    """Tests de exists_by_email."""

    def test_exists_by_email_true(self):
        """Test email existe."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = Mock()

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.exists_by_email(Email("exists@test.com"))

        assert result is True

    def test_exists_by_email_false(self):
        """Test email n'existe pas."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.exists_by_email(Email("notexists@test.com"))

        assert result is False


class TestExistsByCode:
    """Tests de exists_by_code."""

    def test_exists_by_code_true(self):
        """Test code existe."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = Mock()

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.exists_by_code("CODE01")

        assert result is True

    def test_exists_by_code_false(self):
        """Test code n'existe pas."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        repo = SQLAlchemyUserRepository(mock_session)
        result = repo.exists_by_code("INVALID")

        assert result is False


class TestSearch:
    """Tests de search."""

    def test_search_basic(self):
        """Test recherche basique."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = SQLAlchemyUserRepository(mock_session)
        results, total = repo.search()

        assert results == []
        assert total == 0

    def test_search_with_query(self):
        """Test recherche avec terme."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = SQLAlchemyUserRepository(mock_session)
        results, total = repo.search(query="Dupont")

        # Vérifie que le filtre de recherche est appliqué
        assert mock_query.filter.call_count >= 2

    def test_search_with_filters(self):
        """Test recherche avec filtres multiples."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        repo = SQLAlchemyUserRepository(mock_session)
        results, total = repo.search(
            query="test",
            role=Role.ADMIN,
            type_utilisateur=TypeUtilisateur.EMPLOYE,
            active_only=True,
        )

        # Plusieurs filtres appliqués
        assert mock_query.filter.call_count >= 4
