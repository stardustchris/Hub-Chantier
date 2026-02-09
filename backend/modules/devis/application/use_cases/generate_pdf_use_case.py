"""Use Case GenerateDevisPDF - Generation du PDF devis client.

DEV-12: Generation PDF devis client.
"""

from ..dtos.devis_dtos import DevisDetailDTO
from ..ports.pdf_generator import IPDFGenerator
from .devis_use_cases import GetDevisUseCase


class GenerateDevisPDFError(Exception):
    """Erreur levee lors de la generation du PDF."""

    def __init__(self, message: str = "Erreur lors de la generation du PDF"):
        self.message = message
        super().__init__(self.message)


class GenerateDevisPDFUseCase:
    """Cas d'utilisation : Generer le PDF d'un devis pour le client.

    Recupere le devis complet via GetDevisUseCase, puis delegue
    la generation du PDF au port IPDFGenerator (Clean Architecture).

    Le PDF genere est une vue CLIENT : il ne contient ni debourses,
    ni marges, ni informations internes.

    Attributes:
        _get_devis_use_case: Use case pour recuperer le devis detaille.
        _pdf_generator: Port pour la generation du PDF.
    """

    def __init__(
        self,
        get_devis_use_case: GetDevisUseCase,
        pdf_generator: IPDFGenerator,
    ):
        """Initialise le use case.

        Args:
            get_devis_use_case: Use case GetDevis (recuperation complete).
            pdf_generator: Implementation du generateur PDF (interface).
        """
        self._get_devis_use_case = get_devis_use_case
        self._pdf_generator = pdf_generator

    def execute(self, devis_id: int) -> tuple[bytes, str]:
        """Genere le PDF du devis.

        Args:
            devis_id: L'ID du devis a generer en PDF.

        Returns:
            Un tuple (contenu_pdf_bytes, nom_fichier).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            GenerateDevisPDFError: Si la generation echoue.
        """
        # 1. Recuperer le devis complet (lots, lignes, ventilation TVA)
        devis_detail: DevisDetailDTO = self._get_devis_use_case.execute(devis_id)

        # 2. Generer le PDF via le port
        try:
            pdf_bytes = self._pdf_generator.generate(devis_detail)
        except Exception as e:
            raise GenerateDevisPDFError(
                f"Erreur lors de la generation du PDF pour le devis {devis_detail.numero}: {e}"
            )

        # 3. Construire le nom de fichier
        filename = f"{devis_detail.numero}.pdf"

        return pdf_bytes, filename
