"""Use Case UpdateChantier - Mise à jour d'un chantier."""

import logging
from datetime import date
from typing import Optional, Callable, List, Tuple, Any

from shared.domain.value_objects import Couleur

logger = logging.getLogger(__name__)

from ...domain.repositories import ChantierRepository
from ...domain.value_objects import CoordonneesGPS, ContactChantier
from ...domain.events import ChantierUpdatedEvent
from ..dtos import UpdateChantierDTO, ChantierDTO
from .get_chantier import ChantierNotFoundError


class ChantierFermeError(Exception):
    """Exception levée quand on essaie de modifier un chantier fermé."""

    def __init__(self, chantier_id: int) -> None:
        self.chantier_id = chantier_id
        self.message = f"Impossible de modifier le chantier {chantier_id}: il est fermé"
        super().__init__(self.message)


class UpdateChantierUseCase:
    """
    Cas d'utilisation : Mise à jour d'un chantier existant.

    Met à jour les informations d'un chantier selon les données fournies.

    Attributes:
        chantier_repo: Repository pour accéder aux chantiers.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        chantier_repo: ChantierRepository,
        event_publisher: Optional[Callable] = None,
    ) -> None:
        """
        Initialise le use case.

        Args:
            chantier_repo: Repository chantiers (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.chantier_repo = chantier_repo
        self.event_publisher = event_publisher

    def execute(self, chantier_id: int, dto: UpdateChantierDTO) -> ChantierDTO:
        """
        Exécute la mise à jour du chantier.

        Args:
            chantier_id: L'ID du chantier à modifier.
            dto: Les données de mise à jour.

        Returns:
            ChantierDTO du chantier mis à jour.

        Raises:
            ChantierNotFoundError: Si le chantier n'existe pas.
            ChantierFermeError: Si le chantier est fermé.
            ValueError: Si les données sont invalides.
        """
        # Logging structured (GAP-CHT-006)
        logger.info(
            "Use case execution started",
            extra={
                "event": "chantier.use_case.started",
                "use_case": "UpdateChantierUseCase",
                "chantier_id": chantier_id,
                "operation": "update",
            }
        )

        try:
            # Récupérer et valider le chantier
            chantier = self._get_and_validate_chantier(chantier_id)

            # Collecter les changements
            changes = []
            self._update_infos_generales(chantier, dto, changes)
            self._update_coordonnees_et_contact(chantier, dto, changes)
            self._update_dates_et_heures(chantier, dto, changes)
            self._update_photo_couverture(chantier, dto, changes)
            self._update_contexte_tva(chantier, dto, changes)

            # Sauvegarder et publier l'event
            chantier = self.chantier_repo.save(chantier)
            self._publish_update_event(chantier, changes)

            logger.info(
                "Use case execution succeeded",
                extra={
                    "event": "chantier.use_case.succeeded",
                    "use_case": "UpdateChantierUseCase",
                    "chantier_id": chantier.id,
                    "changes_count": len(changes),
                    "changes": changes,
                }
            )

            return ChantierDTO.from_entity(chantier)

        except Exception as e:
            logger.error(
                "Use case execution failed",
                extra={
                    "event": "chantier.use_case.failed",
                    "use_case": "UpdateChantierUseCase",
                    "chantier_id": chantier_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            raise

    def _get_and_validate_chantier(self, chantier_id: int) -> Any:
        """Récupère le chantier et vérifie qu'il peut être modifié."""
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)
        if not chantier.allows_modifications:
            raise ChantierFermeError(chantier_id)
        return chantier

    def _update_infos_generales(self, chantier: Any, dto: UpdateChantierDTO, changes: List[Tuple[str, str]]) -> None:
        """Met à jour les informations générales (nom, adresse, description, couleur, maitre_ouvrage)."""
        if dto.nom is not None or dto.adresse is not None or dto.description is not None or dto.maitre_ouvrage is not None:
            couleur = Couleur(dto.couleur) if dto.couleur else None

            chantier.update_infos(
                nom=dto.nom,
                adresse=dto.adresse,
                description=dto.description,
                couleur=couleur,
                maitre_ouvrage=dto.maitre_ouvrage,
            )

            if dto.nom:
                changes.append(("nom", dto.nom))
            if dto.adresse:
                changes.append(("adresse", dto.adresse))
            if dto.description:
                changes.append(("description", dto.description))
            if dto.couleur:
                changes.append(("couleur", dto.couleur))
            if dto.maitre_ouvrage:
                changes.append(("maitre_ouvrage", dto.maitre_ouvrage))

    def _update_coordonnees_et_contact(self, chantier: Any, dto: UpdateChantierDTO, changes: List[Tuple[str, str]]) -> None:
        """Met à jour les coordonnées GPS et le contact."""
        # Coordonnées GPS
        if dto.latitude is not None and dto.longitude is not None:
            coordonnees = CoordonneesGPS(
                latitude=dto.latitude,
                longitude=dto.longitude,
            )
            chantier.update_coordonnees_gps(coordonnees)
            changes.append(("coordonnees_gps", str(coordonnees)))

        # Contact
        if dto.contact_nom is not None and dto.contact_telephone is not None:
            contact = ContactChantier(
                nom=dto.contact_nom,
                telephone=dto.contact_telephone,
            )
            chantier.update_contact(contact)
            changes.append(("contact", str(contact)))

    def _update_dates_et_heures(self, chantier: Any, dto: UpdateChantierDTO, changes: List[Tuple[str, str]]) -> None:
        """Met à jour les dates et heures estimées."""
        # Dates
        date_debut = date.fromisoformat(dto.date_debut) if dto.date_debut else None
        date_fin = date.fromisoformat(dto.date_fin) if dto.date_fin else None
        if date_debut is not None or date_fin is not None:
            chantier.update_dates(date_debut=date_debut, date_fin=date_fin)
            if date_debut:
                changes.append(("date_debut", str(date_debut)))
            if date_fin:
                changes.append(("date_fin", str(date_fin)))

        # Heures estimées
        if dto.heures_estimees is not None:
            chantier.update_heures_estimees(dto.heures_estimees)
            changes.append(("heures_estimees", str(dto.heures_estimees)))

    def _update_photo_couverture(self, chantier: Any, dto: UpdateChantierDTO, changes: List[Tuple[str, str]]) -> None:
        """Met à jour la photo de couverture."""
        if dto.photo_couverture is not None:
            chantier.update_photo_couverture(dto.photo_couverture)
            changes.append(("photo_couverture", dto.photo_couverture))

    def _update_contexte_tva(self, chantier: Any, dto: UpdateChantierDTO, changes: List[Tuple[str, str]]) -> None:
        """Met a jour le contexte TVA du chantier (DEV-TVA)."""
        if dto.type_travaux is not None:
            chantier.type_travaux = dto.type_travaux
            changes.append(("type_travaux", dto.type_travaux))
        if dto.batiment_plus_2ans is not None:
            chantier.batiment_plus_2ans = dto.batiment_plus_2ans
            changes.append(("batiment_plus_2ans", str(dto.batiment_plus_2ans)))
        if dto.usage_habitation is not None:
            chantier.usage_habitation = dto.usage_habitation
            changes.append(("usage_habitation", str(dto.usage_habitation)))

    def _publish_update_event(self, chantier: Any, changes: List[Tuple[str, str]]) -> None:
        """Publie l'événement de mise à jour si des changements ont été effectués."""
        if self.event_publisher and changes:
            event = ChantierUpdatedEvent(
                chantier_id=chantier.id,
                code=str(chantier.code),
                changes=tuple(changes),
            )
            self.event_publisher(event)
