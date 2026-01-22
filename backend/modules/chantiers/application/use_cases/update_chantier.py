"""Use Case UpdateChantier - Mise à jour d'un chantier."""

from datetime import date
from typing import Optional, Callable

from modules.auth.domain.value_objects import Couleur

from ...domain.repositories import ChantierRepository
from ...domain.value_objects import CoordonneesGPS, ContactChantier
from ...domain.events import ChantierUpdatedEvent
from ..dtos import UpdateChantierDTO, ChantierDTO


class ChantierNotFoundError(Exception):
    """Exception levée quand le chantier n'est pas trouvé."""

    def __init__(self, chantier_id: int):
        self.chantier_id = chantier_id
        self.message = f"Chantier non trouvé: {chantier_id}"
        super().__init__(self.message)


class ChantierFermeError(Exception):
    """Exception levée quand on essaie de modifier un chantier fermé."""

    def __init__(self, chantier_id: int):
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
    ):
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
        # Récupérer le chantier
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)

        # Vérifier que le chantier n'est pas fermé
        if not chantier.allows_modifications:
            raise ChantierFermeError(chantier_id)

        changes = []

        # Mettre à jour les infos générales
        if dto.nom is not None or dto.adresse is not None or dto.description is not None:
            couleur = None
            if dto.couleur:
                couleur = Couleur(dto.couleur)
            chantier.update_infos(
                nom=dto.nom,
                adresse=dto.adresse,
                description=dto.description,
                couleur=couleur,
            )
            if dto.nom:
                changes.append(("nom", dto.nom))
            if dto.adresse:
                changes.append(("adresse", dto.adresse))
            if dto.description:
                changes.append(("description", dto.description))
            if dto.couleur:
                changes.append(("couleur", dto.couleur))

        # Mettre à jour les coordonnées GPS
        if dto.latitude is not None and dto.longitude is not None:
            coordonnees = CoordonneesGPS(
                latitude=dto.latitude,
                longitude=dto.longitude,
            )
            chantier.update_coordonnees_gps(coordonnees)
            changes.append(("coordonnees_gps", str(coordonnees)))

        # Mettre à jour le contact
        if dto.contact_nom is not None and dto.contact_telephone is not None:
            contact = ContactChantier(
                nom=dto.contact_nom,
                telephone=dto.contact_telephone,
            )
            chantier.update_contact(contact)
            changes.append(("contact", str(contact)))

        # Mettre à jour les dates
        date_debut = None
        date_fin = None
        if dto.date_debut:
            date_debut = date.fromisoformat(dto.date_debut)
        if dto.date_fin:
            date_fin = date.fromisoformat(dto.date_fin)
        if date_debut is not None or date_fin is not None:
            chantier.update_dates(date_debut=date_debut, date_fin=date_fin)
            if date_debut:
                changes.append(("date_debut", str(date_debut)))
            if date_fin:
                changes.append(("date_fin", str(date_fin)))

        # Mettre à jour les heures estimées
        if dto.heures_estimees is not None:
            chantier.update_heures_estimees(dto.heures_estimees)
            changes.append(("heures_estimees", str(dto.heures_estimees)))

        # Mettre à jour la photo de couverture
        if dto.photo_couverture is not None:
            chantier.update_photo_couverture(dto.photo_couverture)
            changes.append(("photo_couverture", dto.photo_couverture))

        # Sauvegarder
        chantier = self.chantier_repo.save(chantier)

        # Publier l'event
        if self.event_publisher and changes:
            event = ChantierUpdatedEvent(
                chantier_id=chantier.id,
                code=str(chantier.code),
                changes=tuple(changes),
            )
            self.event_publisher(event)

        return ChantierDTO.from_entity(chantier)
