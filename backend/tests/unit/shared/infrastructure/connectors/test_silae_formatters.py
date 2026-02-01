"""Tests unitaires pour les formatters Silae."""

import pytest

from shared.infrastructure.connectors.silae.formatters import aggregate_pointages_to_hours


class TestAggregatePointagesToHours:
    """Tests pour la fonction d'agrégation des pointages."""

    def test_aggregate_single_pointage(self):
        """Test l'agrégation d'un seul pointage."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal",
                "chantier_code": "CHT001"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        assert len(result) == 1
        assert result[0]["date"] == "2026-01-15"
        assert result[0]["type"] == "normal"
        assert result[0]["quantite"] == 9.0
        assert result[0]["chantier_code"] == "CHT001"

    def test_aggregate_multiple_pointages_same_day(self):
        """Test l'agrégation de plusieurs pointages le même jour."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "12:00",
                "type": "normal",
                "chantier_code": "CHT001"
            },
            {
                "date": "2026-01-15",
                "heure_debut": "13:00",
                "heure_fin": "17:00",
                "type": "normal",
                "chantier_code": "CHT001"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        assert len(result) == 1
        assert result[0]["date"] == "2026-01-15"
        assert result[0]["type"] == "normal"
        assert result[0]["quantite"] == 8.0  # 4h + 4h
        assert result[0]["chantier_code"] == "CHT001"

    def test_aggregate_different_days(self):
        """Test l'agrégation de pointages sur différents jours."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal"
            },
            {
                "date": "2026-01-16",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        assert len(result) == 2
        dates = [h["date"] for h in result]
        assert "2026-01-15" in dates
        assert "2026-01-16" in dates

    def test_aggregate_different_types(self):
        """Test l'agrégation de différents types d'heures."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal"
            },
            {
                "date": "2026-01-15",
                "heure_debut": "18:00",
                "heure_fin": "20:00",
                "type": "supplementaire"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        assert len(result) == 2
        types = [h["type"] for h in result]
        assert "normal" in types
        assert "supplementaire" in types

        # Vérifier les quantités
        for heure in result:
            if heure["type"] == "normal":
                assert heure["quantite"] == 9.0
            elif heure["type"] == "supplementaire":
                assert heure["quantite"] == 2.0

    def test_aggregate_different_chantiers(self):
        """Test l'agrégation de pointages sur différents chantiers."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "12:00",
                "type": "normal",
                "chantier_code": "CHT001"
            },
            {
                "date": "2026-01-15",
                "heure_debut": "13:00",
                "heure_fin": "17:00",
                "type": "normal",
                "chantier_code": "CHT002"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        # Doit créer 2 lignes car chantiers différents
        assert len(result) == 2

        chantiers = [h.get("chantier_code") for h in result]
        assert "CHT001" in chantiers
        assert "CHT002" in chantiers

        for heure in result:
            assert heure["quantite"] == 4.0

    def test_aggregate_without_chantier(self):
        """Test l'agrégation sans code chantier."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        assert len(result) == 1
        assert "chantier_code" not in result[0]

    def test_aggregate_invalid_pointage_missing_fields(self):
        """Test l'agrégation avec des pointages invalides (champs manquants)."""
        pointages = [
            {
                "date": "2026-01-15",
                # heure_debut et heure_fin manquants
                "type": "normal"
            },
            {
                "date": "2026-01-16",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        # Le premier pointage est ignoré, seul le second est traité
        assert len(result) == 1
        assert result[0]["date"] == "2026-01-16"

    def test_aggregate_invalid_time_format(self):
        """Test l'agrégation avec format d'heure invalide."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "invalid",
                "heure_fin": "17:00",
                "type": "normal"
            },
            {
                "date": "2026-01-16",
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "type": "normal"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        # Le premier pointage est ignoré, seul le second est traité
        assert len(result) == 1
        assert result[0]["date"] == "2026-01-16"

    def test_aggregate_complex_scenario(self):
        """Test un scénario complexe d'agrégation."""
        pointages = [
            # Jour 1 - Chantier A - matin
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "12:00",
                "type": "normal",
                "chantier_code": "CHT001"
            },
            # Jour 1 - Chantier A - après-midi
            {
                "date": "2026-01-15",
                "heure_debut": "13:00",
                "heure_fin": "17:00",
                "type": "normal",
                "chantier_code": "CHT001"
            },
            # Jour 1 - Chantier B - heures sup
            {
                "date": "2026-01-15",
                "heure_debut": "18:00",
                "heure_fin": "20:00",
                "type": "supplementaire",
                "chantier_code": "CHT002"
            },
            # Jour 2 - Chantier A
            {
                "date": "2026-01-16",
                "heure_debut": "08:00",
                "heure_fin": "16:00",
                "type": "normal",
                "chantier_code": "CHT001"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        # Doit créer 3 lignes:
        # 1. 2026-01-15, normal, CHT001 (8h)
        # 2. 2026-01-15, supplementaire, CHT002 (2h)
        # 3. 2026-01-16, normal, CHT001 (8h)
        assert len(result) == 3

        # Vérifier l'agrégation du jour 1, chantier A, normal
        jour1_cht1_normal = [
            h for h in result
            if h["date"] == "2026-01-15"
            and h["type"] == "normal"
            and h.get("chantier_code") == "CHT001"
        ]
        assert len(jour1_cht1_normal) == 1
        assert jour1_cht1_normal[0]["quantite"] == 8.0

    def test_aggregate_empty_list(self):
        """Test l'agrégation d'une liste vide."""
        result = aggregate_pointages_to_hours([])

        assert result == []

    def test_aggregate_rounding(self):
        """Test que les heures sont arrondies à 2 décimales."""
        pointages = [
            {
                "date": "2026-01-15",
                "heure_debut": "08:00",
                "heure_fin": "08:20",  # 20 minutes = 0.333... heures
                "type": "normal"
            }
        ]

        result = aggregate_pointages_to_hours(pointages)

        assert len(result) == 1
        assert result[0]["quantite"] == 0.33  # Arrondi à 2 décimales
