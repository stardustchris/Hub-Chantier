"""Entite Ressource - Materiel de l'entreprise.

CDC Section 11 - LOG-01, LOG-02.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import TypeRessource


@dataclass
class Ressource:
    """
    Entite representant une ressource materielle de l'entreprise.

    Selon CDC Section 11:
    - LOG-01: Referentiel materiel (Admin uniquement)
    - LOG-02: Fiche ressource (nom, code, photo, couleur, plage horaire)
    - LOG-10: Option validation N+1

    Note:
        Une ressource appartient a l'entreprise (pas de FK vers chantier).
        Elle peut etre reservee pour differents chantiers.
    """

    # Identifiant (genere par la DB)
    id: Optional[int] = None

    # Identification (LOG-02)
    code: str = ""
    nom: str = ""
    description: Optional[str] = None

    # Type de ressource
    type_ressource: TypeRessource = TypeRessource.OUTILLAGE

    # Identification visuelle (LOG-02)
    photo_url: Optional[str] = None
    couleur: str = "#3498DB"

    # Plage horaire par defaut (LOG-05)
    plage_horaire_debut: str = "08:00"
    plage_horaire_fin: str = "18:00"

    # Option validation N+1 (LOG-10)
    validation_requise: bool = True

    # Statut
    is_active: bool = True

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation apres initialisation."""
        if not self.code:
            raise ValueError("Le code de la ressource est obligatoire")
        if not self.nom:
            raise ValueError("Le nom de la ressource est obligatoire")
        if not self.plage_horaire_debut or not self.plage_horaire_fin:
            raise ValueError("Les plages horaires sont obligatoires")

    @property
    def is_deleted(self) -> bool:
        """Indique si la ressource a ete supprimee (soft delete)."""
        return self.deleted_at is not None

    def activer(self) -> None:
        """Active la ressource."""
        self.is_active = True
        self.updated_at = datetime.now()

    def desactiver(self) -> None:
        """Desactive la ressource."""
        self.is_active = False
        self.updated_at = datetime.now()

    def supprimer(self) -> None:
        """Supprime la ressource (soft delete)."""
        self.deleted_at = datetime.now()
        self.is_active = False
        self.updated_at = datetime.now()

    def restaurer(self) -> None:
        """Restaure une ressource supprimee."""
        self.deleted_at = None
        self.is_active = True
        self.updated_at = datetime.now()

    def update(
        self,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        type_ressource: Optional[TypeRessource] = None,
        photo_url: Optional[str] = None,
        couleur: Optional[str] = None,
        plage_horaire_debut: Optional[str] = None,
        plage_horaire_fin: Optional[str] = None,
        validation_requise: Optional[bool] = None,
    ) -> None:
        """
        Met a jour les proprietes de la ressource.

        Args:
            nom: Nouveau nom
            description: Nouvelle description
            type_ressource: Nouveau type
            photo_url: Nouvelle URL de photo
            couleur: Nouvelle couleur
            plage_horaire_debut: Nouvelle heure de debut
            plage_horaire_fin: Nouvelle heure de fin
            validation_requise: Nouvelle option de validation
        """
        if nom is not None:
            self.nom = nom
        if description is not None:
            self.description = description
        if type_ressource is not None:
            self.type_ressource = type_ressource
        if photo_url is not None:
            self.photo_url = photo_url
        if couleur is not None:
            self.couleur = couleur
        if plage_horaire_debut is not None:
            self.plage_horaire_debut = plage_horaire_debut
        if plage_horaire_fin is not None:
            self.plage_horaire_fin = plage_horaire_fin
        if validation_requise is not None:
            self.validation_requise = validation_requise

        self.updated_at = datetime.now()

    def __repr__(self) -> str:
        return f"<Ressource(id={self.id}, code={self.code}, nom={self.nom})>"
