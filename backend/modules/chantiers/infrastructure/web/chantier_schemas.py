"""Schemas Pydantic pour le module chantiers — request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20)
# =============================================================================


class CoordonneesGPSResponse(BaseModel):
    """Coordonnées GPS d'un chantier."""

    latitude: float
    longitude: float


class ContactResponse(BaseModel):
    """Contact sur place d'un chantier."""

    nom: str
    profession: Optional[str] = None
    telephone: Optional[str] = None


class ContactRequest(BaseModel):
    """Contact pour création/mise à jour."""

    nom: str
    profession: Optional[str] = None
    telephone: Optional[str] = None


class ContactChantierResponse(BaseModel):
    """Contact complet d'un chantier avec profession."""

    id: int
    nom: str
    telephone: str
    profession: Optional[str] = None


class ContactChantierCreate(BaseModel):
    """Requête de création d'un contact chantier."""

    nom: str
    telephone: str
    profession: Optional[str] = None


class ContactChantierUpdate(BaseModel):
    """Requête de mise à jour d'un contact chantier."""

    nom: Optional[str] = None
    telephone: Optional[str] = None
    profession: Optional[str] = None


class PhaseChantierResponse(BaseModel):
    """Phase/étape d'un chantier."""

    id: int
    nom: str
    description: Optional[str] = None
    ordre: int
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None


class PhaseChantierCreate(BaseModel):
    """Requête de création d'une phase de chantier."""

    nom: str
    description: Optional[str] = None
    ordre: Optional[int] = 1
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None


class PhaseChantierUpdate(BaseModel):
    """Requête de mise à jour d'une phase de chantier."""

    nom: Optional[str] = None
    description: Optional[str] = None
    ordre: Optional[int] = None
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None


class CreateChantierRequest(BaseModel):
    """Requête de création de chantier."""

    nom: str
    adresse: str
    code: Optional[str] = None  # Auto-généré si non fourni (CHT-19)
    couleur: Optional[str] = None  # CHT-02
    latitude: Optional[float] = None  # CHT-04
    longitude: Optional[float] = None  # CHT-04
    photo_couverture: Optional[str] = None  # CHT-01
    contact_nom: Optional[str] = None  # CHT-07 (legacy single contact)
    contact_telephone: Optional[str] = None  # CHT-07 (legacy single contact)
    contacts: Optional[List[ContactRequest]] = None  # CHT-07 (multiple contacts)
    heures_estimees: Optional[float] = None  # CHT-18
    date_debut_prevue: Optional[str] = None  # CHT-20 (ISO format) - renommé pour frontend
    date_fin_prevue: Optional[str] = None  # CHT-20 (ISO format) - renommé pour frontend
    description: Optional[str] = None
    # DEV-TVA: Contexte TVA
    type_travaux: Optional[str] = None  # "renovation", "renovation_energetique", "construction_neuve"
    batiment_plus_2ans: Optional[bool] = None
    usage_habitation: Optional[bool] = None


class UpdateChantierRequest(BaseModel):
    """Requête de mise à jour de chantier."""

    nom: Optional[str] = None
    adresse: Optional[str] = None
    couleur: Optional[str] = None
    statut: Optional[str] = None  # Pour changement direct de statut
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_couverture: Optional[str] = None
    contact_nom: Optional[str] = None  # Legacy
    contact_telephone: Optional[str] = None  # Legacy
    contacts: Optional[List[ContactRequest]] = None  # Multiple contacts
    heures_estimees: Optional[float] = None
    date_debut_prevue: Optional[str] = None  # Renommé pour frontend
    date_fin_prevue: Optional[str] = None  # Renommé pour frontend
    description: Optional[str] = None
    maitre_ouvrage: Optional[str] = None
    # DEV-TVA: Contexte TVA
    type_travaux: Optional[str] = None
    batiment_plus_2ans: Optional[bool] = None
    usage_habitation: Optional[bool] = None


class ChangeStatutRequest(BaseModel):
    """Requête de changement de statut."""

    statut: str  # "ouvert", "en_cours", "receptionne", "ferme"


class AssignResponsableRequest(BaseModel):
    """Requête d'assignation de responsable."""

    user_id: int


class UserPublicSummary(BaseModel):
    """
    Résumé public d'un utilisateur (sans données sensibles RGPD).

    Utilisé pour l'affichage des conducteurs/chefs dans les chantiers.
    Le téléphone est inclus UNIQUEMENT pour les chefs de chantier (besoin opérationnel).
    """

    id: str
    nom: str
    prenom: str
    role: str
    type_utilisateur: str
    metier: Optional[str] = None
    couleur: Optional[str] = None
    telephone: Optional[str] = None  # Inclus uniquement pour les chefs de chantier
    is_active: bool


# Alias pour compatibilité (ne pas utiliser pour nouvelles features)
UserSummary = UserPublicSummary


