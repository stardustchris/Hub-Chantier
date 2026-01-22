"""Entite TemplateModele - Modele de taches reutilisable selon CDC TAC-04."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from ..value_objects import UniteMesure


@dataclass
class SousTacheModele:
    """
    Sous-tache d'un modele de template.

    Represente une sous-tache dans la bibliotheque de modeles.
    """

    titre: str
    description: Optional[str] = None
    ordre: int = 0
    unite_mesure: Optional[UniteMesure] = None
    heures_estimees_defaut: Optional[float] = None

    def __post_init__(self) -> None:
        """Valide les donnees."""
        if not self.titre or not self.titre.strip():
            raise ValueError("Le titre de la sous-tache ne peut pas etre vide")
        self.titre = self.titre.strip()


@dataclass
class TemplateModele:
    """
    Entite representant un modele de taches reutilisable.

    Selon CDC Section 13 - TAC-04: Bibliotheque de modeles.
    Les templates sont des modeles de taches avec sous-taches
    qui peuvent etre importes dans n'importe quel chantier (TAC-05).

    Attributes:
        id: Identifiant unique.
        nom: Nom du modele (ex: "Coffrage voiles").
        description: Description du modele.
        categorie: Categorie du modele (ex: "Gros Oeuvre").
        unite_mesure: Unite par defaut (TAC-09).
        heures_estimees_defaut: Heures par defaut pour estimation.
        sous_taches: Liste des sous-taches du modele.
        is_active: Si le modele est actif.
        created_at: Date de creation.
        updated_at: Date de modification.
    """

    nom: str
    id: Optional[int] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[UniteMesure] = None
    heures_estimees_defaut: Optional[float] = None
    sous_taches: List[SousTacheModele] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du modele ne peut pas etre vide")
        self.nom = self.nom.strip()

    def ajouter_sous_tache(
        self,
        titre: str,
        description: Optional[str] = None,
        ordre: Optional[int] = None,
        unite_mesure: Optional[UniteMesure] = None,
        heures_estimees: Optional[float] = None,
    ) -> SousTacheModele:
        """
        Ajoute une sous-tache au modele.

        Args:
            titre: Titre de la sous-tache.
            description: Description optionnelle.
            ordre: Ordre d'affichage.
            unite_mesure: Unite de mesure.
            heures_estimees: Heures estimees par defaut.

        Returns:
            La sous-tache creee.
        """
        if ordre is None:
            ordre = len(self.sous_taches)

        sous_tache = SousTacheModele(
            titre=titre,
            description=description,
            ordre=ordre,
            unite_mesure=unite_mesure,
            heures_estimees_defaut=heures_estimees,
        )
        self.sous_taches.append(sous_tache)
        self.updated_at = datetime.now()
        return sous_tache

    def supprimer_sous_tache(self, index: int) -> None:
        """
        Supprime une sous-tache par son index.

        Args:
            index: Index de la sous-tache a supprimer.
        """
        if 0 <= index < len(self.sous_taches):
            self.sous_taches.pop(index)
            self.updated_at = datetime.now()

    def desactiver(self) -> None:
        """Desactive le modele."""
        self.is_active = False
        self.updated_at = datetime.now()

    def activer(self) -> None:
        """Active le modele."""
        self.is_active = True
        self.updated_at = datetime.now()

    def update(
        self,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        categorie: Optional[str] = None,
        unite_mesure: Optional[UniteMesure] = None,
        heures_estimees_defaut: Optional[float] = None,
    ) -> None:
        """
        Met a jour le modele.

        Args:
            nom: Nouveau nom.
            description: Nouvelle description.
            categorie: Nouvelle categorie.
            unite_mesure: Nouvelle unite.
            heures_estimees_defaut: Nouvelles heures estimees par defaut.
        """
        if nom is not None:
            if not nom.strip():
                raise ValueError("Le nom ne peut pas etre vide")
            self.nom = nom.strip()

        if description is not None:
            self.description = description

        if categorie is not None:
            self.categorie = categorie

        if unite_mesure is not None:
            self.unite_mesure = unite_mesure

        if heures_estimees_defaut is not None:
            self.heures_estimees_defaut = heures_estimees_defaut

        self.updated_at = datetime.now()

    @property
    def nombre_sous_taches(self) -> int:
        """Retourne le nombre de sous-taches."""
        return len(self.sous_taches)

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID."""
        if not isinstance(other, TemplateModele):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))


