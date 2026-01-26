"""Tests unitaires pour BcryptPasswordService."""

import pytest

from modules.auth.adapters.providers.bcrypt_password_service import BcryptPasswordService
from modules.auth.domain.value_objects import PasswordHash


class TestBcryptPasswordServiceInit:
    """Tests d'initialisation."""

    def test_default_rounds(self):
        """Test rounds par défaut."""
        service = BcryptPasswordService()
        assert service.rounds == 12

    def test_custom_rounds(self):
        """Test rounds personnalisés."""
        service = BcryptPasswordService(rounds=10)
        assert service.rounds == 10


class TestBcryptHash:
    """Tests de hash."""

    def test_hash_valid_password(self):
        """Test hash d'un mot de passe valide."""
        service = BcryptPasswordService(rounds=4)  # Rounds bas pour tests rapides
        result = service.hash("SecurePass123!")

        assert isinstance(result, PasswordHash)
        assert result.value.startswith("$2b$")  # Préfixe bcrypt

    def test_hash_returns_different_values(self):
        """Test que hash retourne des valeurs différentes (salt unique)."""
        service = BcryptPasswordService(rounds=4)
        hash1 = service.hash("SecurePass123!")
        hash2 = service.hash("SecurePass123!")

        assert hash1.value != hash2.value  # Salt différent

    def test_hash_weak_password_raises_error(self):
        """Test mot de passe faible lève une erreur."""
        service = BcryptPasswordService()

        with pytest.raises(ValueError) as exc:
            service.hash("weak")
        assert "au moins 8 caractères" in str(exc.value)

    def test_hash_password_no_uppercase_raises_error(self):
        """Test mot de passe sans majuscule lève une erreur."""
        service = BcryptPasswordService()

        with pytest.raises(ValueError):
            service.hash("lowercase123!")

    def test_hash_password_no_lowercase_raises_error(self):
        """Test mot de passe sans minuscule lève une erreur."""
        service = BcryptPasswordService()

        with pytest.raises(ValueError):
            service.hash("UPPERCASE123!")

    def test_hash_password_no_digit_raises_error(self):
        """Test mot de passe sans chiffre lève une erreur."""
        service = BcryptPasswordService()

        with pytest.raises(ValueError):
            service.hash("NoDigitsHere!")


class TestBcryptVerify:
    """Tests de verify."""

    def test_verify_correct_password(self):
        """Test vérification mot de passe correct."""
        service = BcryptPasswordService(rounds=4)
        password_hash = service.hash("SecurePass123!")

        assert service.verify("SecurePass123!", password_hash) is True

    def test_verify_incorrect_password(self):
        """Test vérification mot de passe incorrect."""
        service = BcryptPasswordService(rounds=4)
        password_hash = service.hash("SecurePass123!")

        assert service.verify("WrongPassword123!", password_hash) is False

    def test_verify_case_sensitive(self):
        """Test vérification sensible à la casse."""
        service = BcryptPasswordService(rounds=4)
        password_hash = service.hash("SecurePass123!")

        assert service.verify("securepass123!", password_hash) is False

    def test_verify_invalid_hash_returns_false(self):
        """Test hash invalide retourne False."""
        service = BcryptPasswordService()
        invalid_hash = PasswordHash("invalid_hash")

        assert service.verify("AnyPassword123!", invalid_hash) is False

    def test_verify_empty_password_returns_false(self):
        """Test mot de passe vide retourne False."""
        service = BcryptPasswordService(rounds=4)
        password_hash = service.hash("SecurePass123!")

        assert service.verify("", password_hash) is False


class TestBcryptRoundtrip:
    """Tests de cycle complet hash/verify."""

    def test_roundtrip_multiple_passwords(self):
        """Test plusieurs mots de passe."""
        service = BcryptPasswordService(rounds=4)

        passwords = [
            "SecurePass123!",
            "AnotherOne456@",
            "TestPassword789#",
            "Complex!Pass1234",
        ]

        for password in passwords:
            hashed = service.hash(password)
            assert service.verify(password, hashed) is True
            assert service.verify(password + "x", hashed) is False
