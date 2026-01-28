"""Tests unitaires pour le client Hub Chantier."""

import pytest
from hub_chantier import HubChantierClient, AuthenticationError


def test_client_init_valid_key():
    """Test initialisation avec clé valide."""
    client = HubChantierClient(api_key="hbc_test_key123")
    assert client.api_key == "hbc_test_key123"
    assert client.base_url == "https://api.hub-chantier.fr"
    assert client.timeout == 30


def test_client_init_invalid_key_format():
    """Test initialisation avec format de clé invalide."""
    with pytest.raises(ValueError, match="Invalid API key format"):
        HubChantierClient(api_key="invalid_key")


def test_client_init_empty_key():
    """Test initialisation avec clé vide."""
    with pytest.raises(ValueError, match="api_key is required"):
        HubChantierClient(api_key="")


def test_client_custom_base_url():
    """Test initialisation avec URL custom."""
    client = HubChantierClient(
        api_key="hbc_test_key", base_url="https://sandbox.hub-chantier.fr"
    )
    assert client.base_url == "https://sandbox.hub-chantier.fr"


def test_client_custom_timeout():
    """Test initialisation avec timeout custom."""
    client = HubChantierClient(api_key="hbc_test_key", timeout=60)
    assert client.timeout == 60


def test_client_resources_initialized():
    """Test que toutes les ressources sont initialisées."""
    client = HubChantierClient(api_key="hbc_test_key")
    assert client.chantiers is not None
    assert client.affectations is not None
    assert client.heures is not None
    assert client.documents is not None
    assert client.webhooks is not None
