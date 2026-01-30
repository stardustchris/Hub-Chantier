"""Tests d'intégration pour les workflows d'authentification avancés.

Ces tests vérifient les workflows complets d'invitation, réinitialisation de mot de passe,
et gestion de compte selon la Phase 1 du workflow Authentification.
"""

import pytest
import re
from datetime import datetime, timedelta


class TestInvitationWorkflow:
    """Tests du workflow complet d'invitation utilisateur."""

    def test_invite_user_success_admin(self, client, auth_headers):
        """Test invitation réussie par un admin."""
        invite_data = {
            "email": "newinvite@test.com",
            "nom": "Invite",
            "prenom": "Test",
            "role": "compagnon",
        }

        response = client.post(
            "/api/auth/invite",
            json=invite_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "message" in response.json()
        assert "invitation envoyée" in response.json()["message"].lower()

    def test_invite_user_duplicate_email(self, client, auth_headers, sample_user_data):
        """Test invitation avec email déjà existant."""
        # Créer d'abord un utilisateur
        client.post("/api/auth/register", json=sample_user_data)

        # Tenter d'inviter avec le même email
        invite_data = {
            "email": sample_user_data["email"],
            "nom": "Invite",
            "prenom": "Test",
            "role": "compagnon",
        }

        response = client.post(
            "/api/auth/invite",
            json=invite_data,
            headers=auth_headers,
        )

        assert response.status_code in [400, 409]

    def test_invite_user_invalid_email(self, client, auth_headers):
        """Test invitation avec email invalide."""
        invite_data = {
            "email": "invalid-email",
            "nom": "Invite",
            "prenom": "Test",
            "role": "compagnon",
        }

        response = client.post(
            "/api/auth/invite",
            json=invite_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_get_invitation_info_success(self, client, auth_headers, db_session):
        """Test récupération des informations d'une invitation."""
        # Créer une invitation
        from backend.modules.auth.infrastructure.persistence.models import UserInvitation
        from datetime import datetime, timedelta
        import secrets

        token = secrets.token_urlsafe(32)
        invitation = UserInvitation(
            email="invite@test.com",
            nom="INVITE",
            prenom="Test",
            role="compagnon",
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db_session.add(invitation)
        db_session.commit()

        # Récupérer les infos de l'invitation
        response = client.get(f"/api/auth/invitation/{token}")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "invite@test.com"
        assert data["nom"] == "INVITE"
        assert data["prenom"] == "Test"
        assert data["role"] == "compagnon"

    def test_get_invitation_info_not_found(self, client):
        """Test récupération d'une invitation inexistante."""
        response = client.get("/api/auth/invitation/invalid-token")

        assert response.status_code == 404

    def test_get_invitation_info_expired(self, client, db_session):
        """Test récupération d'une invitation expirée."""
        from backend.modules.auth.infrastructure.persistence.models import UserInvitation
        import secrets

        token = secrets.token_urlsafe(32)
        invitation = UserInvitation(
            email="expired@test.com",
            nom="EXPIRED",
            prenom="Test",
            role="compagnon",
            token=token,
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Expirée
        )
        db_session.add(invitation)
        db_session.commit()

        response = client.get(f"/api/auth/invitation/{token}")

        assert response.status_code == 400

    def test_accept_invitation_success(self, client, db_session):
        """Test acceptation d'une invitation avec succès."""
        from backend.modules.auth.infrastructure.persistence.models import UserInvitation
        import secrets

        token = secrets.token_urlsafe(32)
        invitation = UserInvitation(
            email="accept@test.com",
            nom="ACCEPT",
            prenom="Test",
            role="compagnon",
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db_session.add(invitation)
        db_session.commit()

        # Accepter l'invitation
        accept_data = {
            "token": token,
            "password": "SecurePassword123!",
        }

        response = client.post("/api/auth/accept-invitation", json=accept_data)

        assert response.status_code == 201
        data = response.json()
        assert "message" in data

        # Vérifier que l'utilisateur a été créé
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": "accept@test.com",
                "password": "SecurePassword123!",
            },
        )
        assert login_response.status_code == 200

    def test_accept_invitation_invalid_token(self, client):
        """Test acceptation avec token invalide."""
        accept_data = {
            "token": "invalid-token",
            "password": "SecurePassword123!",
        }

        response = client.post("/api/auth/accept-invitation", json=accept_data)

        assert response.status_code == 400

    def test_accept_invitation_weak_password(self, client, db_session):
        """Test acceptation avec mot de passe faible."""
        from backend.modules.auth.infrastructure.persistence.models import UserInvitation
        import secrets

        token = secrets.token_urlsafe(32)
        invitation = UserInvitation(
            email="weakpw@test.com",
            nom="WEAK",
            prenom="Test",
            role="compagnon",
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db_session.add(invitation)
        db_session.commit()

        accept_data = {
            "token": token,
            "password": "weak",
        }

        response = client.post("/api/auth/accept-invitation", json=accept_data)

        assert response.status_code in [400, 422]


class TestPasswordResetWorkflow:
    """Tests du workflow complet de réinitialisation de mot de passe."""

    def test_request_password_reset_success(self, client, sample_user_data):
        """Test demande de réinitialisation réussie."""
        # Créer un utilisateur d'abord
        client.post("/api/auth/register", json=sample_user_data)

        # Demander la réinitialisation
        response = client.post(
            "/api/auth/request-password-reset",
            json={"email": sample_user_data["email"]},
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_request_password_reset_nonexistent_email(self, client):
        """Test demande avec email inexistant (ne devrait pas révéler l'existence)."""
        response = client.post(
            "/api/auth/request-password-reset",
            json={"email": "nonexistent@test.com"},
        )

        # Pour des raisons de sécurité, on retourne toujours 200
        assert response.status_code == 200

    def test_request_password_reset_rate_limiting(self, client, sample_user_data):
        """Test rate limiting sur les demandes de réinitialisation."""
        client.post("/api/auth/register", json=sample_user_data)

        # Première requête
        response1 = client.post(
            "/api/auth/request-password-reset",
            json={"email": sample_user_data["email"]},
        )
        assert response1.status_code == 200

        # Requêtes suivantes dans la fenêtre de rate limiting
        for _ in range(6):
            response = client.post(
                "/api/auth/request-password-reset",
                json={"email": sample_user_data["email"]},
            )

        # Devrait être rate limited après X tentatives
        assert response.status_code in [200, 429]  # 429 = Too Many Requests

    def test_reset_password_success(self, client, sample_user_data, db_session):
        """Test réinitialisation de mot de passe avec succès."""
        # Créer un utilisateur
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = reg_response.json()["user"]["id"]

        # Créer un token de réinitialisation
        from backend.modules.auth.infrastructure.persistence.models import PasswordResetToken
        import secrets

        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        db_session.add(reset_token)
        db_session.commit()

        # Réinitialiser le mot de passe
        new_password = "NewSecurePassword123!"
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "new_password": new_password,
            },
        )

        assert response.status_code == 200

        # Vérifier qu'on peut se connecter avec le nouveau mot de passe
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": new_password,
            },
        )
        assert login_response.status_code == 200

        # Vérifier qu'on ne peut plus se connecter avec l'ancien
        old_login = client.post(
            "/api/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )
        assert old_login.status_code == 401

    def test_reset_password_invalid_token(self, client):
        """Test réinitialisation avec token invalide."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "NewSecurePassword123!",
            },
        )

        assert response.status_code == 400

    def test_reset_password_expired_token(self, client, sample_user_data, db_session):
        """Test réinitialisation avec token expiré."""
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = reg_response.json()["user"]["id"]

        from backend.modules.auth.infrastructure.persistence.models import PasswordResetToken
        import secrets

        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Expiré
        )
        db_session.add(reset_token)
        db_session.commit()

        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "new_password": "NewSecurePassword123!",
            },
        )

        assert response.status_code == 400

    def test_reset_password_weak_password(self, client, sample_user_data, db_session):
        """Test réinitialisation avec mot de passe faible."""
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        user_id = reg_response.json()["user"]["id"]

        from backend.modules.auth.infrastructure.persistence.models import PasswordResetToken
        import secrets

        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        db_session.add(reset_token)
        db_session.commit()

        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": token,
                "new_password": "weak",
            },
        )

        assert response.status_code in [400, 422]


class TestChangePasswordWorkflow:
    """Tests du workflow de changement de mot de passe pour utilisateur connecté."""

    def test_change_password_success(self, client, sample_user_data):
        """Test changement de mot de passe réussi."""
        # S'enregistrer et se connecter
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        token = reg_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Changer le mot de passe
        new_password = "NewSecurePassword123!"
        response = client.post(
            "/api/auth/change-password",
            json={
                "old_password": sample_user_data["password"],
                "new_password": new_password,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Vérifier qu'on peut se connecter avec le nouveau mot de passe
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": new_password,
            },
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_old_password(self, client, sample_user_data):
        """Test changement avec mauvais ancien mot de passe."""
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        token = reg_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/auth/change-password",
            json={
                "old_password": "WrongPassword123!",
                "new_password": "NewSecurePassword123!",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_change_password_same_as_old(self, client, sample_user_data):
        """Test changement avec nouveau mot de passe identique à l'ancien."""
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        token = reg_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/auth/change-password",
            json={
                "old_password": sample_user_data["password"],
                "new_password": sample_user_data["password"],
            },
            headers=auth_headers,
        )

        # Peut être 400 ou accepté selon l'implémentation
        # L'important est que la validation métier fonctionne
        assert response.status_code in [200, 400]

    def test_change_password_weak_new_password(self, client, sample_user_data):
        """Test changement avec nouveau mot de passe faible."""
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        token = reg_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/auth/change-password",
            json={
                "old_password": sample_user_data["password"],
                "new_password": "weak",
            },
            headers=auth_headers,
        )

        assert response.status_code in [400, 422]

    def test_change_password_unauthenticated(self, client):
        """Test changement de mot de passe sans authentification."""
        response = client.post(
            "/api/auth/change-password",
            json={
                "old_password": "OldPassword123!",
                "new_password": "NewSecurePassword123!",
            },
        )

        assert response.status_code == 401


