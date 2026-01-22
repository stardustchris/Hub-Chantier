"""Entité Pointage - Entrée d'heures pour un jour/utilisateur/chantier."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

from ..value_objects import StatutPointage, Duree


@dataclass
class Pointage:
    """
    Représente un pointage (entrée d'heures).

    Selon CDC Section 7 - Feuilles d'heures.
    Un pointage = heures d'un utilisateur sur un chantier pour une journée.

    Attributes:
        id: Identifiant unique.
        utilisateur_id: ID de l'utilisateur pointé.
        chantier_id: ID du chantier concerné.
        date_pointage: Date du pointage.
        heures_normales: Durée des heures normales travaillées.
        heures_supplementaires: Durée des heures sup (FDH-13).
        statut: Statut de validation (FDH-12).
        commentaire: Commentaire optionnel.
        signature_utilisateur: Signature électronique utilisateur (FDH-12).
        signature_date: Date de signature.
        validateur_id: ID du validateur.
        validation_date: Date de validation.
        affectation_id: ID de l'affectation planning source (FDH-10).
        created_by: ID de l'utilisateur ayant créé le pointage.
        created_at: Date de création.
        updated_at: Date de dernière modification.
    """

    # Champs obligatoires
    utilisateur_id: int
    chantier_id: int
    date_pointage: date

    # Heures travaillées
    heures_normales: Duree = field(default_factory=Duree.zero)
    heures_supplementaires: Duree = field(default_factory=Duree.zero)

    # Statut et validation
    statut: StatutPointage = StatutPointage.BROUILLON
    commentaire: Optional[str] = None

    # Signature électronique (FDH-12)
    signature_utilisateur: Optional[str] = None
    signature_date: Optional[datetime] = None

    # Validation
    validateur_id: Optional[int] = None
    validation_date: Optional[datetime] = None
    motif_rejet: Optional[str] = None

    # Lien avec planning (FDH-10)
    affectation_id: Optional[int] = None

    # Métadonnées
    id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Données calculées / chargées
    _utilisateur_nom: Optional[str] = field(default=None, repr=False)
    _chantier_nom: Optional[str] = field(default=None, repr=False)
    _chantier_couleur: Optional[str] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Valide les données."""
        if self.utilisateur_id <= 0:
            raise ValueError("L'ID utilisateur doit être positif")
        if self.chantier_id <= 0:
            raise ValueError("L'ID chantier doit être positif")

    @property
    def total_heures(self) -> Duree:
        """Calcule le total des heures (normales + sup)."""
        return self.heures_normales + self.heures_supplementaires

    @property
    def total_heures_decimal(self) -> float:
        """Retourne le total en heures décimales."""
        return self.total_heures.decimal

    @property
    def is_editable(self) -> bool:
        """Vérifie si le pointage peut être modifié."""
        return self.statut.is_editable()

    @property
    def is_validated(self) -> bool:
        """Vérifie si le pointage est validé."""
        return self.statut == StatutPointage.VALIDE

    @property
    def is_signed(self) -> bool:
        """Vérifie si le pointage est signé par l'utilisateur."""
        return self.signature_utilisateur is not None

    @property
    def utilisateur_nom(self) -> Optional[str]:
        """Nom de l'utilisateur (chargé depuis la relation)."""
        return self._utilisateur_nom

    @utilisateur_nom.setter
    def utilisateur_nom(self, value: str) -> None:
        """Définit le nom de l'utilisateur."""
        self._utilisateur_nom = value

    @property
    def chantier_nom(self) -> Optional[str]:
        """Nom du chantier (chargé depuis la relation)."""
        return self._chantier_nom

    @chantier_nom.setter
    def chantier_nom(self, value: str) -> None:
        """Définit le nom du chantier."""
        self._chantier_nom = value

    @property
    def chantier_couleur(self) -> Optional[str]:
        """Couleur du chantier (FDH-07)."""
        return self._chantier_couleur

    @chantier_couleur.setter
    def chantier_couleur(self, value: str) -> None:
        """Définit la couleur du chantier."""
        self._chantier_couleur = value

    def set_heures(
        self,
        heures_normales: Optional[Duree] = None,
        heures_supplementaires: Optional[Duree] = None,
    ) -> None:
        """
        Met à jour les heures.

        Args:
            heures_normales: Nouvelles heures normales.
            heures_supplementaires: Nouvelles heures sup.

        Raises:
            ValueError: Si le pointage n'est pas modifiable.
        """
        if not self.is_editable:
            raise ValueError(
                f"Le pointage ne peut pas être modifié (statut: {self.statut.value})"
            )

        if heures_normales is not None:
            self.heures_normales = heures_normales
        if heures_supplementaires is not None:
            self.heures_supplementaires = heures_supplementaires

        self.updated_at = datetime.now()

    def signer(self, signature: str) -> None:
        """
        Signe le pointage (FDH-12).

        Args:
            signature: La signature électronique.

        Raises:
            ValueError: Si déjà signé ou si statut invalide.
        """
        if self.is_signed:
            raise ValueError("Le pointage est déjà signé")
        if self.statut != StatutPointage.BROUILLON:
            raise ValueError("Seul un pointage en brouillon peut être signé")

        self.signature_utilisateur = signature
        self.signature_date = datetime.now()
        self.updated_at = datetime.now()

    def soumettre(self) -> None:
        """
        Soumet le pointage pour validation.

        Raises:
            ValueError: Si la transition n'est pas valide.
        """
        if not self.statut.can_transition_to(StatutPointage.SOUMIS):
            raise ValueError(
                f"Impossible de soumettre depuis le statut {self.statut.value}"
            )

        self.statut = StatutPointage.SOUMIS
        self.updated_at = datetime.now()

    def valider(self, validateur_id: int) -> None:
        """
        Valide le pointage.

        Args:
            validateur_id: ID du validateur.

        Raises:
            ValueError: Si la transition n'est pas valide.
        """
        if not self.statut.can_transition_to(StatutPointage.VALIDE):
            raise ValueError(
                f"Impossible de valider depuis le statut {self.statut.value}"
            )

        self.statut = StatutPointage.VALIDE
        self.validateur_id = validateur_id
        self.validation_date = datetime.now()
        self.motif_rejet = None
        self.updated_at = datetime.now()

    def rejeter(self, validateur_id: int, motif: str) -> None:
        """
        Rejette le pointage.

        Args:
            validateur_id: ID du validateur.
            motif: Raison du rejet.

        Raises:
            ValueError: Si la transition n'est pas valide.
        """
        if not self.statut.can_transition_to(StatutPointage.REJETE):
            raise ValueError(
                f"Impossible de rejeter depuis le statut {self.statut.value}"
            )
        if not motif or not motif.strip():
            raise ValueError("Le motif de rejet est obligatoire")

        self.statut = StatutPointage.REJETE
        self.validateur_id = validateur_id
        self.validation_date = datetime.now()
        self.motif_rejet = motif.strip()
        self.updated_at = datetime.now()

    def corriger(self) -> None:
        """
        Repasse en brouillon pour correction après rejet.

        Raises:
            ValueError: Si la transition n'est pas valide.
        """
        if not self.statut.can_transition_to(StatutPointage.BROUILLON):
            raise ValueError(
                f"Impossible de corriger depuis le statut {self.statut.value}"
            )

        self.statut = StatutPointage.BROUILLON
        # Reset signature pour permettre re-signature
        self.signature_utilisateur = None
        self.signature_date = None
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, Pointage):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
