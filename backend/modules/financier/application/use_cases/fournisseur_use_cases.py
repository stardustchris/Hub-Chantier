"""Use Cases pour la gestion des fournisseurs.

FIN-14: Répertoire fournisseurs - Base fournisseurs partagée.
FIN-15: Fiche fournisseur - Détail et historique.
"""

from datetime import datetime
from typing import Optional

from ..ports.event_bus import EventBus

from ...domain.entities import Fournisseur
from ...domain.repositories import (
    FournisseurRepository,
    JournalFinancierRepository,
    JournalEntry,
)
from ...domain.value_objects import TypeFournisseur
from ...domain.events import (
    FournisseurCreatedEvent,
    FournisseurUpdatedEvent,
    FournisseurDeletedEvent,
)
from ..dtos import (
    FournisseurCreateDTO,
    FournisseurUpdateDTO,
    FournisseurDTO,
    FournisseurListDTO,
)


class FournisseurNotFoundError(Exception):
    """Erreur levée quand un fournisseur n'est pas trouvé."""

    def __init__(self, fournisseur_id: int):
        self.fournisseur_id = fournisseur_id
        super().__init__(f"Fournisseur {fournisseur_id} non trouvé")


class FournisseurSiretExistsError(Exception):
    """Erreur levée quand un SIRET existe déjà."""

    def __init__(self, siret: str):
        self.siret = siret
        super().__init__(f"Un fournisseur avec le SIRET '{siret}' existe déjà")


