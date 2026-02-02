"""Adapter pour ChantierClotureCheckPort.

Utilise les repositories du module financier pour verifier
les pre-requis de cloture d'un chantier.

Conforme Clean Architecture:
- Implementation dans Infrastructure layer (shared)
- Utilise les interfaces des repositories financiers
- Pas de dependance sur les implementations concretes
"""

import logging
from typing import Optional

from shared.application.ports.chantier_cloture_check_port import (
    ChantierClotureCheckPort,
    ClotureCheckResult,
)
from modules.financier.domain.repositories import (
    AchatRepository,
    SituationRepository,
    AvenantRepository,
    BudgetRepository,
)
from modules.financier.domain.value_objects.statut_achat import StatutAchat

logger = logging.getLogger(__name__)


class ChantierClotureCheckAdapter(ChantierClotureCheckPort):
    """Implementation concrete du port de verification cloture.

    Verifie les pre-requis financiers avant la fermeture d'un chantier :
    1. Achats : tous doivent etre au statut FACTURE ou REFUSE
    2. Situations : toutes doivent etre validees ou facturees
    3. Avenants : pas de brouillon (avertissement non bloquant)

    Args:
        achat_repo: Repository des achats.
        situation_repo: Repository des situations de travaux.
        avenant_repo: Repository des avenants budgetaires.
        budget_repo: Repository des budgets (pour lier avenants au chantier).
    """

    def __init__(
        self,
        achat_repo: AchatRepository,
        situation_repo: SituationRepository,
        avenant_repo: AvenantRepository,
        budget_repo: BudgetRepository,
    ) -> None:
        self._achat_repo = achat_repo
        self._situation_repo = situation_repo
        self._avenant_repo = avenant_repo
        self._budget_repo = budget_repo

    def verifier_prerequis_cloture(self, chantier_id: int) -> ClotureCheckResult:
        """Verifie si un chantier peut etre ferme.

        Args:
            chantier_id: ID du chantier a verifier.

        Returns:
            ClotureCheckResult avec blocages et avertissements.
        """
        result = ClotureCheckResult()

        self._verifier_achats(chantier_id, result)
        self._verifier_situations(chantier_id, result)
        self._verifier_avenants(chantier_id, result)

        return result

    def _verifier_achats(
        self, chantier_id: int, result: ClotureCheckResult
    ) -> None:
        """Verifie que tous les achats sont au statut terminal.

        Les statuts terminaux acceptes sont FACTURE et REFUSE.
        Tout autre statut (demande, valide, commande, livre)
        constitue un blocage.

        Args:
            chantier_id: ID du chantier.
            result: Resultat a enrichir.
        """
        try:
            achats = self._achat_repo.find_by_chantier(chantier_id)
            statuts_terminaux = {StatutAchat.FACTURE, StatutAchat.REFUSE}
            achats_non_clos = [
                a for a in achats
                if a.statut not in statuts_terminaux
            ]
            if achats_non_clos:
                result.peut_fermer = False
                result.blocages.append(
                    f"{len(achats_non_clos)} achat(s) non cloture(s) "
                    f"(statut attendu : facture ou refuse)"
                )
        except Exception as e:
            logger.warning(
                "Impossible de verifier les achats pour le chantier %d: %s",
                chantier_id,
                e,
            )
            result.avertissements.append(
                "Verification des achats impossible (module financier indisponible)"
            )

    def _verifier_situations(
        self, chantier_id: int, result: ClotureCheckResult
    ) -> None:
        """Verifie que toutes les situations sont validees ou facturees.

        Les statuts acceptes sont 'validee' et 'facturee'.
        Tout autre statut (brouillon, en_validation, emise)
        constitue un blocage.

        Args:
            chantier_id: ID du chantier.
            result: Resultat a enrichir.
        """
        try:
            situations = self._situation_repo.find_by_chantier_id(chantier_id)
            statuts_acceptes = {"validee", "facturee"}
            situations_non_validees = [
                s for s in situations
                if s.statut not in statuts_acceptes
            ]
            if situations_non_validees:
                result.peut_fermer = False
                result.blocages.append(
                    f"{len(situations_non_validees)} situation(s) de travaux "
                    f"non validee(s) (statut attendu : validee ou facturee)"
                )
        except Exception as e:
            logger.warning(
                "Impossible de verifier les situations pour le chantier %d: %s",
                chantier_id,
                e,
            )
            result.avertissements.append(
                "Verification des situations impossible (module financier indisponible)"
            )

    def _verifier_avenants(
        self, chantier_id: int, result: ClotureCheckResult
    ) -> None:
        """Verifie les avenants en brouillon (avertissement non bloquant).

        Les avenants en brouillon ne bloquent pas la fermeture mais
        generent un avertissement pour informer l'utilisateur.

        Args:
            chantier_id: ID du chantier.
            result: Resultat a enrichir.
        """
        try:
            budget = self._budget_repo.find_by_chantier_id(chantier_id)
            if budget is None:
                # Pas de budget = pas d'avenants a verifier
                return

            avenants = self._avenant_repo.find_by_budget_id(budget.id)
            avenants_brouillon = [
                a for a in avenants
                if a.statut == "brouillon"
            ]
            if avenants_brouillon:
                result.avertissements.append(
                    f"{len(avenants_brouillon)} avenant(s) budgetaire(s) "
                    f"en brouillon (non valide(s))"
                )
        except Exception as e:
            logger.warning(
                "Impossible de verifier les avenants pour le chantier %d: %s",
                chantier_id,
                e,
            )
            result.avertissements.append(
                "Verification des avenants impossible (module financier indisponible)"
            )
