"""Use Case FermerChantier - Fermeture d'un chantier avec vérifications."""

import logging
from typing import Optional

from ...adapters.controllers import ChantierController
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


class FermerChantierUseCase:
    """
    Cas d'utilisation : Fermeture d'un chantier.

    Vérifie les pré-requis financiers avant fermeture (GAP #8):
    - Achats tous clôturés (facturés ou refusés)
    - Situations de travaux toutes validées ou facturées
    - Avenants en brouillon (avertissement non bloquant)

    Le paramètre force=True (admin uniquement) permet de bypasser les vérifications.

    Attributes:
        controller: Controller pour les opérations chantier.
        cloture_check: Port pour vérifier les pré-requis de clôture (optionnel).
    """

    def __init__(
        self,
        controller: ChantierController,
        cloture_check: Optional[ChantierClotureCheckPort] = None,
    ) -> None:
        """
        Initialise le use case.

        Args:
            controller: Controller des chantiers.
            cloture_check: Port de vérification clôture (optionnel, graceful degradation).
        """
        self.controller = controller
        self.cloture_check = cloture_check

    def execute(
        self,
        chantier_id: int,
        force: bool,
        role: str,
        user_id: int,
    ) -> dict:
        """
        Exécute la fermeture du chantier.

        Args:
            chantier_id: ID du chantier à fermer.
            force: Si True, ignore les vérifications de pré-requis (admin uniquement).
            role: Rôle de l'utilisateur connecté.
            user_id: ID de l'utilisateur connecté.

        Returns:
            dict: Chantier fermé avec avertissements éventuels.

        Raises:
            FermetureForceeNonAutoriseeError: Si force=True sans rôle admin.
            PrerequisClotureNonRemplisError: Si pré-requis non remplis et force=False.
            ChantierNotFoundError: Si le chantier n'existe pas.
            TransitionNonAutoriseeError: Si la transition n'est pas permise.
        """
        # Finding #1: Restreindre force=True au rôle admin
        if force and role != "admin":
            raise FermetureForceeNonAutoriseeError()

        # Finding #4: Log quand force est utilisé
        if force:
            logger.warning(
                "Fermeture forcée du chantier",
                extra={
                    "event": "chantier.fermeture_forcee",
                    "chantier_id": chantier_id,
                    "user_id": user_id,
                },
            )

        # Vérification des pré-requis financiers (mode dégradé si indisponible)
        avertissements = []

        if not force and self.cloture_check is not None:
            check_result = self.cloture_check.verifier_prerequis_cloture(chantier_id)
            if not check_result.peut_fermer:
                raise PrerequisClotureNonRemplisError(
                    blocages=check_result.blocages,
                    avertissements=check_result.avertissements,
                )
            avertissements = check_result.avertissements

        # Fermer le chantier
        result = self.controller.fermer(chantier_id)

        # Inclure les avertissements si présents
        if avertissements:
            logger.info(
                "Chantier %d fermé avec avertissements: %s",
                chantier_id,
                avertissements,
            )
            result["avertissements"] = avertissements

        return result
