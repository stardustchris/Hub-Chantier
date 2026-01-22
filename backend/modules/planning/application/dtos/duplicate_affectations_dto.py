"""DTO pour la duplication d'affectations."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DuplicateAffectationsDTO:
    """
    Data Transfer Object pour la duplication d'affectations.

    Permet de copier les affectations d'un utilisateur d'une periode source
    vers une periode cible (ex: dupliquer la semaine precedente).

    Selon CDC Section 5 - Planning Operationnel (PLN-13, PLN-14).

    Attributes:
        utilisateur_id: ID de l'utilisateur dont dupliquer les affectations.
        source_date_debut: Date de debut de la periode source.
        source_date_fin: Date de fin de la periode source.
        target_date_debut: Date de debut de la periode cible.

    Example:
        >>> dto = DuplicateAffectationsDTO(
        ...     utilisateur_id=1,
        ...     source_date_debut=date(2026, 1, 13),  # Semaine precedente
        ...     source_date_fin=date(2026, 1, 17),
        ...     target_date_debut=date(2026, 1, 20),  # Cette semaine
        ... )
    """

    utilisateur_id: int
    source_date_debut: date
    source_date_fin: date
    target_date_debut: date  # Date ou dupliquer (meme structure de semaine)

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.utilisateur_id <= 0:
            raise ValueError("L'ID utilisateur doit etre positif")

        if self.source_date_fin < self.source_date_debut:
            raise ValueError(
                f"La date de fin source ({self.source_date_fin}) doit etre "
                f"posterieure ou egale a la date de debut ({self.source_date_debut})"
            )

        if self.target_date_debut <= self.source_date_fin:
            raise ValueError(
                f"La date cible ({self.target_date_debut}) doit etre "
                f"posterieure a la date de fin source ({self.source_date_fin})"
            )

    @property
    def source_nb_jours(self) -> int:
        """
        Calcule le nombre de jours dans la periode source.

        Returns:
            Le nombre de jours (inclus).
        """
        return (self.source_date_fin - self.source_date_debut).days + 1

    @property
    def days_offset(self) -> int:
        """
        Calcule le decalage en jours entre source et cible.

        Returns:
            Le nombre de jours de decalage.
        """
        return (self.target_date_debut - self.source_date_debut).days

    @classmethod
    def duplicate_week(
        cls,
        utilisateur_id: int,
        source_week_start: date,
        target_week_start: date,
    ) -> "DuplicateAffectationsDTO":
        """
        Cree un DTO pour dupliquer une semaine complete.

        Args:
            utilisateur_id: ID de l'utilisateur.
            source_week_start: Lundi de la semaine source.
            target_week_start: Lundi de la semaine cible.

        Returns:
            Le DTO configure pour la duplication de semaine.
        """
        from datetime import timedelta

        return cls(
            utilisateur_id=utilisateur_id,
            source_date_debut=source_week_start,
            source_date_fin=source_week_start + timedelta(days=4),  # Lun-Ven
            target_date_debut=target_week_start,
        )
