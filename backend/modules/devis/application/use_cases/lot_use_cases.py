"""Use Cases pour la gestion des lots de devis.

DEV-03: Creation devis structure - Arborescence par lots.
"""

from datetime import datetime
from typing import List

from ...domain.entities.lot_devis import LotDevis
from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.lot_dtos import LotDevisCreateDTO, LotDevisUpdateDTO, LotDevisDTO


class LotDevisNotFoundError(Exception):
    """Erreur levee quand un lot n'est pas trouve."""

    def __init__(self, lot_id: int):
        self.lot_id = lot_id
        super().__init__(f"Lot de devis {lot_id} non trouve")


class CreateLotDevisUseCase:
    """Use case pour creer un lot dans un devis."""

    def __init__(
        self,
        lot_repository: LotDevisRepository,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._lot_repository = lot_repository
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, dto: LotDevisCreateDTO, created_by: int
    ) -> LotDevisDTO:
        """Cree un nouveau lot dans un devis.

        Args:
            dto: Les donnees du lot a creer.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO du lot cree.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(dto.devis_id)
        if not devis:
            raise DevisNotFoundError(dto.devis_id)

        lot = LotDevis(
            devis_id=dto.devis_id,
            libelle=dto.titre,
            code_lot=dto.numero or f"LOT-{dto.ordre:03d}",
            ordre=dto.ordre,
            taux_marge_lot=dto.marge_lot_pct,
            created_by=created_by,
        )

        lot = self._lot_repository.save(lot)

        self._journal_repository.save(
            JournalDevis(
                devis_id=dto.devis_id,
                action="ajout_lot",
                details_json={"message": f"Ajout du lot '{dto.titre}'"},
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return LotDevisDTO.from_entity(lot)


class UpdateLotDevisUseCase:
    """Use case pour mettre a jour un lot."""

    def __init__(
        self,
        lot_repository: LotDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository

    def execute(
        self, lot_id: int, dto: LotDevisUpdateDTO, updated_by: int
    ) -> LotDevisDTO:
        """Met a jour un lot de devis.

        Raises:
            LotDevisNotFoundError: Si le lot n'existe pas.
        """
        lot = self._lot_repository.find_by_id(lot_id)
        if not lot:
            raise LotDevisNotFoundError(lot_id)

        if dto.titre is not None:
            lot.libelle = dto.titre
        if dto.numero is not None:
            lot.code_lot = dto.numero
        if dto.ordre is not None:
            lot.ordre = dto.ordre
        if dto.marge_lot_pct is not None:
            lot.taux_marge_lot = dto.marge_lot_pct

        lot = self._lot_repository.save(lot)

        self._journal_repository.save(
            JournalDevis(
                devis_id=lot.devis_id,
                action="modification_lot",
                details_json={"message": f"Modification du lot '{lot.libelle}'"},
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        return LotDevisDTO.from_entity(lot)


class DeleteLotDevisUseCase:
    """Use case pour supprimer un lot."""

    def __init__(
        self,
        lot_repository: LotDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository

    def execute(self, lot_id: int, deleted_by: int) -> None:
        """Supprime un lot de devis.

        Raises:
            LotDevisNotFoundError: Si le lot n'existe pas.
        """
        lot = self._lot_repository.find_by_id(lot_id)
        if not lot:
            raise LotDevisNotFoundError(lot_id)

        self._lot_repository.delete(lot_id)

        self._journal_repository.save(
            JournalDevis(
                devis_id=lot.devis_id,
                action="suppression_lot",
                details_json={"message": f"Suppression du lot '{lot.libelle}'"},
                auteur_id=deleted_by,
                created_at=datetime.utcnow(),
            )
        )


class ReorderLotsUseCase:
    """Use case pour reordonner les lots d'un devis."""

    def __init__(
        self,
        lot_repository: LotDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, lot_ids: List[int], updated_by: int
    ) -> List[LotDevisDTO]:
        """Reordonne les lots d'un devis.

        Args:
            devis_id: L'ID du devis.
            lot_ids: Liste des IDs de lots dans le nouvel ordre.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Liste des lots reordonnes.
        """
        # Reordonner manuellement en mettant a jour l'ordre de chaque lot
        for new_order, lot_id in enumerate(lot_ids):
            lot = self._lot_repository.find_by_id(lot_id)
            if lot and lot.devis_id == devis_id:
                lot.ordre = new_order
                self._lot_repository.save(lot)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="reordonnement_lots",
                details_json={"message": "Reordonnement des lots"},
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        lots = self._lot_repository.find_by_devis(devis_id)
        return [LotDevisDTO.from_entity(lot) for lot in lots]
