"""Entité Document - Représente un document/fichier dans la GED."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from ..value_objects import NiveauAcces, TypeDocument


# Constantes pour les limites (GED-06, GED-07)
MAX_TAILLE_FICHIER = 10 * 1024 * 1024 * 1024  # 10 Go en bytes
MAX_FICHIERS_UPLOAD = 10  # Maximum de fichiers simultanés


@dataclass
class Document:
    """
    Entité représentant un document dans la GED.

    Selon CDC Section 9 - Gestion Documentaire.

    Attributes:
        id: Identifiant unique.
        chantier_id: Identifiant du chantier associé.
        dossier_id: Identifiant du dossier parent.
        nom: Nom du fichier.
        nom_original: Nom original du fichier uploadé.
        type_document: Type de document (PDF, Image, etc.).
        taille: Taille en bytes.
        chemin_stockage: Chemin de stockage sur le serveur.
        mime_type: Type MIME du fichier.
        niveau_acces: Niveau d'accès minimum (hérité ou spécifique).
        uploaded_by: ID de l'utilisateur qui a uploadé.
        uploaded_at: Date d'upload.
        updated_at: Date de modification.
        description: Description optionnelle.
        version: Numéro de version (GED-08 historique).
    """

    chantier_id: int
    dossier_id: int
    nom: str
    nom_original: str
    chemin_stockage: str
    taille: int
    mime_type: str
    uploaded_by: int
    type_document: TypeDocument = TypeDocument.AUTRE
    niveau_acces: Optional[NiveauAcces] = None  # Si None, hérite du dossier
    id: Optional[int] = None
    description: Optional[str] = None
    version: int = 1
    uploaded_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du document ne peut pas être vide")

        if self.taille < 0:
            raise ValueError("La taille ne peut pas être négative")

        if self.taille > MAX_TAILLE_FICHIER:
            raise ValueError(f"La taille dépasse la limite de 10 Go (GED-07)")

        self.nom = self.nom.strip()

        # Détecter le type de document si non spécifié
        if self.type_document == TypeDocument.AUTRE:
            extension = self._get_extension()
            if extension:
                self.type_document = TypeDocument.from_extension(extension)

    def _get_extension(self) -> str:
        """Retourne l'extension du fichier."""
        if "." in self.nom:
            return "." + self.nom.rsplit(".", 1)[-1].lower()
        return ""

    @property
    def extension(self) -> str:
        """Retourne l'extension du fichier."""
        return self._get_extension()

    @property
    def taille_formatee(self) -> str:
        """Retourne la taille formatée (Ko, Mo, Go)."""
        if self.taille < 1024:
            return f"{self.taille} o"
        elif self.taille < 1024 * 1024:
            return f"{self.taille / 1024:.1f} Ko"
        elif self.taille < 1024 * 1024 * 1024:
            return f"{self.taille / (1024 * 1024):.1f} Mo"
        else:
            return f"{self.taille / (1024 * 1024 * 1024):.2f} Go"

    @property
    def icone(self) -> str:
        """Retourne l'icône associée au type de document."""
        return self.type_document.icone

    def peut_acceder(
        self,
        role_utilisateur: str,
        user_id: Optional[int] = None,
        autorisations_nominatives: Optional[List[int]] = None,
        niveau_dossier: Optional[NiveauAcces] = None,
    ) -> bool:
        """
        Vérifie si un utilisateur peut accéder au document.

        Args:
            role_utilisateur: Le rôle de l'utilisateur.
            user_id: L'ID de l'utilisateur.
            autorisations_nominatives: Liste des user_ids avec accès spécifique.
            niveau_dossier: Niveau d'accès du dossier parent (si pas de niveau propre).

        Returns:
            True si l'utilisateur a accès.
        """
        # L'uploadeur a toujours accès
        if user_id and user_id == self.uploaded_by:
            return True

        # Vérifier les autorisations nominatives (GED-05)
        if autorisations_nominatives and user_id in autorisations_nominatives:
            return True

        # Utiliser le niveau propre ou celui du dossier
        niveau_effectif = self.niveau_acces or niveau_dossier or NiveauAcces.COMPAGNON
        return niveau_effectif.peut_acceder(role_utilisateur)

    def renommer(self, nouveau_nom: str) -> None:
        """
        Renomme le document.

        Args:
            nouveau_nom: Le nouveau nom.

        Raises:
            ValueError: Si le nom est vide.
        """
        if not nouveau_nom or not nouveau_nom.strip():
            raise ValueError("Le nom du document ne peut pas être vide")
        self.nom = nouveau_nom.strip()
        self.updated_at = datetime.now()

    def deplacer(self, nouveau_dossier_id: int) -> None:
        """
        Déplace le document vers un autre dossier.

        Args:
            nouveau_dossier_id: L'ID du nouveau dossier.
        """
        self.dossier_id = nouveau_dossier_id
        self.updated_at = datetime.now()

    def changer_niveau_acces(self, nouveau_niveau: Optional[NiveauAcces]) -> None:
        """
        Change le niveau d'accès du document.

        Args:
            nouveau_niveau: Le nouveau niveau (None pour hériter du dossier).
        """
        self.niveau_acces = nouveau_niveau
        self.updated_at = datetime.now()

    def incrementer_version(self) -> None:
        """Incrémente le numéro de version."""
        self.version += 1
        self.updated_at = datetime.now()

    @staticmethod
    def valider_taille(taille: int) -> bool:
        """
        Valide la taille d'un fichier.

        Args:
            taille: Taille en bytes.

        Returns:
            True si la taille est valide.
        """
        return 0 <= taille <= MAX_TAILLE_FICHIER

    @staticmethod
    def valider_extension(extension: str) -> bool:
        """
        Valide l'extension d'un fichier.

        Args:
            extension: L'extension à valider.

        Returns:
            True si l'extension est acceptée.
        """
        ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        return ext in TypeDocument.list_extensions_acceptees()

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, Document):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
