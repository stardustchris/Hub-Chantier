"""Entité MacroPaie - Calculs automatisés paramétrables de paie (FDH-18).

Permet de définir des formules de calcul automatique pour les variables de paie :
- Indemnités trajet (basées sur la distance chantier)
- Panier repas (par jour travaillé)
- Primes intempéries (conditions météo)
- Toute autre formule paramétrable
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List

from modules.pointages.domain.services.formule_evaluator import evaluer_formule_safe


class TypeMacroPaie(Enum):
    """Types de macros de paie disponibles."""

    INDEMNITE_TRAJET = "indemnite_trajet"
    PANIER_REPAS = "panier_repas"
    PRIME_INTEMPERIES = "prime_intemperies"
    HEURES_SUPPLEMENTAIRES = "heures_supplementaires"
    PRIME_OUTILLAGE = "prime_outillage"
    PRIME_SALISSURE = "prime_salissure"
    PERSONNALISE = "personnalise"

    @property
    def label(self) -> str:
        labels = {
            TypeMacroPaie.INDEMNITE_TRAJET: "Indemnité trajet",
            TypeMacroPaie.PANIER_REPAS: "Panier repas",
            TypeMacroPaie.PRIME_INTEMPERIES: "Prime intempéries",
            TypeMacroPaie.HEURES_SUPPLEMENTAIRES: "Heures supplémentaires",
            TypeMacroPaie.PRIME_OUTILLAGE: "Prime outillage",
            TypeMacroPaie.PRIME_SALISSURE: "Prime salissure",
            TypeMacroPaie.PERSONNALISE: "Formule personnalisée",
        }
        return labels.get(self, self.value)

    @classmethod
    def from_string(cls, value: str) -> "TypeMacroPaie":
        try:
            return cls(value.lower())
        except ValueError:
            valid = [t.value for t in cls]
            raise ValueError(f"Type macro invalide: {value}. Valeurs: {valid}")


@dataclass
class MacroPaie:
    """
    Entité représentant une macro de paie paramétrable (FDH-18).

    Une macro définit une formule de calcul automatique pour une variable de paie.
    Les formules utilisent des variables prédéfinies qui sont résolues au moment
    du calcul.

    Attributes:
        id: Identifiant unique.
        nom: Nom descriptif de la macro.
        type_macro: Type de macro.
        description: Description détaillée.
        formule: Expression de calcul (ex: "jours_travailles * montant_unitaire").
        parametres: Paramètres de la formule (montants, seuils, etc.).
        active: Si la macro est active.
        created_by: ID de l'administrateur qui a créé la macro.
        created_at: Date de création.
        updated_at: Date de dernière modification.

    Variables disponibles dans les formules:
        - jours_travailles: Nombre de jours travaillés sur la période
        - heures_totales: Heures totales travaillées
        - heures_supplementaires: Heures sup (> seuil hebdo)
        - distance_chantier: Distance en km du chantier
        - montant_unitaire: Montant unitaire paramétré
        - seuil_declenchement: Seuil de déclenchement
    """

    nom: str
    type_macro: TypeMacroPaie
    formule: str
    parametres: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    description: Optional[str] = None
    active: bool = True
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom de la macro ne peut pas être vide")
        self.nom = self.nom.strip()

        if not self.formule or not self.formule.strip():
            raise ValueError("La formule de la macro ne peut pas être vide")
        self.formule = self.formule.strip()

        if self.description:
            self.description = self.description.strip()

    def calculer(self, contexte: Dict[str, Any]) -> Decimal:
        """
        Exécute le calcul de la macro avec le contexte fourni.

        Le calcul utilise une évaluation sécurisée qui ne permet que
        les opérations arithmétiques de base sur les variables du contexte.

        Ordre de fusion des variables:
        1. contexte (données calculées depuis les pointages)
        2. parametres de la macro (écrasent les defaults du contexte)
        3. Cela permet aux paramètres macro (montant_unitaire, tarif_km) de
           toujours avoir la valeur configurée par l'admin.

        Args:
            contexte: Variables disponibles pour le calcul.
                Ex: {"jours_travailles": 22, "montant_unitaire": 10.50}

        Returns:
            Résultat du calcul en Decimal.

        Raises:
            ValueError: Si la formule est invalide ou le contexte incomplet.
        """
        # Contexte d'abord, puis parametres macro écrasent les defaults
        variables = {**contexte, **self.parametres}

        try:
            result = self._evaluer_formule(self.formule, variables)
            return Decimal(str(round(result, 2)))
        except Exception as e:
            raise ValueError(
                f"Erreur calcul macro '{self.nom}': {e}. "
                f"Formule: {self.formule}, Variables: {list(variables.keys())}"
            )

    @staticmethod
    def _evaluer_formule(formule: str, variables: Dict[str, Any]) -> float:
        """
        Évalue une formule de manière sécurisée.

        Délègue à evaluer_formule_safe (domain service) qui utilise le
        parser AST pour n'autoriser que les opérations arithmétiques de base.

        Args:
            formule: Expression à évaluer.
            variables: Variables disponibles.

        Returns:
            Résultat numérique.

        Raises:
            ValueError: Si la formule contient des éléments non autorisés.
        """
        return evaluer_formule_safe(formule, variables)

    def activer(self) -> None:
        """Active la macro."""
        self.active = True
        self.updated_at = datetime.now()

    def desactiver(self) -> None:
        """Désactive la macro."""
        self.active = False
        self.updated_at = datetime.now()

    def modifier_parametres(self, parametres: Dict[str, Any]) -> None:
        """Met à jour les paramètres de la macro.

        Args:
            parametres: Nouveaux paramètres.
        """
        self.parametres.update(parametres)
        self.updated_at = datetime.now()

    def modifier_formule(self, formule: str) -> None:
        """Met à jour la formule de la macro.

        Args:
            formule: Nouvelle formule.

        Raises:
            ValueError: Si la formule est vide.
        """
        if not formule or not formule.strip():
            raise ValueError("La formule ne peut pas être vide")
        self.formule = formule.strip()
        self.updated_at = datetime.now()

    @classmethod
    def creer_macro_panier_repas(
        cls,
        montant_unitaire: float = 10.10,
        created_by: Optional[int] = None,
    ) -> "MacroPaie":
        """Factory pour créer une macro panier repas standard.

        Args:
            montant_unitaire: Montant du panier par jour.
            created_by: ID du créateur.

        Returns:
            MacroPaie configurée.
        """
        return cls(
            nom="Panier repas journalier",
            type_macro=TypeMacroPaie.PANIER_REPAS,
            description="Indemnité panier repas par jour travaillé sur chantier",
            formule="jours_travailles * montant_unitaire",
            parametres={"montant_unitaire": montant_unitaire},
            created_by=created_by,
        )

    @classmethod
    def creer_macro_indemnite_trajet(
        cls,
        tarif_km: float = 0.45,
        plafond_journalier: float = 50.0,
        created_by: Optional[int] = None,
    ) -> "MacroPaie":
        """Factory pour créer une macro indemnité trajet.

        Args:
            tarif_km: Tarif au kilomètre.
            plafond_journalier: Plafond par jour.
            created_by: ID du créateur.

        Returns:
            MacroPaie configurée.
        """
        return cls(
            nom="Indemnité trajet chantier",
            type_macro=TypeMacroPaie.INDEMNITE_TRAJET,
            description="Indemnité kilométrique trajet domicile-chantier avec plafond",
            formule="min(distance_chantier * 2 * tarif_km * jours_travailles, plafond_journalier * jours_travailles)",
            parametres={
                "tarif_km": tarif_km,
                "plafond_journalier": plafond_journalier,
            },
            created_by=created_by,
        )

    @classmethod
    def creer_macro_prime_intemperies(
        cls,
        montant_journalier: float = 15.0,
        created_by: Optional[int] = None,
    ) -> "MacroPaie":
        """Factory pour créer une macro prime intempéries.

        Args:
            montant_journalier: Montant par jour d'intempéries.
            created_by: ID du créateur.

        Returns:
            MacroPaie configurée.
        """
        return cls(
            nom="Prime intempéries",
            type_macro=TypeMacroPaie.PRIME_INTEMPERIES,
            description="Prime versée les jours de conditions météo défavorables",
            formule="jours_intemperies * montant_journalier",
            parametres={"montant_journalier": montant_journalier},
            created_by=created_by,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MacroPaie):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id else hash(id(self))
