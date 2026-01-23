"""DTOs pour les formulaires remplis."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any

from ...domain.entities import FormulaireRempli, ChampRempli, PhotoFormulaire
from ...domain.value_objects import StatutFormulaire, TypeChamp


@dataclass
class PhotoFormulaireDTO:
    """DTO pour une photo de formulaire."""

    url: str
    nom_fichier: str
    champ_nom: str
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @classmethod
    def from_entity(cls, photo: PhotoFormulaire) -> "PhotoFormulaireDTO":
        """Cree un DTO depuis une entite."""
        return cls(
            id=photo.id,
            url=photo.url,
            nom_fichier=photo.nom_fichier,
            champ_nom=photo.champ_nom,
            timestamp=photo.timestamp,
            latitude=photo.latitude,
            longitude=photo.longitude,
        )


@dataclass
class ChampRempliDTO:
    """DTO pour un champ rempli."""

    nom: str
    type_champ: str
    valeur: Optional[Any] = None
    timestamp: Optional[datetime] = None

    @classmethod
    def from_entity(cls, champ: ChampRempli) -> "ChampRempliDTO":
        """Cree un DTO depuis une entite."""
        return cls(
            nom=champ.nom,
            type_champ=champ.type_champ.value,
            valeur=champ.valeur,
            timestamp=champ.timestamp,
        )


@dataclass
class FormulaireRempliDTO:
    """DTO pour un formulaire rempli."""

    id: int
    template_id: int
    chantier_id: int
    user_id: int
    statut: str
    champs: List[ChampRempliDTO]
    photos: List[PhotoFormulaireDTO]
    est_signe: bool
    signature_nom: Optional[str]
    signature_timestamp: Optional[datetime]
    est_geolocalise: bool
    localisation_latitude: Optional[float]
    localisation_longitude: Optional[float]
    soumis_at: Optional[datetime]
    valide_by: Optional[int]
    valide_at: Optional[datetime]
    version: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, formulaire: FormulaireRempli) -> "FormulaireRempliDTO":
        """Cree un DTO depuis une entite."""
        return cls(
            id=formulaire.id,
            template_id=formulaire.template_id,
            chantier_id=formulaire.chantier_id,
            user_id=formulaire.user_id,
            statut=formulaire.statut.value,
            champs=[ChampRempliDTO.from_entity(c) for c in formulaire.champs],
            photos=[PhotoFormulaireDTO.from_entity(p) for p in formulaire.photos],
            est_signe=formulaire.est_signe,
            signature_nom=formulaire.signature_nom,
            signature_timestamp=formulaire.signature_timestamp,
            est_geolocalise=formulaire.est_geolocalise,
            localisation_latitude=formulaire.localisation_latitude,
            localisation_longitude=formulaire.localisation_longitude,
            soumis_at=formulaire.soumis_at,
            valide_by=formulaire.valide_by,
            valide_at=formulaire.valide_at,
            version=formulaire.version,
            parent_id=formulaire.parent_id,
            created_at=formulaire.created_at,
            updated_at=formulaire.updated_at,
        )


@dataclass
class CreateFormulaireDTO:
    """DTO pour la creation d'un formulaire (FOR-11)."""

    template_id: int
    chantier_id: int
    user_id: int
    # Localisation auto-remplie (FOR-03)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class UpdateFormulaireDTO:
    """DTO pour la mise a jour d'un formulaire."""

    champs: Optional[List[dict]] = None  # [{nom, valeur, type_champ}]
    # Localisation (FOR-03)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class SubmitFormulaireDTO:
    """DTO pour la soumission d'un formulaire (FOR-07)."""

    formulaire_id: int
    # Signature optionnelle (FOR-05)
    signature_url: Optional[str] = None
    signature_nom: Optional[str] = None
