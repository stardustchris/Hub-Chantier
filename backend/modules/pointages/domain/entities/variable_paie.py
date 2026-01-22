"""Entité VariablePaie - Variable de paie associée à un pointage."""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from ..value_objects import TypeVariablePaie


@dataclass
class VariablePaie:
    """
    Représente une variable de paie.

    Selon CDC Section 7.3 - Variables de Paie (FDH-13).
    Panier, transport, congés, primes, absences.

    Attributes:
        id: Identifiant unique.
        pointage_id: ID du pointage associé.
        type_variable: Type de variable (heures sup, panier, etc.).
        valeur: Valeur de la variable (heures ou montant).
        date_application: Date d'application de la variable.
        commentaire: Commentaire optionnel.
        created_at: Date de création.
    """

    type_variable: TypeVariablePaie
    valeur: Decimal
    date_application: date
    pointage_id: Optional[int] = None
    id: Optional[int] = None
    commentaire: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données."""
        if self.valeur < 0:
            raise ValueError("La valeur ne peut pas être négative")

        # Conversion en Decimal si nécessaire
        if not isinstance(self.valeur, Decimal):
            self.valeur = Decimal(str(self.valeur))

    @property
    def is_hours(self) -> bool:
        """Indique si la variable est en heures."""
        return self.type_variable.is_hours_type()

    @property
    def is_amount(self) -> bool:
        """Indique si la variable est un montant."""
        return self.type_variable.is_allowance_type()

    @property
    def is_absence(self) -> bool:
        """Indique si la variable est une absence."""
        return self.type_variable.is_absence_type()

    @property
    def libelle(self) -> str:
        """Retourne le libellé de la variable."""
        return self.type_variable.libelle

    def update_valeur(self, nouvelle_valeur: Decimal) -> None:
        """
        Met à jour la valeur.

        Args:
            nouvelle_valeur: La nouvelle valeur.
        """
        if nouvelle_valeur < 0:
            raise ValueError("La valeur ne peut pas être négative")
        self.valeur = Decimal(str(nouvelle_valeur))
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, VariablePaie):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
