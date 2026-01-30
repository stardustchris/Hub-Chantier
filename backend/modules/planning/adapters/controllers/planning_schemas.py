"""Schemas Pydantic pour le module Planning.

Ce module definit les schemas de validation des requetes/reponses API
pour le module Planning Operationnel.

Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import datetime


class CreateAffectationRequest(BaseModel):
    """
    Schema de requete pour creer une affectation.

    Attributes:
        utilisateur_id: ID de l'utilisateur a affecter.
        chantier_id: ID du chantier cible.
        date: Date de l'affectation (YYYY-MM-DD).
        heures_prevues: Nombre d'heures prevues (defaut: 8.0 pour journee standard).
        heure_debut: Heure de debut au format "HH:MM" (optionnel).
        heure_fin: Heure de fin au format "HH:MM" (optionnel).
        note: Commentaire prive pour l'affectation (optionnel, max 500 chars).
        type_affectation: Type "unique" ou "recurrente" (defaut: unique).
        jours_recurrence: Jours de recurrence [0-6] pour Lun-Dim (optionnel).
        date_fin_recurrence: Date de fin de la recurrence (optionnel).

    Example:
        >>> request = CreateAffectationRequest(
        ...     utilisateur_id=1,
        ...     chantier_id=2,
        ...     date=datetime.date(2026, 1, 22),
        ...     heure_debut="08:00",
        ...     heure_fin="17:00",
        ... )
    """

    utilisateur_id: int = Field(..., gt=0, description="ID de l'utilisateur a affecter")
    chantier_id: int = Field(..., gt=0, description="ID du chantier cible")
    date: datetime.date = Field(..., description="Date de l'affectation")
    date_fin: Optional[datetime.date] = Field(
        None,
        description="Date de fin pour affectation unique multi-jours (incluse)",
    )
    heures_prevues: float = Field(
        8.0,
        gt=0,
        le=24,
        description="Nombre d'heures prevues pour l'affectation (defaut: 8.0)",
    )
    heure_debut: Optional[str] = Field(
        None,
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Heure de debut (format HH:MM, ex: 08:00)",
    )
    heure_fin: Optional[str] = Field(
        None,
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Heure de fin (format HH:MM, ex: 17:00)",
    )
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Commentaire prive (max 500 caracteres)",
    )
    type_affectation: str = Field(
        "unique",
        pattern=r"^(unique|recurrente)$",
        description="Type d'affectation (unique ou recurrente)",
    )
    jours_recurrence: Optional[List[int]] = Field(
        None,
        description="Jours de recurrence (0=Lundi, 6=Dimanche)",
    )
    date_fin_recurrence: Optional[datetime.date] = Field(
        None,
        description="Date de fin de la recurrence",
    )

    @field_validator("jours_recurrence")
    @classmethod
    def validate_jours_recurrence(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Valide que les jours de recurrence sont entre 0 et 6."""
        if v is not None:
            for jour in v:
                if not isinstance(jour, int) or jour < 0 or jour > 6:
                    raise ValueError(
                        f"Jour de recurrence invalide: {jour}. "
                        "Valeurs valides: 0 (Lundi) a 6 (Dimanche)"
                    )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "utilisateur_id": 1,
                "chantier_id": 2,
                "date": "2026-01-22",
                "heures_prevues": 8.0,
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "note": "Travaux de fondation",
                "type_affectation": "unique",
            }
        }
    }


