"""Entite TemplateFormulaire - Template de formulaire personnalisable."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from ..value_objects import TypeChamp, CategorieFormulaire


@dataclass
class ChampTemplate:
    """
    Definition d'un champ dans un template de formulaire.

    Attributes:
        id: Identifiant unique du champ.
        nom: Nom technique du champ (snake_case).
        label: Libelle affiche a l'utilisateur.
        type_champ: Type de champ (texte, photo, signature, etc.).
        obligatoire: Si le champ est requis.
        ordre: Ordre d'affichage.
        placeholder: Texte d'aide dans le champ.
        options: Options pour les champs de selection (radio, select, etc.).
        valeur_defaut: Valeur par defaut.
        validation_regex: Regex de validation optionnelle.
        min_value: Valeur minimale (pour nombres).
        max_value: Valeur maximale (pour nombres).
    """

    nom: str
    label: str
    type_champ: TypeChamp
    id: Optional[int] = None
    obligatoire: bool = False
    ordre: int = 0
    placeholder: Optional[str] = None
    options: List[str] = field(default_factory=list)
    valeur_defaut: Optional[str] = None
    validation_regex: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du champ ne peut pas etre vide")
        self.nom = self.nom.strip().lower().replace(" ", "_")

        if not self.label or not self.label.strip():
            raise ValueError("Le label du champ ne peut pas etre vide")
        self.label = self.label.strip()

        # Validation des options pour certains types
        if self.type_champ in [TypeChamp.RADIO, TypeChamp.SELECT, TypeChamp.MULTI_SELECT]:
            if not self.options:
                raise ValueError(f"Le champ {self.type_champ} necessite des options")


@dataclass
class TemplateFormulaire:
    """
    Entite representant un template de formulaire personnalisable.

    Selon CDC Section 8 - Formulaires Chantier (FOR-01).

    Attributes:
        id: Identifiant unique (None si non persiste).
        nom: Nom du template.
        description: Description du template.
        categorie: Categorie du formulaire.
        champs: Liste des champs du formulaire.
        is_active: Si le template est actif.
        version: Version du template (FOR-08 - historique).
        created_by: ID de l'utilisateur createur.
        created_at: Date de creation.
        updated_at: Date de derniere modification.
    """

    nom: str
    categorie: CategorieFormulaire

    id: Optional[int] = None
    description: Optional[str] = None
    champs: List[ChampTemplate] = field(default_factory=list)
    is_active: bool = True
    version: int = 1
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du template ne peut pas etre vide")
        self.nom = self.nom.strip()

    @property
    def nombre_champs(self) -> int:
        """Retourne le nombre de champs dans le template."""
        return len(self.champs)

    @property
    def champs_obligatoires(self) -> List[ChampTemplate]:
        """Retourne la liste des champs obligatoires."""
        return [c for c in self.champs if c.obligatoire]

    @property
    def a_signature(self) -> bool:
        """Verifie si le template contient un champ signature."""
        return any(c.type_champ.est_signature for c in self.champs)

    @property
    def a_photo(self) -> bool:
        """Verifie si le template contient des champs photo."""
        return any(c.type_champ.est_media for c in self.champs)

    def ajouter_champ(self, champ: ChampTemplate) -> None:
        """
        Ajoute un champ au template.

        Args:
            champ: Le champ a ajouter.
        """
        # Verifier unicite du nom
        if any(c.nom == champ.nom for c in self.champs):
            raise ValueError(f"Un champ avec le nom '{champ.nom}' existe deja")

        # Definir l'ordre si non specifie
        if champ.ordre == 0:
            champ.ordre = len(self.champs) + 1

        self.champs.append(champ)
        self.updated_at = datetime.now()

    def retirer_champ(self, nom_champ: str) -> bool:
        """
        Retire un champ du template.

        Args:
            nom_champ: Nom du champ a retirer.

        Returns:
            True si le champ a ete retire, False sinon.
        """
        initial_count = len(self.champs)
        self.champs = [c for c in self.champs if c.nom != nom_champ]

        if len(self.champs) < initial_count:
            self._reordonner_champs()
            self.updated_at = datetime.now()
            return True
        return False

    def get_champ(self, nom_champ: str) -> Optional[ChampTemplate]:
        """
        Recupere un champ par son nom.

        Args:
            nom_champ: Nom du champ.

        Returns:
            Le champ trouve ou None.
        """
        for champ in self.champs:
            if champ.nom == nom_champ:
                return champ
        return None

    def reordonner_champ(self, nom_champ: str, nouvel_ordre: int) -> None:
        """
        Modifie l'ordre d'un champ.

        Args:
            nom_champ: Nom du champ a deplacer.
            nouvel_ordre: Nouvelle position.
        """
        champ = self.get_champ(nom_champ)
        if champ:
            champ.ordre = nouvel_ordre
            self._reordonner_champs()
            self.updated_at = datetime.now()

    def _reordonner_champs(self) -> None:
        """Reordonne les champs par leur ordre."""
        self.champs.sort(key=lambda c: c.ordre)
        for i, champ in enumerate(self.champs, 1):
            champ.ordre = i

    def desactiver(self) -> None:
        """Desactive le template."""
        self.is_active = False
        self.updated_at = datetime.now()

    def activer(self) -> None:
        """Active le template."""
        self.is_active = True
        self.updated_at = datetime.now()

    def incrementer_version(self) -> None:
        """Incremente la version du template (FOR-08)."""
        self.version += 1
        self.updated_at = datetime.now()

    def update(
        self,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        categorie: Optional[CategorieFormulaire] = None,
    ) -> None:
        """
        Met a jour les informations du template.

        Args:
            nom: Nouveau nom (optionnel).
            description: Nouvelle description (optionnel).
            categorie: Nouvelle categorie (optionnel).
        """
        if nom is not None:
            if not nom.strip():
                raise ValueError("Le nom ne peut pas etre vide")
            self.nom = nom.strip()

        if description is not None:
            self.description = description

        if categorie is not None:
            self.categorie = categorie

        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, TemplateFormulaire):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
