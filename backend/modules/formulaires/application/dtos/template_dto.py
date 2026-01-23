"""DTOs pour les templates de formulaire."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from ...domain.entities import TemplateFormulaire, ChampTemplate
from ...domain.value_objects import TypeChamp, CategorieFormulaire


@dataclass
class ChampTemplateDTO:
    """DTO pour un champ de template."""

    nom: str
    label: str
    type_champ: str
    id: Optional[int] = None
    obligatoire: bool = False
    ordre: int = 0
    placeholder: Optional[str] = None
    options: List[str] = field(default_factory=list)
    valeur_defaut: Optional[str] = None
    validation_regex: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    @classmethod
    def from_entity(cls, champ: ChampTemplate) -> "ChampTemplateDTO":
        """Cree un DTO depuis une entite."""
        return cls(
            id=champ.id,
            nom=champ.nom,
            label=champ.label,
            type_champ=champ.type_champ.value,
            obligatoire=champ.obligatoire,
            ordre=champ.ordre,
            placeholder=champ.placeholder,
            options=champ.options,
            valeur_defaut=champ.valeur_defaut,
            validation_regex=champ.validation_regex,
            min_value=champ.min_value,
            max_value=champ.max_value,
        )

    def to_entity(self) -> ChampTemplate:
        """Convertit le DTO en entite."""
        return ChampTemplate(
            id=self.id,
            nom=self.nom,
            label=self.label,
            type_champ=TypeChamp.from_string(self.type_champ),
            obligatoire=self.obligatoire,
            ordre=self.ordre,
            placeholder=self.placeholder,
            options=self.options,
            valeur_defaut=self.valeur_defaut,
            validation_regex=self.validation_regex,
            min_value=self.min_value,
            max_value=self.max_value,
        )


@dataclass
class TemplateFormulaireDTO:
    """DTO pour un template de formulaire."""

    id: int
    nom: str
    categorie: str
    description: Optional[str]
    champs: List[ChampTemplateDTO]
    is_active: bool
    version: int
    nombre_champs: int
    a_signature: bool
    a_photo: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, template: TemplateFormulaire) -> "TemplateFormulaireDTO":
        """Cree un DTO depuis une entite."""
        return cls(
            id=template.id,
            nom=template.nom,
            categorie=template.categorie.value,
            description=template.description,
            champs=[ChampTemplateDTO.from_entity(c) for c in template.champs],
            is_active=template.is_active,
            version=template.version,
            nombre_champs=template.nombre_champs,
            a_signature=template.a_signature,
            a_photo=template.a_photo,
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )


@dataclass
class CreateTemplateDTO:
    """DTO pour la creation d'un template."""

    nom: str
    categorie: str
    description: Optional[str] = None
    champs: List[ChampTemplateDTO] = field(default_factory=list)
    created_by: Optional[int] = None


@dataclass
class UpdateTemplateDTO:
    """DTO pour la mise a jour d'un template."""

    nom: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    champs: Optional[List[ChampTemplateDTO]] = None
    is_active: Optional[bool] = None