class UpdateAffectationRequest(BaseModel):
    """
    Schema de requete pour mettre a jour une affectation.

    Tous les champs sont optionnels - seuls ceux fournis seront mis a jour.

    Attributes:
        date: Nouvelle date de l'affectation (pour drag & drop PLN-27).
        utilisateur_id: Nouvel ID utilisateur (pour drag & drop PLN-27).
        heures_prevues: Nouveau nombre d'heures prevues.
        heure_debut: Nouvelle heure de debut au format "HH:MM".
        heure_fin: Nouvelle heure de fin au format "HH:MM".
        note: Nouveau commentaire prive.
        chantier_id: Nouvel ID de chantier.

    Example:
        >>> request = UpdateAffectationRequest(
        ...     heure_debut="09:00",
        ...     heure_fin="18:00",
        ... )
    """

    date: Optional[datetime.date] = Field(
        None,
        description="Nouvelle date de l'affectation (pour drag & drop)",
    )
    utilisateur_id: Optional[int] = Field(
        None,
        gt=0,
        description="Nouvel ID utilisateur (pour drag & drop)",
    )
    heures_prevues: Optional[float] = Field(
        None,
        gt=0,
        le=24,
        description="Nouveau nombre d'heures prevues",
    )
    heure_debut: Optional[str] = Field(
        None,
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Nouvelle heure de debut (format HH:MM, ex: 09:00)",
    )
    heure_fin: Optional[str] = Field(
        None,
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Nouvelle heure de fin (format HH:MM, ex: 18:00)",
    )
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Nouveau commentaire prive",
    )
    chantier_id: Optional[int] = Field(
        None,
        gt=0,
        description="Nouvel ID de chantier",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2026-01-22",
                "utilisateur_id": 2,
                "heure_debut": "09:00",
                "heure_fin": "18:00",
                "note": "Modification des horaires",
            }
        }
    }


class UpdateAffectationNoteRequest(BaseModel):
    """
    Schema de requete pour mettre a jour uniquement la note d'une affectation.

    Ce schema est specifiquement concu pour les Chefs de Chantier qui peuvent
    ajouter ou modifier des notes sur les affectations de leurs chantiers,
    sans pouvoir modifier les autres attributs (PLN-25, matrice des droits section 5.5).

    Attributes:
        note: Nouvelle note (vide ou null pour supprimer).

    Example:
        >>> request = UpdateAffectationNoteRequest(
        ...     note="Apporter outils specifiques"
        ... )
    """

    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Note privee pour l'utilisateur affecte (null ou vide pour supprimer)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "note": "Apporter outils specifiques pour fondations"
            }
        }
    }


