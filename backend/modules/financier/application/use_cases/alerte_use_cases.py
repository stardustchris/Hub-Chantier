"""Use Cases pour la gestion des alertes de depassement budgetaire.

FIN-12: Alertes depassements - verification, acquittement, listing.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..ports.event_bus import EventBus

from ...domain.entities.alerte_depassement import AlerteDepassement
from ...domain.repositories.alerte_repository import AlerteRepository
from ...domain.repositories import (
    BudgetRepository,
    AchatRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.repositories.cout_main_oeuvre_repository import (
    CoutMainOeuvreRepository,
)
from ...domain.repositories.cout_materiel_repository import (
    CoutMaterielRepository,
)
from ...domain.events import DepassementBudgetEvent
from ..dtos.alerte_dtos import AlerteDTO


class AlerteNotFoundError(Exception):
    """Erreur levee quand une alerte n'est pas trouvee."""

    def __init__(self, alerte_id: int):
        self.alerte_id = alerte_id
        super().__init__(f"Alerte {alerte_id} non trouvee")


class VerifierDepassementUseCase:
    """Use case pour verifier les depassements budgetaires d'un chantier.

    FIN-12: Verifie le budget vs les montants engages/realises et cree
    des alertes si les seuils sont atteints.
    """

    def __init__(
        self,
        alerte_repository: AlerteRepository,
        budget_repository: BudgetRepository,
        achat_repository: AchatRepository,
        cout_mo_repository: CoutMainOeuvreRepository,
        cout_materiel_repository: CoutMaterielRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._alerte_repository = alerte_repository
        self._budget_repository = budget_repository
        self._achat_repository = achat_repository
        self._cout_mo_repository = cout_mo_repository
        self._cout_materiel_repository = cout_materiel_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, chantier_id: int) -> List[AlerteDTO]:
        """Verifie les depassements budgetaires et cree les alertes.

        Args:
            chantier_id: L'ID du chantier a verifier.

        Returns:
            Liste des alertes creees.

        Raises:
            ValueError: Si le budget du chantier n'existe pas.
        """
        budget = self._budget_repository.find_by_chantier_id(chantier_id)
        if not budget:
            raise ValueError(
                f"Aucun budget trouve pour le chantier {chantier_id}"
            )

        montant_budget_ht = budget.montant_revise_ht
        seuil_alerte_pct = budget.seuil_alerte_pct

        if montant_budget_ht <= Decimal("0"):
            return []

        # Calculer le montant engage (achats valides + commandes)
        montant_engage = self._achat_repository.somme_by_chantier(
            chantier_id,
            statuts=["valide", "commande", "livre", "facture"],
        )

        # Calculer le montant realise (achats livres/factures + MO + materiel interne)
        # IMPORTANT: cout_materiel = parc materiel INTERNE (amortissement/location).
        # Les achats materiel fournisseurs sont deja dans montant_achats_realises.
        montant_achats_realises = self._achat_repository.somme_by_chantier(
            chantier_id,
            statuts=["livre", "facture"],
        )
        cout_mo = self._cout_mo_repository.calculer_cout_chantier(chantier_id)
        cout_materiel = self._cout_materiel_repository.calculer_cout_chantier(
            chantier_id
        )
        montant_realise = montant_achats_realises + cout_mo + cout_materiel

        alertes_creees = []

        # Verifier seuil engage
        pourcentage_engage = (
            montant_engage * Decimal("100") / montant_budget_ht
        )
        if pourcentage_engage >= seuil_alerte_pct:
            alerte = self._creer_alerte(
                chantier_id=chantier_id,
                budget_id=budget.id,
                type_alerte="seuil_engage",
                message=(
                    f"Le montant engage ({montant_engage} EUR HT) "
                    f"atteint {pourcentage_engage:.1f}% du budget "
                    f"({montant_budget_ht} EUR HT). "
                    f"Seuil d'alerte: {seuil_alerte_pct}%."
                ),
                pourcentage_atteint=pourcentage_engage,
                seuil_configure=seuil_alerte_pct,
                montant_budget_ht=montant_budget_ht,
                montant_atteint_ht=montant_engage,
            )
            alertes_creees.append(alerte)

            # Publier event
            self._event_bus.publish(
                DepassementBudgetEvent(
                    chantier_id=chantier_id,
                    budget_id=budget.id,
                    montant_budget_ht=montant_budget_ht,
                    montant_engage_ht=montant_engage,
                    pourcentage_consomme=pourcentage_engage,
                    seuil_alerte_pct=seuil_alerte_pct,
                )
            )

        # Verifier seuil realise
        pourcentage_realise = (
            montant_realise * Decimal("100") / montant_budget_ht
        )
        if pourcentage_realise >= seuil_alerte_pct:
            alerte = self._creer_alerte(
                chantier_id=chantier_id,
                budget_id=budget.id,
                type_alerte="seuil_realise",
                message=(
                    f"Le montant realise ({montant_realise} EUR HT) "
                    f"atteint {pourcentage_realise:.1f}% du budget "
                    f"({montant_budget_ht} EUR HT). "
                    f"Seuil d'alerte: {seuil_alerte_pct}%."
                ),
                pourcentage_atteint=pourcentage_realise,
                seuil_configure=seuil_alerte_pct,
                montant_budget_ht=montant_budget_ht,
                montant_atteint_ht=montant_realise,
            )
            alertes_creees.append(alerte)

        return alertes_creees

    def _creer_alerte(
        self,
        chantier_id: int,
        budget_id: int,
        type_alerte: str,
        message: str,
        pourcentage_atteint: Decimal,
        seuil_configure: Decimal,
        montant_budget_ht: Decimal,
        montant_atteint_ht: Decimal,
    ) -> AlerteDTO:
        """Cree et persiste une alerte de depassement.

        Args:
            chantier_id: L'ID du chantier.
            budget_id: L'ID du budget.
            type_alerte: Le type d'alerte.
            message: Le message de l'alerte.
            pourcentage_atteint: Pourcentage atteint.
            seuil_configure: Seuil configure.
            montant_budget_ht: Montant du budget HT.
            montant_atteint_ht: Montant atteint HT.

        Returns:
            Le DTO de l'alerte creee.
        """
        alerte = AlerteDepassement(
            chantier_id=chantier_id,
            budget_id=budget_id,
            type_alerte=type_alerte,
            message=message,
            pourcentage_atteint=pourcentage_atteint,
            seuil_configure=seuil_configure,
            montant_budget_ht=montant_budget_ht,
            montant_atteint_ht=montant_atteint_ht,
            created_at=datetime.utcnow(),
        )

        alerte = self._alerte_repository.save(alerte)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="alerte",
                entite_id=alerte.id,
                chantier_id=chantier_id,
                action="creation",
                details=message,
                auteur_id=0,  # Alerte automatique
                created_at=datetime.utcnow(),
            )
        )

        return AlerteDTO.from_entity(alerte)