# Modeles pre-definis pour le Gros Oeuvre selon CDC Section 13.3
MODELES_GROS_OEUVRE = [
    {
        "nom": "Coffrage voiles",
        "description": "Mise en place des banches, reglage d'aplomb, serrage",
        "categorie": "Gros Oeuvre",
        "unite_mesure": UniteMesure.M2,
        "sous_taches": [
            {"titre": "Preparation et nettoyage banches", "ordre": 0},
            {"titre": "Positionnement et alignement", "ordre": 1},
            {"titre": "Reglage aplomb et verticalite", "ordre": 2},
            {"titre": "Serrage et verification", "ordre": 3},
        ],
    },
    {
        "nom": "Ferraillage plancher",
        "description": "Pose des armatures, ligatures, verification enrobages",
        "categorie": "Gros Oeuvre",
        "unite_mesure": UniteMesure.KG,
        "sous_taches": [
            {"titre": "Debit et facon des aciers", "ordre": 0},
            {"titre": "Pose des armatures principales", "ordre": 1},
            {"titre": "Ligatures et raidisseurs", "ordre": 2},
            {"titre": "Verification enrobages", "ordre": 3},
        ],
    },
    {
        "nom": "Coulage beton",
        "description": "Preparation, vibration, talochage, cure",
        "categorie": "Gros Oeuvre",
        "unite_mesure": UniteMesure.M3,
        "sous_taches": [
            {"titre": "Preparation et verification avant coulage", "ordre": 0},
            {"titre": "Reception et controle beton", "ordre": 1},
            {"titre": "Mise en place et vibration", "ordre": 2},
            {"titre": "Talochage et finition", "ordre": 3},
            {"titre": "Cure beton", "ordre": 4},
        ],
    },
    {
        "nom": "Decoffrage",
        "description": "Retrait des banches, nettoyage, stockage",
        "categorie": "Gros Oeuvre",
        "unite_mesure": UniteMesure.M2,
        "sous_taches": [
            {"titre": "Verification delai decoffrage", "ordre": 0},
            {"titre": "Desserrage et retrait banches", "ordre": 1},
            {"titre": "Nettoyage et huilage", "ordre": 2},
            {"titre": "Stockage et rangement", "ordre": 3},
        ],
    },
    {
        "nom": "Pose predalles",
        "description": "Manutention, calage, etaiement provisoire",
        "categorie": "Gros Oeuvre",
        "unite_mesure": UniteMesure.M2,
        "sous_taches": [
            {"titre": "Preparation zone de pose", "ordre": 0},
            {"titre": "Manutention et levage", "ordre": 1},
            {"titre": "Calage et ajustement", "ordre": 2},
            {"titre": "Etaiement provisoire", "ordre": 3},
        ],
    },
    {
        "nom": "Reservations",
        "description": "Mise en place des reservations techniques",
        "categorie": "Gros Oeuvre",
        "unite_mesure": UniteMesure.UNITE,
        "sous_taches": [
            {"titre": "Reperage sur plans", "ordre": 0},
            {"titre": "Fabrication des reservations", "ordre": 1},
            {"titre": "Fixation et positionnement", "ordre": 2},
            {"titre": "Verification et controle", "ordre": 3},
        ],
    },
    {
        "nom": "Traitement reprise",
        "description": "Preparation surfaces, application produit adherence",
        "categorie": "Gros Oeuvre",
        "unite_mesure": UniteMesure.ML,
        "sous_taches": [
            {"titre": "Nettoyage surface", "ordre": 0},
            {"titre": "Piquage si necessaire", "ordre": 1},
            {"titre": "Application produit adherence", "ordre": 2},
        ],
    },
]
