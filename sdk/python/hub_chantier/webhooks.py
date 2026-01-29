"""Helpers pour webhooks."""

import hmac
import hashlib
import json
from typing import Dict, Any


def verify_webhook_signature(
    payload: Dict[str, Any], signature: str, secret: str
) -> bool:
    """
    Vérifie la signature HMAC d'un webhook.

    Args:
        payload: Payload JSON reçu
        signature: Header X-Hub-Chantier-Signature (format: 'sha256=...')
        secret: Secret webhook (reçu à la création)

    Returns:
        True si signature valide

    Example:
        >>> from flask import request
        >>> payload = request.json
        >>> signature = request.headers.get('X-Hub-Chantier-Signature')
        >>>
        >>> if verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        >>>     # Traiter webhook
        >>>     pass
        >>> else:
        >>>     # Rejeter (signature invalide)
        >>>     return 'Invalid signature', 401
    """
    if not signature or not signature.startswith("sha256="):
        return False

    expected_signature = signature[7:]  # Retirer "sha256="

    # Recalculer signature
    computed_signature = hmac.new(
        secret.encode(), json.dumps(payload, separators=(",", ":")).encode(), hashlib.sha256
    ).hexdigest()

    # Comparaison sécurisée (timing-attack resistant)
    return hmac.compare_digest(expected_signature, computed_signature)
