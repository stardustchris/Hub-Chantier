"""Entite AffectationIntervention.

INT-10: Affectation technicien - Drag & drop ou via modal
INT-17: Affectation sous-traitants - Prestataires externes
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AffectationIntervention:
    """Represente l'affectation d'un technicien a une intervention.

    Selon le CDC Section 12:
    - Une intervention peut avoir 1-2 techniciens (duree courte)
    - Les sous-traitants peuvent aussi etre affectes (INT-17)

    Attributes:
        id: Identifiant unique.
        intervention_id: ID de l'intervention.
        utilisateur_id: ID de l'utilisateur affecte (technicien ou sous-traitant).
        est_principal: Indique si c'est le technicien principal.
        commentaire: Note optionnelle sur l'affectation.
        created_by: ID de l'utilisateur qui a cree l'affectation.
        created_at: Date de creation.
    """

    intervention_id: int
    utilisateur_id: int
    created_by: int

    id: Optional[int] = None
    est_principal: bool = False
    commentaire: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    # Soft delete
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.intervention_id <= 0:
            raise ValueError("L'ID de l'intervention doit etre positif")
        if self.utilisateur_id <= 0:
            raise ValueError("L'ID de l'utilisateur doit etre positif")
        if self.created_by <= 0:
            raise ValueError("L'ID du createur doit etre positif")

        # Normalisation du commentaire
        if self.commentaire:
            self.commentaire = self.commentaire.strip() or None

    @property
    def est_supprimee(self) -> bool:
        """Verifie si l'affectation a ete supprimee (soft delete)."""
        return self.deleted_at is not None

    def definir_principal(self) -> None:
        """Definit ce technicien comme principal."""
        self.est_principal = True
        self.updated_at = datetime.utcnow()

    def retirer_principal(self) -> None:
        """Retire le statut de technicien principal."""
        self.est_principal = False
        self.updated_at = datetime.utcnow()

    def ajouter_commentaire(self, commentaire: str) -> None:
        """Ajoute ou modifie le commentaire."""
        self.commentaire = commentaire.strip() if commentaire.strip() else None
        self.updated_at = datetime.utcnow()

    def supprimer(self, deleted_by: int) -> None:
        """Marque l'affectation comme supprimee (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID."""
        if not isinstance(other, AffectationIntervention):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __str__(self) -> str:
        """Representation textuelle."""
        role = "principal" if self.est_principal else "secondaire"
        return f"Affectation ({role}): User {self.utilisateur_id} -> INT {self.intervention_id}"

    def __repr__(self) -> str:
        """Representation technique."""
        return (
            f"AffectationIntervention(id={self.id}, intervention_id={self.intervention_id}, "
            f"utilisateur_id={self.utilisateur_id}, est_principal={self.est_principal})"
        )
