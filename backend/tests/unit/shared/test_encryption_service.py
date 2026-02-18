"""Tests unitaires pour EncryptionService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import base64

from shared.infrastructure.security.encryption_service import (
    EncryptionService,
    EncryptedString,
    get_encryption_service,
)


class TestEncryptionServiceInit:
    """Tests d'initialisation du service."""

    def test_init_with_key(self):
        """Test init avec une cle."""
        service = EncryptionService(key="my_secret_key")

        # La cle doit etre derivee en 256 bits (32 bytes)
        assert len(service._key) == 32

    def test_init_derives_key_consistently(self):
        """Test que la meme cle donne la meme derivation."""
        service1 = EncryptionService(key="test_key")
        service2 = EncryptionService(key="test_key")

        assert service1._key == service2._key

    def test_different_keys_give_different_derived_keys(self):
        """Test que des cles differentes donnent des derivations differentes."""
        service1 = EncryptionService(key="key1")
        service2 = EncryptionService(key="key2")

        assert service1._key != service2._key


class TestEncryptionServiceEncrypt:
    """Tests du chiffrement."""

    @pytest.fixture
    def service(self):
        return EncryptionService(key="test_encryption_key_123")

    def test_encrypt_returns_base64(self, service):
        """Test que encrypt retourne du base64 valide."""
        encrypted = service.encrypt("Hello World")

        # Doit etre decodable en base64
        decoded = base64.b64decode(encrypted)
        assert len(decoded) > 0

    def test_encrypt_empty_string(self, service):
        """Test chiffrement chaine vide."""
        encrypted = service.encrypt("")
        assert encrypted == ""

    def test_encrypt_produces_different_output_each_time(self, service):
        """Test que le chiffrement produit des sorties differentes (nonce unique)."""
        plaintext = "Same text"

        encrypted1 = service.encrypt(plaintext)
        encrypted2 = service.encrypt(plaintext)

        # Les deux chiffrements doivent etre differents (nonce different)
        assert encrypted1 != encrypted2

    def test_encrypt_unicode(self, service):
        """Test chiffrement avec caracteres unicode."""
        plaintext = "Héllo Wörld 你好 🎉"
        encrypted = service.encrypt(plaintext)

        assert encrypted != ""
        assert encrypted != plaintext

    def test_encrypt_long_text(self, service):
        """Test chiffrement texte long."""
        plaintext = "A" * 10000
        encrypted = service.encrypt(plaintext)

        assert len(encrypted) > len(plaintext)


class TestEncryptionServiceDecrypt:
    """Tests du dechiffrement."""

    @pytest.fixture
    def service(self):
        return EncryptionService(key="test_encryption_key_123")

    def test_decrypt_reverses_encrypt(self, service):
        """Test que decrypt inverse encrypt."""
        plaintext = "Secret message"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_decrypt_empty_string(self, service):
        """Test dechiffrement chaine vide."""
        decrypted = service.decrypt("")
        assert decrypted == ""

    def test_decrypt_unicode(self, service):
        """Test dechiffrement avec caracteres unicode."""
        plaintext = "Héllo Wörld 你好 🎉"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_decrypt_with_wrong_key_fails(self):
        """Test que le dechiffrement avec mauvaise cle echoue."""
        service1 = EncryptionService(key="correct_key")
        service2 = EncryptionService(key="wrong_key")

        encrypted = service1.encrypt("Secret")

        with pytest.raises(ValueError) as exc_info:
            service2.decrypt(encrypted)

        assert "Echec du dechiffrement" in str(exc_info.value)

    def test_decrypt_corrupted_data_fails(self, service):
        """Test que le dechiffrement de donnees corrompues echoue."""
        encrypted = service.encrypt("Secret")
        # Corrompre les donnees
        corrupted = encrypted[:-5] + "XXXXX"

        with pytest.raises(ValueError) as exc_info:
            service.decrypt(corrupted)

        assert "Echec du dechiffrement" in str(exc_info.value)

    def test_decrypt_invalid_base64_fails(self, service):
        """Test que le dechiffrement de base64 invalide echoue."""
        with pytest.raises(ValueError):
            service.decrypt("not_valid_base64!!!")


