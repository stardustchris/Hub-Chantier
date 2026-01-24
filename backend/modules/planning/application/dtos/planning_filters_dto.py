"""DTO pour les filtres de recherche du planning."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, List


@dataclass(frozen=True)
class PlanningFiltersDTO:
    """
    Data Transfer Object pour les filtres de recherche du planning.

    Permet de filtrer les affectations selon differents criteres.

    Selon CDC Section 5 - Planning Operationnel (PLN-03, PLN-10).

    Attributes:
        date_debut: Date de debut de la periode (incluse).
        date_fin: Date de fin de la periode (incluse).
        utilisateur_ids: Liste d'IDs utilisateurs a filtrer (optionnel).
        chantier_ids: Liste d'IDs chantiers a filtrer (optionnel).
        metiers: Liste de metiers a filtrer (optionnel).
        planifies_only: True pour afficher seulement les utilisateurs planifies.
        non_planifies_only: True pour afficher seulement les utilisateurs non planifies.

    Example:
        >>> filters = PlanningFiltersDTO(
        ...     date_debut=date(2026, 1, 20),
        ...     date_fin=date(2026, 1, 26),
        ...     utilisateur_ids=[1, 2, 3],
        ... )
    """

    date_debut: date
    date_fin: date
    utilisateur_ids: Optional[List[int]] = None
    chantier_ids: Optional[List[int]] = None
    metiers: Optional[List[str]] = None
    planifies_only: bool = False  # True = seulement planifies
    non_planifies_only: bool = False  # True = seulement non planifies

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.date_fin < self.date_debut:
            raise ValueError(
                f"La date de fin ({self.date_fin}) doit etre posterieure "
                f"ou egale a la date de debut ({self.date_debut})"
            )

        # Validation des IDs utilisateurs si fournis
        if self.utilisateur_ids:
            for uid in self.utilisateur_ids:
                if not isinstance(uid, int) or uid <= 0:
                    raise ValueError(f"ID utilisateur invalide: {uid}")

        # Validation des IDs chantiers si fournis
        if self.chantier_ids:
            for cid in self.chantier_ids:
                if not isinstance(cid, int) or cid <= 0:
                    raise ValueError(f"ID chantier invalide: {cid}")

        # planifies_only et non_planifies_only sont mutuellement exclusifs
        if self.planifies_only and self.non_planifies_only:
            raise ValueError(
                "Les filtres planifies_only et non_planifies_only sont mutuellement exclusifs"
            )

    @property
    def nb_jours(self) -> int:
        """
        Calcule le nombre de jours dans la periode.

        Returns:
            Le nombre de jours (inclus).
        """
        return (self.date_fin - self.date_debut).days + 1

    @property
    def has_utilisateur_filter(self) -> bool:
        """Indique si un filtre utilisateur est applique."""
        return self.utilisateur_ids is not None and len(self.utilisateur_ids) > 0

    @property
    def has_chantier_filter(self) -> bool:
        """Indique si un filtre chantier est applique."""
        return self.chantier_ids is not None and len(self.chantier_ids) > 0

    @property
    def has_metier_filter(self) -> bool:
        """Indique si un filtre metier est applique."""
        return self.metiers is not None and len(self.metiers) > 0

    @classmethod
    def for_week(cls, start_date: date) -> "PlanningFiltersDTO":
        """
        Cree un filtre pour une semaine complete (Lundi-Dimanche).

        Args:
            start_date: Date dans la semaine souhaitee.

        Returns:
            Filtre pour la semaine contenant la date.
        """
        from datetime import timedelta

        # Trouver le lundi de la semaine
        days_since_monday = start_date.weekday()
        monday = start_date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)

        return cls(date_debut=monday, date_fin=sunday)

    @classmethod
    def for_month(cls, year: int, month: int) -> "PlanningFiltersDTO":
        """
        Cree un filtre pour un mois complet.

        Args:
            year: L'annee.
            month: Le mois (1-12).

        Returns:
            Filtre pour le mois specifie.
        """
        import calendar

        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])

        return cls(date_debut=first_day, date_fin=last_day)

    @classmethod
    def for_day(cls, target_date: date) -> "PlanningFiltersDTO":
        """
        Cree un filtre pour une journee.

        Args:
            target_date: La date cible.

        Returns:
            Filtre pour la journee.
        """
        return cls(date_debut=target_date, date_fin=target_date)
