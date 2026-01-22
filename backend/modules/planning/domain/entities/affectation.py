"""Entite Affectation - Represente une affectation d'un utilisateur a un chantier."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

from ..value_objects import HeureAffectation, TypeAffectation, JourSemaine


@dataclass
class Affectation:
    """
    Entite representant une affectation d'un utilisateur a un chantier.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).
    Une affectation lie un utilisateur a un chantier pour une date donnee,
    avec des horaires optionnels et la possibilite de recurrence.

    Attributes:
        id: Identifiant unique (None si non persiste).
        utilisateur_id: ID de l'utilisateur affecte (reference User).
        chantier_id: ID du chantier concerne (reference Chantier).
        date: Date de l'affectation.
        heure_debut: Heure de debut optionnelle.
        heure_fin: Heure de fin optionnelle.
        note: Commentaire prive pour l'utilisateur affecte.
        type_affectation: Type unique ou recurrent.
        jours_recurrence: Jours de la semaine pour recurrence.
        created_at: Date de creation.
        updated_at: Date de derniere modification.
        created_by: ID de l'utilisateur qui a cree l'affectation.

    Raises:
        ValueError: Si les donnees sont invalides (ex: heure_fin < heure_debut).

    Example:
        >>> affectation = Affectation(
        ...     utilisateur_id=1,
        ...     chantier_id=2,
        ...     date=date(2026, 1, 22),
        ...     created_by=3,
        ... )
    """

    # Champs obligatoires
    utilisateur_id: int
    chantier_id: int
    date: date
    created_by: int

    # Champs avec valeurs par defaut
    id: Optional[int] = None
    heure_debut: Optional[HeureAffectation] = None
    heure_fin: Optional[HeureAffectation] = None
    note: Optional[str] = None
    type_affectation: TypeAffectation = field(default=TypeAffectation.UNIQUE)
    jours_recurrence: Optional[List[JourSemaine]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        # Validation des IDs
        if self.utilisateur_id <= 0:
            raise ValueError("L'ID utilisateur doit etre positif")

        if self.chantier_id <= 0:
            raise ValueError("L'ID chantier doit etre positif")

        if self.created_by <= 0:
            raise ValueError("L'ID du createur doit etre positif")

        # Validation des horaires
        if self.heure_debut is not None and self.heure_fin is not None:
            if self.heure_fin <= self.heure_debut:
                raise ValueError(
                    f"L'heure de fin ({self.heure_fin}) doit etre posterieure "
                    f"a l'heure de debut ({self.heure_debut})"
                )

        # Validation coherence type/recurrence
        if self.type_affectation == TypeAffectation.RECURRENTE:
            if not self.jours_recurrence or len(self.jours_recurrence) == 0:
                raise ValueError(
                    "Une affectation recurrente doit specifier les jours de recurrence"
                )
        else:
            # Pour une affectation unique, on ignore les jours de recurrence
            if self.jours_recurrence:
                object.__setattr__(self, "jours_recurrence", None)

        # Normalisation de la note
        if self.note is not None:
            self.note = self.note.strip() if self.note.strip() else None

    @property
    def has_horaires(self) -> bool:
        """
        Verifie si l'affectation a des horaires definis.

        Returns:
            True si heure_debut ET heure_fin sont definis.
        """
        return self.heure_debut is not None and self.heure_fin is not None

    @property
    def duree_minutes(self) -> Optional[int]:
        """
        Calcule la duree de l'affectation en minutes.

        Returns:
            La duree en minutes, ou None si pas d'horaires definis.
        """
        if not self.has_horaires:
            return None
        return self.heure_debut.duree_vers(self.heure_fin)

    @property
    def duree_heures(self) -> Optional[float]:
        """
        Calcule la duree de l'affectation en heures.

        Returns:
            La duree en heures (float), ou None si pas d'horaires definis.
        """
        if self.duree_minutes is None:
            return None
        return self.duree_minutes / 60.0

    @property
    def is_recurrente(self) -> bool:
        """
        Verifie si l'affectation est recurrente.

        Returns:
            True si le type est RECURRENTE.
        """
        return self.type_affectation == TypeAffectation.RECURRENTE

    @property
    def has_note(self) -> bool:
        """
        Verifie si l'affectation a une note.

        Returns:
            True si une note est definie.
        """
        return self.note is not None and len(self.note) > 0

    def modifier_horaires(
        self,
        heure_debut: Optional[HeureAffectation],
        heure_fin: Optional[HeureAffectation],
    ) -> None:
        """
        Modifie les horaires de l'affectation.

        Valide que l'heure de fin est posterieure a l'heure de debut
        si les deux sont specifiees.

        Args:
            heure_debut: Nouvelle heure de debut (ou None pour supprimer).
            heure_fin: Nouvelle heure de fin (ou None pour supprimer).

        Raises:
            ValueError: Si heure_fin <= heure_debut.

        Example:
            >>> affectation.modifier_horaires(
            ...     HeureAffectation(8, 0),
            ...     HeureAffectation(17, 0)
            ... )
        """
        if heure_debut is not None and heure_fin is not None:
            if heure_fin <= heure_debut:
                raise ValueError(
                    f"L'heure de fin ({heure_fin}) doit etre posterieure "
                    f"a l'heure de debut ({heure_debut})"
                )

        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.updated_at = datetime.now()

    def ajouter_note(self, note: str) -> None:
        """
        Ajoute ou modifie la note de l'affectation.

        La note est un commentaire prive visible par l'utilisateur affecte.

        Args:
            note: Le texte de la note.

        Example:
            >>> affectation.ajouter_note("Apporter les outils specifiques")
        """
        self.note = note.strip() if note and note.strip() else None
        self.updated_at = datetime.now()

    def supprimer_note(self) -> None:
        """
        Supprime la note de l'affectation.
        """
        self.note = None
        self.updated_at = datetime.now()

    def dupliquer(self, nouvelle_date: date) -> "Affectation":
        """
        Cree une copie de l'affectation pour une nouvelle date.

        L'affectation dupliquee conserve les memes horaires, note et
        informations, mais avec un nouvel ID (None) et la nouvelle date.

        Args:
            nouvelle_date: La date pour la nouvelle affectation.

        Returns:
            Une nouvelle instance d'Affectation.

        Example:
            >>> nouvelle = affectation.dupliquer(date(2026, 1, 23))
        """
        return Affectation(
            id=None,  # Nouvel ID sera attribue a la persistence
            utilisateur_id=self.utilisateur_id,
            chantier_id=self.chantier_id,
            date=nouvelle_date,
            heure_debut=self.heure_debut,
            heure_fin=self.heure_fin,
            note=self.note,
            type_affectation=TypeAffectation.UNIQUE,  # Duplication = unique
            jours_recurrence=None,
            created_by=self.created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def convertir_en_unique(self) -> None:
        """
        Convertit l'affectation en type unique.

        Supprime les informations de recurrence.
        """
        self.type_affectation = TypeAffectation.UNIQUE
        self.jours_recurrence = None
        self.updated_at = datetime.now()

    def convertir_en_recurrente(self, jours: List[JourSemaine]) -> None:
        """
        Convertit l'affectation en type recurrent.

        Args:
            jours: Liste des jours de recurrence.

        Raises:
            ValueError: Si la liste de jours est vide.

        Example:
            >>> affectation.convertir_en_recurrente([
            ...     JourSemaine.LUNDI,
            ...     JourSemaine.MERCREDI,
            ...     JourSemaine.VENDREDI
            ... ])
        """
        if not jours or len(jours) == 0:
            raise ValueError(
                "La liste des jours de recurrence ne peut pas etre vide"
            )

        self.type_affectation = TypeAffectation.RECURRENTE
        self.jours_recurrence = list(jours)  # Copie pour eviter modifications externes
        self.updated_at = datetime.now()

    def changer_chantier(self, nouveau_chantier_id: int) -> None:
        """
        Change le chantier de l'affectation.

        Args:
            nouveau_chantier_id: L'ID du nouveau chantier.

        Raises:
            ValueError: Si l'ID est invalide.
        """
        if nouveau_chantier_id <= 0:
            raise ValueError("L'ID du chantier doit etre positif")

        self.chantier_id = nouveau_chantier_id
        self.updated_at = datetime.now()

    def changer_utilisateur(self, nouvel_utilisateur_id: int) -> None:
        """
        Change l'utilisateur affecte.

        Args:
            nouvel_utilisateur_id: L'ID du nouvel utilisateur.

        Raises:
            ValueError: Si l'ID est invalide.
        """
        if nouvel_utilisateur_id <= 0:
            raise ValueError("L'ID de l'utilisateur doit etre positif")

        self.utilisateur_id = nouvel_utilisateur_id
        self.updated_at = datetime.now()

    def changer_date(self, nouvelle_date: date) -> None:
        """
        Change la date de l'affectation.

        Args:
            nouvelle_date: La nouvelle date.
        """
        self.date = nouvelle_date
        self.updated_at = datetime.now()

    def est_pour_jour(self, jour: JourSemaine) -> bool:
        """
        Verifie si l'affectation recurrente inclut un jour donne.

        Args:
            jour: Le jour de la semaine a verifier.

        Returns:
            True si l'affectation s'applique ce jour (toujours True si unique).
        """
        if not self.is_recurrente or not self.jours_recurrence:
            return True  # Affectation unique = s'applique a sa date

        return jour in self.jours_recurrence

    def horaires_str(self) -> Optional[str]:
        """
        Retourne les horaires sous forme de chaine.

        Returns:
            Chaine "HH:MM - HH:MM" ou None si pas d'horaires.

        Example:
            >>> affectation.horaires_str()
            '08:00 - 17:00'
        """
        if not self.has_horaires:
            return None
        return f"{self.heure_debut} - {self.heure_fin}"

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, Affectation):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __str__(self) -> str:
        """Representation textuelle."""
        type_str = "recurrente" if self.is_recurrente else "unique"
        horaires = f" ({self.horaires_str()})" if self.has_horaires else ""
        return (
            f"Affectation {type_str}: User {self.utilisateur_id} -> "
            f"Chantier {self.chantier_id} le {self.date}{horaires}"
        )

    def __repr__(self) -> str:
        """Representation technique."""
        return (
            f"Affectation(id={self.id}, utilisateur_id={self.utilisateur_id}, "
            f"chantier_id={self.chantier_id}, date={self.date}, "
            f"type={self.type_affectation.value})"
        )
