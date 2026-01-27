"""
Rate limiter avancé avec backoff exponentiel et limites par endpoint.

Amélioration L-01 : Rate limiting progressif pour protection renforcée
contre les attaques par force brute sophistiquées.
"""

from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import threading

from slowapi import Limiter
from slowapi.util import get_remote_address


class ExponentialBackoffLimiter:
    """
    Rate limiter avec backoff exponentiel.

    Augmente progressivement les délais de blocage pour les IPs
    qui dépassent répétitivement les limites.

    Attributes:
        violations: Compteur de violations par IP {ip: count}.
        last_violation: Timestamp dernière violation {ip: datetime}.
        lock: Thread lock pour accès concurrent.
    """

    def __init__(self):
        """Initialise le limiter avec backoff."""
        self.violations: Dict[str, int] = defaultdict(int)
        self.last_violation: Dict[str, datetime] = {}
        self.lock = threading.Lock()

    def check_and_increment(self, ip: str) -> Tuple[bool, int]:
        """
        Vérifie si l'IP est bloquée et incrémente le compteur.

        Args:
            ip: Adresse IP à vérifier.

        Returns:
            Tuple (is_blocked, retry_after_seconds).
        """
        with self.lock:
            now = datetime.now()

            # Réinitialiser après 1 heure sans violation
            if ip in self.last_violation:
                if now - self.last_violation[ip] > timedelta(hours=1):
                    self.violations[ip] = 0
                    del self.last_violation[ip]

            # Calculer le délai de backoff exponentiel
            # violations: 1 → 30s, 2 → 60s, 3 → 120s, 4 → 240s, 5+ → 300s
            violation_count = self.violations[ip]

            if violation_count == 0:
                return (False, 0)

            # Backoff exponentiel: min(30 * 2^(n-1), 300)
            retry_after = min(30 * (2 ** (violation_count - 1)), 300)

            # Vérifier si toujours bloqué
            if ip in self.last_violation:
                elapsed = (now - self.last_violation[ip]).total_seconds()
                if elapsed < retry_after:
                    # Toujours bloqué
                    remaining = int(retry_after - elapsed)
                    return (True, remaining)

            # Pas bloqué ou période expirée
            return (False, 0)

    def record_violation(self, ip: str) -> int:
        """
        Enregistre une violation et retourne le délai de retry.

        Args:
            ip: Adresse IP violant la limite.

        Returns:
            Délai en secondes avant prochain essai.
        """
        with self.lock:
            self.violations[ip] += 1
            self.last_violation[ip] = datetime.now()

            violation_count = self.violations[ip]
            retry_after = min(30 * (2 ** (violation_count - 1)), 300)

            return retry_after

    def reset(self, ip: str) -> None:
        """
        Réinitialise les violations pour une IP (après succès).

        Args:
            ip: Adresse IP à réinitialiser.
        """
        with self.lock:
            if ip in self.violations:
                del self.violations[ip]
            if ip in self.last_violation:
                del self.last_violation[ip]


# Instance globale du backoff limiter
backoff_limiter = ExponentialBackoffLimiter()

# Limiter slowapi standard (pour compatibilité)
limiter = Limiter(key_func=get_remote_address)

# Limites par endpoint (requêtes/période)
ENDPOINT_LIMITS = {
    # Authentification (plus restrictif)
    "/api/auth/login": "5/minute",
    "/api/auth/register": "3/hour",
    "/api/auth/refresh": "10/minute",

    # Upload (protection resources)
    "/api/upload": "10/minute",
    "/api/documents/upload": "10/minute",

    # Recherche (protection CPU)
    "/api/search": "30/minute",
    "/api/chantiers/search": "30/minute",

    # Création (protection spam)
    "/api/posts/create": "20/minute",
    "/api/signalements/create": "10/minute",
    "/api/interventions/create": "15/minute",

    # Lecture (plus permissif)
    "/api/dashboard/feed": "100/minute",
    "/api/planning": "60/minute",
    "/api/chantiers": "60/minute",

    # Export (protection resources)
    "/api/export/feuilles-heures": "5/minute",
    "/api/export/planning": "5/minute",
    "/api/taches/export-pdf": "3/minute",
    "/api/formulaires/export-pdf": "3/minute",
}


def get_limit_for_endpoint(path: str) -> str:
    """
    Retourne la limite pour un endpoint donné.

    Args:
        path: Chemin de l'endpoint.

    Returns:
        Limite au format slowapi (ex: "5/minute").
    """
    # Chercher correspondance exacte
    if path in ENDPOINT_LIMITS:
        return ENDPOINT_LIMITS[path]

    # Chercher correspondance par préfixe
    for endpoint, limit in ENDPOINT_LIMITS.items():
        if path.startswith(endpoint):
            return limit

    # Limite par défaut (généreuse)
    return "120/minute"
