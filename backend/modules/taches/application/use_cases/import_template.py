"""Use Case ImportTemplate - Import d'un modele dans un chantier (TAC-05)."""

from typing import Optional, Callable, List

from ...domain.entities import Tache
from ...domain.repositories import TacheRepository, TemplateModeleRepository
from ...domain.events import TachesImportedFromTemplateEvent
from ..dtos import TacheDTO


class TemplateNotFoundError(Exception):
    """Exception levee quand un template n'est pas trouve."""

    def __init__(self, template_id: int):
        self.template_id = template_id
        self.message = f"Template {template_id} non trouve"
        super().__init__(self.message)


class ImportTemplateUseCase:
    """
    Cas d'utilisation : Import d'un modele de taches dans un chantier.

    Selon CDC Section 13 - TAC-05: Creation depuis modele.

    Attributes:
        tache_repo: Repository pour les taches.
        template_repo: Repository pour les templates.
        event_publisher: Fonction pour publier les events (optionnel).
    """

    def __init__(
        self,
        tache_repo: TacheRepository,
        template_repo: TemplateModeleRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
            template_repo: Repository templates (interface).
            event_publisher: Fonction pour publier les domain events.
        """
        self.tache_repo = tache_repo
        self.template_repo = template_repo
        self.event_publisher = event_publisher

    def execute(self, template_id: int, chantier_id: int) -> List[TacheDTO]:
        """
        Import un template dans un chantier.

        Cree une tache principale et ses sous-taches depuis le template.

        Args:
            template_id: ID du template a importer.
            chantier_id: ID du chantier cible.

        Returns:
            Liste des TacheDTO crees.

        Raises:
            TemplateNotFoundError: Si le template n'existe pas.
        """
        # Recuperer le template
        template = self.template_repo.find_by_id(template_id)
        if not template:
            raise TemplateNotFoundError(template_id)

        # Determiner l'ordre de la nouvelle tache
        taches_existantes = self.tache_repo.find_by_chantier(
            chantier_id, include_sous_taches=False
        )
        ordre_suivant = 0
        if taches_existantes:
            ordre_suivant = max(t.ordre for t in taches_existantes) + 1

        # Creer la tache principale depuis le template
        tache_principale = Tache(
            chantier_id=chantier_id,
            titre=template.nom,
            description=template.description,
            ordre=ordre_suivant,
            unite_mesure=template.unite_mesure,
            heures_estimees=template.heures_estimees_defaut,
            template_id=template_id,
        )

        # Sauvegarder la tache principale
        tache_principale = self.tache_repo.save(tache_principale)

        taches_creees = [tache_principale]
        ids_taches = [tache_principale.id]

        # Creer les sous-taches
        for i, sous_tache_modele in enumerate(template.sous_taches):
            sous_tache = Tache(
                chantier_id=chantier_id,
                titre=sous_tache_modele.titre,
                description=sous_tache_modele.description,
                parent_id=tache_principale.id,
                ordre=sous_tache_modele.ordre if sous_tache_modele.ordre else i,
                unite_mesure=sous_tache_modele.unite_mesure,
                heures_estimees=sous_tache_modele.heures_estimees_defaut,
                template_id=template_id,
            )
            sous_tache = self.tache_repo.save(sous_tache)
            taches_creees.append(sous_tache)
            ids_taches.append(sous_tache.id)
            tache_principale.sous_taches.append(sous_tache)

        # Publier l'event
        if self.event_publisher:
            event = TachesImportedFromTemplateEvent(
                template_id=template_id,
                chantier_id=chantier_id,
                taches_creees=ids_taches,
            )
            self.event_publisher(event)

        # Retourner les DTOs
        return [TacheDTO.from_entity(t) for t in taches_creees]
