"""Value Object pour les options de presentation d'un devis.

DEV-11: Personnalisation presentation - Modeles de mise en page configurables.
"""

from typing import Any, Dict, Optional


# Templates predefinis avec leurs configurations
TEMPLATES_PRESENTATION: Dict[str, Dict[str, Any]] = {
    "standard": {
        "nom": "standard",
        "description": "Presentation standard - Tout visible sauf debourses et composants",
        "options": {
            "afficher_debourses": False,
            "afficher_composants": False,
            "afficher_quantites": True,
            "afficher_prix_unitaires": True,
            "afficher_tva_detaillee": True,
            "afficher_conditions_generales": True,
            "afficher_logo": True,
            "afficher_coordonnees_entreprise": True,
            "afficher_retenue_garantie": True,
            "afficher_frais_chantier_detail": True,
        },
    },
    "simplifie": {
        "nom": "simplifie",
        "description": "Presentation simplifiee - Sans detail TVA, composants ni debourses",
        "options": {
            "afficher_debourses": False,
            "afficher_composants": False,
            "afficher_quantites": True,
            "afficher_prix_unitaires": True,
            "afficher_tva_detaillee": False,
            "afficher_conditions_generales": True,
            "afficher_logo": True,
            "afficher_coordonnees_entreprise": True,
            "afficher_retenue_garantie": True,
            "afficher_frais_chantier_detail": False,
        },
    },
    "detaille": {
        "nom": "detaille",
        "description": "Presentation detaillee - Tout visible y compris composants (jamais les debourses)",
        "options": {
            "afficher_debourses": False,
            "afficher_composants": True,
            "afficher_quantites": True,
            "afficher_prix_unitaires": True,
            "afficher_tva_detaillee": True,
            "afficher_conditions_generales": True,
            "afficher_logo": True,
            "afficher_coordonnees_entreprise": True,
            "afficher_retenue_garantie": True,
            "afficher_frais_chantier_detail": True,
        },
    },
    "minimaliste": {
        "nom": "minimaliste",
        "description": "Presentation minimaliste - Juste les lots avec totaux, pas de lignes detaillees",
        "options": {
            "afficher_debourses": False,
            "afficher_composants": False,
            "afficher_quantites": False,
            "afficher_prix_unitaires": False,
            "afficher_tva_detaillee": False,
            "afficher_conditions_generales": True,
            "afficher_logo": True,
            "afficher_coordonnees_entreprise": True,
            "afficher_retenue_garantie": True,
            "afficher_frais_chantier_detail": False,
        },
    },
}

TEMPLATES_VALIDES = list(TEMPLATES_PRESENTATION.keys())