class ChantierResponse(BaseModel):
    """Réponse chantier complète selon CDC - format frontend."""

    id: str = Field(
        ...,
        description="Identifiant unique du chantier",
        example="42"
    )
    code: str = Field(
        ...,
        description="Code unique du chantier (auto-généré si non fourni)",
        min_length=3,
        max_length=50,
        example="CHT-2026-001"
    )
    nom: str = Field(
        ...,
        description="Nom du chantier",
        min_length=3,
        max_length=255,
        example="Villa Lyon 3ème - Construction neuve"
    )
    adresse: str = Field(
        ...,
        description="Adresse complète du chantier",
        example="45 Avenue Lacassagne, 69003 Lyon"
    )
    statut: str = Field(
        ...,
        description="Statut actuel du chantier",
        pattern="^(ouvert|en_cours|receptionne|ferme)$",
        example="en_cours"
    )
    couleur: Optional[str] = Field(
        None,
        description="Couleur d'identification (hex)",
        pattern="^#[0-9A-Fa-f]{6}$",
        example="#3B82F6"
    )
    latitude: Optional[float] = Field(
        None,
        description="Latitude GPS du chantier",
        ge=-90,
        le=90,
        example=45.7578
    )
    longitude: Optional[float] = Field(
        None,
        description="Longitude GPS du chantier",
        ge=-180,
        le=180,
        example=4.8320
    )
    contact_nom: Optional[str] = Field(
        None,
        description="Nom du contact principal (legacy field)",
        example="Jean Dupont"
    )
    contact_telephone: Optional[str] = Field(
        None,
        description="Téléphone du contact principal (legacy field)",
        example="06 12 34 56 78"
    )
    contacts: List[ContactResponse] = Field(
        default_factory=list,
        description="Liste des contacts sur place"
    )
    phases: List[PhaseChantierResponse] = Field(
        default_factory=list,
        description="Phases/étapes du chantier"
    )
    maitre_ouvrage: Optional[str] = Field(
        None,
        description="Nom du maître d'ouvrage",
        max_length=255,
        example="OPAC Savoie"
    )
    heures_estimees: Optional[float] = Field(
        None,
        description="Nombre d'heures estimées pour le chantier",
        ge=0,
        example=320.5
    )
    date_debut_prevue: Optional[str] = Field(
        None,
        description="Date de début prévue (format ISO 8601)",
        example="2026-01-15"
    )
    date_fin_prevue: Optional[str] = Field(
        None,
        description="Date de fin prévue (format ISO 8601)",
        example="2026-02-28"
    )
    description: Optional[str] = Field(
        None,
        description="Description détaillée du chantier",
        example="Construction d'une villa individuelle de 150m² avec garage et piscine"
    )
    conducteurs: List[UserPublicSummary] = Field(
        default_factory=list,
        description="Conducteurs de travaux assignés (sans données sensibles)"
    )
    chefs: List[UserPublicSummary] = Field(
        default_factory=list,
        description="Chefs de chantier assignés (sans données sensibles)"
    )
    ouvriers: List[UserPublicSummary] = Field(
        default_factory=list,
        description="Ouvriers, intérimaires et sous-traitants assignés"
    )
    created_at: str = Field(
        ...,
        description="Date de création de la fiche chantier (ISO 8601)",
        example="2026-01-10T08:30:00Z"
    )
    updated_at: Optional[str] = Field(
        None,
        description="Date de dernière modification (ISO 8601)",
        example="2026-01-28T14:22:00Z"
    )
    # DEV-TVA: Contexte TVA pour pre-remplissage
    type_travaux: Optional[str] = Field(
        None,
        description="Type de travaux: renovation, renovation_energetique, construction_neuve"
    )
    batiment_plus_2ans: Optional[bool] = Field(
        None,
        description="Batiment acheve depuis plus de 2 ans"
    )
    usage_habitation: Optional[bool] = Field(
        None,
        description="Immeuble affecte a l'habitation"
    )

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "42",
                "code": "CHT-2026-001",
                "nom": "Villa Lyon 3ème - Construction neuve",
                "adresse": "45 Avenue Lacassagne, 69003 Lyon",
                "statut": "en_cours",
                "couleur": "#3B82F6",
                "latitude": 45.7578,
                "longitude": 4.8320,
                "contact_nom": "Jean Dupont",
                "contact_telephone": "06 12 34 56 78",
                "contacts": [
                    {"nom": "Jean Dupont", "profession": "Architecte", "telephone": "06 12 34 56 78"}
                ],
                "phases": [],
                "heures_estimees": 320.5,
                "date_debut_prevue": "2026-01-15",
                "date_fin_prevue": "2026-02-28",
                "description": "Construction d'une villa individuelle de 150m² avec garage et piscine",
                "conducteurs": [
                    {"id": "5", "nom": "Martin", "prenom": "Sophie", "role": "conducteur", "type_utilisateur": "salarie", "metier": "Conducteur de travaux", "couleur": "#10B981", "is_active": True}
                ],
                "chefs": [],
                "ouvriers": [],
                "created_at": "2026-01-10T08:30:00Z",
                "updated_at": "2026-01-28T14:22:00Z"
            }
        }


class ChantierListResponse(BaseModel):
    """Réponse liste chantiers paginée (CHT-14) - format frontend."""

    items: List[ChantierResponse]
    total: int
    page: int
    size: int
    pages: int


class DeleteResponse(BaseModel):
    """Réponse de suppression."""

    deleted: bool
    id: int
