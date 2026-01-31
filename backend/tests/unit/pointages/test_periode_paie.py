"""Tests unitaires pour PeriodePaie (Value Object)."""

import pytest
from datetime import date
from freezegun import freeze_time

from modules.pointages.domain.value_objects import PeriodePaie


class TestPeriodePaie:
    """Tests pour le value object PeriodePaie et le verrouillage mensuel."""

    def test_is_locked_retourne_false_pour_mois_en_cours(self):
        """Test: Pointage du mois en cours jamais verrouillé.

        Selon la règle métier § 4.4, un pointage du mois en cours
        reste toujours modifiable même après la date de verrouillage.
        """
        # Arrange: On est le 25 janvier 2026
        with freeze_time("2026-01-25"):
            date_pointage = date(2026, 1, 10)  # Pointage du mois en cours
            today = date(2026, 1, 25)

            # Act
            result = PeriodePaie.is_locked(date_pointage, today)

            # Assert
            assert result is False, "Pointage du mois en cours ne doit jamais être verrouillé"

    def test_is_locked_retourne_true_apres_verrouillage(self):
        """Test: Après vendredi de verrouillage, pointage verrouillé.

        Janvier 2026:
        - Dernière semaine: Lun 26 → Dim 31
        - Vendredi précédant: Ven 23/01
        - Verrouillage effectif: Sam 24 janvier 00:00

        Pour qu'un pointage de janvier soit verrouillé, il faut être
        dans un mois suivant (février ou après).
        """
        # Arrange: Pointage de janvier, on est en février
        date_pointage = date(2026, 1, 5)  # Pointage de janvier
        today = date(2026, 2, 5)  # Février (mois suivant)

        # Act
        result = PeriodePaie.is_locked(date_pointage, today)

        # Assert
        assert result is True, "Pointage après verrouillage doit être verrouillé"

    def test_is_locked_retourne_false_avant_verrouillage(self):
        """Test: Avant vendredi de verrouillage, pointage modifiable."""
        # Arrange: On est le 20 janvier (avant le vendredi 23)
        date_pointage = date(2026, 1, 5)
        today = date(2026, 1, 20)

        # Act
        result = PeriodePaie.is_locked(date_pointage, today)

        # Assert
        assert result is False, "Pointage avant verrouillage doit être modifiable"

    def test_is_locked_le_jour_du_verrouillage(self):
        """Test: Le vendredi de verrouillage, le pointage est encore modifiable.

        La période se verrouille le samedi 00:00, donc le vendredi
        on peut encore modifier.
        """
        # Arrange: On est le vendredi 23 janvier (jour de verrouillage)
        date_pointage = date(2026, 1, 5)
        today = date(2026, 1, 23)  # Vendredi 23 janvier

        # Act
        result = PeriodePaie.is_locked(date_pointage, today)

        # Assert
        assert result is False, "Le jour du verrouillage, encore modifiable"

    def test_is_locked_retourne_false_pour_mois_futur(self):
        """Test: Pointage d'un mois futur jamais verrouillé."""
        # Arrange: On est le 20 janvier, pointage en février
        date_pointage = date(2026, 2, 10)
        today = date(2026, 1, 20)

        # Act
        result = PeriodePaie.is_locked(date_pointage, today)

        # Assert
        assert result is False, "Pointage futur ne peut pas être verrouillé"

    def test_calculate_lockdown_date_janvier_2026(self):
        """Test: Calcul exact de la date de verrouillage pour janvier 2026.

        Janvier 2026:
        - Dernier jour: 31 (vendredi)
        - Dernière semaine: Lun 26 → Ven 31
        - Vendredi précédent la dernière semaine: Ven 23 janvier
        """
        # Act
        lockdown_date = PeriodePaie._calculate_lockdown_date(2026, 1)

        # Assert
        assert lockdown_date == date(2026, 1, 23), "Verrouillage janvier 2026 = 23/01"
        assert lockdown_date.weekday() == 4, "Doit être un vendredi (4)"

    def test_calculate_lockdown_date_fevrier_2026(self):
        """Test: Calcul de la date de verrouillage pour février 2026.

        Février 2026:
        - Dernier jour: 28 (samedi)
        - Dernière semaine: Lun 23 → Sam 28
        - Vendredi précédent: Ven 20 février
        """
        # Act
        lockdown_date = PeriodePaie._calculate_lockdown_date(2026, 2)

        # Assert
        assert lockdown_date == date(2026, 2, 20), "Verrouillage février 2026 = 20/02"
        assert lockdown_date.weekday() == 4, "Doit être un vendredi"

    def test_calculate_lockdown_date_mars_2026(self):
        """Test: Calcul de la date de verrouillage pour mars 2026.

        Mars 2026:
        - Dernier jour: 31 (mardi)
        - Dernière semaine: Lun 30 → Mar 31
        - Vendredi précédent: Ven 27 mars
        """
        # Act
        lockdown_date = PeriodePaie._calculate_lockdown_date(2026, 3)

        # Assert
        assert lockdown_date == date(2026, 3, 27), "Verrouillage mars 2026 = 27/03"
        assert lockdown_date.weekday() == 4, "Doit être un vendredi"

    def test_calculate_lockdown_date_decembre_2026(self):
        """Test: Calcul pour décembre 2026 (mois se terminant jeudi)."""
        # Act
        lockdown_date = PeriodePaie._calculate_lockdown_date(2026, 12)

        # Assert
        # Décembre 2026 finit le 31 (jeudi)
        # Dernière semaine: Lun 28 → Jeu 31
        # Vendredi précédent: Ven 25 décembre
        assert lockdown_date == date(2026, 12, 25), "Verrouillage décembre 2026 = 25/12"
        assert lockdown_date.weekday() == 4, "Doit être un vendredi"

    def test_get_lockdown_date(self):
        """Test: Méthode publique retourne bonne date.

        Cette méthode est exposée pour l'UI afin d'afficher
        la date limite de modification.
        """
        # Act
        lockdown_date = PeriodePaie.get_lockdown_date(2026, 1)

        # Assert
        assert lockdown_date == date(2026, 1, 23)
        assert isinstance(lockdown_date, date)

    def test_is_locked_utilise_date_du_jour_par_defaut(self):
        """Test: Si today non fourni, utilise date.today()."""
        # Arrange: On freeze le temps au 5 février (mois suivant)
        with freeze_time("2026-02-05"):
            date_pointage = date(2026, 1, 5)  # Pointage de janvier

            # Act: appel sans today
            result = PeriodePaie.is_locked(date_pointage)

            # Assert: doit utiliser le 5 février comme today
            assert result is True, "Doit utiliser date.today() si today non fourni"

    def test_is_locked_pointage_ancien_plusieurs_mois(self):
        """Test: Pointage très ancien (plusieurs mois) est verrouillé."""
        # Arrange: On est en mars, pointage de janvier
        date_pointage = date(2026, 1, 10)
        today = date(2026, 3, 15)

        # Act
        result = PeriodePaie.is_locked(date_pointage, today)

        # Assert
        assert result is True, "Pointage ancien de plusieurs mois doit être verrouillé"

    def test_is_locked_premier_jour_mois_suivant(self):
        """Test: Le 1er jour du mois suivant, pointage du mois précédent verrouillé."""
        # Arrange: On est le 1er février, pointage du 5 janvier
        date_pointage = date(2026, 1, 5)
        today = date(2026, 2, 1)

        # Act
        result = PeriodePaie.is_locked(date_pointage, today)

        # Assert
        # Janvier verrouillé le 23/01, on est le 01/02 → verrouillé
        assert result is True, "1er jour mois suivant, mois précédent verrouillé"

    def test_is_locked_edge_case_meme_jour_meme_mois(self):
        """Test: Pointage du jour même, jamais verrouillé."""
        # Arrange: Pointage et today = même date
        date_pointage = date(2026, 1, 20)
        today = date(2026, 1, 20)

        # Act
        result = PeriodePaie.is_locked(date_pointage, today)

        # Assert
        assert result is False, "Pointage du jour même ne peut être verrouillé"

    def test_calculate_lockdown_date_fevrier_annee_bissextile(self):
        """Test: Calcul correct pour février en année bissextile.

        2024 est bissextile (29 jours).
        """
        # Act
        lockdown_date = PeriodePaie._calculate_lockdown_date(2024, 2)

        # Assert
        # Février 2024: 29 jours (jeudi)
        # Dernière semaine: Lun 26 → Jeu 29
        # Vendredi précédent: Ven 23 février
        assert lockdown_date == date(2024, 2, 23), "Année bissextile correctement gérée"
        assert lockdown_date.weekday() == 4

    def test_calculate_lockdown_date_tous_les_mois_2026(self):
        """Test: Vérification que toutes les dates calculées sont des vendredis."""
        # Act & Assert
        for month in range(1, 13):
            lockdown_date = PeriodePaie._calculate_lockdown_date(2026, month)
            assert lockdown_date.weekday() == 4, (
                f"Mois {month}: date {lockdown_date} doit être un vendredi"
            )
            assert lockdown_date.month == month, (
                f"Mois {month}: date {lockdown_date} doit être dans le même mois"
            )
