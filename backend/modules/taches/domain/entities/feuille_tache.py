"""Entite FeuilleTache - Declaration quotidienne de travail selon CDC TAC-18."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum


class StatutValidation(Enum):
    """Statut de validation d'une feuille de tache."""

    EN_ATTENTE = "en_attente"
    VALIDEE = "validee"
    REJETEE = "rejetee"


@dataclass
class FeuilleTache:
    """
    Entite representant une declaration quotidienne de travail realise.

    Selon CDC Section 13 - TAC-18: Feuilles de taches.
    Permet aux compagnons de declarer le travail effectue sur une tache,
    avec validation par le conducteur (TAC-19).

    Attributes:
        id: Identifiant unique.
        tache_id: ID de la tache concernee.
        utilisateur_id: ID du compagnon declarant.
        chantier_id: ID du chantier.
        date_travail: Date du travail effectue.
        heures_travaillees: Nombre d'heures passees.
        quantite_realisee: Quantite effectuee (selon unite de la tache).
        commentaire: Commentaire du compagnon.
        statut_validation: Statut de validation (TAC-19).
        validateur_id: ID du conducteur validateur.
        date_validation: Date de validation.
        motif_rejet: Motif si rejete.
        created_at: Date de creation.
        updated_at: Date de modification.
    """

    tache_id: int
    utilisateur_id: int
    chantier_id: int
    date_travail: date

    id: Optional[int] = None
    heures_travaillees: float = 0.0
    quantite_realisee: float = 0.0
    commentaire: Optional[str] = None
    statut_validation: StatutValidation = StatutValidation.EN_ATTENTE
    validateur_id: Optional[int] = None
    date_validation: Optional[datetime] = None
    motif_rejet: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.heures_travaillees < 0:
            raise ValueError("Les heures travaillees ne peuvent pas etre negatives")
        if self.quantite_realisee < 0:
            raise ValueError("La quantite realisee ne peut pas etre negative")

    @property
    def est_validee(self) -> bool:
        """Verifie si la feuille est validee."""
        return self.statut_validation == StatutValidation.VALIDEE

    @property
    def est_en_attente(self) -> bool:
        """Verifie si la feuille est en attente de validation."""
        return self.statut_validation == StatutValidation.EN_ATTENTE

    @property
    def est_rejetee(self) -> bool:
        """Verifie si la feuille a ete rejetee."""
        return self.statut_validation == StatutValidation.REJETEE

    def valider(self, validateur_id: int) -> None:
        """
        Valide la feuille de tache (TAC-19).

        Args:
            validateur_id: ID du conducteur qui valide.
        """
        self.statut_validation = StatutValidation.VALIDEE
        self.validateur_id = validateur_id
        self.date_validation = datetime.now()
        self.motif_rejet = None
        self.updated_at = datetime.now()

    def rejeter(self, validateur_id: int, motif: str) -> None:
        """
        Rejette la feuille de tache.

        Args:
            validateur_id: ID du conducteur qui rejette.
            motif: Motif du rejet.
        """
        if not motif or not motif.strip():
            raise ValueError("Le motif de rejet est obligatoire")

        self.statut_validation = StatutValidation.REJETEE
        self.validateur_id = validateur_id
        self.date_validation = datetime.now()
        self.motif_rejet = motif.strip()
        self.updated_at = datetime.now()

    def remettre_en_attente(self) -> None:
        """Remet la feuille en attente de validation."""
        self.statut_validation = StatutValidation.EN_ATTENTE
        self.validateur_id = None
        self.date_validation = None
        self.motif_rejet = None
        self.updated_at = datetime.now()

    def modifier(
        self,
        heures_travaillees: Optional[float] = None,
        quantite_realisee: Optional[float] = None,
        commentaire: Optional[str] = None,
    ) -> None:
        """
        Modifie la feuille de tache.

        Ne peut etre modifiee que si en attente de validation.

        Args:
            heures_travaillees: Nouvelles heures.
            quantite_realisee: Nouvelle quantite.
            commentaire: Nouveau commentaire.

        Raises:
            ValueError: Si la feuille est deja validee.
        """
        if self.est_validee:
            raise ValueError("Impossible de modifier une feuille validee")

        if heures_travaillees is not None:
            if heures_travaillees < 0:
                raise ValueError("Les heures ne peuvent pas etre negatives")
            self.heures_travaillees = heures_travaillees

        if quantite_realisee is not None:
            if quantite_realisee < 0:
                raise ValueError("La quantite ne peut pas etre negative")
            self.quantite_realisee = quantite_realisee

        if commentaire is not None:
            self.commentaire = commentaire

        # Si rejetee et modifiee, remettre en attente
        if self.est_rejetee:
            self.remettre_en_attente()

        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID."""
        if not isinstance(other, FeuilleTache):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
