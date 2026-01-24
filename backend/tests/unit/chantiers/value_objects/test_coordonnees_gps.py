"""Tests unitaires pour CoordonneesGPS Value Object."""

import pytest

from modules.chantiers.domain.value_objects import CoordonneesGPS


class TestCoordonneesGPS:
    """Tests pour le Value Object CoordonneesGPS (CHT-04, CHT-08, CHT-09)."""

    # ==========================================================================
    # Tests de création valide
    # ==========================================================================

    def test_create_valid_coordinates_lyon(self):
        """Test: création avec coordonnées Lyon valides."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        assert coords.latitude == 45.764043
        assert coords.longitude == 4.835659

    def test_create_valid_coordinates_paris(self):
        """Test: création avec coordonnées Paris."""
        coords = CoordonneesGPS(latitude=48.856614, longitude=2.3522219)
        assert coords.latitude == 48.856614

    def test_create_valid_coordinates_equator(self):
        """Test: création avec latitude 0 (équateur)."""
        coords = CoordonneesGPS(latitude=0.0, longitude=0.0)
        assert coords.latitude == 0.0

    def test_create_valid_coordinates_limits(self):
        """Test: création avec valeurs limites."""
        coords = CoordonneesGPS(latitude=90.0, longitude=180.0)
        assert coords.latitude == 90.0
        assert coords.longitude == 180.0

    def test_create_valid_coordinates_negative_limits(self):
        """Test: création avec valeurs limites négatives."""
        coords = CoordonneesGPS(latitude=-90.0, longitude=-180.0)
        assert coords.latitude == -90.0
        assert coords.longitude == -180.0

    # ==========================================================================
    # Tests de création invalide
    # ==========================================================================

    def test_create_invalid_latitude_too_high(self):
        """Test: latitude > 90 lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CoordonneesGPS(latitude=91.0, longitude=0.0)
        assert "Latitude invalide" in str(exc_info.value)

    def test_create_invalid_latitude_too_low(self):
        """Test: latitude < -90 lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CoordonneesGPS(latitude=-91.0, longitude=0.0)
        assert "Latitude invalide" in str(exc_info.value)

    def test_create_invalid_longitude_too_high(self):
        """Test: longitude > 180 lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CoordonneesGPS(latitude=0.0, longitude=181.0)
        assert "Longitude invalide" in str(exc_info.value)

    def test_create_invalid_longitude_too_low(self):
        """Test: longitude < -180 lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CoordonneesGPS(latitude=0.0, longitude=-181.0)
        assert "Longitude invalide" in str(exc_info.value)

    # ==========================================================================
    # Tests des URLs de navigation (CHT-08)
    # ==========================================================================

    def test_google_maps_url(self):
        """Test: URL Google Maps correcte."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        url = coords.google_maps_url
        assert "google.com/maps" in url
        assert "45.764043" in url
        assert "4.835659" in url

    def test_waze_url(self):
        """Test: URL Waze correcte."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        url = coords.waze_url
        assert "waze.com" in url
        assert "45.764043" in url
        assert "navigate=yes" in url

    def test_apple_maps_url(self):
        """Test: URL Apple Maps correcte."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        url = coords.apple_maps_url
        assert "maps.apple.com" in url
        assert "45.764043" in url

    # ==========================================================================
    # Tests de sérialisation (CHT-09)
    # ==========================================================================

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        d = coords.to_dict()
        assert d["latitude"] == 45.764043
        assert d["longitude"] == 4.835659

    def test_from_dict(self):
        """Test: création depuis dictionnaire."""
        d = {"latitude": 45.764043, "longitude": 4.835659}
        coords = CoordonneesGPS.from_dict(d)
        assert coords.latitude == 45.764043
        assert coords.longitude == 4.835659

    def test_from_dict_missing_latitude_raises_error(self):
        """Test: dictionnaire sans latitude lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CoordonneesGPS.from_dict({"longitude": 4.835659})
        assert "latitude" in str(exc_info.value).lower()

    def test_from_dict_missing_longitude_raises_error(self):
        """Test: dictionnaire sans longitude lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            CoordonneesGPS.from_dict({"latitude": 45.764043})
        assert "longitude" in str(exc_info.value).lower()

    def test_from_string(self):
        """Test: création depuis chaîne 'lat,lon'."""
        coords = CoordonneesGPS.from_string("45.764043, 4.835659")
        assert coords.latitude == 45.764043
        assert coords.longitude == 4.835659

    def test_from_string_no_spaces(self):
        """Test: création depuis chaîne sans espaces."""
        coords = CoordonneesGPS.from_string("45.764043,4.835659")
        assert coords.latitude == 45.764043

    def test_from_string_invalid_format_raises_error(self):
        """Test: format invalide lève une erreur."""
        with pytest.raises(ValueError):
            CoordonneesGPS.from_string("invalid")

    def test_str_format(self):
        """Test: format string des coordonnées."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        s = str(coords)
        assert "45.764043" in s
        assert "4.835659" in s

    # ==========================================================================
    # Tests de calcul de distance
    # ==========================================================================

    def test_distance_to_same_point(self):
        """Test: distance vers le même point = 0."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        distance = coords.distance_to(coords)
        assert distance == 0.0

    def test_distance_lyon_to_paris(self):
        """Test: distance Lyon-Paris ~465 km."""
        lyon = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        paris = CoordonneesGPS(latitude=48.856614, longitude=2.3522219)
        distance = lyon.distance_to(paris)
        # La distance réelle est ~465 km, on accepte une marge
        assert 400 < distance < 500

    def test_distance_is_symmetric(self):
        """Test: la distance est symétrique (A->B = B->A)."""
        lyon = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        paris = CoordonneesGPS(latitude=48.856614, longitude=2.3522219)
        assert abs(lyon.distance_to(paris) - paris.distance_to(lyon)) < 0.01

    # ==========================================================================
    # Tests de vérification France
    # ==========================================================================

    def test_is_in_france_lyon(self):
        """Test: Lyon est en France."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        assert coords.is_in_france() is True

    def test_is_in_france_paris(self):
        """Test: Paris est en France."""
        coords = CoordonneesGPS(latitude=48.856614, longitude=2.3522219)
        assert coords.is_in_france() is True

    def test_is_in_france_london_not(self):
        """Test: Londres n'est pas en France."""
        coords = CoordonneesGPS(latitude=51.507351, longitude=-0.127758)
        assert coords.is_in_france() is False

    def test_is_in_france_new_york_not(self):
        """Test: New York n'est pas en France."""
        coords = CoordonneesGPS(latitude=40.712776, longitude=-74.005974)
        assert coords.is_in_france() is False

    # ==========================================================================
    # Tests d'immutabilité
    # ==========================================================================

    def test_immutability(self):
        """Test: les coordonnées sont immuables (frozen)."""
        coords = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        with pytest.raises(AttributeError):
            coords.latitude = 48.0

    def test_equality(self):
        """Test: deux coordonnées identiques sont égales."""
        coords1 = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        coords2 = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        assert coords1 == coords2

    def test_inequality(self):
        """Test: deux coordonnées différentes ne sont pas égales."""
        coords1 = CoordonneesGPS(latitude=45.764043, longitude=4.835659)
        coords2 = CoordonneesGPS(latitude=48.856614, longitude=2.3522219)
        assert coords1 != coords2
