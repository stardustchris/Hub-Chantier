"""Use Case AssignResponsable - Assignation d'un responsable à un chantier."""

from typing import Optional, Callable

from ...domain.repositories import ChantierRepository
from ...domain.events import ConducteurAssigneEvent, ChefChantierAssigneEvent
from ..dtos import AssignResponsableDTO, ChantierDTO


class ChantierNotFoundError(Exception):
    """Exception levée quand le chantier n'est pas trouvé."""

    def __init__(self, chantier_id: int):
        self.chantier_id = chantier_id
        self.message = f"Chantier non trouvé: {chantier_id}"
        super().__init__(self.message)


class InvalidRoleTypeError(Exception):
    """Exception levée quand le type de rôle est invalide."""

    def __init__(self, role_type: str):
        self.role_type = role_type
        self.message = (
            f"Type de rôle invalide: {role_type}. "
            f"Valeurs acceptées: 'conducteur', 'chef_chantier'"
        )
        super().__init__(self.message)


class AssignResponsableUseCase:
    """
    Cas d'utilisation : Assignation d'un responsable à un chantier.

    Permet d'assigner un conducteur (CHT-05) ou un chef de chantier (CHT-06).

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

    def execute(self, chantier_id: int, dto: AssignResponsableDTO) -> ChantierDTO:
        """
        Exécute l'assignation du responsable.

        Args:
            chantier_id: L'ID du chantier.
            dto: Les données d'assignation (user_id, role_type).

        Returns:
            ChantierDTO du chantier mis à jour.

        Raises:
            ChantierNotFoundError: Si le chantier n'existe pas.
            InvalidRoleTypeError: Si le type de rôle est invalide.
        """
        # Récupérer le chantier
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)

        # Valider et appliquer selon le type de rôle
        role_type = dto.role_type.lower().strip()

        if role_type == "conducteur":
            chantier.assigner_conducteur(dto.user_id)
            event_class = ConducteurAssigneEvent
        elif role_type in ("chef_chantier", "chef"):
            chantier.assigner_chef_chantier(dto.user_id)
            event_class = ChefChantierAssigneEvent
        else:
            raise InvalidRoleTypeError(dto.role_type)

        # Sauvegarder
        chantier = self.chantier_repo.save(chantier)

        # Publier l'event
        if self.event_publisher:
            if role_type == "conducteur":
                event = ConducteurAssigneEvent(
                    chantier_id=chantier.id,
                    code=str(chantier.code),
                    conducteur_id=dto.user_id,
                )
            else:
                event = ChefChantierAssigneEvent(
                    chantier_id=chantier.id,
                    code=str(chantier.code),
                    chef_id=dto.user_id,
                )
            self.event_publisher(event)

        return ChantierDTO.from_entity(chantier)

    def assigner_conducteur(self, chantier_id: int, user_id: int) -> ChantierDTO:
        """
        Raccourci pour assigner un conducteur.

        Args:
            chantier_id: L'ID du chantier.
            user_id: L'ID du conducteur.

        Returns:
            ChantierDTO du chantier mis à jour.
        """
        return self.execute(
            chantier_id,
            AssignResponsableDTO(user_id=user_id, role_type="conducteur"),
        )

    def assigner_chef_chantier(self, chantier_id: int, user_id: int) -> ChantierDTO:
        """
        Raccourci pour assigner un chef de chantier.

        Args:
            chantier_id: L'ID du chantier.
            user_id: L'ID du chef de chantier.

        Returns:
            ChantierDTO du chantier mis à jour.
        """
        return self.execute(
            chantier_id,
            AssignResponsableDTO(user_id=user_id, role_type="chef_chantier"),
        )

    def retirer_conducteur(self, chantier_id: int, user_id: int) -> ChantierDTO:
        """
        Retire un conducteur d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            user_id: L'ID du conducteur.

        Returns:
            ChantierDTO du chantier mis à jour.
        """
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)

        chantier.retirer_conducteur(user_id)
        chantier = self.chantier_repo.save(chantier)
        return ChantierDTO.from_entity(chantier)

    def retirer_chef_chantier(self, chantier_id: int, user_id: int) -> ChantierDTO:
        """
        Retire un chef de chantier d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            user_id: L'ID du chef de chantier.

        Returns:
            ChantierDTO du chantier mis à jour.
        """
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)

        chantier.retirer_chef_chantier(user_id)
        chantier = self.chantier_repo.save(chantier)
        return ChantierDTO.from_entity(chantier)