class CreateFournisseurUseCase:
    """Use case pour créer un fournisseur.

    FIN-14: Seuls les admins/conducteurs peuvent créer des fournisseurs.
    """

    def __init__(
        self,
        fournisseur_repository: FournisseurRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._fournisseur_repository = fournisseur_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, dto: FournisseurCreateDTO, created_by: int) -> FournisseurDTO:
        """Crée un nouveau fournisseur.

        Args:
            dto: Les données du fournisseur à créer.
            created_by: L'ID de l'utilisateur créateur.

        Returns:
            Le DTO du fournisseur créé.

        Raises:
            FournisseurSiretExistsError: Si le SIRET existe déjà.
        """
        # Vérifier unicité du SIRET si renseigné
        if dto.siret and dto.siret.strip():
            existing = self._fournisseur_repository.find_by_siret(dto.siret.strip())
            if existing:
                raise FournisseurSiretExistsError(dto.siret)

        # Créer l'entité
        fournisseur = Fournisseur(
            raison_sociale=dto.raison_sociale,
            type=dto.type,
            siret=dto.siret,
            adresse=dto.adresse,
            contact_principal=dto.contact_principal,
            telephone=dto.telephone,
            email=dto.email,
            conditions_paiement=dto.conditions_paiement,
            notes=dto.notes,
            created_at=datetime.utcnow(),
            created_by=created_by,
        )

        # Persister
        fournisseur = self._fournisseur_repository.save(fournisseur)

        # Journal
        self._journal_repository.save(
            JournalEntry(
                entite_type="fournisseur",
                entite_id=fournisseur.id,
                action="creation",
                details=f"Création du fournisseur '{fournisseur.raison_sociale}'",
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        # Publier l'event
        self._event_bus.publish(
            FournisseurCreatedEvent(
                fournisseur_id=fournisseur.id,
                raison_sociale=fournisseur.raison_sociale,
                type_fournisseur=fournisseur.type.value,
                created_by=created_by,
            )
        )

        return FournisseurDTO.from_entity(fournisseur)


class UpdateFournisseurUseCase:
    """Use case pour mettre à jour un fournisseur."""

    def __init__(
        self,
        fournisseur_repository: FournisseurRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._fournisseur_repository = fournisseur_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(
        self, fournisseur_id: int, dto: FournisseurUpdateDTO, updated_by: int
    ) -> FournisseurDTO:
        """Met à jour un fournisseur.

        Args:
            fournisseur_id: L'ID du fournisseur à mettre à jour.
            dto: Les données à mettre à jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO du fournisseur mis à jour.

        Raises:
            FournisseurNotFoundError: Si le fournisseur n'existe pas.
            FournisseurSiretExistsError: Si le nouveau SIRET existe déjà.
        """
        fournisseur = self._fournisseur_repository.find_by_id(fournisseur_id)
        if not fournisseur:
            raise FournisseurNotFoundError(fournisseur_id)

        modifications = []

        # Vérifier unicité du SIRET si modifié
        if dto.siret is not None and dto.siret != fournisseur.siret:
            if dto.siret and dto.siret.strip():
                existing = self._fournisseur_repository.find_by_siret(dto.siret.strip())
                if existing and existing.id != fournisseur_id:
                    raise FournisseurSiretExistsError(dto.siret)
            fournisseur.siret = dto.siret
            modifications.append("siret")

        # Appliquer les modifications
        if dto.raison_sociale is not None:
            fournisseur.raison_sociale = dto.raison_sociale
            modifications.append("raison_sociale")
        if dto.type is not None:
            fournisseur.type = dto.type
            modifications.append("type")
        if dto.adresse is not None:
            fournisseur.adresse = dto.adresse
            modifications.append("adresse")
        if dto.contact_principal is not None:
            fournisseur.contact_principal = dto.contact_principal
            modifications.append("contact_principal")
        if dto.telephone is not None:
            fournisseur.telephone = dto.telephone
            modifications.append("telephone")
        if dto.email is not None:
            fournisseur.email = dto.email
            modifications.append("email")
        if dto.conditions_paiement is not None:
            fournisseur.conditions_paiement = dto.conditions_paiement
            modifications.append("conditions_paiement")
        if dto.notes is not None:
            fournisseur.notes = dto.notes
            modifications.append("notes")
        if dto.actif is not None:
            fournisseur.actif = dto.actif
            modifications.append("actif")

        fournisseur.updated_at = datetime.utcnow()

        # Persister
        fournisseur = self._fournisseur_repository.save(fournisseur)

        # Journal pour chaque champ modifié
        for champ in modifications:
            self._journal_repository.save(
                JournalEntry(
                    entite_type="fournisseur",
                    entite_id=fournisseur.id,
                    action="modification",
                    details=f"Modification du champ '{champ}'",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        # Publier l'event
        self._event_bus.publish(
            FournisseurUpdatedEvent(
                fournisseur_id=fournisseur.id,
                raison_sociale=fournisseur.raison_sociale,
                updated_by=updated_by,
            )
        )

        return FournisseurDTO.from_entity(fournisseur)


class DeleteFournisseurUseCase:
    """Use case pour supprimer un fournisseur (soft delete)."""

    def __init__(
        self,
        fournisseur_repository: FournisseurRepository,
        journal_repository: JournalFinancierRepository,
        event_bus: EventBus,
    ):
        self._fournisseur_repository = fournisseur_repository
        self._journal_repository = journal_repository
        self._event_bus = event_bus

    def execute(self, fournisseur_id: int, deleted_by: int) -> bool:
        """Supprime un fournisseur (soft delete).

        Args:
            fournisseur_id: L'ID du fournisseur à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimé.

        Raises:
            FournisseurNotFoundError: Si le fournisseur n'existe pas.
        """
        fournisseur = self._fournisseur_repository.find_by_id(fournisseur_id)
        if not fournisseur:
            raise FournisseurNotFoundError(fournisseur_id)

        deleted = self._fournisseur_repository.delete(
            fournisseur_id, deleted_by=deleted_by
        )

        if deleted:
            # Journal
            self._journal_repository.save(
                JournalEntry(
                    entite_type="fournisseur",
                    entite_id=fournisseur_id,
                    action="suppression",
                    details=f"Suppression du fournisseur '{fournisseur.raison_sociale}'",
                    auteur_id=deleted_by,
                    created_at=datetime.utcnow(),
                )
            )

            # Event
            self._event_bus.publish(
                FournisseurDeletedEvent(
                    fournisseur_id=fournisseur_id,
                    deleted_by=deleted_by,
                )
            )

        return deleted


class GetFournisseurUseCase:
    """Use case pour récupérer un fournisseur."""

    def __init__(self, fournisseur_repository: FournisseurRepository):
        self._fournisseur_repository = fournisseur_repository

    def execute(self, fournisseur_id: int) -> FournisseurDTO:
        """Récupère un fournisseur par son ID.

        Args:
            fournisseur_id: L'ID du fournisseur.

        Returns:
            Le DTO du fournisseur.

        Raises:
            FournisseurNotFoundError: Si le fournisseur n'existe pas.
        """
        fournisseur = self._fournisseur_repository.find_by_id(fournisseur_id)
        if not fournisseur:
            raise FournisseurNotFoundError(fournisseur_id)

        return FournisseurDTO.from_entity(fournisseur)


class ListFournisseursUseCase:
    """Use case pour lister les fournisseurs."""

    def __init__(self, fournisseur_repository: FournisseurRepository):
        self._fournisseur_repository = fournisseur_repository

    def execute(
        self,
        type: Optional[TypeFournisseur] = None,
        actif_seulement: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> FournisseurListDTO:
        """Liste les fournisseurs avec filtres.

        Args:
            type: Filtrer par type de fournisseur.
            actif_seulement: Ne retourner que les actifs.
            limit: Nombre max de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste paginée de fournisseurs.
        """
        fournisseurs = self._fournisseur_repository.find_all(
            type=type,
            actif_seulement=actif_seulement,
            limit=limit,
            offset=offset,
        )
        total = self._fournisseur_repository.count(
            type=type,
            actif_seulement=actif_seulement,
        )

        return FournisseurListDTO(
            items=[FournisseurDTO.from_entity(f) for f in fournisseurs],
            total=total,
            limit=limit,
            offset=offset,
        )
