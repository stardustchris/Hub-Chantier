"""Use Case ExportFormulairePDF - Export PDF d'un formulaire (FOR-09)."""

import base64
import io
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

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

    def export_as_pdf(self, formulaire_id: int) -> PDFExportResult:
        """
        Genere le PDF et retourne le resultat encode en base64.

        Args:
            formulaire_id: ID du formulaire a exporter.

        Returns:
            PDFExportResult avec le contenu base64 du PDF.
        """
        content = self.execute(formulaire_id)
        pdf_bytes = self._generate_pdf_bytes(content)
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        filename = f"formulaire_{formulaire_id}_{content.template_nom.lower().replace(' ', '_')}.pdf"

        return PDFExportResult(
            formulaire_id=formulaire_id,
            filename=filename,
            content_type="application/pdf",
            content_base64=pdf_base64,
        )

    def _generate_pdf_bytes(self, content: PDFContent) -> bytes:
        """Genere les bytes du PDF a partir du contenu structure."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=18,
            spaceAfter=6 * mm,
            textColor=colors.HexColor("#1a1a2e"),
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=13,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
            textColor=colors.HexColor("#16213e"),
        )
        normal_style = styles["Normal"]

        elements = []

        # Titre
        elements.append(Paragraph(content.titre, title_style))

        # Metadata
        statut_label = {
            "brouillon": "Brouillon",
            "soumis": "Soumis",
            "valide": "Valide",
            "refuse": "Refuse",
        }.get(content.statut, content.statut)

        meta_data = [
            ["Categorie", content.categorie],
            ["Statut", statut_label],
            ["Version", str(content.version)],
            ["Cree le", content.created_at.strftime("%d/%m/%Y %H:%M") if content.created_at else "-"],
        ]
        if content.soumis_at:
            meta_data.append(["Soumis le", content.soumis_at.strftime("%d/%m/%Y %H:%M")])
        if content.valide_at:
            meta_data.append(["Valide le", content.valide_at.strftime("%d/%m/%Y %H:%M")])

        meta_table = Table(meta_data, colWidths=[50 * mm, 120 * mm])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#555555")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 4 * mm))
        elements.append(HRFlowable(width="100%", color=colors.HexColor("#e0e0e0")))

        # Champs
        elements.append(Paragraph("Champs du formulaire", heading_style))

        for champ in content.champs:
            label = champ.get("label", champ.get("nom", ""))
            valeur = champ.get("valeur", "")
            if valeur is None or valeur == "":
                valeur = "-"
            else:
                valeur = str(valeur)

            champ_data = [[label, valeur]]
            champ_table = Table(champ_data, colWidths=[60 * mm, 110 * mm])
            champ_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#333333")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
            ]))
            elements.append(champ_table)

        # Photos
        if content.photos:
            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", color=colors.HexColor("#e0e0e0")))
            elements.append(Paragraph(f"Photos ({len(content.photos)})", heading_style))

            for photo in content.photos:
                nom = photo.get("nom_fichier", "photo")
                champ = photo.get("champ_nom", "")
                info = f"{nom}"
                if champ:
                    info += f" (champ: {champ})"
                elements.append(Paragraph(f"• {info}", normal_style))

        # Localisation
        if content.localisation:
            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", color=colors.HexColor("#e0e0e0")))
            elements.append(Paragraph("Localisation", heading_style))
            lat = content.localisation.get("latitude", "")
            lng = content.localisation.get("longitude", "")
            elements.append(Paragraph(f"Latitude: {lat}, Longitude: {lng}", normal_style))

        # Signature
        if content.signature:
            elements.append(Spacer(1, 4 * mm))
            elements.append(HRFlowable(width="100%", color=colors.HexColor("#e0e0e0")))
            elements.append(Paragraph("Signature", heading_style))
            nom_sig = content.signature.get("nom", "")
            ts_sig = content.signature.get("timestamp", "")
            if ts_sig and isinstance(ts_sig, datetime):
                ts_sig = ts_sig.strftime("%d/%m/%Y %H:%M")
            elements.append(Paragraph(f"Signe par: {nom_sig}", normal_style))
            if ts_sig:
                elements.append(Paragraph(f"Le: {ts_sig}", normal_style))

        # Footer
        elements.append(Spacer(1, 10 * mm))
        elements.append(HRFlowable(width="100%", color=colors.HexColor("#cccccc")))
        footer_style = ParagraphStyle(
            "Footer",
            parent=normal_style,
            fontSize=8,
            textColor=colors.HexColor("#999999"),
            spaceBefore=3 * mm,
        )
        elements.append(Paragraph(
            f"Document genere automatiquement - Hub Chantier - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            footer_style,
        ))

        doc.build(elements)
        return buffer.getvalue()

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
