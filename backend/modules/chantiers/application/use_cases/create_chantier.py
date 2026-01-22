"""Use Case CreateChantier - Création d'un nouveau chantier."""

from datetime import date
from typing import Optional, Callable

from shared.domain.value_objects import Couleur

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

    def __init__(self, code: str):
        self.code = code
        self.message = f"Le code chantier {code} est déjà utilisé"
        super().__init__(self.message)


class InvalidDatesError(Exception):
    """Exception levée quand les dates sont invalides."""

    def __init__(self, message: str):
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
    ):
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
        # Générer ou valider le code chantier (CHT-19)
        if dto.code:
            code = CodeChantier(dto.code)
            if self.chantier_repo.exists_by_code(code):
                raise CodeChantierAlreadyExistsError(dto.code)
        else:
            # Auto-générer le prochain code
            last_code = self.chantier_repo.get_last_code()
            code = CodeChantier.generate_next(last_code)

        # Parser les coordonnées GPS (CHT-04)
        coordonnees_gps = None
        if dto.latitude is not None and dto.longitude is not None:
            coordonnees_gps = CoordonneesGPS(
                latitude=dto.latitude,
                longitude=dto.longitude,
            )

        # Parser le contact (CHT-07)
        contact = None
        if dto.contact_nom and dto.contact_telephone:
            contact = ContactChantier(
                nom=dto.contact_nom,
                telephone=dto.contact_telephone,
            )

        # Parser les dates (CHT-20)
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

        # Parser la couleur (CHT-02)
        couleur = Couleur.default()
        if dto.couleur:
            couleur = Couleur(dto.couleur)

        # Créer l'entité chantier
        chantier = Chantier(
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

        # Sauvegarder
        chantier = self.chantier_repo.save(chantier)

        # Publier l'event
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

        return ChantierDTO.from_entity(chantier)
