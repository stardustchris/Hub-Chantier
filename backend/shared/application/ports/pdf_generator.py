"""Port (interface) pour la génération de PDF.

Ce port définit le contrat pour les services de génération de PDF,
permettant l'inversion de dépendance selon Clean Architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class PdfGeneratorPort(ABC):
    """Interface pour les services de génération de PDF.

    Cette interface permet aux use cases de dépendre d'une abstraction
    plutôt que d'une implémentation concrète.

    Example:
        >>> class MyPdfGenerator(PdfGeneratorPort):
        ...     def generate_taches_pdf(self, taches, chantier_nom, stats):
        ...         return b"PDF content"
    """

    @abstractmethod
    def generate_taches_pdf(
        self,
        taches: list,
        chantier_nom: str,
        stats: Dict[str, Any],
    ) -> bytes:
        """Génère un PDF de rapport de tâches.

        Args:
            taches: Liste des tâches à inclure dans le rapport.
            chantier_nom: Nom du chantier pour le titre.
            stats: Statistiques globales (total, terminées, heures).

        Returns:
            Contenu PDF en bytes.

        Raises:
            ValueError: Si les paramètres sont invalides.
            RuntimeError: Si la génération PDF échoue.
        """
        pass
