"""Use Case ChangeStatut - Changement de statut d'un chantier."""

from typing import Optional, Callable

from ...domain.repositories import ChantierRepository
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
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            chantier_repo: Repository chantiers (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.chantier_repo = chantier_repo
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
        # Récupérer le chantier
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)

        # Parser le nouveau statut
        nouveau_statut = StatutChantier.from_string(dto.nouveau_statut)

        # Sauvegarder l'ancien statut pour l'event
        ancien_statut = str(chantier.statut)

        # Tenter la transition (lève ValueError si non autorisée)
        try:
            chantier.change_statut(nouveau_statut)
        except ValueError as e:
            raise TransitionNonAutoriseeError(ancien_statut, dto.nouveau_statut) from e

        # Sauvegarder
        chantier = self.chantier_repo.save(chantier)

        # Publier l'event
        if self.event_publisher:
            event = ChantierStatutChangedEvent(
                chantier_id=chantier.id,
                code=str(chantier.code),
                ancien_statut=ancien_statut,
                nouveau_statut=str(chantier.statut),
            )
            self.event_publisher(event)

        return ChantierDTO.from_entity(chantier)

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
