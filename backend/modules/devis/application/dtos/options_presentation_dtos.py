"""DTOs pour les options de presentation de devis.

DEV-11: Personnalisation presentation - Modeles de mise en page configurables.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.value_objects.options_presentation import OptionsPresentation


@dataclass
class OptionsPresentationDTO:
    """DTO pour les options de presentation d'un devis."""

    afficher_debourses: bool = False
    afficher_composants: bool = False
    afficher_quantites: bool = True
    afficher_prix_unitaires: bool = True
    afficher_tva_detaillee: bool = True
    afficher_conditions_generales: bool = True
    afficher_logo: bool = True
    afficher_coordonnees_entreprise: bool = True
    afficher_retenue_garantie: bool = True
    afficher_frais_chantier_detail: bool = True
    template_nom: str = "standard"

    @classmethod
    def from_value_object(cls, options: OptionsPresentation) -> OptionsPresentationDTO:
        """Cree un DTO depuis le value object OptionsPresentation.

        Args:
            options: Le value object source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            afficher_debourses=options.afficher_debourses,
            afficher_composants=options.afficher_composants,
            afficher_quantites=options.afficher_quantites,
            afficher_prix_unitaires=options.afficher_prix_unitaires,
            afficher_tva_detaillee=options.afficher_tva_detaillee,
            afficher_conditions_generales=options.afficher_conditions_generales,
            afficher_logo=options.afficher_logo,
            afficher_coordonnees_entreprise=options.afficher_coordonnees_entreprise,
            afficher_retenue_garantie=options.afficher_retenue_garantie,
            afficher_frais_chantier_detail=options.afficher_frais_chantier_detail,
            template_nom=options.template_nom,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire.

        Returns:
            Dictionnaire serialisable.
        """
        return {
            "afficher_debourses": self.afficher_debourses,
            "afficher_composants": self.afficher_composants,
            "afficher_quantites": self.afficher_quantites,
            "afficher_prix_unitaires": self.afficher_prix_unitaires,
            "afficher_tva_detaillee": self.afficher_tva_detaillee,
            "afficher_conditions_generales": self.afficher_conditions_generales,
            "afficher_logo": self.afficher_logo,
            "afficher_coordonnees_entreprise": self.afficher_coordonnees_entreprise,
            "afficher_retenue_garantie": self.afficher_retenue_garantie,
            "afficher_frais_chantier_detail": self.afficher_frais_chantier_detail,
            "template_nom": self.template_nom,
        }


@dataclass
class UpdateOptionsPresentationDTO:
    """DTO pour la mise a jour des options de presentation."""

    afficher_debourses: Optional[bool] = None
    afficher_composants: Optional[bool] = None
    afficher_quantites: Optional[bool] = None
    afficher_prix_unitaires: Optional[bool] = None
    afficher_tva_detaillee: Optional[bool] = None
    afficher_conditions_generales: Optional[bool] = None
    afficher_logo: Optional[bool] = None
    afficher_coordonnees_entreprise: Optional[bool] = None
    afficher_retenue_garantie: Optional[bool] = None
    afficher_frais_chantier_detail: Optional[bool] = None
    template_nom: Optional[str] = None


@dataclass
class TemplatePresentationDTO:
    """DTO pour un template de presentation."""

    nom: str
    description: str
    options: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "nom": self.nom,
            "description": self.description,
            "options": self.options,
        }


@dataclass
class ListeTemplatesPresentationDTO:
    """DTO pour la liste des templates disponibles."""

    templates: List[TemplatePresentationDTO]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "templates": [t.to_dict() for t in self.templates],
        }
