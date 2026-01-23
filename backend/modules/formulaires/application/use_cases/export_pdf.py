"""Use Case ExportFormulairePDF - Export PDF d'un formulaire (FOR-09)."""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from ...domain.repositories import (
    FormulaireRempliRepository,
    TemplateFormulaireRepository,
)
from ..dtos import FormulaireRempliDTO


class FormulaireNotFoundError(Exception):
    """Erreur levee si le formulaire n'est pas trouve."""

    pass


class TemplateNotFoundError(Exception):
    """Erreur levee si le template n'est pas trouve."""

    pass


@dataclass
class PDFContent:
    """Contenu structure pour generer un PDF."""

    titre: str
    template_nom: str
    categorie: str
    chantier_id: int
    user_id: int
    statut: str
    champs: List[dict]
    photos: List[dict]
    signature: Optional[dict]
    localisation: Optional[dict]
    soumis_at: Optional[datetime]
    valide_at: Optional[datetime]
    valide_by: Optional[int]
    version: int
    created_at: datetime


class ExportFormulairePDFUseCase:
    """
    Use Case pour exporter un formulaire en PDF.

    Implemente FOR-09 - Export PDF.
    """

    def __init__(
        self,
        formulaire_repo: FormulaireRempliRepository,
        template_repo: TemplateFormulaireRepository,
    ):
        """
        Initialise le use case.

        Args:
            formulaire_repo: Repository des formulaires.
            template_repo: Repository des templates.
        """
        self._formulaire_repo = formulaire_repo
        self._template_repo = template_repo

    def execute(self, formulaire_id: int) -> PDFContent:
        """
        Execute la preparation du contenu PDF.

        Args:
            formulaire_id: ID du formulaire a exporter.

        Returns:
            Le contenu structure pour generer le PDF.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
            TemplateNotFoundError: Si le template n'existe pas.
        """
        # Recuperer le formulaire
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        # Recuperer le template
        template = self._template_repo.find_by_id(formulaire.template_id)
        if not template:
            raise TemplateNotFoundError(
                f"Template {formulaire.template_id} non trouve"
            )

        # Preparer les champs avec labels
        champs_data = []
        for champ in formulaire.champs:
            # Trouver le label dans le template
            template_champ = template.get_champ(champ.nom)
            label = template_champ.label if template_champ else champ.nom

            champs_data.append({
                "nom": champ.nom,
                "label": label,
                "type": champ.type_champ.value,
                "valeur": champ.valeur,
                "timestamp": champ.timestamp,
            })

        # Preparer les photos
        photos_data = [
            {
                "url": photo.url,
                "nom_fichier": photo.nom_fichier,
                "champ_nom": photo.champ_nom,
                "timestamp": photo.timestamp,
                "latitude": photo.latitude,
                "longitude": photo.longitude,
            }
            for photo in formulaire.photos
        ]

        # Preparer la signature
        signature_data = None
        if formulaire.est_signe:
            signature_data = {
                "url": formulaire.signature_url,
                "nom": formulaire.signature_nom,
                "timestamp": formulaire.signature_timestamp,
            }

        # Preparer la localisation
        localisation_data = None
        if formulaire.est_geolocalise:
            localisation_data = {
                "latitude": formulaire.localisation_latitude,
                "longitude": formulaire.localisation_longitude,
            }

        return PDFContent(
            titre=f"Formulaire {template.nom}",
            template_nom=template.nom,
            categorie=template.categorie.label,
            chantier_id=formulaire.chantier_id,
            user_id=formulaire.user_id,
            statut=formulaire.statut.value,
            champs=champs_data,
            photos=photos_data,
            signature=signature_data,
            localisation=localisation_data,
            soumis_at=formulaire.soumis_at,
            valide_at=formulaire.valide_at,
            valide_by=formulaire.valide_by,
            version=formulaire.version,
            created_at=formulaire.created_at,
        )

    def get_dto(self, formulaire_id: int) -> FormulaireRempliDTO:
        """
        Retourne le DTO du formulaire pour export.

        Args:
            formulaire_id: ID du formulaire.

        Returns:
            Le DTO du formulaire.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
        """
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        return FormulaireRempliDTO.from_entity(formulaire)
