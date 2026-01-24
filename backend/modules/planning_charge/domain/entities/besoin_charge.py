"""Entite BesoinCharge - Represente un besoin en main d'oeuvre."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import Semaine, TypeMetier


@dataclass
class BesoinCharge:
    """
    Entite representant un besoin en main d'oeuvre pour un chantier.

    Selon CDC Section 6 - Planning de Charge (PDC-01 a PDC-17).
    Un besoin lie un chantier, une semaine et un type de metier
    avec une quantite de main d'oeuvre necessaire.

    Attributes:
        id: Identifiant unique (None si non persiste).
        chantier_id: ID du chantier concerne.
        semaine: Semaine du besoin.
        type_metier: Type de metier requis.
        besoin_heures: Nombre d'heures de main d'oeuvre necessaires.
        note: Commentaire optionnel sur le besoin.
        created_by: ID de l'utilisateur qui a cree le besoin.
        created_at: Date de creation.
        updated_at: Date de derniere modification.
    """

    # Champs obligatoires
    chantier_id: int
    semaine: Semaine
    type_metier: TypeMetier
    besoin_heures: float
    created_by: int

    # Champs avec valeurs par defaut
    id: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier doit etre positif")

        if self.created_by <= 0:
            raise ValueError("L'ID du createur doit etre positif")

        if self.besoin_heures < 0:
            raise ValueError("Le besoin en heures doit etre >= 0")

        # Normalisation de la note
        if self.note is not None:
            self.note = self.note.strip() if self.note.strip() else None

    @property
    def besoin_jours_homme(self) -> float:
        """
        Retourne le besoin en jours/homme (base 7h/jour).

        Returns:
            Le besoin en J/H.
        """
        return self.besoin_heures / 7.0 if self.besoin_heures > 0 else 0.0

    @property
    def has_note(self) -> bool:
        """Verifie si le besoin a une note."""
        return self.note is not None and len(self.note) > 0

    @property
    def code_unique(self) -> str:
        """
        Retourne un code unique pour ce besoin.

        Format: chantier_id-semaine_code-type_metier
        """
        return f"{self.chantier_id}-{self.semaine.code}-{self.type_metier.value}"

    def modifier_besoin(self, nouvelles_heures: float) -> None:
        """
        Modifie le besoin en heures.

        Args:
            nouvelles_heures: Nouveau nombre d'heures.

        Raises:
            ValueError: Si les heures sont negatives.
        """
        if nouvelles_heures < 0:
            raise ValueError("Le besoin en heures doit etre >= 0")

        self.besoin_heures = nouvelles_heures
        self.updated_at = datetime.now()

    def ajouter_note(self, note: str) -> None:
        """
        Ajoute ou modifie la note du besoin.

        Args:
            note: Le texte de la note.
        """
        self.note = note.strip() if note and note.strip() else None
        self.updated_at = datetime.now()

    def supprimer_note(self) -> None:
        """Supprime la note du besoin."""
        self.note = None
        self.updated_at = datetime.now()

    def changer_type_metier(self, nouveau_type: TypeMetier) -> None:
        """
        Change le type de metier.

        Args:
            nouveau_type: Le nouveau type de metier.
        """
        self.type_metier = nouveau_type
        self.updated_at = datetime.now()

    def est_pour_semaine(self, semaine: Semaine) -> bool:
        """
        Verifie si le besoin concerne une semaine donnee.

        Args:
            semaine: La semaine a verifier.

        Returns:
            True si le besoin est pour cette semaine.
        """
        return self.semaine == semaine

    def est_pour_chantier(self, chantier_id: int) -> bool:
        """
        Verifie si le besoin concerne un chantier donne.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            True si le besoin est pour ce chantier.
        """
        return self.chantier_id == chantier_id

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, BesoinCharge):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __str__(self) -> str:
        """Representation textuelle."""
        return (
            f"BesoinCharge: Chantier {self.chantier_id} - {self.semaine} - "
            f"{self.type_metier.label}: {self.besoin_heures}h"
        )

    def __repr__(self) -> str:
        """Representation technique."""
        return (
            f"BesoinCharge(id={self.id}, chantier_id={self.chantier_id}, "
            f"semaine={self.semaine.code}, type={self.type_metier.value}, "
            f"besoin={self.besoin_heures}h)"
        )