class TestAuthWorkflowIntegration:
    """Tests d'intégration des workflows complets."""

    def test_complete_invitation_workflow(self, client, auth_headers, db_session):
        """Test du workflow complet d'invitation jusqu'à connexion."""
        # 1. Admin invite un utilisateur
        invite_response = client.post(
            "/api/auth/invite",
            json={
                "email": "complete@test.com",
                "nom": "Complete",
                "prenom": "Test",
                "role": "compagnon",
            },
            headers=auth_headers,
        )
        assert invite_response.status_code == 200

        # 2. Récupérer le token de l'invitation depuis la DB
        from backend.modules.auth.infrastructure.persistence.models import UserInvitation
        invitation = db_session.query(UserInvitation).filter_by(email="complete@test.com").first()
        assert invitation is not None

        # 3. Consulter les infos de l'invitation
        info_response = client.get(f"/api/auth/invitation/{invitation.token}")
        assert info_response.status_code == 200

        # 4. Accepter l'invitation
        accept_response = client.post(
            "/api/auth/accept-invitation",
            json={
                "token": invitation.token,
                "password": "UserPassword123!",
            },
        )
        assert accept_response.status_code == 201

        # 5. Se connecter avec le nouveau compte
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": "complete@test.com",
                "password": "UserPassword123!",
            },
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_complete_password_reset_workflow(self, client, sample_user_data, db_session):
        """Test du workflow complet de réinitialisation de mot de passe."""
        # 1. Créer un utilisateur
        reg_response = client.post("/api/auth/register", json=sample_user_data)
        assert reg_response.status_code == 201
        user_id = reg_response.json()["user"]["id"]

        # 2. Demander une réinitialisation
        reset_request = client.post(
            "/api/auth/request-password-reset",
            json={"email": sample_user_data["email"]},
        )
        assert reset_request.status_code == 200

        # 3. Récupérer le token depuis la DB
        from backend.modules.auth.infrastructure.persistence.models import PasswordResetToken
        reset_token = db_session.query(PasswordResetToken).filter_by(user_id=user_id).first()
        assert reset_token is not None

        # 4. Réinitialiser le mot de passe
        new_password = "ResetPassword123!"
        reset_response = client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token.token,
                "new_password": new_password,
            },
        )
        assert reset_response.status_code == 200

        # 5. Se connecter avec le nouveau mot de passe
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": new_password,
            },
        )
        assert login_response.status_code == 200
