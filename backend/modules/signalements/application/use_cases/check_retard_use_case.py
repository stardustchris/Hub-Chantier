"""Use Case CheckSignalementsRetardUseCase - Alertes retard signalements (SIG-16).

Vérifie les signalements non traités dans les délais et déclenche
les alertes et escalades correspondantes.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ...domain.entities import Signalement, EscaladeHistorique
from ...domain.repositories import SignalementRepository, EscaladeRepository
from ...domain.services import EscaladeService
from ...domain.services.escalade_service import EscaladeInfo

logger = logging.getLogger(__name__)


@dataclass
class RetardAlertResult:
    """Résultat d'une vérification de retard."""

    signalements_verifies: int = 0
    alertes_emises: int = 0
    escalades_effectuees: int = 0
    erreurs: int = 0
    details: List[dict] = field(default_factory=list)


class CheckSignalementsRetardUseCase:
    """
    Use case pour vérifier les signalements en retard (SIG-16).

    Exécuté toutes les 15 minutes par le scheduler APScheduler.
    Détecte les signalements dont le délai est dépassé ou approche
    et déclenche les escalades correspondantes.
    """

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        escalade_repository: EscaladeRepository,
        escalade_service: Optional[EscaladeService] = None,
    ):
        self._signalement_repo = signalement_repository
        self._escalade_repo = escalade_repository
        self._escalade_service = escalade_service or EscaladeService()

    def execute(self) -> RetardAlertResult:
        """
        Vérifie tous les signalements actifs et déclenche les alertes.

        Returns:
            RetardAlertResult avec les statistiques d'exécution.
        """
        result = RetardAlertResult()

        try:
            # Récupérer les signalements actifs à potentiellement escalader
            signalements = self._signalement_repo.find_a_escalader(
                seuil_pourcentage=50.0,
            )
            result.signalements_verifies = len(signalements)

            if not signalements:
                logger.debug("Aucun signalement à escalader")
                return result

            # Déterminer les escalades nécessaires
            escalades = self._escalade_service.determiner_escalades(signalements)

            for escalade_info in escalades:
                try:
                    self._traiter_escalade(escalade_info, result)
                except Exception as e:
                    logger.error(
                        f"Erreur escalade signalement #{escalade_info.signalement.id}: {e}",
                        exc_info=True,
                    )
                    result.erreurs += 1

        except Exception as e:
            logger.error(f"Erreur vérification retards: {e}", exc_info=True)
            result.erreurs += 1

        logger.info(
            f"Vérification retards terminée: "
            f"{result.signalements_verifies} vérifiés, "
            f"{result.escalades_effectuees} escaladés, "
            f"{result.erreurs} erreurs"
        )

        return result

    def _traiter_escalade(
        self,
        escalade_info: EscaladeInfo,
        result: RetardAlertResult,
    ) -> None:
        """
        Traite une escalade individuelle.

        Enregistre l'historique et met à jour le signalement.

        Args:
            escalade_info: Informations sur l'escalade à effectuer.
            result: Résultat en cours d'accumulation.
        """
        sig = escalade_info.signalement

        # Vérifier si cette escalade n'a pas déjà été faite
        last_escalade = self._escalade_repo.find_last_by_signalement(sig.id)
        if last_escalade and last_escalade.niveau == escalade_info.niveau:
            logger.debug(
                f"Escalade {escalade_info.niveau} déjà effectuée pour #{sig.id}"
            )
            return

        # Enregistrer l'historique d'escalade
        historique = EscaladeHistorique(
            signalement_id=sig.id,
            niveau=escalade_info.niveau,
            pourcentage_temps=escalade_info.pourcentage_temps,
            destinataires_roles=escalade_info.destinataires_roles,
            message=self._escalade_service.generer_message_escalade(
                escalade_info, f"Chantier #{sig.chantier_id}"
            ),
        )
        self._escalade_repo.save(historique)

        # Mettre à jour le compteur d'escalade du signalement
        sig.enregistrer_escalade()
        self._signalement_repo.save(sig)

        result.escalades_effectuees += 1
        result.alertes_emises += 1
        result.details.append({
            "signalement_id": sig.id,
            "niveau": escalade_info.niveau,
            "pourcentage_temps": escalade_info.pourcentage_temps,
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(
            f"Escalade {escalade_info.niveau} pour signalement #{sig.id} "
            f"(temps: {escalade_info.pourcentage_temps:.0f}%)"
        )
