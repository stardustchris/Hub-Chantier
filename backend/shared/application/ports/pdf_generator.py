"""Port (interface) pour la génération de PDF.

Ce port définit le contrat pour les services de génération de PDF,
permettant l'inversion de dépendance selon Clean Architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from modules.interventions.domain.entities import (
        Intervention,
        AffectationIntervention,
        InterventionMessage,
        SignatureIntervention,
    )
    from modules.interventions.application.use_cases.pdf_use_cases import (
        InterventionPDFOptionsDTO,
    )


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

    @abstractmethod
    def generate_intervention_pdf(
        self,
        intervention: "Intervention",
        techniciens: List["AffectationIntervention"],
        messages: List["InterventionMessage"],
        signatures: List["SignatureIntervention"],
        options: Optional["InterventionPDFOptionsDTO"] = None,
    ) -> bytes:
        """Genere un PDF de rapport d'intervention.

        INT-14: Rapport PDF - Generation automatique.

        Args:
            intervention: L'entite intervention.
            techniciens: Liste des techniciens affectes.
            messages: Messages a inclure dans le rapport (filtre inclure_rapport).
            signatures: Signatures (client + technicien).
            options: Options de generation (sections a inclure).

        Returns:
            Contenu PDF en bytes.

        Raises:
            ValueError: Si les parametres sont invalides.
            RuntimeError: Si la generation PDF echoue.
        """
        pass
