"""Rate limiter partagé pour l'application.

Configuration slowapi pour protection contre brute force.
Utilisé principalement sur /login (5 req/minute par IP).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Instance partagée du rate limiter
limiter = Limiter(key_func=get_remote_address)
