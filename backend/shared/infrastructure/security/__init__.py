"""Security infrastructure module.

Provides encryption services for RGPD compliance (Art. 32).
"""

from .encryption_service import EncryptionService, EncryptedString

__all__ = ["EncryptionService", "EncryptedString"]
