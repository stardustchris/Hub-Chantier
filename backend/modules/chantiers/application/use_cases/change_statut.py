"""Use Case ChangeStatut - Changement de statut d'un chantier."""

import logging
from typing import Optional, Callable, List, Dict, Any

from ...domain.repositories import ChantierRepository

logger = logging.getLogger(__name__)
from ...domain.value_objects import StatutChantier
from ...domain.events import ChantierStatutChangedEvent
from ..dtos import ChangeStatutDTO, ChantierDTO
from .get_chantier import ChantierNotFoundError


class TransitionNonAutoriseeError(Exception):
    """Exception levée quand la transition de statut n'est pas autorisée."""

    def __init__(self, ancien_statut: str, nouveau_statut: str):
        self.ancien_statut = ancien_statut
        self.nouveau_statut = nouveau_statut
        self.message = (
            f"Transition non autorisée: {ancien_statut} → {nouveau_statut}"
        )
        super().__init__(self.message)


class PrerequisReceptionNonRemplisError(Exception):
    """Levée quand les prérequis de réception ne sont pas remplis.

    Gap: GAP-CHT-001
    """

    def __init__(
        self,
        chantier_id: int,
        prerequis_manquants: List[str],
        details: Dict[str, Any]
    ):
        self.chantier_id = chantier_id
        self.prerequis_manquants = prerequis_manquants
        self.details = details

        manquants_str = "\n  - ".join(prerequis_manquants)
        self.message = (
            f"Impossible de réceptionner le chantier #{chantier_id}.\n"
            f"Prérequis manquants :\n  - {manquants_str}"
        )
        super().__init__(self.message)


class ChangeStatutUseCase:
    """
    Cas d'utilisation : Changement de statut d'un chantier.

    Selon CDC Section 4.4 - Statuts de chantier:
    - Ouvert → En cours, Fermé
    - En cours → Réceptionné, Fermé
    - Réceptionné → En cours, Fermé
    - Fermé → (aucune transition)

    Attributes:
        chantier_repo: Repository pour accéder aux chantiers.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        chantier_repo: ChantierRepository,
        formulaire_repo=None,      # NOUVEAU (GAP-CHT-001)
        signalement_repo=None,     # NOUVEAU (GAP-CHT-001)
        pointage_repo=None,        # NOUVEAU (GAP-CHT-001)
        audit_service=None,        # NOUVEAU (GAP-CHT-005)
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            chantier_repo: Repository chantiers (interface).
            formulaire_repo: Repository formulaires (optionnel, GAP-CHT-001).
            signalement_repo: Repository signalements (optionnel, GAP-CHT-001).
            pointage_repo: Repository pointages (optionnel, GAP-CHT-001).
            audit_service: Service d'audit pour traçabilité (optionnel, GAP-CHT-005).
            event_publisher: Fonction pour publier les domain events.
        """
        self.chantier_repo = chantier_repo
        self.formulaire_repo = formulaire_repo
        self.signalement_repo = signalement_repo
        self.pointage_repo = pointage_repo
        self.audit_service = audit_service
        self.event_publisher = event_publisher

    def execute(self, chantier_id: int, dto: ChangeStatutDTO) -> ChantierDTO:
        """
        Exécute le changement de statut.

        Args:
            chantier_id: L'ID du chantier.
            dto: Les données de changement (nouveau statut).

        Returns:
            ChantierDTO du chantier mis à jour.

        Raises:
            ChantierNotFoundError: Si le chantier n'existe pas.
            TransitionNonAutoriseeError: Si la transition n'est pas permise.
            ValueError: Si le statut est invalide.
        """
        # Logging structured (GAP-CHT-006)
        logger.info(
            "Use case execution started",
            extra={
                "event": "chantier.use_case.started",
                "use_case": "ChangeStatutUseCase",
                "chantier_id": chantier_id,
                "operation": "change_statut",
                "nouveau_statut": dto.nouveau_statut,
            }
        )

        try:
            # Récupérer le chantier
            chantier = self.chantier_repo.find_by_id(chantier_id)
            if not chantier:
                raise ChantierNotFoundError(chantier_id)

            # Parser le nouveau statut
            nouveau_statut = StatutChantier.from_string(dto.nouveau_statut)

            # 2.5. Validation prérequis si transition vers RECEPTIONNE (GAP-CHT-001)
            if nouveau_statut == StatutChantier.receptionne():
                from ...domain.services.prerequis_service import (
                    PrerequisReceptionService
                )

                service = PrerequisReceptionService()
                result = service.verifier_prerequis(
                    chantier_id=chantier_id,
                    formulaire_repo=self.formulaire_repo,
                    signalement_repo=self.signalement_repo,
                    pointage_repo=self.pointage_repo,
                )

                if not result.est_valide:
                    raise PrerequisReceptionNonRemplisError(
                        chantier_id,
                        result.prerequis_manquants,
                        result.details
                    )

            # Sauvegarder l'ancien statut pour l'event
            ancien_statut = str(chantier.statut)

            # Tenter la transition (lève ValueError si non autorisée)
            try:
                chantier.change_statut(nouveau_statut)
            except ValueError as e:
                raise TransitionNonAutoriseeError(ancien_statut, dto.nouveau_statut) from e

            # Sauvegarder
            chantier = self.chantier_repo.save(chantier)

            # Logger dans audit_logs (GAP-CHT-005)
            if self.audit_service:
                self.audit_service.log_chantier_status_changed(
                    chantier_id=chantier.id,
                    user_id=None,  # TODO: Injecter depuis context utilisateur
                    old_status=ancien_statut,
                    new_status=str(chantier.statut),
                    ip_address=None,  # TODO: Injecter depuis request
                )

            # Publier l'event
            if self.event_publisher:
                event = ChantierStatutChangedEvent(
                    chantier_id=chantier.id,
                    code=str(chantier.code),
                    ancien_statut=ancien_statut,
                    nouveau_statut=str(chantier.statut),
                )
                self.event_publisher(event)

            logger.info(
                "Use case execution succeeded",
                extra={
                    "event": "chantier.use_case.succeeded",
                    "use_case": "ChangeStatutUseCase",
                    "chantier_id": chantier.id,
                    "ancien_statut": ancien_statut,
                    "nouveau_statut": str(chantier.statut),
                }
            )

            return ChantierDTO.from_entity(chantier)

        except Exception as e:
            logger.error(
                "Use case execution failed",
                extra={
                    "event": "chantier.use_case.failed",
                    "use_case": "ChangeStatutUseCase",
                    "chantier_id": chantier_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            raise

    def demarrer(self, chantier_id: int) -> ChantierDTO:
        """
        Raccourci pour passer en statut 'En cours'.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            ChantierDTO du chantier mis à jour.
        """
        return self.execute(chantier_id, ChangeStatutDTO(nouveau_statut="en_cours"))

    def receptionner(self, chantier_id: int) -> ChantierDTO:
        """
        Raccourci pour passer en statut 'Réceptionné'.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            ChantierDTO du chantier mis à jour.
        """
        return self.execute(chantier_id, ChangeStatutDTO(nouveau_statut="receptionne"))

    def fermer(self, chantier_id: int) -> ChantierDTO:
        """
        Raccourci pour passer en statut 'Fermé'.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            ChantierDTO du chantier mis à jour.
        """
        return self.execute(chantier_id, ChangeStatutDTO(nouveau_statut="ferme"))
