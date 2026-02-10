"""Port pour la generation de PDF devis client.

DEV-12: Generation PDF devis client.

Ce port definit l'interface abstraite pour la generation de PDF.
L'implementation concrete (fpdf2, reportlab, etc.) est dans infrastructure/pdf/.
"""

from abc import ABC, abstractmethod

from ..dtos.devis_dtos import DevisDetailDTO


class IPDFGenerator(ABC):
    """Interface abstraite pour la generation de PDF devis.

    Le use case utilise cette interface sans connaitre l'implementation
    concrete (respect Clean Architecture - Dependency Inversion).
    """

    @abstractmethod
    def generate(self, devis: DevisDetailDTO) -> bytes:
        """Genere un PDF a partir des donnees du devis.

        Args:
            devis: Le DTO detaille du devis (vue client, sans debourses/marges).

        Returns:
            Le contenu du PDF en bytes.
        """
        ...
