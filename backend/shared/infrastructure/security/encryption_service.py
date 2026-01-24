"""Service de chiffrement AES-256 pour les donnees sensibles (RGPD Art. 32).

Ce module fournit:
- EncryptionService: Service de chiffrement/dechiffrement AES-256-GCM
- EncryptedString: Type SQLAlchemy pour champs chiffres automatiquement
"""

import base64
import hashlib
import os
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from sqlalchemy import TypeDecorator, String


class EncryptionService:
    """
    Service de chiffrement AES-256-GCM.

    Utilise AES-256 en mode GCM (Galois/Counter Mode) qui fournit:
    - Confidentialite (chiffrement)
    - Integrite (authentification)
    - Nonce unique par chiffrement

    Conforme RGPD Art. 32 - Mesures techniques appropriees.
    """

    # Taille du nonce en bytes (96 bits recommandes pour GCM)
    NONCE_SIZE = 12
    # Taille du tag d'authentification en bytes
    TAG_SIZE = 16

    def __init__(self, key: str):
        """
        Initialise le service avec une cle de chiffrement.

        Args:
            key: Cle de chiffrement (sera hashee en 256 bits).
        """
        # Derive une cle de 256 bits a partir de la cle fournie
        self._key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, plaintext: str) -> str:
        """
        Chiffre une chaine de caracteres.

        Args:
            plaintext: Texte en clair a chiffrer.

        Returns:
            Texte chiffre encode en base64 (nonce + ciphertext + tag).
        """
        if not plaintext:
            return ""

        # Genere un nonce unique
        nonce = os.urandom(self.NONCE_SIZE)

        # Cree le cipher AES-256-GCM
        cipher = Cipher(
            algorithms.AES(self._key),
            modes.GCM(nonce),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()

        # Chiffre les donnees
        ciphertext = encryptor.update(plaintext.encode("utf-8")) + encryptor.finalize()

        # Combine nonce + ciphertext + tag et encode en base64
        encrypted = nonce + ciphertext + encryptor.tag
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted: str) -> str:
        """
        Dechiffre une chaine de caracteres.

        Args:
            encrypted: Texte chiffre encode en base64.

        Returns:
            Texte en clair.

        Raises:
            ValueError: Si le dechiffrement echoue (donnees corrompues ou cle invalide).
        """
        if not encrypted:
            return ""

        try:
            # Decode le base64
            data = base64.b64decode(encrypted.encode("utf-8"))

            # Extrait nonce, ciphertext et tag
            nonce = data[: self.NONCE_SIZE]
            tag = data[-self.TAG_SIZE :]
            ciphertext = data[self.NONCE_SIZE : -self.TAG_SIZE]

            # Cree le cipher pour dechiffrement
            cipher = Cipher(
                algorithms.AES(self._key),
                modes.GCM(nonce, tag),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()

            # Dechiffre
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext.decode("utf-8")

        except Exception as e:
            raise ValueError(f"Echec du dechiffrement: {e}")


# Instance globale du service (initialisee au chargement)
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Retourne l'instance globale du service de chiffrement.

    Returns:
        Instance du service de chiffrement.
    """
    global _encryption_service
    if _encryption_service is None:
        from shared.infrastructure.config import settings

        _encryption_service = EncryptionService(settings.ENCRYPTION_KEY)
    return _encryption_service


class EncryptedString(TypeDecorator):
    """
    Type SQLAlchemy pour champs chiffres automatiquement.

    Chiffre automatiquement les donnees avant stockage
    et les dechiffre a la lecture.

    Usage:
        class User(Base):
            telephone = Column(EncryptedString(20), nullable=True)
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 500, **kwargs):
        """
        Args:
            length: Longueur maximale du champ chiffre.
                   Note: Le chiffrement augmente la taille (~1.5x).
        """
        # Augmente la taille pour accommoder le chiffrement
        super().__init__(length=length * 2, **kwargs)

    def process_bind_param(self, value, dialect) -> Optional[str]:
        """Chiffre la valeur avant stockage."""
        if value is None:
            return None
        service = get_encryption_service()
        return service.encrypt(str(value))

    def process_result_value(self, value, dialect) -> Optional[str]:
        """Dechiffre la valeur a la lecture."""
        if value is None:
            return None
        try:
            service = get_encryption_service()
            return service.decrypt(value)
        except ValueError:
            # Donnees non chiffrees (migration) - retourne tel quel
            return value
