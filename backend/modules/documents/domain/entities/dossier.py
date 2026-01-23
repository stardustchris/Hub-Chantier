"""Entité Dossier - Représente un dossier dans l'arborescence GED."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from ..value_objects import NiveauAcces, DossierType


@dataclass
class Dossier:
    """
    Entité représentant un dossier dans la GED.

    Selon CDC Section 9 - Gestion Documentaire (GED-02, GED-04).

    Attributes:
        id: Identifiant unique.
        chantier_id: Identifiant du chantier associé.
        nom: Nom du dossier.
        type_dossier: Type de dossier (Plans, Sécurité, etc.).
        niveau_acces: Niveau d'accès minimum requis (GED-04).
        parent_id: ID du dossier parent (pour arborescence).
        ordre: Ordre d'affichage.
        created_at: Date de création.
        updated_at: Date de modification.
    """

    chantier_id: int
    nom: str
    type_dossier: DossierType = DossierType.CUSTOM
    niveau_acces: NiveauAcces = NiveauAcces.COMPAGNON
    id: Optional[int] = None
    parent_id: Optional[int] = None
    ordre: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du dossier ne peut pas être vide")
        self.nom = self.nom.strip()

    @property
    def chemin_complet(self) -> str:
        """Retourne le chemin avec le numéro de type si applicable."""
        if self.type_dossier != DossierType.CUSTOM:
            return f"{self.type_dossier.numero} - {self.nom}"
        return self.nom

    def peut_acceder(self, role_utilisateur: str, user_id: Optional[int] = None,
                      autorisations_nominatives: Optional[List[int]] = None) -> bool:
        """
        Vérifie si un utilisateur peut accéder au dossier.

        Args:
            role_utilisateur: Le rôle de l'utilisateur.
            user_id: L'ID de l'utilisateur (pour autorisations nominatives).
            autorisations_nominatives: Liste des user_ids avec accès spécifique.

        Returns:
            True si l'utilisateur a accès.
        """
        # Vérifier d'abord les autorisations nominatives (GED-05)
        if autorisations_nominatives and user_id in autorisations_nominatives:
            return True

        # Vérifier selon le niveau d'accès (GED-04)
        return self.niveau_acces.peut_acceder(role_utilisateur)

    def changer_niveau_acces(self, nouveau_niveau: NiveauAcces) -> None:
        """
        Change le niveau d'accès du dossier.

        Args:
            nouveau_niveau: Le nouveau niveau d'accès.
        """
        self.niveau_acces = nouveau_niveau
        self.updated_at = datetime.now()

    def renommer(self, nouveau_nom: str) -> None:
        """
        Renomme le dossier.

        Args:
            nouveau_nom: Le nouveau nom.

        Raises:
            ValueError: Si le nom est vide.
        """
        if not nouveau_nom or not nouveau_nom.strip():
            raise ValueError("Le nom du dossier ne peut pas être vide")
        self.nom = nouveau_nom.strip()
        self.updated_at = datetime.now()

    def deplacer(self, nouveau_parent_id: Optional[int]) -> None:
        """
        Déplace le dossier vers un autre parent.

        Args:
            nouveau_parent_id: L'ID du nouveau parent (None pour racine).
        """
        self.parent_id = nouveau_parent_id
        self.updated_at = datetime.now()

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, Dossier):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
