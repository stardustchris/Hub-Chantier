"""Use Case FermerChantier - Fermeture d'un chantier avec vérifications."""

import logging
from typing import Optional, List

from ..dtos import ChantierDTO
from shared.application.ports.chantier_cloture_check_port import ChantierClotureCheckPort

logger = logging.getLogger(__name__)


class PrerequisClotureNonRemplisError(Exception):
    """Exception levée quand les prérequis de clôture ne sont pas remplis."""

    def __init__(self, blocages: list, avertissements: list) -> None:
        self.blocages = blocages
        self.avertissements = avertissements
        self.message = "Impossible de fermer le chantier : pré-requis non remplis"
        super().__init__(self.message)


class FermetureForceeNonAutoriseeError(Exception):
    """Exception levée quand force=True est utilisé sans rôle admin."""

    def __init__(self) -> None:
        self.message = "Seul un administrateur peut forcer la fermeture d'un chantier"
        super().__init__(self.message)


class FermerChantierResult:
    """Résultat de la fermeture d'un chantier."""

    def __init__(self, chantier: ChantierDTO, avertissements: Optional[List[str]] = None) -> None:
        self.chantier = chantier
        self.avertissements = avertissements or []


class FermerChantierUseCase:
    """
    Cas d'utilisation : Fermeture d'un chantier.

    Vérifie les pré-requis financiers avant fermeture (GAP #8):
    - Achats tous clôturés (facturés ou refusés)
    - Situations de travaux toutes validées ou facturées
    - Avenants en brouillon (avertissement non bloquant)

    Le paramètre force=True (admin uniquement) permet de bypasser les vérifications.
    """

    def __init__(
        self,
        change_statut_use_case: "ChangeStatutUseCase",
        cloture_check: Optional[ChantierClotureCheckPort] = None,
    ) -> None:
        self.change_statut_use_case = change_statut_use_case
        self.cloture_check = cloture_check

    def execute(
        self,
        chantier_id: int,
        force: bool,
        role: str,
        user_id: int,
    ) -> FermerChantierResult:
        """
        Exécute la fermeture du chantier.

        Returns:
            FermerChantierResult contenant le ChantierDTO et les avertissements.

        Raises:
            FermetureForceeNonAutoriseeError: Si force=True sans rôle admin.
            PrerequisClotureNonRemplisError: Si pré-requis non remplis et force=False.
        """
        if force and role != "admin":
            raise FermetureForceeNonAutoriseeError()

        if force:
            logger.warning(
                "Fermeture forcée du chantier",
                extra={
                    "event": "chantier.fermeture_forcee",
                    "chantier_id": chantier_id,
                    "user_id": user_id,
                },
            )

        avertissements: List[str] = []

        if not force and self.cloture_check is not None:
            check_result = self.cloture_check.verifier_prerequis_cloture(chantier_id)
            if not check_result.peut_fermer:
                raise PrerequisClotureNonRemplisError(
                    blocages=check_result.blocages,
                    avertissements=check_result.avertissements,
                )
            avertissements = check_result.avertissements

        dto = self.change_statut_use_case.fermer(chantier_id)

        if avertissements:
            logger.info(
                "Chantier %d fermé avec avertissements: %s",
                chantier_id,
                avertissements,
            )

        return FermerChantierResult(chantier=dto, avertissements=avertissements)
