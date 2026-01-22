"""DTO pour la creation d'une affectation."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List


@dataclass(frozen=True)
class CreateAffectationDTO:
    """
    Data Transfer Object pour la creation d'une affectation.

    Utilise pour transferer les donnees de creation d'affectation
    entre la couche Adapters et la couche Application.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

    Attributes:
        utilisateur_id: ID de l'utilisateur a affecter.
        chantier_id: ID du chantier cible.
        date: Date de l'affectation.
        heure_debut: Heure de debut au format "HH:MM" (optionnel).
        heure_fin: Heure de fin au format "HH:MM" (optionnel).
        note: Commentaire prive pour l'utilisateur affecte (optionnel).
        type_affectation: Type "unique" ou "recurrente" (defaut: "unique").
        jours_recurrence: Jours de recurrence [0-6] pour Lundi-Dimanche (optionnel).
        date_fin_recurrence: Date de fin de la recurrence (optionnel).

    Example:
        >>> dto = CreateAffectationDTO(
        ...     utilisateur_id=1,
        ...     chantier_id=2,
        ...     date=date(2026, 1, 22),
        ...     heure_debut="08:00",
        ...     heure_fin="17:00",
        ... )
    """

    utilisateur_id: int
    chantier_id: int
    date: date
    heure_debut: Optional[str] = None  # Format "HH:MM"
    heure_fin: Optional[str] = None  # Format "HH:MM"
    note: Optional[str] = None
    type_affectation: str = "unique"  # "unique" ou "recurrente"
    jours_recurrence: Optional[List[int]] = None  # [0,1,2,3,4] = Lun-Ven
    date_fin_recurrence: Optional[date] = None  # Si recurrente

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.utilisateur_id <= 0:
            raise ValueError("L'ID utilisateur doit etre positif")

        if self.chantier_id <= 0:
            raise ValueError("L'ID chantier doit etre positif")

        if self.type_affectation not in ("unique", "recurrente"):
            raise ValueError(
                f"Type d'affectation invalide: {self.type_affectation}. "
                "Valeurs valides: 'unique', 'recurrente'"
            )

        # Validation coherence type/recurrence
        if self.type_affectation == "recurrente":
            if not self.jours_recurrence or len(self.jours_recurrence) == 0:
                raise ValueError(
                    "Une affectation recurrente doit specifier les jours de recurrence"
                )
            if not self.date_fin_recurrence:
                raise ValueError(
                    "Une affectation recurrente doit specifier une date de fin"
                )
            if self.date_fin_recurrence <= self.date:
                raise ValueError(
                    "La date de fin de recurrence doit etre posterieure a la date de debut"
                )

        # Validation des jours de recurrence (0-6)
        if self.jours_recurrence:
            for jour in self.jours_recurrence:
                if not isinstance(jour, int) or jour < 0 or jour > 6:
                    raise ValueError(
                        f"Jour de recurrence invalide: {jour}. "
                        "Valeurs valides: 0 (Lundi) a 6 (Dimanche)"
                    )

        # Validation format heure
        if self.heure_debut and not self._validate_heure_format(self.heure_debut):
            raise ValueError(
                f"Format d'heure de debut invalide: {self.heure_debut}. "
                "Format attendu: HH:MM"
            )

        if self.heure_fin and not self._validate_heure_format(self.heure_fin):
            raise ValueError(
                f"Format d'heure de fin invalide: {self.heure_fin}. "
                "Format attendu: HH:MM"
            )

    @staticmethod
    def _validate_heure_format(heure: str) -> bool:
        """
        Valide le format d'une heure HH:MM.

        Args:
            heure: La chaine a valider.

        Returns:
            True si le format est valide.
        """
        if not heure or not isinstance(heure, str):
            return False

        parts = heure.strip().split(":")
        if len(parts) != 2:
            return False

        try:
            h, m = int(parts[0]), int(parts[1])
            return 0 <= h <= 23 and 0 <= m <= 59
        except ValueError:
            return False