class AcquitterAlerteUseCase:
    """Use case pour acquitter une alerte de depassement."""

    def __init__(
        self,
        alerte_repository: AlerteRepository,
        journal_repository: JournalFinancierRepository,
    ):
        self._alerte_repository = alerte_repository
        self._journal_repository = journal_repository

    def execute(self, alerte_id: int, user_id: int) -> AlerteDTO:
        """Acquitte une alerte de depassement.

        Args:
            alerte_id: L'ID de l'alerte.
            user_id: L'ID de l'utilisateur qui acquitte.

        Returns:
            Le DTO de l'alerte acquittee.

        Raises:
            AlerteNotFoundError: Si l'alerte n'existe pas.
            ValueError: Si l'alerte est deja acquittee.
        """
        alerte = self._alerte_repository.find_by_id(alerte_id)
        if not alerte:
            raise AlerteNotFoundError(alerte_id)

        alerte.acquitter(user_id)
        self._alerte_repository.acquitter(alerte_id, user_id)

        # Recharger l'alerte apres acquittement
        alerte = self._alerte_repository.find_by_id(alerte_id)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="alerte",
                entite_id=alerte_id,
                chantier_id=alerte.chantier_id,
                action="acquittement",
                details=f"Acquittement de l'alerte {alerte_id}",
                auteur_id=user_id,
                created_at=datetime.utcnow(),
            )
        )

        return AlerteDTO.from_entity(alerte)


class ListAlertesUseCase:
    """Use case pour lister les alertes d'un chantier."""

    def __init__(self, alerte_repository: AlerteRepository):
        self._alerte_repository = alerte_repository

    def execute(
        self,
        chantier_id: int,
        non_acquittees_seulement: bool = False,
    ) -> List[AlerteDTO]:
        """Liste les alertes d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            non_acquittees_seulement: Si True, ne retourne que les non acquittees.

        Returns:
            Liste des DTOs d'alertes.
        """
        if non_acquittees_seulement:
            alertes = self._alerte_repository.find_non_acquittees(chantier_id)
        else:
            alertes = self._alerte_repository.find_by_chantier_id(chantier_id)

        return [AlerteDTO.from_entity(a) for a in alertes]