class AffectationResponse(BaseModel):
    """
    Schema de reponse pour une affectation.

    Inclut les champs d'enrichissement pour l'affichage UI.

    Attributes:
        id: Identifiant unique de l'affectation.
        utilisateur_id: ID de l'utilisateur affecte.
        chantier_id: ID du chantier.
        date: Date de l'affectation (ISO format).
        heures_prevues: Nombre d'heures prevues pour l'affectation.
        heure_debut: Heure de debut (format HH:MM).
        heure_fin: Heure de fin (format HH:MM).
        note: Commentaire prive.
        type_affectation: Type unique ou recurrente.
        jours_recurrence: Jours de recurrence [0-6].
        created_at: Date de creation (ISO format).
        updated_at: Date de modification (ISO format).
        created_by: ID du createur.
        utilisateur_nom: Nom complet de l'utilisateur (enrichissement).
        utilisateur_couleur: Couleur de l'utilisateur (enrichissement).
        utilisateur_metier: Metier de l'utilisateur (enrichissement).
        chantier_nom: Nom du chantier (enrichissement).
        chantier_couleur: Couleur du chantier (enrichissement).
    """

    id: int = Field(..., description="Identifiant unique de l'affectation", example=42)
    utilisateur_id: int = Field(..., description="ID de l'utilisateur affecté", example=5)
    chantier_id: int = Field(..., description="ID du chantier", example=12)
    date: str = Field(..., description="Date de l'affectation (format ISO 8601)", example="2026-01-22")
    heures_prevues: float = Field(..., description="Nombre d'heures prévues pour l'affectation", example=8.0)
    heure_debut: Optional[str] = Field(
        None,
        description="Heure de début (format HH:MM)",
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        example="08:00"
    )
    heure_fin: Optional[str] = Field(
        None,
        description="Heure de fin (format HH:MM)",
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        example="17:00"
    )
    note: Optional[str] = Field(
        None,
        description="Commentaire privé pour l'affectation",
        max_length=500,
        example="Travaux de fondation - prévoir béton"
    )
    type_affectation: str = Field(
        ...,
        description="Type d'affectation (unique ou recurrente)",
        pattern="^(unique|recurrente)$",
        example="unique"
    )
    jours_recurrence: Optional[List[int]] = Field(
        None,
        description="Jours de récurrence (0=Lundi, 6=Dimanche) pour affectations récurrentes",
        example=[1, 3, 5]
    )
    created_at: str = Field(
        ...,
        description="Date de création de l'affectation (format ISO 8601)",
        example="2026-01-21T10:00:00Z"
    )
    updated_at: str = Field(
        ...,
        description="Date de dernière modification (format ISO 8601)",
        example="2026-01-21T14:30:00Z"
    )
    created_by: int = Field(..., description="ID de l'utilisateur créateur", example=3)
    # Enrichissement pour l'UI
    utilisateur_nom: Optional[str] = Field(
        None,
        description="Nom complet de l'utilisateur (enrichissement UI)",
        example="Jean Dupont"
    )
    utilisateur_couleur: Optional[str] = Field(
        None,
        description="Couleur d'identification de l'utilisateur (hex)",
        pattern="^#[0-9A-Fa-f]{6}$",
        example="#FF5733"
    )
    utilisateur_metier: Optional[str] = Field(
        None,
        description="Métier de l'utilisateur (enrichissement UI)",
        example="Maçon"
    )
    utilisateur_role: Optional[str] = Field(
        None,
        description="Rôle de l'utilisateur dans l'application",
        example="ouvrier"
    )
    utilisateur_type: Optional[str] = Field(
        None,
        description="Type d'utilisateur (salarié, intérimaire, sous-traitant)",
        example="salarie"
    )
    chantier_nom: Optional[str] = Field(
        None,
        description="Nom du chantier (enrichissement UI)",
        example="Villa Lyon 3ème"
    )
    chantier_couleur: Optional[str] = Field(
        None,
        description="Couleur d'identification du chantier (hex)",
        pattern="^#[0-9A-Fa-f]{6}$",
        example="#33FF57"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "utilisateur_id": 1,
                "chantier_id": 2,
                "date": "2026-01-22",
                "heures_prevues": 8.0,
                "heure_debut": "08:00",
                "heure_fin": "17:00",
                "note": "Travaux de fondation",
                "type_affectation": "unique",
                "jours_recurrence": None,
                "created_at": "2026-01-21T10:00:00",
                "updated_at": "2026-01-21T10:00:00",
                "created_by": 1,
                "utilisateur_nom": "Jean Dupont",
                "utilisateur_couleur": "#FF5733",
                "utilisateur_metier": "Macon",
                "chantier_nom": "Chantier A",
                "chantier_couleur": "#33FF57",
            }
        }
    }


class PlanningFiltersRequest(BaseModel):
    """
    Schema pour les filtres de recherche du planning.

    Attributes:
        date_debut: Date de debut de la periode (incluse).
        date_fin: Date de fin de la periode (incluse).
        utilisateur_ids: Liste d'IDs utilisateurs a filtrer.
        chantier_ids: Liste d'IDs chantiers a filtrer.
        metiers: Liste de metiers a filtrer.
        planifies_only: True pour afficher seulement les planifies.
        non_planifies_only: True pour afficher seulement les non planifies.

    Example:
        >>> filters = PlanningFiltersRequest(
        ...     date_debut=date(2026, 1, 20),
        ...     date_fin=date(2026, 1, 26),
        ...     utilisateur_ids=[1, 2, 3],
        ... )
    """

    date_debut: datetime.date = Field(..., description="Date de debut de la periode")
    date_fin: datetime.date = Field(..., description="Date de fin de la periode")
    utilisateur_ids: Optional[List[int]] = Field(
        None,
        description="Liste d'IDs utilisateurs a filtrer",
    )
    chantier_ids: Optional[List[int]] = Field(
        None,
        description="Liste d'IDs chantiers a filtrer",
    )
    metiers: Optional[List[str]] = Field(
        None,
        description="Liste de metiers a filtrer",
    )
    planifies_only: bool = Field(
        False,
        description="True pour afficher seulement les planifies",
    )
    non_planifies_only: bool = Field(
        False,
        description="True pour afficher seulement les non planifies",
    )

    @field_validator("date_fin")
    @classmethod
    def validate_date_fin(cls, v: datetime.date, info) -> datetime.date:
        """Valide que la date de fin est >= date de debut."""
        if "date_debut" in info.data and v < info.data["date_debut"]:
            raise ValueError(
                "La date de fin doit etre posterieure ou egale a la date de debut"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "date_debut": "2026-01-20",
                "date_fin": "2026-01-26",
                "utilisateur_ids": [1, 2, 3],
                "chantier_ids": None,
                "metiers": ["Macon", "Electricien"],
                "planifies_only": False,
                "non_planifies_only": False,
            }
        }
    }


