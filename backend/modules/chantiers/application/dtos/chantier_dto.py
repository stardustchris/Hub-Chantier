"""DTOs pour les chantiers."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from ...domain.entities import Chantier


@dataclass(frozen=True)
class ContactDTO:
    """DTO pour un contact sur chantier."""
    nom: str
    profession: Optional[str] = None
    telephone: Optional[str] = None


@dataclass(frozen=True)
class ChantierDTO:
    """
    Data Transfer Object pour un chantier.

    Utilisé pour transférer les données chantier entre les couches.
    Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20).
    """

    id: int
    code: str
    nom: str
    adresse: str
    statut: str
    statut_icon: str
    couleur: str
    coordonnees_gps: Optional[dict]  # {"latitude": float, "longitude": float}
    photo_couverture: Optional[str]
    contact: Optional[dict]  # {"nom": str, "profession": str, "telephone": str} - legacy single contact
    heures_estimees: Optional[float]
    date_debut: Optional[str]  # ISO format
    date_fin: Optional[str]  # ISO format
    description: Optional[str]
    conducteur_ids: List[int]
    chef_chantier_ids: List[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    contacts: List[ContactDTO] = field(default_factory=list)  # Liste des contacts (CHT-07)

    @classmethod
    def from_entity(cls, chantier: Chantier) -> "ChantierDTO":
        """
        Crée un DTO à partir d'une entité Chantier.

        Args:
            chantier: L'entité Chantier source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=chantier.id,
            code=str(chantier.code),
            nom=chantier.nom,
            adresse=chantier.adresse,
            statut=str(chantier.statut),
            statut_icon=chantier.statut.icon,
            couleur=str(chantier.couleur) if chantier.couleur else "#3498DB",
            coordonnees_gps=(
                chantier.coordonnees_gps.to_dict()
                if chantier.coordonnees_gps
                else None
            ),
            photo_couverture=chantier.photo_couverture,
            contact=(
                chantier.contact.to_dict()
                if chantier.contact
                else None
            ),
            heures_estimees=chantier.heures_estimees,
            date_debut=(
                chantier.date_debut.isoformat()
                if chantier.date_debut
                else None
            ),
            date_fin=(
                chantier.date_fin.isoformat()
                if chantier.date_fin
                else None
            ),
            description=chantier.description,
            conducteur_ids=list(chantier.conducteur_ids),
            chef_chantier_ids=list(chantier.chef_chantier_ids),
            is_active=chantier.is_active,
            created_at=chantier.created_at,
            updated_at=chantier.updated_at,
            contacts=[],  # Les contacts sont chargés séparément via l'infrastructure
        )


@dataclass(frozen=True)
class ChantierListDTO:
    """
    DTO pour une liste paginée de chantiers (CHT-14).
    """

    chantiers: List[ChantierDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_next(self) -> bool:
        """Indique s'il y a une page suivante."""
        return self.skip + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """Indique s'il y a une page précédente."""
        return self.skip > 0


@dataclass
class CreateChantierDTO:
    """
    DTO pour la création d'un chantier.

    Selon CDC Section 4 - tous les champs chantier.
    """

    nom: str
    adresse: str
    code: Optional[str] = None  # Auto-généré si non fourni (CHT-19)
    couleur: Optional[str] = None  # Défaut si non fourni (CHT-02)
    latitude: Optional[float] = None  # CHT-04
    longitude: Optional[float] = None  # CHT-04
    photo_couverture: Optional[str] = None  # CHT-01
    contact_nom: Optional[str] = None  # CHT-07 (legacy)
    contact_telephone: Optional[str] = None  # CHT-07 (legacy)
    contacts: Optional[List[ContactDTO]] = None  # CHT-07 (multiple contacts)
    heures_estimees: Optional[float] = None  # CHT-18
    date_debut: Optional[str] = None  # CHT-20 (ISO format)
    date_fin: Optional[str] = None  # CHT-20 (ISO format)
    description: Optional[str] = None
    conducteur_ids: Optional[List[int]] = None  # CHT-05
    chef_chantier_ids: Optional[List[int]] = None  # CHT-06


@dataclass
class UpdateChantierDTO:
    """
    DTO pour la mise à jour d'un chantier.

    Tous les champs sont optionnels - seuls ceux fournis seront mis à jour.
    """

    nom: Optional[str] = None
    adresse: Optional[str] = None
    couleur: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_couverture: Optional[str] = None
    contact_nom: Optional[str] = None  # Legacy
    contact_telephone: Optional[str] = None  # Legacy
    contacts: Optional[List[ContactDTO]] = None  # Multiple contacts
    heures_estimees: Optional[float] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class ChangeStatutDTO:
    """
    DTO pour le changement de statut d'un chantier.
    """

    nouveau_statut: str  # "ouvert", "en_cours", "receptionne", "ferme"


@dataclass(frozen=True)
class AssignResponsableDTO:
    """
    DTO pour l'assignation d'un responsable (conducteur ou chef).
    """

    user_id: int
    role_type: str  # "conducteur" ou "chef_chantier"
