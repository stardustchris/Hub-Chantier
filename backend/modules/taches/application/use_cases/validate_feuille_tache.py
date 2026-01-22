"""Use Case ValidateFeuilleTache - Validation d'une feuille (TAC-19)."""

from typing import Optional, Callable

from ...domain.repositories import FeuilleTacheRepository, TacheRepository
from ...domain.events import FeuilleTacheValidatedEvent, FeuilleTacheRejectedEvent
from ..dtos import ValidateFeuilleTacheDTO, FeuilleTacheDTO


class FeuilleTacheNotFoundError(Exception):
    """Exception levee quand une feuille n'est pas trouvee."""

    def __init__(self, feuille_id: int):
        self.feuille_id = feuille_id
        self.message = f"Feuille de tache {feuille_id} non trouvee"
        super().__init__(self.message)


class ValidateFeuilleTacheUseCase:
    """
    Cas d'utilisation : Validation ou rejet d'une feuille de tache.

    Selon CDC Section 13 - TAC-19: Validation conducteur.

    Attributes:
        feuille_repo: Repository pour les feuilles de taches.
        tache_repo: Repository pour les taches.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        feuille_repo: FeuilleTacheRepository,
        tache_repo: TacheRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            feuille_repo: Repository feuilles (interface).
            tache_repo: Repository taches (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.feuille_repo = feuille_repo
        self.tache_repo = tache_repo
        self.event_publisher = event_publisher

    def execute(self, feuille_id: int, dto: ValidateFeuilleTacheDTO) -> FeuilleTacheDTO:
        """
        Execute la validation ou le rejet d'une feuille.

        Args:
            feuille_id: ID de la feuille a valider/rejeter.
            dto: Les donnees de validation.

        Returns:
            FeuilleTacheDTO de la feuille mise a jour.

        Raises:
            FeuilleTacheNotFoundError: Si la feuille n'existe pas.
            ValueError: Si les donnees sont invalides.
        """
        # Recuperer la feuille
        feuille = self.feuille_repo.find_by_id(feuille_id)
        if not feuille:
            raise FeuilleTacheNotFoundError(feuille_id)

        if dto.valider:
            # Valider la feuille
            feuille.valider(dto.validateur_id)

            # Mettre a jour les heures realisees de la tache
            tache = self.tache_repo.find_by_id(feuille.tache_id)
            if tache:
                tache.ajouter_heures(feuille.heures_travaillees)
                if feuille.quantite_realisee > 0:
                    tache.ajouter_quantite(feuille.quantite_realisee)
                self.tache_repo.save(tache)

            # Publier l'event
            if self.event_publisher:
                event = FeuilleTacheValidatedEvent(
                    feuille_id=feuille.id,
                    tache_id=feuille.tache_id,
                    utilisateur_id=feuille.utilisateur_id,
                    validateur_id=dto.validateur_id,
                    heures_travaillees=feuille.heures_travaillees,
                )
                self.event_publisher(event)
        else:
            # Rejeter la feuille
            if not dto.motif_rejet:
                raise ValueError("Le motif de rejet est obligatoire")
            feuille.rejeter(dto.validateur_id, dto.motif_rejet)

            # Publier l'event
            if self.event_publisher:
                event = FeuilleTacheRejectedEvent(
                    feuille_id=feuille.id,
                    tache_id=feuille.tache_id,
                    utilisateur_id=feuille.utilisateur_id,
                    validateur_id=dto.validateur_id,
                    motif=dto.motif_rejet,
                )
                self.event_publisher(event)

        # Sauvegarder
        feuille = self.feuille_repo.save(feuille)

        return FeuilleTacheDTO.from_entity(feuille)
