"""Service de notifications push avec Firebase Cloud Messaging.

Gère l'envoi de notifications push vers les appareils mobiles et navigateurs :
- LOG-13 : Notification demande réservation
- LOG-14 : Notification décision réservation
- LOG-15 : Rappel J-1 réservation
- SIG-13 : Notification nouveau signalement
- FEED-17 : Notifications tableau de bord
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Singleton
_notification_service: Optional["NotificationService"] = None


@dataclass
class NotificationPayload:
    """Payload d'une notification push.

    Attributes:
        title: Titre de la notification
        body: Corps du message
        data: Données additionnelles (pour navigation dans l'app)
        image_url: URL d'une image optionnelle
        click_action: Action au clic (URL ou route)
    """
    title: str
    body: str
    data: Dict[str, str] = field(default_factory=dict)
    image_url: Optional[str] = None
    click_action: Optional[str] = None

    def to_fcm_message(self) -> Dict[str, Any]:
        """Convertit en format FCM."""
        notification = {
            "title": self.title,
            "body": self.body,
        }
        if self.image_url:
            notification["image"] = self.image_url

        message = {
            "notification": notification,
            "data": self.data,
        }

        if self.click_action:
            message["webpush"] = {
                "fcm_options": {
                    "link": self.click_action
                }
            }

        return message


class NotificationService:
    """Service d'envoi de notifications push via Firebase Cloud Messaging.

    Configuration requise :
    - Variable d'environnement FIREBASE_CREDENTIALS_PATH pointant vers le fichier JSON
    - Ou variable FIREBASE_CREDENTIALS contenant le JSON encodé
    """

    def __init__(self):
        """Initialise le service Firebase."""
        self._initialized = False
        self._app = None
        self._init_firebase()

    def _init_firebase(self) -> None:
        """Initialise l'application Firebase."""
        try:
            import firebase_admin
            from firebase_admin import credentials

            # Vérifier si déjà initialisé
            try:
                self._app = firebase_admin.get_app()
                self._initialized = True
                logger.info("Firebase déjà initialisé")
                return
            except ValueError:
                pass

            # Chemin vers le fichier de credentials
            creds_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")

            if creds_path and os.path.exists(creds_path):
                cred = credentials.Certificate(creds_path)
                self._app = firebase_admin.initialize_app(cred)
                self._initialized = True
                logger.info("Firebase initialisé avec credentials")
            else:
                # Mode développement sans credentials
                logger.warning(
                    "Firebase credentials non trouvées. "
                    "Les notifications seront simulées. "
                    "Définir FIREBASE_CREDENTIALS_PATH pour activer."
                )
                self._initialized = False

        except ImportError:
            logger.error("firebase-admin non installé. pip install firebase-admin")
            self._initialized = False
        except Exception as e:
            logger.error(f"Erreur initialisation Firebase: {e}")
            self._initialized = False

    @property
    def is_available(self) -> bool:
        """Vérifie si Firebase est disponible."""
        return self._initialized

    def send_to_token(
        self,
        token: str,
        payload: NotificationPayload,
    ) -> bool:
        """Envoie une notification à un token spécifique.

        Args:
            token: Token FCM de l'appareil
            payload: Contenu de la notification

        Returns:
            True si envoyé, False sinon
        """
        if not self._initialized:
            logger.info(f"[SIMULATED] Notification → {token[:20]}...: {payload.title}")
            return True

        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=payload.title,
                    body=payload.body,
                    image=payload.image_url,
                ),
                data=payload.data,
                token=token,
            )

            if payload.click_action:
                message.webpush = messaging.WebpushConfig(
                    fcm_options=messaging.WebpushFCMOptions(
                        link=payload.click_action
                    )
                )

            response = messaging.send(message)
            logger.info(f"Notification envoyée: {response}")
            return True

        except Exception as e:
            logger.error(f"Erreur envoi notification: {e}")
            return False

    def send_to_tokens(
        self,
        tokens: List[str],
        payload: NotificationPayload,
    ) -> Dict[str, bool]:
        """Envoie une notification à plusieurs tokens.

        Args:
            tokens: Liste de tokens FCM
            payload: Contenu de la notification

        Returns:
            Dict avec status par token
        """
        if not tokens:
            return {}

        if not self._initialized:
            logger.info(
                f"[SIMULATED] Notification multi ({len(tokens)} tokens): {payload.title}"
            )
            return {token: True for token in tokens}

        try:
            from firebase_admin import messaging

            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=payload.title,
                    body=payload.body,
                    image=payload.image_url,
                ),
                data=payload.data,
                tokens=tokens,
            )

            response = messaging.send_multicast(message)

            results = {}
            for i, resp in enumerate(response.responses):
                results[tokens[i]] = resp.success

            logger.info(
                f"Notifications envoyées: {response.success_count}/{len(tokens)} succès"
            )
            return results

        except Exception as e:
            logger.error(f"Erreur envoi notifications: {e}")
            return {token: False for token in tokens}

    def send_to_topic(
        self,
        topic: str,
        payload: NotificationPayload,
    ) -> bool:
        """Envoie une notification à un topic (groupe d'utilisateurs).

        Args:
            topic: Nom du topic (ex: "chantier_123", "conducteurs")
            payload: Contenu de la notification

        Returns:
            True si envoyé
        """
        if not self._initialized:
            logger.info(f"[SIMULATED] Notification topic '{topic}': {payload.title}")
            return True

        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=payload.title,
                    body=payload.body,
                    image=payload.image_url,
                ),
                data=payload.data,
                topic=topic,
            )

            response = messaging.send(message)
            logger.info(f"Notification topic envoyée: {response}")
            return True

        except Exception as e:
            logger.error(f"Erreur envoi notification topic: {e}")
            return False


def get_notification_service() -> NotificationService:
    """Factory pour obtenir l'instance singleton du service."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
