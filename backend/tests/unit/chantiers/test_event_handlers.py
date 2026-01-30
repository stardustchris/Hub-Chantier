"""Tests unitaires pour les event handlers du module chantiers."""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock


class TestHandleChantierCreated:
    """Tests du handler chantier.created."""

    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    @patch("modules.chantiers.infrastructure.event_handlers.SessionLocal")
    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyEntityInfoService")
    def test_creates_notifications_for_assignees(
        self, mock_entity_svc_class, mock_session_local, mock_repo_class
    ):
        """Test que des notifications sont creees pour les conducteurs et chefs."""
        from modules.chantiers.infrastructure.event_handlers import handle_chantier_created

        mock_db = Mock()
        mock_session_local.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_entity_svc = Mock()
        mock_user_info = Mock()
        mock_user_info.nom = "Jean Dupont"
        mock_entity_svc.get_user_info.return_value = mock_user_info
        mock_entity_svc_class.return_value = mock_entity_svc

        event = Mock()
        event.data = {
            'chantier_id': 1,
            'nom': 'Chantier Test',
        }
        event.metadata = {
            'created_by': 5,
            'conducteur_ids': [10, 11],
            'chef_chantier_ids': [20],
        }

        handle_chantier_created(event)

        # 3 destinataires (10, 11, 20) - le createur (5) n'est pas dedans
        assert mock_repo.save.call_count == 3
        mock_db.close.assert_called_once()

    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    @patch("modules.chantiers.infrastructure.event_handlers.SessionLocal")
    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyEntityInfoService")
    def test_excludes_creator_from_notifications(
        self, mock_entity_svc_class, mock_session_local, mock_repo_class
    ):
        """Test que le createur n'est pas notifie."""
        from modules.chantiers.infrastructure.event_handlers import handle_chantier_created

        mock_db = Mock()
        mock_session_local.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_entity_svc = Mock()
        mock_entity_svc.get_user_info.return_value = Mock(nom="Admin")
        mock_entity_svc_class.return_value = mock_entity_svc

        event = Mock()
        event.data = {'chantier_id': 1, 'nom': 'Test'}
        event.metadata = {
            'created_by': 10,
            'conducteur_ids': [10],  # Le createur est aussi conducteur
            'chef_chantier_ids': [],
        }

        handle_chantier_created(event)

        # 0 notification car le seul destinataire est le createur
        assert mock_repo.save.call_count == 0

    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    @patch("modules.chantiers.infrastructure.event_handlers.SessionLocal")
    def test_handles_no_metadata(self, mock_session_local, mock_repo_class):
        """Test avec un evenement sans metadata."""
        from modules.chantiers.infrastructure.event_handlers import handle_chantier_created

        mock_db = Mock()
        mock_session_local.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        event = Mock(spec=['data'])
        event.data = {'chantier_id': 1, 'nom': 'Test'}

        handle_chantier_created(event)

        # Pas de notification car pas de metadata avec les IDs
        assert mock_repo.save.call_count == 0
        mock_db.close.assert_called_once()

    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    @patch("modules.chantiers.infrastructure.event_handlers.SessionLocal")
    def test_closes_session_on_error(self, mock_session_local, mock_repo_class):
        """Test que la session est fermee meme en cas d'erreur."""
        from modules.chantiers.infrastructure.event_handlers import handle_chantier_created

        mock_db = Mock()
        mock_session_local.return_value = mock_db
        mock_repo_class.side_effect = Exception("DB error")

        event = Mock()
        event.data = {'chantier_id': 1, 'nom': 'Test'}
        event.metadata = {'created_by': 5, 'conducteur_ids': [10], 'chef_chantier_ids': []}

        # Ne doit pas crasher (erreur catchee)
        handle_chantier_created(event)

        mock_db.close.assert_called_once()


