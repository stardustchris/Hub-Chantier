"""Use Case ExportFormulairePDF - Export PDF d'un formulaire (FOR-09)."""

from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict, Callable
from datetime import datetime

from shared.infrastructure.pdf import PdfGeneratorService

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
    soumis_at: Optional[datetime]
    valide_at: Optional[datetime]
    valide_by: Optional[int]
    version: int
    created_at: datetime
    # Enrichment fields
    chantier_nom: Optional[str] = None
    user_nom: Optional[str] = None
    valideur_nom: Optional[str] = None


@dataclass
class PDFExportResult:
    """Resultat de l'export PDF."""

    formulaire_id: int
    filename: str
    content_type: str
    content_base64: str


class ExportFormulairePDFUseCase:
    """
    Use Case pour exporter un formulaire en PDF.

    Implemente FOR-09 - Export PDF.
    """

    def __init__(
        self,
        formulaire_repo: FormulaireRempliRepository,
        template_repo: TemplateFormulaireRepository,
        pdf_service: Optional[PdfGeneratorService] = None,
    ):
        self._formulaire_repo = formulaire_repo
        self._template_repo = template_repo
        self.pdf_service = pdf_service or PdfGeneratorService()

    def execute(self, formulaire_id: int) -> PDFContent:
        """Prepare le contenu structure pour le PDF."""
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
            soumis_at=formulaire.soumis_at,
            valide_at=formulaire.valide_at,
            valide_by=formulaire.valide_by,
            version=formulaire.version,
            created_at=formulaire.created_at,
        )

    def export_as_pdf(
        self,
        formulaire_id: int,
        resolve_names: Callable | None = None,
    ) -> PDFExportResult:
        """Genere le PDF et retourne le resultat encode en base64."""
        content = self.execute(formulaire_id)

        # Enrichir avec les noms si le resolver est disponible
        if resolve_names:
            names = resolve_names(content.chantier_id, content.user_id, content.valide_by)
            content.chantier_nom = names.get("chantier_nom")
            content.user_nom = names.get("user_nom")
            content.valideur_nom = names.get("valideur_nom")

        pdf_bytes = self._generate_pdf_bytes_with_service(content)
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        filename = f"formulaire_{formulaire_id}_{content.template_nom.lower().replace(' ', '_')}.pdf"

        return PDFExportResult(
            formulaire_id=formulaire_id,
            filename=filename,
            content_type="application/pdf",
            content_base64=pdf_base64,
        )

    def _generate_pdf_bytes_with_service(self, content: PDFContent) -> bytes:
        """Génère les bytes du PDF en utilisant le service PDF centralisé.

        Cette fonction remplace l'ancienne _generate_pdf_bytes (196 lignes)
        par un appel au PdfGeneratorService qui utilise des templates Jinja2.
        """
        # Préparer les champs pour le template
        champs_formatted = self._format_champs_for_template(content.champs, content.photos)

        # Appeler le service PDF
        return self.pdf_service.generate_formulaire_pdf(
            titre=content.titre,
            chantier_nom=content.chantier_nom,
            categorie=content.categorie,
            statut=content.statut,
            version=content.version,
            user_nom=content.user_nom,
            created_at=content.created_at,
            soumis_at=content.soumis_at,
            valide_at=content.valide_at,
            valideur_nom=content.valideur_nom,
            champs=champs_formatted,
            commentaires=content.commentaires if hasattr(content, 'commentaires') else None,
        )

    def _format_champs_for_template(
        self,
        champs: List[Dict[str, Any]],
        photos: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Formate les champs du formulaire pour le template Jinja2.

        Args:
            champs: Liste des champs du formulaire.
            photos: Liste des photos (optionnel).

        Returns:
            Liste des champs formatés avec leurs labels, types et valeurs.
        """
        formatted_champs = []

        # Mapping des types de champs
        type_labels = {
            "texte": "Texte",
            "nombre": "Nombre",
            "date": "Date",
            "heure": "Heure",
            "textarea": "Texte long",
            "checkbox": "Cases à cocher",
            "radio": "Choix unique",
            "select": "Liste déroulante",
            "photo": "Photo",
            "signature": "Signature",
        }

        for champ in champs:
            label = champ.get("label", champ.get("nom", ""))
            type_champ = champ.get("type", "texte")
            valeur = champ.get("valeur")

            formatted_champ = {
                "label": label,
                "type": type_champ,
                "type_label": type_labels.get(type_champ, type_champ.capitalize()),
                "valeur": str(valeur) if valeur is not None and valeur != "" else None,
                "options": champ.get("options", []),
                "valeurs_selectionnees": champ.get("valeurs_selectionnees", []),
            }

            # Pour les photos, ajouter les URLs
            if type_champ == "photo" and photos:
                champ_photos = [
                    {
                        "url": photo.get("url", ""),
                        "nom": photo.get("nom_fichier", "photo"),
                    }
                    for photo in photos
                    if photo.get("champ_nom") == champ.get("nom")
                ]
                formatted_champ["photos"] = champ_photos

            # Pour les signatures
            if type_champ == "signature" and champ.get("signature"):
                sig = champ["signature"]
                formatted_champ["signature_url"] = sig.get("url", "")
                formatted_champ["signature_signataire"] = sig.get("nom", "")
                formatted_champ["signature_date"] = (
                    sig["timestamp"].strftime("%d/%m/%Y %H:%M")
                    if sig.get("timestamp") and isinstance(sig["timestamp"], datetime)
                    else ""
                )

            formatted_champs.append(formatted_champ)

        return formatted_champs

    def _generate_pdf_bytes(self, content: PDFContent) -> bytes:
        """Genere les bytes du PDF a partir du contenu structure.

        DEPRECATED: Cette méthode est obsolète. Utilisez _generate_pdf_bytes_with_service().
        Conservée temporairement pour compatibilité arrière.
        """
        # Rediriger vers la nouvelle implémentation
        return self._generate_pdf_bytes_with_service(content)

    def get_dto(self, formulaire_id: int) -> FormulaireRempliDTO:
        """Retourne le DTO du formulaire pour export."""
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        return FormulaireRempliDTO.from_entity(formulaire)
