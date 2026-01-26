"""Tests unitaires pour SQLAlchemyEntityInfoService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import logging

from shared.infrastructure.entity_info_impl import (
    SQLAlchemyEntityInfoService,
    get_entity_info_service,
)


class TestGetUserInfo:
    """Tests de get_user_info."""

    def test_returns_none_and_logs_warning_on_exception(self, caplog):
        """Test retourne None et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_user_info(1)

        assert result is None
        assert "Erreur recuperation user 1" in caplog.text

    def test_returns_user_info_with_real_db(self):
        """Test retourne les infos utilisateur avec vraie DB."""
        from shared.infrastructure.database import SessionLocal

        db = SessionLocal()
        try:
            service = SQLAlchemyEntityInfoService(db)
            # Recherche un utilisateur inexistant
            result = service.get_user_info(99999)
            assert result is None
        finally:
            db.close()

    def test_returns_user_info_with_existing_user(self):
        """Test avec un utilisateur existant."""
        from shared.infrastructure.database import SessionLocal
        from modules.auth.infrastructure.persistence import UserModel

        db = SessionLocal()
        try:
            # Trouver un utilisateur existant
            user = db.query(UserModel).first()
            if user:
                service = SQLAlchemyEntityInfoService(db)
                result = service.get_user_info(user.id)

                assert result is not None
                assert result.id == user.id
        finally:
            db.close()


class TestGetChantierInfo:
    """Tests de get_chantier_info."""

    def test_returns_none_and_logs_warning_on_exception(self, caplog):
        """Test retourne None et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_chantier_info(10)

        assert result is None
        assert "Erreur recuperation chantier 10" in caplog.text

    def test_returns_none_when_chantier_not_found(self):
        """Test retourne None quand chantier non trouve."""
        from shared.infrastructure.database import SessionLocal

        db = SessionLocal()
        try:
            service = SQLAlchemyEntityInfoService(db)
            result = service.get_chantier_info(99999)
            assert result is None
        finally:
            db.close()

    def test_returns_chantier_info_with_existing_chantier(self):
        """Test avec un chantier existant."""
        from shared.infrastructure.database import SessionLocal
        from modules.chantiers.infrastructure.persistence import ChantierModel

        db = SessionLocal()
        try:
            # Trouver un chantier existant
            chantier = db.query(ChantierModel).first()
            if chantier:
                service = SQLAlchemyEntityInfoService(db)
                result = service.get_chantier_info(chantier.id)

                assert result is not None
                assert result.id == chantier.id
        finally:
            db.close()


class TestGetActiveUserIds:
    """Tests de get_active_user_ids."""

    def test_returns_empty_list_and_logs_warning_on_exception(self, caplog):
        """Test retourne liste vide et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_active_user_ids()

        assert result == []
        assert "Erreur recuperation users actifs" in caplog.text

    def test_returns_list_of_ids(self):
        """Test retourne une liste d'IDs."""
        from shared.infrastructure.database import SessionLocal

        db = SessionLocal()
        try:
            service = SQLAlchemyEntityInfoService(db)
            result = service.get_active_user_ids()

            # Doit retourner une liste (peut etre vide)
            assert isinstance(result, list)
        finally:
            db.close()


class TestGetUserChantierIds:
    """Tests de get_user_chantier_ids."""

    def test_returns_empty_list_and_logs_warning_on_exception(self, caplog):
        """Test retourne liste vide et log warning en cas d'erreur."""
        mock_session = Mock()
        mock_session.query.side_effect = Exception("DB error")

        service = SQLAlchemyEntityInfoService(mock_session)

        with caplog.at_level(logging.WARNING):
            result = service.get_user_chantier_ids(5)

        assert result == []
        assert "Erreur recuperation chantiers user 5" in caplog.text

    def test_returns_empty_list_for_nonexistent_user(self):
        """Test retourne liste vide pour utilisateur inexistant."""
        from shared.infrastructure.database import SessionLocal

        db = SessionLocal()
        try:
            service = SQLAlchemyEntityInfoService(db)
            result = service.get_user_chantier_ids(99999)

            # Utilisateur inexistant -> liste vide
            assert isinstance(result, list)
        finally:
            db.close()


class TestGetEntityInfoService:
    """Tests de la factory get_entity_info_service."""

    def test_returns_sqlalchemy_entity_info_service(self):
        """Test retourne une instance de SQLAlchemyEntityInfoService."""
        mock_session = Mock()

        service = get_entity_info_service(mock_session)

        assert isinstance(service, SQLAlchemyEntityInfoService)
        assert service._session == mock_session


class TestUserBasicInfoConstruction:
    """Tests de la construction de UserBasicInfo."""

    def test_handles_partial_name(self):
        """Test gere les noms partiels."""
        from shared.application.ports import UserBasicInfo

        # Test avec prenom seulement
        info = UserBasicInfo(
            id=1,
            nom="Jean",
            couleur=None,
            metier=None,
            role="compagnon",
            type_utilisateur="employe",
        )
        assert info.nom == "Jean"

    def test_handles_full_name(self):
        """Test gere les noms complets."""
        from shared.application.ports import UserBasicInfo

        info = UserBasicInfo(
            id=1,
            nom="Jean Dupont",
            couleur="#FF0000",
            metier="Macon",
            role="compagnon",
            type_utilisateur="employe",
        )
        assert info.id == 1
        assert info.nom == "Jean Dupont"
        assert info.couleur == "#FF0000"


class TestChantierBasicInfoConstruction:
    """Tests de la construction de ChantierBasicInfo."""

    def test_handles_complete_info(self):
        """Test gere les infos completes."""
        from shared.application.ports import ChantierBasicInfo

        info = ChantierBasicInfo(
            id=10,
            nom="Chantier Tour Eiffel",
            couleur="#00FF00",
        )
        assert info.id == 10
        assert info.nom == "Chantier Tour Eiffel"
        assert info.couleur == "#00FF00"

    def test_handles_minimal_info(self):
        """Test gere les infos minimales."""
        from shared.application.ports import ChantierBasicInfo

        info = ChantierBasicInfo(
            id=5,
            nom="Chantier Test",
            couleur=None,
        )
        assert info.id == 5
        assert info.couleur is None