class TestHandleChantierStatutChanged:
    """Tests du handler chantier.statut_changed."""

    @patch("modules.chantiers.infrastructure.event_handlers._get_chantier_users")
    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    @patch("modules.chantiers.infrastructure.event_handlers.SessionLocal")
    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyEntityInfoService")
    def test_notifies_team_on_statut_change(
        self, mock_entity_svc_class, mock_session_local, mock_repo_class, mock_get_users
    ):
        """Test notification equipe sur changement de statut."""
        from modules.chantiers.infrastructure.event_handlers import handle_chantier_statut_changed

        mock_db = Mock()
        mock_session_local.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_get_users.return_value = [10, 20, 30]

        mock_entity_svc = Mock()
        mock_entity_svc.get_user_info.return_value = Mock(nom="Admin")
        mock_entity_svc_class.return_value = mock_entity_svc

        event = Mock()
        event.data = {'chantier_id': 1, 'nouveau_statut': 'en_cours'}
        event.metadata = {'changed_by': 5}

        handle_chantier_statut_changed(event)

        # 3 destinataires (10, 20, 30 - le changer 5 n'est pas dans la liste)
        assert mock_repo.save.call_count == 3
        mock_db.close.assert_called_once()

    @patch("modules.chantiers.infrastructure.event_handlers.SessionLocal")
    def test_returns_early_without_chantier_id(self, mock_session_local):
        """Test retour anticipe si pas de chantier_id."""
        from modules.chantiers.infrastructure.event_handlers import handle_chantier_statut_changed

        event = Mock(spec=['data'])
        event.data = {'nouveau_statut': 'en_cours'}

        handle_chantier_statut_changed(event)

        # SessionLocal ne doit pas etre appele
        mock_session_local.assert_not_called()

    @patch("modules.chantiers.infrastructure.event_handlers._get_chantier_users")
    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyNotificationRepository")
    @patch("modules.chantiers.infrastructure.event_handlers.SessionLocal")
    @patch("modules.chantiers.infrastructure.event_handlers.SQLAlchemyEntityInfoService")
    def test_excludes_changer_from_notifications(
        self, mock_entity_svc_class, mock_session_local, mock_repo_class, mock_get_users
    ):
        """Test que le changeur n'est pas notifie."""
        from modules.chantiers.infrastructure.event_handlers import handle_chantier_statut_changed

        mock_db = Mock()
        mock_session_local.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_get_users.return_value = [5, 10]  # 5 est le changeur

        mock_entity_svc = Mock()
        mock_entity_svc.get_user_info.return_value = Mock(nom="Admin")
        mock_entity_svc_class.return_value = mock_entity_svc

        event = Mock()
        event.data = {'chantier_id': 1, 'nouveau_statut': 'ferme'}
        event.metadata = {'changed_by': 5}

        handle_chantier_statut_changed(event)

        # Seulement user 10 notifie (5 exclu car changeur)
        assert mock_repo.save.call_count == 1


class TestRegisterChantierHandlers:
    """Tests de l'enregistrement des handlers."""

    def test_register_logs_message(self, caplog):
        """Test que l'enregistrement logge un message."""
        from modules.chantiers.infrastructure.event_handlers import register_chantier_handlers

        with caplog.at_level(logging.INFO):
            register_chantier_handlers()

        assert "Chantier event handlers registered" in caplog.text


class TestGetChantierUsers:
    """Tests de la fonction _get_chantier_users."""

    @patch("modules.chantiers.infrastructure.event_handlers.ChantierChefModel", create=True)
    @patch("modules.chantiers.infrastructure.event_handlers.ChantierConducteurModel", create=True)
    def test_returns_unique_user_ids(self, mock_conducteur_model, mock_chef_model):
        """Test que les IDs retournes sont uniques."""
        # Utilisation de lazy import donc on patch au niveau du module
        with patch(
            "modules.chantiers.infrastructure.persistence.ChantierConducteurModel"
        ) as mock_cond, patch(
            "modules.chantiers.infrastructure.persistence.ChantierChefModel"
        ) as mock_chef:
            from modules.chantiers.infrastructure.event_handlers import _get_chantier_users

            mock_db = Mock()
            # Conducteurs: user 10, 20
            mock_db.query.return_value.filter.return_value.all.side_effect = [
                [(10,), (20,)],  # conducteurs
                [(20,), (30,)],  # chefs (20 est en double)
            ]

            result = _get_chantier_users(mock_db, chantier_id=1)

            assert set(result) == {10, 20, 30}
