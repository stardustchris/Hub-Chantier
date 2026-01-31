"""Value Object PeriodePaie - Gestion du verrouillage mensuel des pointages."""

import calendar
from datetime import date, timedelta


class PeriodePaie:
    """
    Value Object pour gérer les périodes de paie et le verrouillage mensuel.

    Selon le workflow de validation (§ 4.4 Règle de verrouillage mensuel),
    un pointage reste modifiable jusqu'au vendredi précédant la dernière semaine
    du mois en cours.

    Exemple janvier 2026 :
    - Dernière semaine : Lun 26 → Dim 31
    - Vendredi précédant : Ven 23/01
    - Verrouillage : Samedi 24 janvier 00:00

    Règle métier critique pour éviter les modifications rétroactives
    après la clôture paie.
    """

    @staticmethod
    def is_locked(date_pointage: date, today: date = None) -> bool:
        """
        Vérifie si un pointage est verrouillé (période de paie fermée).

        Un pointage est verrouillé si la date du jour est postérieure
        au vendredi précédant la dernière semaine du mois du pointage.

        Args:
            date_pointage: Date du pointage à vérifier.
            today: Date de référence (défaut: date du jour).

        Returns:
            True si le pointage est verrouillé (non modifiable).
            False si le pointage est encore modifiable.

        Examples:
            >>> # Pointage du 5 janvier 2026, on est le 20 janvier
            >>> PeriodePaie.is_locked(date(2026, 1, 5), today=date(2026, 1, 20))
            False  # Pas encore verrouillé (verrouillage le 24/01)

            >>> # Pointage du 5 janvier 2026, on est le 25 janvier
            >>> PeriodePaie.is_locked(date(2026, 1, 5), today=date(2026, 1, 25))
            True  # Verrouillé (après le 23/01)

            >>> # Pointage du mois en cours ou futur
            >>> PeriodePaie.is_locked(date(2026, 2, 10), today=date(2026, 2, 5))
            False  # Jamais verrouillé si dans le mois en cours
        """
        # Utilise la date du jour si non fournie
        if today is None:
            today = date.today()

        # Si le pointage est dans le mois en cours ou un mois futur,
        # il n'est jamais verrouillé
        pointage_month_start = date_pointage.replace(day=1)
        today_month_start = today.replace(day=1)

        if pointage_month_start >= today_month_start:
            return False

        # Calculer la date de verrouillage pour le mois du pointage
        lockdown_date = PeriodePaie._calculate_lockdown_date(
            date_pointage.year, date_pointage.month
        )

        # Le pointage est verrouillé si today > date de verrouillage
        return today > lockdown_date

    @staticmethod
    def _calculate_lockdown_date(year: int, month: int) -> date:
        """
        Calcule la date de verrouillage pour un mois donné.

        La date de verrouillage est le vendredi précédant la dernière
        semaine du mois.

        Args:
            year: Année.
            month: Mois (1-12).

        Returns:
            Date de verrouillage (vendredi précédant la dernière semaine).

        Examples:
            >>> # Janvier 2026 : dernière semaine 26-31, vendredi précédent = 23/01
            >>> PeriodePaie._calculate_lockdown_date(2026, 1)
            date(2026, 1, 23)

            >>> # Février 2026 : dernière semaine 23-01/03, vendredi précédent = 20/02
            >>> PeriodePaie._calculate_lockdown_date(2026, 2)
            date(2026, 2, 20)
        """
        # Dernier jour du mois
        last_day_of_month = calendar.monthrange(year, month)[1]
        last_date = date(year, month, last_day_of_month)

        # Trouver le lundi de la dernière semaine du mois
        # On recule depuis la fin du mois jusqu'à trouver un lundi
        current_date = last_date
        while current_date.weekday() != 0:  # 0 = lundi
            current_date -= timedelta(days=1)

        # Le vendredi précédant est 3 jours avant ce lundi
        # (samedi -2, dimanche -1, lundi 0 → vendredi -3)
        lockdown_friday = current_date - timedelta(days=3)

        return lockdown_friday

    @staticmethod
    def get_lockdown_date(year: int, month: int) -> date:
        """
        Retourne la date de verrouillage pour un mois donné.

        Méthode publique pour obtenir la date de verrouillage
        (utile pour l'affichage dans l'UI).

        Args:
            year: Année.
            month: Mois (1-12).

        Returns:
            Date de verrouillage.
        """
        return PeriodePaie._calculate_lockdown_date(year, month)
