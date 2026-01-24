"""Entité Ressource - Représente un engin/équipement/véhicule.

LOG-01: Référentiel matériel - Liste des engins disponibles (Admin uniquement)
LOG-02: Fiche ressource - Nom, code, photo, couleur, plage horaire par défaut
LOG-10: Option validation N+1 - Activation/désactivation par ressource
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects import CategorieRessource, PlageHoraire


@dataclass
class Ressource:
    """Représente une ressource matérielle de l'entreprise.

    Une ressource peut être un engin, un véhicule ou un équipement
    qui peut être réservé par les utilisateurs pour un chantier.
    """

    id: Optional[int] = None
    nom: str = ""
    code: str = ""
    categorie: CategorieRessource = CategorieRessource.EQUIPEMENT
    photo_url: Optional[str] = None
    couleur: str = "#3B82F6"  # Bleu par défaut
    plage_horaire_defaut: PlageHoraire = field(default_factory=PlageHoraire.par_defaut)
    validation_requise: bool = True
    actif: bool = True
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation à la création."""
        if not self.nom:
            raise ValueError("Le nom de la ressource est obligatoire")
        if not self.code:
            raise ValueError("Le code de la ressource est obligatoire")
        if len(self.code) > 20:
            raise ValueError("Le code ne peut pas dépasser 20 caractères")
        # Si validation_requise n'est pas explicitement définie,
        # utiliser la valeur par défaut de la catégorie
        if self.validation_requise is None:
            self.validation_requise = self.categorie.validation_requise

    def activer(self) -> None:
        """Active la ressource."""
        self.actif = True
        self.updated_at = datetime.utcnow()

    def desactiver(self) -> None:
        """Désactive la ressource (ne peut plus être réservée)."""
        self.actif = False
        self.updated_at = datetime.utcnow()

    def modifier_plage_horaire(self, nouvelle_plage: PlageHoraire) -> None:
        """Modifie la plage horaire par défaut.

        Args:
            nouvelle_plage: La nouvelle plage horaire
        """
        self.plage_horaire_defaut = nouvelle_plage
        self.updated_at = datetime.utcnow()

    def activer_validation(self) -> None:
        """Active la validation N+1 pour cette ressource.

        LOG-10: Option validation N+1.
        """
        self.validation_requise = True
        self.updated_at = datetime.utcnow()

    def desactiver_validation(self) -> None:
        """Désactive la validation N+1 pour cette ressource.

        LOG-10: Option validation N+1.
        """
        self.validation_requise = False
        self.updated_at = datetime.utcnow()

    def peut_etre_reservee(self) -> bool:
        """Vérifie si la ressource peut être réservée."""
        return self.actif

    @property
    def label_complet(self) -> str:
        """Retourne un libellé complet pour l'affichage."""
        return f"[{self.code}] {self.nom}"

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        return {
            "id": self.id,
            "nom": self.nom,
            "code": self.code,
            "categorie": self.categorie.value,
            "photo_url": self.photo_url,
            "couleur": self.couleur,
            "plage_horaire_defaut": self.plage_horaire_defaut.to_dict(),
            "validation_requise": self.validation_requise,
            "actif": self.actif,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
