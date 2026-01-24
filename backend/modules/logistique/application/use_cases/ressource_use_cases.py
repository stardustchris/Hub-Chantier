"""Use Cases pour la gestion des ressources.

LOG-01: Référentiel matériel - Liste des engins disponibles (Admin uniquement)
LOG-02: Fiche ressource - Nom, code, photo, couleur, plage horaire par défaut
LOG-10: Option validation N+1 - Activation/désactivation par ressource
"""

from datetime import datetime
from typing import Optional

from ..ports.event_bus import EventBus

from ...domain.entities import Ressource
from ...domain.repositories import RessourceRepository
from ...domain.value_objects import CategorieRessource, PlageHoraire
from ...domain.events import RessourceCreatedEvent, RessourceUpdatedEvent, RessourceDeletedEvent
from ..dtos import RessourceCreateDTO, RessourceUpdateDTO, RessourceDTO, RessourceListDTO


class RessourceNotFoundError(Exception):
    """Erreur levée quand une ressource n'est pas trouvée."""

    def __init__(self, ressource_id: int):
        self.ressource_id = ressource_id
        super().__init__(f"Ressource {ressource_id} non trouvée")


class RessourceCodeExistsError(Exception):
    """Erreur levée quand un code de ressource existe déjà."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Une ressource avec le code '{code}' existe déjà")


class CreateRessourceUseCase:
    """Use case pour créer une ressource.

    LOG-01: Seuls les admins peuvent créer des ressources.
    """

    def __init__(
        self,
        ressource_repository: RessourceRepository,
        event_bus: EventBus,
    ):
        self._ressource_repository = ressource_repository
        self._event_bus = event_bus

    def execute(self, dto: RessourceCreateDTO, created_by: int) -> RessourceDTO:
        """Crée une nouvelle ressource.

        Args:
            dto: Les données de la ressource à créer
            created_by: L'ID de l'utilisateur créateur (admin)

        Returns:
            Le DTO de la ressource créée

        Raises:
            RessourceCodeExistsError: Si le code existe déjà
        """
        # Vérifier unicité du code
        existing = self._ressource_repository.find_by_code(dto.code)
        if existing:
            raise RessourceCodeExistsError(dto.code)

        # Créer la plage horaire
        plage = PlageHoraire(
            heure_debut=dto.heure_debut_defaut,
            heure_fin=dto.heure_fin_defaut,
        )

        # Déterminer si validation requise
        validation_requise = dto.validation_requise
        if validation_requise is None:
            validation_requise = dto.categorie.validation_requise

        # Créer l'entité
        ressource = Ressource(
            nom=dto.nom,
            code=dto.code,
            categorie=dto.categorie,
            photo_url=dto.photo_url,
            couleur=dto.couleur,
            plage_horaire_defaut=plage,
            validation_requise=validation_requise,
            description=dto.description,
            created_at=datetime.utcnow(),
            created_by=created_by,
        )

        # Persister
        ressource = self._ressource_repository.save(ressource)

        # Publier l'event
        self._event_bus.publish(
            RessourceCreatedEvent(
                ressource_id=ressource.id,
                nom=ressource.nom,
                code=ressource.code,
                categorie=ressource.categorie.value,
                created_by=created_by,
            )
        )

        return RessourceDTO.from_entity(ressource)


class UpdateRessourceUseCase:
    """Use case pour mettre à jour une ressource."""

    def __init__(
        self,
        ressource_repository: RessourceRepository,
        event_bus: EventBus,
    ):
        self._ressource_repository = ressource_repository
        self._event_bus = event_bus

    def execute(
        self, ressource_id: int, dto: RessourceUpdateDTO, updated_by: int
    ) -> RessourceDTO:
        """Met à jour une ressource.

        Args:
            ressource_id: L'ID de la ressource à mettre à jour
            dto: Les données à mettre à jour
            updated_by: L'ID de l'utilisateur

        Returns:
            Le DTO de la ressource mise à jour

        Raises:
            RessourceNotFoundError: Si la ressource n'existe pas
            RessourceCodeExistsError: Si le nouveau code existe déjà
        """
        ressource = self._ressource_repository.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(ressource_id)

        # Vérifier unicité du code si modifié
        if dto.code and dto.code != ressource.code:
            existing = self._ressource_repository.find_by_code(dto.code)
            if existing:
                raise RessourceCodeExistsError(dto.code)
            ressource.code = dto.code

        # Appliquer les modifications
        if dto.nom is not None:
            ressource.nom = dto.nom
        if dto.categorie is not None:
            ressource.categorie = dto.categorie
        if dto.photo_url is not None:
            ressource.photo_url = dto.photo_url
        if dto.couleur is not None:
            ressource.couleur = dto.couleur
        if dto.validation_requise is not None:
            ressource.validation_requise = dto.validation_requise
        if dto.actif is not None:
            ressource.actif = dto.actif
        if dto.description is not None:
            ressource.description = dto.description

        # Mise à jour plage horaire si spécifiée
        if dto.heure_debut_defaut is not None or dto.heure_fin_defaut is not None:
            heure_debut = (
                dto.heure_debut_defaut
                if dto.heure_debut_defaut
                else ressource.plage_horaire_defaut.heure_debut
            )
            heure_fin = (
                dto.heure_fin_defaut
                if dto.heure_fin_defaut
                else ressource.plage_horaire_defaut.heure_fin
            )
            ressource.plage_horaire_defaut = PlageHoraire(
                heure_debut=heure_debut, heure_fin=heure_fin
            )

        ressource.updated_at = datetime.utcnow()

        # Persister
        ressource = self._ressource_repository.save(ressource)

        # Publier l'event
        self._event_bus.publish(
            RessourceUpdatedEvent(
                ressource_id=ressource.id,
                nom=ressource.nom,
                code=ressource.code,
                updated_by=updated_by,
            )
        )

        return RessourceDTO.from_entity(ressource)


class DeleteRessourceUseCase:
    """Use case pour supprimer une ressource."""

    def __init__(
        self,
        ressource_repository: RessourceRepository,
        event_bus: EventBus,
    ):
        self._ressource_repository = ressource_repository
        self._event_bus = event_bus

    def execute(self, ressource_id: int, deleted_by: int) -> bool:
        """Supprime une ressource.

        Args:
            ressource_id: L'ID de la ressource à supprimer
            deleted_by: L'ID de l'utilisateur

        Returns:
            True si supprimée

        Raises:
            RessourceNotFoundError: Si la ressource n'existe pas
        """
        ressource = self._ressource_repository.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(ressource_id)

        deleted = self._ressource_repository.delete(ressource_id)

        if deleted:
            self._event_bus.publish(
                RessourceDeletedEvent(
                    ressource_id=ressource_id,
                    deleted_by=deleted_by,
                )
            )

        return deleted


class GetRessourceUseCase:
    """Use case pour récupérer une ressource."""

    def __init__(self, ressource_repository: RessourceRepository):
        self._ressource_repository = ressource_repository

    def execute(self, ressource_id: int) -> RessourceDTO:
        """Récupère une ressource par son ID.

        Args:
            ressource_id: L'ID de la ressource

        Returns:
            Le DTO de la ressource

        Raises:
            RessourceNotFoundError: Si la ressource n'existe pas
        """
        ressource = self._ressource_repository.find_by_id(ressource_id)
        if not ressource:
            raise RessourceNotFoundError(ressource_id)

        return RessourceDTO.from_entity(ressource)


class ListRessourcesUseCase:
    """Use case pour lister les ressources."""

    def __init__(self, ressource_repository: RessourceRepository):
        self._ressource_repository = ressource_repository

    def execute(
        self,
        categorie: Optional[CategorieRessource] = None,
        actif_seulement: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> RessourceListDTO:
        """Liste les ressources avec filtres.

        Args:
            categorie: Filtrer par catégorie
            actif_seulement: Ne retourner que les actives
            limit: Nombre max de résultats
            offset: Décalage pour pagination

        Returns:
            Liste paginée de ressources
        """
        ressources = self._ressource_repository.find_all(
            categorie=categorie,
            actif_seulement=actif_seulement,
            limit=limit,
            offset=offset,
        )
        total = self._ressource_repository.count(
            categorie=categorie,
            actif_seulement=actif_seulement,
        )

        return RessourceListDTO(
            items=[RessourceDTO.from_entity(r) for r in ressources],
            total=total,
            limit=limit,
            offset=offset,
        )
