"""Entite Tache - Represente une tache de chantier selon CDC Section 13."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

from ..value_objects import StatutTache, UniteMesure, CouleurProgression


@dataclass
class Tache:
    """
    Entite representant une tache de chantier.

    Selon CDC Section 13 - Gestion des Taches (TAC-01 a TAC-20).

    Attributes:
        id: Identifiant unique (None si non persiste).
        chantier_id: ID du chantier associe (TAC-01).
        titre: Titre de la tache.
        description: Description detaillee.
        parent_id: ID de la tache parente pour structure hierarchique (TAC-02).
        ordre: Ordre d'affichage pour drag & drop (TAC-15).
        statut: Statut de la tache (TAC-13).
        date_echeance: Deadline pour la tache (TAC-08).
        unite_mesure: Unite de mesure (TAC-09).
        quantite_estimee: Volume/quantite prevu (TAC-10).
        quantite_realisee: Volume/quantite effectivement realise.
        heures_estimees: Temps prevu pour realisation (TAC-11).
        heures_realisees: Temps effectivement passe (TAC-12).
        template_id: ID du template source si cree depuis modele (TAC-05).
        created_at: Date de creation.
        updated_at: Date de derniere modification.
        sous_taches: Liste des sous-taches (TAC-02).
    """

    # Champs obligatoires
    chantier_id: int
    titre: str

    # Champs avec valeurs par defaut
    id: Optional[int] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    ordre: int = 0
    statut: StatutTache = StatutTache.A_FAIRE
    date_echeance: Optional[date] = None
    unite_mesure: Optional[UniteMesure] = None
    quantite_estimee: Optional[float] = None
    quantite_realisee: float = 0.0
    heures_estimees: Optional[float] = None
    heures_realisees: float = 0.0
    template_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    sous_taches: List["Tache"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if not self.titre or not self.titre.strip():
            raise ValueError("Le titre de la tache ne peut pas etre vide")
        self.titre = self.titre.strip()

        if self.heures_estimees is not None and self.heures_estimees < 0:
            raise ValueError("Les heures estimees ne peuvent pas etre negatives")

        if self.heures_realisees < 0:
            raise ValueError("Les heures realisees ne peuvent pas etre negatives")

        if self.quantite_estimee is not None and self.quantite_estimee < 0:
            raise ValueError("La quantite estimee ne peut pas etre negative")

        if self.quantite_realisee < 0:
            raise ValueError("La quantite realisee ne peut pas etre negative")

    @property
    def est_terminee(self) -> bool:
        """Verifie si la tache est terminee."""
        return self.statut == StatutTache.TERMINE

    @property
    def est_en_retard(self) -> bool:
        """Verifie si la tache est en retard par rapport a l'echeance."""
        if not self.date_echeance or self.est_terminee:
            return False
        return date.today() > self.date_echeance

    @property
    def progression_heures(self) -> float:
        """Calcule le pourcentage de progression basé sur les heures."""
        if not self.heures_estimees or self.heures_estimees <= 0:
            return 0.0
        return min((self.heures_realisees / self.heures_estimees) * 100, 100.0)

    @property
    def progression_quantite(self) -> float:
        """Calcule le pourcentage de progression basé sur la quantité."""
        if not self.quantite_estimee or self.quantite_estimee <= 0:
            return 0.0
        return min((self.quantite_realisee / self.quantite_estimee) * 100, 100.0)

    @property
    def couleur_progression(self) -> CouleurProgression:
        """Determine la couleur d'avancement selon CDC TAC-20."""
        return CouleurProgression.from_progression(
            self.heures_realisees,
            self.heures_estimees or 0
        )

    @property
    def a_sous_taches(self) -> bool:
        """Verifie si la tache a des sous-taches."""
        return len(self.sous_taches) > 0

    @property
    def nombre_sous_taches(self) -> int:
        """Retourne le nombre de sous-taches."""
        return len(self.sous_taches)

    @property
    def nombre_sous_taches_terminees(self) -> int:
        """Retourne le nombre de sous-taches terminees."""
        return sum(1 for st in self.sous_taches if st.est_terminee)

    def terminer(self) -> None:
        """Marque la tache comme terminee (TAC-13)."""
        self.statut = StatutTache.TERMINE
        self.updated_at = datetime.now()

    def rouvrir(self) -> None:
        """Remet la tache en statut A faire."""
        self.statut = StatutTache.A_FAIRE
        self.updated_at = datetime.now()

    def ajouter_heures(self, heures: float) -> None:
        """
        Ajoute des heures realisees (TAC-12).

        Args:
            heures: Nombre d'heures a ajouter.

        Raises:
            ValueError: Si les heures sont negatives.
        """
        if heures < 0:
            raise ValueError("Les heures ne peuvent pas etre negatives")
        self.heures_realisees += heures
        self.updated_at = datetime.now()

    def ajouter_quantite(self, quantite: float) -> None:
        """
        Ajoute une quantite realisee.

        Args:
            quantite: Quantite a ajouter.

        Raises:
            ValueError: Si la quantite est negative.
        """
        if quantite < 0:
            raise ValueError("La quantite ne peut pas etre negative")
        self.quantite_realisee += quantite
        self.updated_at = datetime.now()

    def modifier_ordre(self, nouvel_ordre: int) -> None:
        """
        Modifie l'ordre d'affichage (TAC-15 - drag & drop).

        Args:
            nouvel_ordre: Nouvelle position.
        """
        self.ordre = nouvel_ordre
        self.updated_at = datetime.now()

    def ajouter_sous_tache(self, sous_tache: "Tache") -> None:
        """
        Ajoute une sous-tache (TAC-02).

        Args:
            sous_tache: La sous-tache a ajouter.
        """
        sous_tache.parent_id = self.id
        sous_tache.chantier_id = self.chantier_id
        self.sous_taches.append(sous_tache)
        self.updated_at = datetime.now()

    def update(
        self,
        titre: Optional[str] = None,
        description: Optional[str] = None,
        date_echeance: Optional[date] = None,
        unite_mesure: Optional[UniteMesure] = None,
        quantite_estimee: Optional[float] = None,
        heures_estimees: Optional[float] = None,
    ) -> None:
        """
        Met a jour les informations de la tache.

        Args:
            titre: Nouveau titre (optionnel).
            description: Nouvelle description (optionnel).
            date_echeance: Nouvelle echeance (optionnel).
            unite_mesure: Nouvelle unite (optionnel).
            quantite_estimee: Nouvelle quantite estimee (optionnel).
            heures_estimees: Nouvelles heures estimees (optionnel).
        """
        if titre is not None:
            if not titre.strip():
                raise ValueError("Le titre ne peut pas etre vide")
            self.titre = titre.strip()

        if description is not None:
            self.description = description

        if date_echeance is not None:
            self.date_echeance = date_echeance

        if unite_mesure is not None:
            self.unite_mesure = unite_mesure

        if quantite_estimee is not None:
            if quantite_estimee < 0:
                raise ValueError("La quantite estimee ne peut pas etre negative")
            self.quantite_estimee = quantite_estimee

        if heures_estimees is not None:
            if heures_estimees < 0:
                raise ValueError("Les heures estimees ne peuvent pas etre negatives")
            self.heures_estimees = heures_estimees

        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, Tache):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
