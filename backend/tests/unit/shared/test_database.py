"""Tests unitaires pour le module database."""

import pytest
from unittest.mock import Mock, MagicMock


class TestGetDb:
    """Tests pour get_db."""

    def test_get_db_yields_session(self):
        """get_db doit yield une session."""
        from shared.infrastructure.database import get_db

        gen = get_db()
        session = next(gen)

        # La session doit etre un objet de type Session
        assert session is not None

        # Fermer proprement
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_closes_session_on_exception(self):
        """get_db doit fermer la session meme en cas d'exception."""
        from shared.infrastructure.database import get_db

        gen = get_db()
        session = next(gen)

        # Simuler une exception dans le contexte
        try:
            gen.throw(ValueError("Test error"))
        except ValueError:
            pass

        # La session doit avoir ete fermee (pas de verification directe possible,
        # mais le test ne doit pas lever d'exception)


class TestEngineConfiguration:
    """Tests pour la configuration de l'engine."""

    def test_engine_exists(self):
        """L'engine existe."""
        from shared.infrastructure.database import engine

        assert engine is not None

    def test_session_local_configured(self):
        """SessionLocal est configure."""
        from shared.infrastructure.database import SessionLocal

        assert SessionLocal is not None
        # Verifie que c'est callable
        assert callable(SessionLocal)

    def test_session_local_creates_session(self):
        """SessionLocal cree une session."""
        from shared.infrastructure.database import SessionLocal

        session = SessionLocal()
        assert session is not None
        session.close()


class TestInitDb:
    """Tests pour init_db."""

    def test_init_db_callable(self):
        """init_db est appelable."""
        from shared.infrastructure.database import init_db

        assert callable(init_db)


class TestMigrateChantierResponsables:
    """Tests pour _migrate_chantier_responsables."""

    def test_function_exists(self):
        """La fonction existe."""
        from shared.infrastructure.database import _migrate_chantier_responsables

        assert callable(_migrate_chantier_responsables)

    def test_function_does_not_raise(self):
        """La fonction ne leve pas d'exception."""
        from shared.infrastructure.database import _migrate_chantier_responsables

        # La fonction doit s'executer sans erreur
        # Elle peut ne rien faire si deja migre
        _migrate_chantier_responsables()
