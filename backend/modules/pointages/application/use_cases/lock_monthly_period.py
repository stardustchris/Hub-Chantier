"""Use Case: Verrouiller une période de paie mensuelle (GAP-FDH-009)."""

from typing import Optional, List

from ...domain.value_objects import PeriodePaie
from ...domain.events.periode_paie_locked import PeriodePaieLockedEvent
from ..dtos.lock_period_dtos import (
    LockMonthlyPeriodDTO,
    LockMonthlyPeriodResultDTO,
)
from ..ports import EventBus, NullEventBus


class LockMonthlyPeriodError(Exception):
    """Exception pour les erreurs de verrouillage de période."""

    def __init__(self, message: str = "Erreur lors du verrouillage de la période"):
        self.message = message
        super().__init__(self.message)


class LockMonthlyPeriodUseCase:
    """
    Cas d'utilisation : Verrouillage d'une période de paie (GAP-FDH-009).

    Permet de verrouiller manuellement ou automatiquement (via scheduler)
    une période de paie mensuelle. Après le verrouillage, aucun pointage
    de ce mois ne peut plus être modifié.

    Le verrouillage automatique est déclenché par un scheduler APScheduler
    le dernier vendredi du mois précédant la dernière semaine, à 23:59.

    Attributes:
        event_bus: Bus d'événements pour publier les events.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialise le use case.

        Args:
            event_bus: Bus d'événements (optionnel).
        """
        self.event_bus = event_bus or NullEventBus()

    def execute(
        self,
        dto: LockMonthlyPeriodDTO,
        auto_locked: bool = True,
        locked_by: Optional[int] = None,
    ) -> LockMonthlyPeriodResultDTO:
        """
        Exécute le verrouillage de la période de paie.

        Args:
            dto: Les données de verrouillage.
            auto_locked: True si déclenchement automatique (scheduler).
            locked_by: ID de l'utilisateur (si verrouillage manuel).

        Returns:
            LockMonthlyPeriodResultDTO contenant le résultat du verrouillage.

        Raises:
            LockMonthlyPeriodError: Si les paramètres sont invalides.
        """
        # 1. Validation des paramètres
        if dto.month < 1 or dto.month > 12:
            raise LockMonthlyPeriodError("Le mois doit être compris entre 1 et 12")
        if dto.year < 2000 or dto.year > 2100:
            raise LockMonthlyPeriodError("L'année doit être comprise entre 2000 et 2100")

        # 2. Calcule la date de verrouillage effective
        lockdown_date = PeriodePaie.get_lockdown_date(dto.year, dto.month)

        # 3. Publie l'événement de verrouillage
        event = PeriodePaieLockedEvent(
            year=dto.year,
            month=dto.month,
            lockdown_date=lockdown_date,
            auto_locked=auto_locked,
            locked_by=locked_by,
        )
        self.event_bus.publish(event)

        # 4. Récupère la liste des utilisateurs à notifier
        # (admins + conducteurs)
        notified_users = self._get_users_to_notify()

        # 5. Construit le résultat
        month_label = self._get_month_label(dto.month)
        message = (
            f"Période de paie {month_label} {dto.year} verrouillée. "
            f"Date de verrouillage: {lockdown_date.strftime('%d/%m/%Y')}. "
            f"Aucune modification de pointage n'est possible après cette date."
        )

        return LockMonthlyPeriodResultDTO(
            year=dto.year,
            month=dto.month,
            lockdown_date=lockdown_date,
            success=True,
            message=message,
            notified_users=notified_users,
        )

    def _get_users_to_notify(self) -> List[int]:
        """
        Récupère les IDs des utilisateurs à notifier (admins + conducteurs).

        Returns:
            Liste des IDs utilisateurs.

        Note:
            Pour l'instant retourne une liste vide.
            À implémenter avec requête DB vers module auth (role admin + conducteur).
        """
        # TODO: Requête vers le module auth pour récupérer les admins et conducteurs
        # from modules.auth.domain.value_objects import Role
        # users = user_repo.find_by_roles([Role.ADMIN, Role.CONDUCTEUR])
        return []

    def _get_month_label(self, month: int) -> str:
        """Retourne le libellé du mois en français."""
        labels = [
            "",
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre",
        ]
        return labels[month]
