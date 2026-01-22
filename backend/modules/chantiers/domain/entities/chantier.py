"""Entité Chantier - Représente un chantier de construction."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

from modules.auth.domain.value_objects import Couleur

from ..value_objects import (
    StatutChantier,
    CoordonneesGPS,
    CodeChantier,
    ContactChantier,
)


@dataclass
class Chantier:
    """
    Entité représentant un chantier de construction.

    Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20).

    Attributes:
        id: Identifiant unique (None si non persisté).
        code: Code unique du chantier (CHT-19, ex: A001).
        nom: Nom du chantier.
        adresse: Adresse complète du chantier.
        statut: Statut du chantier (CHT-03).
        couleur: Couleur d'identification (CHT-02).
        coordonnees_gps: Latitude/Longitude (CHT-04).
        photo_couverture: URL de la photo de couverture (CHT-01).
        contact: Contact sur place (CHT-07).
        heures_estimees: Budget temps prévisionnel (CHT-18).
        date_debut: Date de début prévisionnelle (CHT-20).
        date_fin: Date de fin prévisionnelle (CHT-20).
        description: Description du chantier.
        conducteur_ids: IDs des conducteurs assignés (CHT-05).
        chef_chantier_ids: IDs des chefs de chantier (CHT-06).
        created_at: Date de création.
        updated_at: Date de dernière modification.
    """

    # Champs obligatoires
    code: CodeChantier
    nom: str
    adresse: str

    # Champs avec valeurs par défaut
    id: Optional[int] = None
    statut: StatutChantier = field(default_factory=StatutChantier.ouvert)
    couleur: Optional[Couleur] = None
    coordonnees_gps: Optional[CoordonneesGPS] = None
    photo_couverture: Optional[str] = None
    contact: Optional[ContactChantier] = None
    heures_estimees: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    description: Optional[str] = None
    conducteur_ids: list[int] = field(default_factory=list)
    chef_chantier_ids: list[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du chantier ne peut pas être vide")
        if not self.adresse or not self.adresse.strip():
            raise ValueError("L'adresse du chantier ne peut pas être vide")

        # Normalisation
        self.nom = self.nom.strip()
        self.adresse = self.adresse.strip()

        # Couleur par défaut si non spécifiée
        if self.couleur is None:
            self.couleur = Couleur.default()

        # Validation des dates
        if self.date_debut and self.date_fin:
            if self.date_fin < self.date_debut:
                raise ValueError(
                    "La date de fin ne peut pas être antérieure à la date de début"
                )

    @property
    def code_str(self) -> str:
        """Retourne le code sous forme de chaîne."""
        return str(self.code)

    @property
    def is_active(self) -> bool:
        """Vérifie si le chantier est actif (non fermé)."""
        return self.statut.is_active()

    @property
    def allows_modifications(self) -> bool:
        """Vérifie si le chantier permet des modifications."""
        return self.statut.allows_modifications()

    @property
    def has_gps(self) -> bool:
        """Vérifie si le chantier a des coordonnées GPS."""
        return self.coordonnees_gps is not None

    @property
    def has_contact(self) -> bool:
        """Vérifie si le chantier a un contact défini."""
        return self.contact is not None

    @property
    def duree_prevue_jours(self) -> Optional[int]:
        """
        Calcule la durée prévue en jours.

        Returns:
            Nombre de jours entre date_debut et date_fin, ou None.
        """
        if self.date_debut and self.date_fin:
            return (self.date_fin - self.date_debut).days
        return None

    def change_statut(self, nouveau_statut: StatutChantier) -> None:
        """
        Change le statut du chantier.

        Args:
            nouveau_statut: Le nouveau statut.

        Raises:
            ValueError: Si la transition n'est pas autorisée.
        """
        if not self.statut.can_transition_to(nouveau_statut):
            raise ValueError(
                f"Transition non autorisée: {self.statut} → {nouveau_statut}. "
                f"Transitions possibles depuis {self.statut}: "
                f"{[str(s) for s in self.statut.TRANSITIONS[self.statut.value]]}"
            )
        self.statut = nouveau_statut
        self.updated_at = datetime.now()

    def demarrer(self) -> None:
        """Passe le chantier en statut 'En cours'."""
        self.change_statut(StatutChantier.en_cours())

    def receptionner(self) -> None:
        """Passe le chantier en statut 'Réceptionné'."""
        self.change_statut(StatutChantier.receptionne())

    def fermer(self) -> None:
        """Passe le chantier en statut 'Fermé'."""
        self.change_statut(StatutChantier.ferme())

    def rouvrir(self) -> None:
        """Rouvre un chantier réceptionné (retour 'En cours')."""
        if self.statut.value.value != "receptionne":
            raise ValueError("Seul un chantier réceptionné peut être rouvert")
        self.change_statut(StatutChantier.en_cours())

    def assigner_conducteur(self, conducteur_id: int) -> None:
        """
        Assigne un conducteur au chantier (CHT-05: Multi-conducteurs).

        Args:
            conducteur_id: ID du conducteur à assigner.
        """
        if conducteur_id not in self.conducteur_ids:
            self.conducteur_ids.append(conducteur_id)
            self.updated_at = datetime.now()

    def retirer_conducteur(self, conducteur_id: int) -> None:
        """
        Retire un conducteur du chantier.

        Args:
            conducteur_id: ID du conducteur à retirer.
        """
        if conducteur_id in self.conducteur_ids:
            self.conducteur_ids.remove(conducteur_id)
            self.updated_at = datetime.now()

    def assigner_chef_chantier(self, chef_id: int) -> None:
        """
        Assigne un chef de chantier (CHT-06: Multi-chefs de chantier).

        Args:
            chef_id: ID du chef de chantier à assigner.
        """
        if chef_id not in self.chef_chantier_ids:
            self.chef_chantier_ids.append(chef_id)
            self.updated_at = datetime.now()

    def retirer_chef_chantier(self, chef_id: int) -> None:
        """
        Retire un chef de chantier.

        Args:
            chef_id: ID du chef de chantier à retirer.
        """
        if chef_id in self.chef_chantier_ids:
            self.chef_chantier_ids.remove(chef_id)
            self.updated_at = datetime.now()

    def update_coordonnees_gps(self, coordonnees: CoordonneesGPS) -> None:
        """
        Met à jour les coordonnées GPS (CHT-04).

        Args:
            coordonnees: Nouvelles coordonnées GPS.
        """
        self.coordonnees_gps = coordonnees
        self.updated_at = datetime.now()

    def update_contact(self, contact: ContactChantier) -> None:
        """
        Met à jour le contact sur place (CHT-07).

        Args:
            contact: Nouveau contact.
        """
        self.contact = contact
        self.updated_at = datetime.now()

    def update_dates(
        self,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
    ) -> None:
        """
        Met à jour les dates prévisionnelles (CHT-20).

        Args:
            date_debut: Nouvelle date de début.
            date_fin: Nouvelle date de fin.

        Raises:
            ValueError: Si date_fin < date_debut.
        """
        new_debut = date_debut if date_debut is not None else self.date_debut
        new_fin = date_fin if date_fin is not None else self.date_fin

        if new_debut and new_fin and new_fin < new_debut:
            raise ValueError(
                "La date de fin ne peut pas être antérieure à la date de début"
            )

        if date_debut is not None:
            self.date_debut = date_debut
        if date_fin is not None:
            self.date_fin = date_fin
        self.updated_at = datetime.now()

    def update_heures_estimees(self, heures: float) -> None:
        """
        Met à jour le budget temps (CHT-18).

        Args:
            heures: Nombre d'heures estimées.

        Raises:
            ValueError: Si heures <= 0.
        """
        if heures <= 0:
            raise ValueError("Les heures estimées doivent être positives")
        self.heures_estimees = heures
        self.updated_at = datetime.now()

    def update_photo_couverture(self, url: str) -> None:
        """
        Met à jour la photo de couverture (CHT-01).

        Args:
            url: URL de la nouvelle photo.
        """
        self.photo_couverture = url
        self.updated_at = datetime.now()

    def update_infos(
        self,
        nom: Optional[str] = None,
        adresse: Optional[str] = None,
        description: Optional[str] = None,
        couleur: Optional[Couleur] = None,
    ) -> None:
        """
        Met à jour les informations générales du chantier.

        Args:
            nom: Nouveau nom.
            adresse: Nouvelle adresse.
            description: Nouvelle description.
            couleur: Nouvelle couleur.
        """
        if nom is not None:
            if not nom.strip():
                raise ValueError("Le nom ne peut pas être vide")
            self.nom = nom.strip()

        if adresse is not None:
            if not adresse.strip():
                raise ValueError("L'adresse ne peut pas être vide")
            self.adresse = adresse.strip()

        if description is not None:
            self.description = description.strip() if description.strip() else None

        if couleur is not None:
            self.couleur = couleur

        self.updated_at = datetime.now()

    def is_conducteur(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est conducteur de ce chantier."""
        return user_id in self.conducteur_ids

    def is_chef_chantier(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est chef de ce chantier."""
        return user_id in self.chef_chantier_ids

    def is_responsable(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est responsable (conducteur ou chef)."""
        return self.is_conducteur(user_id) or self.is_chef_chantier(user_id)

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID (entité)."""
        if not isinstance(other, Chantier):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def __str__(self) -> str:
        """Représentation textuelle."""
        return f"{self.code} - {self.nom}"
