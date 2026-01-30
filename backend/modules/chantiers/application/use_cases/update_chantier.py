"""Use Case UpdateChantier - Mise à jour d'un chantier."""

from datetime import date
from typing import Optional, Callable

from shared.domain.value_objects import Couleur

from ...domain.repositories import ChantierRepository
from ...domain.value_objects import CoordonneesGPS, ContactChantier
from ...domain.events import ChantierUpdatedEvent
from ..dtos import UpdateChantierDTO, ChantierDTO
from .get_chantier import ChantierNotFoundError


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
        print(f"[DEBUG UseCase] execute() called with chantier_id={chantier_id}")
        print(f"[DEBUG UseCase] dto values: nom={dto.nom}, couleur={dto.couleur}, maitre_ouvrage={dto.maitre_ouvrage}")

        # Récupérer et valider le chantier
        print(f"[DEBUG UseCase] Calling _get_and_validate_chantier")
        chantier = self._get_and_validate_chantier(chantier_id)
        print(f"[DEBUG UseCase] Chantier loaded: id={chantier.id}, allows_modifications={chantier.allows_modifications}")

        # Collecter les changements
        changes = []
        print(f"[DEBUG UseCase] Calling _update_infos_generales")
        self._update_infos_generales(chantier, dto, changes)
        print(f"[DEBUG UseCase] After _update_infos_generales, changes={changes}")

        print(f"[DEBUG UseCase] Calling _update_coordonnees_et_contact")
        self._update_coordonnees_et_contact(chantier, dto, changes)
        print(f"[DEBUG UseCase] After _update_coordonnees_et_contact")

        print(f"[DEBUG UseCase] Calling _update_dates_et_heures")
        self._update_dates_et_heures(chantier, dto, changes)
        print(f"[DEBUG UseCase] After _update_dates_et_heures")

        print(f"[DEBUG UseCase] Calling _update_photo_couverture")
        self._update_photo_couverture(chantier, dto, changes)
        print(f"[DEBUG UseCase] After _update_photo_couverture")

        # Sauvegarder et publier l'event
        print(f"[DEBUG UseCase] Calling repo.save")
        chantier = self.chantier_repo.save(chantier)
        print(f"[DEBUG UseCase] After repo.save")

        self._publish_update_event(chantier, changes)
        print(f"[DEBUG UseCase] Returning ChantierDTO")

        return ChantierDTO.from_entity(chantier)

    def _get_and_validate_chantier(self, chantier_id: int):
        """Récupère le chantier et vérifie qu'il peut être modifié."""
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(chantier_id)
        if not chantier.allows_modifications:
            raise ChantierFermeError(chantier_id)
        return chantier

    def _update_infos_generales(self, chantier, dto: UpdateChantierDTO, changes: list):
        """Met à jour les informations générales (nom, adresse, description, couleur, maitre_ouvrage)."""
        print(f"[DEBUG UseCase] _update_infos_generales: dto.nom={dto.nom}, dto.couleur={dto.couleur}, dto.maitre_ouvrage={dto.maitre_ouvrage}")
        if dto.nom is not None or dto.adresse is not None or dto.description is not None or dto.maitre_ouvrage is not None:
            print(f"[DEBUG UseCase] Creating Couleur from: {dto.couleur}")
            try:
                couleur = Couleur(dto.couleur) if dto.couleur else None
                print(f"[DEBUG UseCase] Couleur created successfully: {couleur}")
            except Exception as e:
                print(f"[DEBUG UseCase] ERROR creating Couleur: {type(e).__name__}: {str(e)}")
                raise

            print(f"[DEBUG UseCase] Calling chantier.update_infos")
            try:
                chantier.update_infos(
                    nom=dto.nom,
                    adresse=dto.adresse,
                    description=dto.description,
                    couleur=couleur,
                    maitre_ouvrage=dto.maitre_ouvrage,
                )
                print(f"[DEBUG UseCase] chantier.update_infos completed successfully")
            except Exception as e:
                print(f"[DEBUG UseCase] ERROR in chantier.update_infos: {type(e).__name__}: {str(e)}")
                raise

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

    def _update_coordonnees_et_contact(self, chantier, dto: UpdateChantierDTO, changes: list):
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

    def _update_dates_et_heures(self, chantier, dto: UpdateChantierDTO, changes: list):
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

    def _update_photo_couverture(self, chantier, dto: UpdateChantierDTO, changes: list):
        """Met à jour la photo de couverture."""
        if dto.photo_couverture is not None:
            chantier.update_photo_couverture(dto.photo_couverture)
            changes.append(("photo_couverture", dto.photo_couverture))

    def _publish_update_event(self, chantier, changes: list):
        """Publie l'événement de mise à jour si des changements ont été effectués."""
        if self.event_publisher and changes:
            event = ChantierUpdatedEvent(
                chantier_id=chantier.id,
                code=str(chantier.code),
                changes=tuple(changes),
            )
            self.event_publisher(event)
