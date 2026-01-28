"""Use Case ExportTachesPDF - Export PDF des taches (TAC-16)."""

from datetime import datetime
from io import BytesIO
from typing import Optional

from shared.infrastructure.pdf import PdfGeneratorService
from ...domain.repositories import TacheRepository
from ...domain.value_objects import CouleurProgression


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
        pdf_service: Optional[PdfGeneratorService] = None,
    ):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
            pdf_service: Service PDF (optionnel, créé automatiquement si absent).
        """
        self.tache_repo = tache_repo
        self.pdf_service = pdf_service or PdfGeneratorService()

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
            chantier_nom: Nom du chantier pour le titre.
            include_completed: Inclure les taches terminees.

        Returns:
            Contenu PDF en bytes.
        """
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

