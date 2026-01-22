"""DTO pour la mise a jour d'une affectation."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UpdateAffectationDTO:
    """
    Data Transfer Object pour la mise a jour d'une affectation.

    Tous les champs sont optionnels - seuls ceux fournis seront mis a jour.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

    Attributes:
        heure_debut: Nouvelle heure de debut au format "HH:MM" (optionnel).
        heure_fin: Nouvelle heure de fin au format "HH:MM" (optionnel).
        note: Nouveau commentaire prive (optionnel).
        chantier_id: Nouvel ID de chantier (optionnel).

    Example:
        >>> dto = UpdateAffectationDTO(
        ...     heure_debut="09:00",
        ...     heure_fin="18:00",
        ... )
    """

    heure_debut: Optional[str] = None  # Format "HH:MM"
    heure_fin: Optional[str] = None  # Format "HH:MM"
    note: Optional[str] = None
    chantier_id: Optional[int] = None

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        # Validation du chantier_id si fourni
        if self.chantier_id is not None and self.chantier_id <= 0:
            raise ValueError("L'ID chantier doit etre positif")

        # Validation format heure
        if self.heure_debut is not None and not self._validate_heure_format(self.heure_debut):
            raise ValueError(
                f"Format d'heure de debut invalide: {self.heure_debut}. "
                "Format attendu: HH:MM"
            )

        if self.heure_fin is not None and not self._validate_heure_format(self.heure_fin):
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

    @property
    def has_changes(self) -> bool:
        """
        Verifie si le DTO contient au moins une modification.

        Returns:
            True si au moins un champ est defini.
        """
        return any([
            self.heure_debut is not None,
            self.heure_fin is not None,
            self.note is not None,
            self.chantier_id is not None,
        ])