class TestEncryptDecryptRoundTrip:
    """Tests aller-retour chiffrement/dechiffrement."""

    @pytest.fixture
    def service(self):
        return EncryptionService(key="roundtrip_test_key")

    def test_roundtrip_various_lengths(self, service):
        """Test aller-retour avec differentes longueurs."""
        for length in [1, 10, 100, 1000, 5000]:
            plaintext = "X" * length
            encrypted = service.encrypt(plaintext)
            decrypted = service.decrypt(encrypted)
            assert decrypted == plaintext

    def test_roundtrip_special_characters(self, service):
        """Test aller-retour avec caracteres speciaux."""
        special_texts = [
            "Line1\nLine2\nLine3",
            "Tab\there",
            "Quote\"test",
            "Backslash\\test",
            "Null\x00char",
        ]

        for plaintext in special_texts:
            encrypted = service.encrypt(plaintext)
            decrypted = service.decrypt(encrypted)
            assert decrypted == plaintext


class TestGetEncryptionService:
    """Tests de la factory singleton."""

    def test_returns_service_instance(self):
        """Test que la factory retourne une instance."""
        service = get_encryption_service()
        assert isinstance(service, EncryptionService)

    def test_returns_singleton(self):
        """Test que la factory retourne un singleton."""
        service1 = get_encryption_service()
        service2 = get_encryption_service()

        assert service1 is service2


class TestEncryptedStringType:
    """Tests du type SQLAlchemy EncryptedString."""

    def test_init_quadruples_length(self):
        """Test que l'init quadruple la longueur pour le chiffrement AES-256 + base64."""
        es = EncryptedString(length=100)
        # AES-256 + base64 augmente la taille ~4x
        assert es.impl.length == 400

    def test_process_bind_param_encrypts(self):
        """Test que process_bind_param chiffre."""
        es = EncryptedString(length=100)

        with patch("shared.infrastructure.security.encryption_service.get_encryption_service") as mock_get:
            mock_service = Mock()
            mock_service.encrypt.return_value = "encrypted_value"
            mock_get.return_value = mock_service

            result = es.process_bind_param("plain_text", None)

            mock_service.encrypt.assert_called_once_with("plain_text")
            assert result == "encrypted_value"

    def test_process_bind_param_none_returns_none(self):
        """Test que None reste None."""
        es = EncryptedString(length=100)

        result = es.process_bind_param(None, None)

        assert result is None

    def test_process_result_value_decrypts(self):
        """Test que process_result_value dechiffre."""
        es = EncryptedString(length=100)

        with patch("shared.infrastructure.security.encryption_service.get_encryption_service") as mock_get:
            mock_service = Mock()
            mock_service.decrypt.return_value = "decrypted_value"
            mock_get.return_value = mock_service

            result = es.process_result_value("encrypted_value", None)

            mock_service.decrypt.assert_called_once_with("encrypted_value")
            assert result == "decrypted_value"

    def test_process_result_value_none_returns_none(self):
        """Test que None reste None au dechiffrement."""
        es = EncryptedString(length=100)

        result = es.process_result_value(None, None)

        assert result is None

    def test_process_result_value_handles_unencrypted_data(self):
        """Test que les donnees non chiffrees sont retournees telles quelles."""
        es = EncryptedString(length=100)

        with patch("shared.infrastructure.security.encryption_service.get_encryption_service") as mock_get:
            mock_service = Mock()
            mock_service.decrypt.side_effect = ValueError("Not encrypted")
            mock_get.return_value = mock_service

            result = es.process_result_value("plain_text", None)

            # Doit retourner la valeur originale si le dechiffrement echoue
            assert result == "plain_text"

    def test_cache_ok_is_true(self):
        """Test que cache_ok est True pour SQLAlchemy."""
        es = EncryptedString(length=100)
        assert es.cache_ok is True