class DuplicateAffectationsRequest(BaseModel):
    """
    Schema de requete pour dupliquer des affectations.

    Attributes:
        utilisateur_id: ID de l'utilisateur dont dupliquer les affectations.
        source_date_debut: Date de debut de la periode source.
        source_date_fin: Date de fin de la periode source.
        target_date_debut: Date de debut de la periode cible.

    Example:
        >>> request = DuplicateAffectationsRequest(
        ...     utilisateur_id=1,
        ...     source_date_debut=date(2026, 1, 13),
        ...     source_date_fin=date(2026, 1, 17),
        ...     target_date_debut=date(2026, 1, 20),
        ... )
    """

    utilisateur_id: int = Field(
        ...,
        gt=0,
        description="ID de l'utilisateur dont dupliquer les affectations",
    )
    source_date_debut: datetime.date = Field(
        ...,
        description="Date de debut de la periode source",
    )
    source_date_fin: datetime.date = Field(
        ...,
        description="Date de fin de la periode source",
    )
    target_date_debut: datetime.date = Field(
        ...,
        description="Date de debut de la periode cible",
    )

    @field_validator("source_date_fin")
    @classmethod
    def validate_source_date_fin(cls, v: datetime.date, info) -> datetime.date:
        """Valide que la date de fin source est >= date de debut source."""
        if "source_date_debut" in info.data and v < info.data["source_date_debut"]:
            raise ValueError(
                "La date de fin source doit etre posterieure ou egale a la date de debut"
            )
        return v

    @field_validator("target_date_debut")
    @classmethod
    def validate_target_date_debut(cls, v: datetime.date, info) -> datetime.date:
        """Valide que la date cible est posterieure a la date de fin source."""
        if "source_date_fin" in info.data and v <= info.data["source_date_fin"]:
            raise ValueError(
                "La date cible doit etre posterieure a la date de fin source"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "utilisateur_id": 1,
                "source_date_debut": "2026-01-13",
                "source_date_fin": "2026-01-17",
                "target_date_debut": "2026-01-20",
            }
        }
    }


class ResizeAffectationRequest(BaseModel):
    """
    Schema de requete pour redimensionner une affectation.

    Permet d'etendre ou reduire la duree d'une affectation
    en specifiant une nouvelle plage de dates.

    Attributes:
        date_debut: Nouvelle date de debut.
        date_fin: Nouvelle date de fin.

    Example:
        >>> request = ResizeAffectationRequest(
        ...     date_debut=datetime.date(2026, 1, 20),
        ...     date_fin=datetime.date(2026, 1, 24),
        ... )
    """

    date_debut: datetime.date = Field(..., description="Nouvelle date de debut")
    date_fin: datetime.date = Field(..., description="Nouvelle date de fin")

    @field_validator("date_fin")
    @classmethod
    def validate_date_fin(cls, v: datetime.date, info) -> datetime.date:
        """Valide que la date de fin est >= date de debut."""
        if "date_debut" in info.data and v < info.data["date_debut"]:
            raise ValueError(
                "La date de fin doit etre posterieure ou egale a la date de debut"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "date_debut": "2026-01-20",
                "date_fin": "2026-01-24",
            }
        }
    }


class DeleteResponse(BaseModel):
    """Schema de reponse pour une suppression."""

    deleted: bool
    id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "deleted": True,
                "id": 1,
            }
        }
    }


class NonPlanifiesResponse(BaseModel):
    """Schema de reponse pour la liste des utilisateurs non planifies."""

    utilisateur_ids: List[int]
    date_debut: str
    date_fin: str
    count: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "utilisateur_ids": [3, 5, 7],
                "date_debut": "2026-01-20",
                "date_fin": "2026-01-24",
                "count": 3,
            }
        }
    }