class OptionsPresentationInvalideError(ValueError):
    """Erreur levee quand les options de presentation sont invalides."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class OptionsPresentation:
    """Value Object representant les options de presentation d'un devis.

    DEV-11: Personnalisation presentation - Permet de configurer quels
    elements sont visibles dans le rendu final du devis.

    REGLE METIER: Les debourses ne sont JAMAIS montres au client,
    meme en mode detaille. Le flag afficher_debourses est toujours
    force a False lors de la validation.

    Attributes:
        afficher_debourses: Afficher les debourses (toujours False pour le client).
        afficher_composants: Afficher le detail des composants d'un article.
        afficher_quantites: Afficher les quantites par ligne.
        afficher_prix_unitaires: Afficher les prix unitaires par ligne.
        afficher_tva_detaillee: Afficher le detail TVA par taux.
        afficher_conditions_generales: Afficher les conditions generales.
        afficher_logo: Afficher le logo de l'entreprise.
        afficher_coordonnees_entreprise: Afficher les coordonnees de l'entreprise.
        afficher_retenue_garantie: Afficher la retenue de garantie (si > 0).
        afficher_frais_chantier_detail: Afficher le detail des frais de chantier.
        template_nom: Nom du template utilise.
    """

    def __init__(
        self,
        afficher_debourses: bool = False,
        afficher_composants: bool = False,
        afficher_quantites: bool = True,
        afficher_prix_unitaires: bool = True,
        afficher_tva_detaillee: bool = True,
        afficher_conditions_generales: bool = True,
        afficher_logo: bool = True,
        afficher_coordonnees_entreprise: bool = True,
        afficher_retenue_garantie: bool = True,
        afficher_frais_chantier_detail: bool = True,
        template_nom: str = "standard",
    ) -> None:
        """Initialise les options de presentation.

        Args:
            afficher_debourses: Afficher les debourses (force a False).
            afficher_composants: Afficher les composants.
            afficher_quantites: Afficher les quantites.
            afficher_prix_unitaires: Afficher les prix unitaires.
            afficher_tva_detaillee: Afficher le detail TVA.
            afficher_conditions_generales: Afficher les conditions generales.
            afficher_logo: Afficher le logo.
            afficher_coordonnees_entreprise: Afficher les coordonnees.
            afficher_retenue_garantie: Afficher la retenue de garantie.
            afficher_frais_chantier_detail: Afficher le detail des frais.
            template_nom: Nom du template.

        Raises:
            OptionsPresentationInvalideError: Si le template n'est pas valide.
        """
        if template_nom not in TEMPLATES_VALIDES:
            raise OptionsPresentationInvalideError(
                f"Template '{template_nom}' invalide. "
                f"Templates disponibles: {', '.join(TEMPLATES_VALIDES)}"
            )

        # REGLE METIER: Les debourses ne sont JAMAIS montres au client
        self._afficher_debourses = False
        self._afficher_composants = bool(afficher_composants)
        self._afficher_quantites = bool(afficher_quantites)
        self._afficher_prix_unitaires = bool(afficher_prix_unitaires)
        self._afficher_tva_detaillee = bool(afficher_tva_detaillee)
        self._afficher_conditions_generales = bool(afficher_conditions_generales)
        self._afficher_logo = bool(afficher_logo)
        self._afficher_coordonnees_entreprise = bool(afficher_coordonnees_entreprise)
        self._afficher_retenue_garantie = bool(afficher_retenue_garantie)
        self._afficher_frais_chantier_detail = bool(afficher_frais_chantier_detail)
        self._template_nom = template_nom

    @classmethod
    def from_template(cls, template_nom: str) -> "OptionsPresentation":
        """Cree des options depuis un template predefini.

        Args:
            template_nom: Nom du template.

        Returns:
            Les options de presentation correspondant au template.

        Raises:
            OptionsPresentationInvalideError: Si le template n'existe pas.
        """
        if template_nom not in TEMPLATES_PRESENTATION:
            raise OptionsPresentationInvalideError(
                f"Template '{template_nom}' invalide. "
                f"Templates disponibles: {', '.join(TEMPLATES_VALIDES)}"
            )

        template = TEMPLATES_PRESENTATION[template_nom]
        options = template["options"]
        return cls(
            template_nom=template_nom,
            **options,
        )

    @classmethod
    def defaut(cls) -> "OptionsPresentation":
        """Retourne les options par defaut (template standard).

        Returns:
            Les options de presentation standard.
        """
        return cls.from_template("standard")

    # ─────────────────────────────────────────────────────────────────
    # Properties (lecture seule)
    # ─────────────────────────────────────────────────────────────────

    @property
    def afficher_debourses(self) -> bool:
        """Afficher les debourses (toujours False)."""
        return self._afficher_debourses

    @property
    def afficher_composants(self) -> bool:
        """Afficher les composants."""
        return self._afficher_composants

    @property
    def afficher_quantites(self) -> bool:
        """Afficher les quantites."""
        return self._afficher_quantites

    @property
    def afficher_prix_unitaires(self) -> bool:
        """Afficher les prix unitaires."""
        return self._afficher_prix_unitaires

    @property
    def afficher_tva_detaillee(self) -> bool:
        """Afficher le detail TVA."""
        return self._afficher_tva_detaillee

    @property
    def afficher_conditions_generales(self) -> bool:
        """Afficher les conditions generales."""
        return self._afficher_conditions_generales

    @property
    def afficher_logo(self) -> bool:
        """Afficher le logo."""
        return self._afficher_logo

    @property
    def afficher_coordonnees_entreprise(self) -> bool:
        """Afficher les coordonnees de l'entreprise."""
        return self._afficher_coordonnees_entreprise

    @property
    def afficher_retenue_garantie(self) -> bool:
        """Afficher la retenue de garantie."""
        return self._afficher_retenue_garantie

    @property
    def afficher_frais_chantier_detail(self) -> bool:
        """Afficher le detail des frais de chantier."""
        return self._afficher_frais_chantier_detail

    @property
    def template_nom(self) -> str:
        """Nom du template utilise."""
        return self._template_nom

    # ─────────────────────────────────────────────────────────────────
    # Serialisation
    # ─────────────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Convertit les options en dictionnaire (pour stockage JSON).

        Returns:
            Dictionnaire serialisable des options.
        """
        return {
            "afficher_debourses": self._afficher_debourses,
            "afficher_composants": self._afficher_composants,
            "afficher_quantites": self._afficher_quantites,
            "afficher_prix_unitaires": self._afficher_prix_unitaires,
            "afficher_tva_detaillee": self._afficher_tva_detaillee,
            "afficher_conditions_generales": self._afficher_conditions_generales,
            "afficher_logo": self._afficher_logo,
            "afficher_coordonnees_entreprise": self._afficher_coordonnees_entreprise,
            "afficher_retenue_garantie": self._afficher_retenue_garantie,
            "afficher_frais_chantier_detail": self._afficher_frais_chantier_detail,
            "template_nom": self._template_nom,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "OptionsPresentation":
        """Reconstruit les options depuis un dictionnaire.

        Args:
            data: Le dictionnaire source (peut etre None pour les defauts).

        Returns:
            Les options de presentation.
        """
        if data is None:
            return cls.defaut()

        return cls(
            afficher_debourses=data.get("afficher_debourses", False),
            afficher_composants=data.get("afficher_composants", False),
            afficher_quantites=data.get("afficher_quantites", True),
            afficher_prix_unitaires=data.get("afficher_prix_unitaires", True),
            afficher_tva_detaillee=data.get("afficher_tva_detaillee", True),
            afficher_conditions_generales=data.get("afficher_conditions_generales", True),
            afficher_logo=data.get("afficher_logo", True),
            afficher_coordonnees_entreprise=data.get("afficher_coordonnees_entreprise", True),
            afficher_retenue_garantie=data.get("afficher_retenue_garantie", True),
            afficher_frais_chantier_detail=data.get("afficher_frais_chantier_detail", True),
            template_nom=data.get("template_nom", "standard"),
        )

    # ─────────────────────────────────────────────────────────────────
    # Egalite et hash
    # ─────────────────────────────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur toutes les options."""
        if not isinstance(other, OptionsPresentation):
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        """Hash base sur les options."""
        return hash(tuple(sorted(self.to_dict().items())))

    def __repr__(self) -> str:
        return f"OptionsPresentation(template='{self._template_nom}')"
