"""Service d'envoi d'emails."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from pathlib import Path
import os

from ..infrastructure.config import settings
from ..application.ports.email_service import EmailServicePort


class EmailService(EmailServicePort):
    """
    Service pour envoyer des emails.

    Supporte SMTP ou mode console (dev).
    """

    def __init__(self) -> None:
        """Initialise le service d'email."""
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.smtp_from_email = getattr(settings, 'SMTP_FROM_EMAIL', 'noreply@hub-chantier.fr')
        self.smtp_from_name = getattr(settings, 'SMTP_FROM_NAME', 'Hub Chantier')
        self.smtp_use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        # Mode console pour développement
        self.console_mode = getattr(settings, 'EMAIL_CONSOLE_MODE', True)

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Envoie un email.

        Args:
            to: Destinataire principal.
            subject: Sujet de l'email.
            html_content: Contenu HTML de l'email.
            text_content: Contenu texte brut (fallback).
            cc: Liste des destinataires en copie.
            bcc: Liste des destinataires en copie cachée.

        Returns:
            True si l'envoi a réussi, False sinon.
        """
        if self.console_mode:
            # Mode console : affiche l'email dans les logs
            print("\n" + "="*80)
            print(f"EMAIL [CONSOLE MODE]")
            print(f"From: {self.smtp_from_name} <{self.smtp_from_email}>")
            print(f"To: {to}")
            if cc:
                print(f"CC: {', '.join(cc)}")
            if bcc:
                print(f"BCC: {', '.join(bcc)}")
            print(f"Subject: {subject}")
            print("-"*80)
            print(html_content)
            print("="*80 + "\n")
            return True

        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            msg['To'] = to

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Ajouter les contenus
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)

            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)

            # Construire la liste complète des destinataires
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # Envoyer via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, from_addr=self.smtp_from_email, to_addrs=recipients)

            return True

        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False

    def send_password_reset_email(self, to: str, token: str, user_name: str) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe.

        Args:
            to: Email du destinataire.
            token: Token de réinitialisation.
            user_name: Nom complet de l'utilisateur.

        Returns:
            True si l'envoi a réussi.
        """
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        reset_url = f"{frontend_url}/reset-password?token={token}"

        html_content = self._render_template(
            'email_reset_password.html',
            {
                'user_name': user_name,
                'reset_url': reset_url,
                'expiry_hours': 1,
            }
        )

        text_content = f"""
Bonjour {user_name},

Vous avez demandé à réinitialiser votre mot de passe sur Hub Chantier.

Pour créer un nouveau mot de passe, cliquez sur le lien ci-dessous :
{reset_url}

Ce lien expirera dans 1 heure.

Si vous n'avez pas fait cette demande, ignorez cet email.

L'équipe Hub Chantier
        """.strip()

        return self.send_email(
            to=to,
            subject="Réinitialisation de votre mot de passe - Hub Chantier",
            html_content=html_content,
            text_content=text_content,
        )

    def send_invitation_email(
        self,
        to: str,
        token: str,
        user_name: str,
        inviter_name: str,
        role: str,
    ) -> bool:
        """
        Envoie un email d'invitation.

        Args:
            to: Email du destinataire.
            token: Token d'invitation.
            user_name: Nom complet de l'utilisateur invité.
            inviter_name: Nom de la personne qui invite.
            role: Rôle assigné.

        Returns:
            True si l'envoi a réussi.
        """
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        invitation_url = f"{frontend_url}/accept-invitation?token={token}"

        role_labels = {
            'ADMIN': 'Administrateur',
            'CONDUCTEUR': 'Conducteur de travaux',
            'CHEF_CHANTIER': 'Chef de chantier',
            'COMPAGNON': 'Compagnon',
        }
        role_label = role_labels.get(role, role)

        html_content = self._render_template(
            'email_invitation.html',
            {
                'user_name': user_name,
                'inviter_name': inviter_name,
                'role': role_label,
                'invitation_url': invitation_url,
                'expiry_days': 7,
            }
        )

        text_content = f"""
Bonjour {user_name},

{inviter_name} vous invite à rejoindre Hub Chantier en tant que {role_label}.

Pour activer votre compte et définir votre mot de passe, cliquez sur le lien ci-dessous :
{invitation_url}

Cette invitation expire dans 7 jours.

Bienvenue dans l'équipe !

L'équipe Hub Chantier
        """.strip()

        return self.send_email(
            to=to,
            subject=f"Invitation à rejoindre Hub Chantier - {role_label}",
            html_content=html_content,
            text_content=text_content,
        )

    def send_email_verification(self, to: str, token: str, user_name: str) -> bool:
        """
        Envoie un email de vérification d'adresse.

        Args:
            to: Email du destinataire.
            token: Token de vérification.
            user_name: Nom complet de l'utilisateur.

        Returns:
            True si l'envoi a réussi.
        """
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        verification_url = f"{frontend_url}/verify-email?token={token}"

        html_content = self._render_template(
            'email_verification.html',
            {
                'user_name': user_name,
                'verification_url': verification_url,
            }
        )

        text_content = f"""
Bonjour {user_name},

Merci de vous être inscrit sur Hub Chantier !

Pour vérifier votre adresse email, cliquez sur le lien ci-dessous :
{verification_url}

L'équipe Hub Chantier
        """.strip()

        return self.send_email(
            to=to,
            subject="Vérifiez votre adresse email - Hub Chantier",
            html_content=html_content,
            text_content=text_content,
        )

    def _render_template(self, template_name: str, context: dict) -> str:
        """
        Rend un template HTML.

        Args:
            template_name: Nom du fichier template.
            context: Variables du template.

        Returns:
            Contenu HTML rendu.
        """
        templates_dir = Path(__file__).parent.parent.parent / 'templates' / 'email'
        template_path = templates_dir / template_name

        if not template_path.exists():
            # Fallback : template simple
            return self._render_simple_template(context)

        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Remplacement simple des variables (pas de Jinja2 pour simplifier)
        for key, value in context.items():
            template = template.replace('{{ ' + key + ' }}', str(value))

        return template

    def _render_simple_template(self, context: dict) -> str:
        """Template HTML simple par défaut."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: white;
            padding: 30px;
            border: 1px solid #e5e7eb;
            border-top: none;
        }}
        .button {{
            display: inline-block;
            background: #3B82F6;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏗️ Hub Chantier</h1>
    </div>
    <div class="content">
        {context.get('content', '')}
    </div>
    <div class="footer">
        <p>Hub Chantier - Gestion de chantiers BTP</p>
        <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
    </div>
</body>
</html>
        """


# Instance globale
email_service = EmailService()
