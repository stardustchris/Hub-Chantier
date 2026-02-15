"""Use Case GenerateInterventionPDF - Generation du rapport PDF d'intervention.

INT-14: Rapport PDF - Generation automatique avec tous les details.
INT-15: Selection posts pour rapport - Choisir les elements a inclure.
"""

from dataclasses import dataclass
from typing import Optional, List

from ...domain.entities import Intervention, InterventionMessage, SignatureIntervention, AffectationIntervention
from ...domain.repositories import (
    InterventionRepository,
    InterventionMessageRepository,
    SignatureInterventionRepository,
    AffectationInterventionRepository,
)
from shared.application.ports import PdfGeneratorPort


@dataclass
class InterventionPDFOptionsDTO:
    """Options de generation du rapport PDF d'intervention.

    INT-15: Permet de choisir les sections a inclure dans le rapport.

    Attributes:
        inclure_photos: Inclure les photos des messages marques pour le rapport.
        inclure_signatures: Inclure les signatures (client + technicien).
        inclure_travaux: Inclure la section travaux realises.
        inclure_anomalies: Inclure la section anomalies constatees.
        inclure_messages: Inclure les messages/commentaires du fil d'activite.
    """

    inclure_photos: bool = True
    inclure_signatures: bool = True
    inclure_travaux: bool = True
    inclure_anomalies: bool = True
    inclure_messages: bool = True


class GenerateInterventionPDFError(Exception):
    """Erreur levee lors de la generation du PDF d'intervention."""

    def __init__(self, message: str = "Erreur lors de la generation du rapport PDF"):
        self.message = message
        super().__init__(self.message)


class GenerateInterventionPDFUseCase:
    """Cas d'utilisation : Generer le rapport PDF d'une intervention.

    INT-14: Rapport PDF - Generation automatique.
    INT-15: Selection posts pour rapport.

    Recupere l'intervention, ses techniciens, messages (filtre inclure_rapport)
    et signatures, puis delegue la generation au port PdfGeneratorPort.

    Attributes:
        _intervention_repo: Repository pour acceder aux interventions.
        _affectation_repo: Repository pour acceder aux affectations techniciens.
        _message_repo: Repository pour acceder aux messages.
        _signature_repo: Repository pour acceder aux signatures.
        _pdf_generator: Port pour la generation du PDF.
    """

    def __init__(
        self,
        intervention_repo: InterventionRepository,
        affectation_repo: AffectationInterventionRepository,
        message_repo: InterventionMessageRepository,
        signature_repo: SignatureInterventionRepository,
        pdf_generator: PdfGeneratorPort,
    ):
        """Initialise le use case.

        Args:
            intervention_repo: Repository interventions.
            affectation_repo: Repository affectations techniciens.
            message_repo: Repository messages.
            signature_repo: Repository signatures.
            pdf_generator: Implementation du generateur PDF (interface).
        """
        self._intervention_repo = intervention_repo
        self._affectation_repo = affectation_repo
        self._message_repo = message_repo
        self._signature_repo = signature_repo
        self._pdf_generator = pdf_generator

    def execute(
        self,
        intervention_id: int,
        options: Optional[InterventionPDFOptionsDTO] = None,
    ) -> tuple[bytes, str]:
        """Genere le rapport PDF de l'intervention.

        Args:
            intervention_id: L'ID de l'intervention.
            options: Options de generation (sections a inclure). Defaut: tout inclure.

        Returns:
            Un tuple (contenu_pdf_bytes, nom_fichier).

        Raises:
            ValueError: Si l'intervention n'existe pas.
            GenerateInterventionPDFError: Si la generation echoue.
        """
        if options is None:
            options = InterventionPDFOptionsDTO()

        # 1. Recuperer l'intervention
        intervention = self._intervention_repo.get_by_id(intervention_id)
        if not intervention:
            raise ValueError(f"Intervention {intervention_id} non trouvee")

        # 2. Recuperer les techniciens affectes
        techniciens = self._affectation_repo.list_by_intervention(intervention_id)

        # 3. Recuperer les messages marques pour le rapport (INT-15)
        messages: List[InterventionMessage] = []
        if options.inclure_messages or options.inclure_photos:
            messages = self._message_repo.list_for_rapport(intervention_id)

            # Filtrage additionnel selon les options
            if not options.inclure_photos:
                messages = [m for m in messages if not m.a_photos]
            if not options.inclure_messages:
                messages = [m for m in messages if m.a_photos]

        # 4. Recuperer les signatures
        signatures: List[SignatureIntervention] = []
        if options.inclure_signatures:
            signatures = self._signature_repo.list_by_intervention(intervention_id)

        # 5. Generer le PDF
        try:
            pdf_bytes = self._pdf_generator.generate_intervention_pdf(
                intervention=intervention,
                techniciens=techniciens,
                messages=messages,
                signatures=signatures,
                options=options,
            )
        except Exception as e:
            raise GenerateInterventionPDFError(
                f"Erreur lors de la generation du rapport PDF pour "
                f"l'intervention {intervention.code}: {e}"
            )

        # 6. Construire le nom de fichier
        code = intervention.code or f"INT-{intervention_id}"
        filename = f"rapport_{code}.pdf"

        return pdf_bytes, filename
