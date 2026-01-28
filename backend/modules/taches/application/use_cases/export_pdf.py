"""Use Case ExportTachesPDF - Export PDF des taches (TAC-16)."""

from datetime import datetime
from io import BytesIO
import re

from shared.application.ports import PdfGeneratorPort
from ...domain.repositories import TacheRepository


class ExportTachesPDFUseCase:
    """
    Cas d'utilisation : Exporter les taches en PDF.

    Selon CDC Section 13 - TAC-16: Export rapport PDF.

    Attributes:
        tache_repo: Repository pour les taches.
        pdf_service: Service de génération PDF (utilise templates Jinja2).
    """

    def __init__(
        self,
        tache_repo: TacheRepository,
        pdf_service: PdfGeneratorPort,
    ):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
            pdf_service: Service PDF (injecté via DI).
        """
        self.tache_repo = tache_repo
        self.pdf_service = pdf_service

    def execute(
        self,
        chantier_id: int,
        chantier_nom: str,
        include_completed: bool = True,
    ) -> bytes:
        """
        Genere un PDF des taches d'un chantier.

        Args:
            chantier_id: ID du chantier.
            chantier_nom: Nom du chantier pour le titre (max 200 caractères alphanumériques).
            include_completed: Inclure les taches terminees.

        Returns:
            Contenu PDF en bytes.

        Raises:
            ValueError: Si chantier_nom est invalide (vide, trop long, caractères interdits).
        """
        # Valider chantier_nom (sécurité: prévention XSS/injection)
        if not chantier_nom or not chantier_nom.strip():
            raise ValueError("Le nom du chantier ne peut pas être vide")

        if len(chantier_nom) > 200:
            raise ValueError("Le nom du chantier ne peut pas dépasser 200 caractères")

        # Pattern: lettres, chiffres, espaces, tirets, points, apostrophes (caractères sûrs)
        pattern = r'^[\w\s\-\.\'À-ÿ]+$'
        if not re.match(pattern, chantier_nom):
            raise ValueError(
                "Le nom du chantier contient des caractères non autorisés. "
                "Seuls les lettres, chiffres, espaces, tirets, points et apostrophes sont acceptés."
            )

        # Nettoyer les espaces multiples
        chantier_nom = ' '.join(chantier_nom.split())

        # Recuperer les taches
        taches = self.tache_repo.find_by_chantier(
            chantier_id=chantier_id,
            include_sous_taches=True,
        )

        # Filtrer si necessaire
        if not include_completed:
            taches = [t for t in taches if not t.est_terminee]

        # Calculer les stats
        stats = self.tache_repo.get_stats_chantier(chantier_id)

        # Generer le PDF via le service (utilise templates Jinja2)
        pdf_bytes = self.pdf_service.generate_taches_pdf(
            taches=taches,
            chantier_nom=chantier_nom,
            stats=stats,
        )

        return pdf_bytes

