"""Use Case CreateChantier - Création d'un nouveau chantier."""

import logging
from datetime import date
from typing import Optional, Callable, List, Tuple

from shared.domain.value_objects import Couleur

logger = logging.getLogger(__name__)

from ...domain.entities import Chantier
from ...domain.repositories import ChantierRepository
from ...domain.value_objects import (
    CodeChantier,
    CoordonneesGPS,
    ContactChantier,
    StatutChantier,
)
from ...domain.events import ChantierCreatedEvent
from ..dtos import CreateChantierDTO, ChantierDTO


class CodeChantierAlreadyExistsError(Exception):
    """Exception levée quand le code chantier est déjà utilisé."""

    def __init__(self, code: str) -> None:
        self.code = code
        self.message = f"Le code chantier {code} est déjà utilisé"
        super().__init__(self.message)


class InvalidDatesError(Exception):
    """Exception levée quand les dates sont invalides."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class CreateChantierUseCase:
    """
    Cas d'utilisation : Création d'un nouveau chantier.

    Crée un chantier avec toutes ses informations selon CDC Section 4.

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

    def execute(self, dto: CreateChantierDTO) -> ChantierDTO:
        """
        Exécute la création du chantier.

        Args:
            dto: Les données de création.

        Returns:
            ChantierDTO contenant le chantier créé.

        Raises:
            CodeChantierAlreadyExistsError: Si le code est déjà utilisé.
            InvalidDatesError: Si les dates sont invalides.
            ValueError: Si les données sont invalides.
        """
        # Logging structured (GAP-CHT-006)
        logger.info(
            "Use case execution started",
            extra={
                "event": "chantier.use_case.started",
                "use_case": "CreateChantierUseCase",
                "operation": "create",
                "chantier_nom": dto.nom,
                "chantier_code": dto.code,
            }
        )

        try:
            code = self._generate_or_validate_code(dto)
            coordonnees_gps = self._parse_coordonnees_gps(dto)
            contact = self._parse_contact(dto)
            date_debut, date_fin = self._parse_and_validate_dates(dto)
            couleur = self._parse_couleur(dto)

            chantier = self._create_chantier_entity(
                code, dto, couleur, coordonnees_gps, contact, date_debut, date_fin
            )

            chantier = self.chantier_repo.save(chantier)
            self._publish_created_event(chantier)

            logger.info(
                "Use case execution succeeded",
                extra={
                    "event": "chantier.use_case.succeeded",
                    "use_case": "CreateChantierUseCase",
                    "chantier_id": chantier.id,
                    "chantier_code": str(chantier.code),
                    "chantier_nom": chantier.nom,
                }
            )

            return ChantierDTO.from_entity(chantier)

        except Exception as e:
            logger.error(
                "Use case execution failed",
                extra={
                    "event": "chantier.use_case.failed",
                    "use_case": "CreateChantierUseCase",
                    "operation": "create",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            raise

    def _generate_or_validate_code(self, dto: CreateChantierDTO) -> CodeChantier:
        """Génère ou valide le code chantier (CHT-19)."""
        if dto.code:
            code = CodeChantier(dto.code)
            if self.chantier_repo.exists_by_code(code):
                raise CodeChantierAlreadyExistsError(dto.code)
            return code
        else:
            last_code = self.chantier_repo.get_last_code()
            return CodeChantier.generate_next(last_code)

    def _parse_coordonnees_gps(
        self, dto: CreateChantierDTO
    ) -> Optional[CoordonneesGPS]:
        """Parse les coordonnées GPS (CHT-04)."""
        if dto.latitude is not None and dto.longitude is not None:
            return CoordonneesGPS(
                latitude=dto.latitude,
                longitude=dto.longitude,
            )
        return None

    def _parse_contact(self, dto: CreateChantierDTO) -> Optional[ContactChantier]:
        """Parse le contact (CHT-07)."""
        if dto.contact_nom and dto.contact_telephone:
            return ContactChantier(
                nom=dto.contact_nom,
                telephone=dto.contact_telephone,
            )
        return None

    def _parse_and_validate_dates(
        self, dto: CreateChantierDTO
    ) -> tuple[Optional[date], Optional[date]]:
        """Parse et valide les dates (CHT-20)."""
        date_debut = None
        date_fin = None

        if dto.date_debut:
            date_debut = date.fromisoformat(dto.date_debut)
        if dto.date_fin:
            date_fin = date.fromisoformat(dto.date_fin)

        if date_debut and date_fin and date_fin < date_debut:
            raise InvalidDatesError(
                "La date de fin ne peut pas être antérieure à la date de début"
            )

        return date_debut, date_fin

    def _parse_couleur(self, dto: CreateChantierDTO) -> Couleur:
        """Parse la couleur (CHT-02)."""
        if dto.couleur:
            return Couleur(dto.couleur)
        return Couleur.default()

    def _create_chantier_entity(
        self,
        code: CodeChantier,
        dto: CreateChantierDTO,
        couleur: Couleur,
        coordonnees_gps: Optional[CoordonneesGPS],
        contact: Optional[ContactChantier],
        date_debut: Optional[date],
        date_fin: Optional[date],
    ) -> Chantier:
        """Crée l'entité chantier avec tous les paramètres."""
        return Chantier(
            code=code,
            nom=dto.nom,
            adresse=dto.adresse,
            statut=StatutChantier.ouvert(),
            couleur=couleur,
            coordonnees_gps=coordonnees_gps,
            photo_couverture=dto.photo_couverture,
            contact=contact,
            heures_estimees=dto.heures_estimees,
            date_debut=date_debut,
            date_fin=date_fin,
            description=dto.description,
            conducteur_ids=list(dto.conducteur_ids or []),
            chef_chantier_ids=list(dto.chef_chantier_ids or []),
        )

    def _publish_created_event(self, chantier: Chantier) -> None:
        """Publie l'événement de création."""
        if self.event_publisher:
            event = ChantierCreatedEvent(
                chantier_id=chantier.id,
                code=str(chantier.code),
                nom=chantier.nom,
                statut=str(chantier.statut),
                conducteur_ids=tuple(chantier.conducteur_ids),
                chef_chantier_ids=tuple(chantier.chef_chantier_ids),
            )
            self.event_publisher(event)
