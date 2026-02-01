"""Use Cases pour la gestion des lignes de devis.

DEV-03 + DEV-05: Lignes de devis avec debourses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from ...domain.entities.ligne_devis import LigneDevis
from ...domain.entities.debourse_detail import DebourseDetail
from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.ligne_dtos import LigneDevisCreateDTO, LigneDevisUpdateDTO, LigneDevisDTO
from ..dtos.debourse_dtos import DebourseDetailDTO


class LigneDevisNotFoundError(Exception):
    """Erreur levee quand une ligne n'est pas trouvee."""

    def __init__(self, ligne_id: int):
        self.ligne_id = ligne_id
        super().__init__(f"Ligne de devis {ligne_id} non trouvee")


class CreateLigneDevisUseCase:
    """Use case pour creer une ligne dans un lot de devis.

    DEV-03 + DEV-05: Ligne avec debourses inline.
    """

    def __init__(
        self,
        ligne_repository: LigneDevisRepository,
        lot_repository: LotDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._ligne_repository = ligne_repository
        self._lot_repository = lot_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository

    def execute(
        self, dto: LigneDevisCreateDTO, created_by: int
    ) -> LigneDevisDTO:
        """Cree une nouvelle ligne avec ses debourses.

        Args:
            dto: Les donnees de la ligne a creer.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de la ligne creee avec debourses.
        """
        from .lot_use_cases import LotDevisNotFoundError

        lot = self._lot_repository.find_by_id(dto.lot_devis_id)
        if not lot:
            raise LotDevisNotFoundError(dto.lot_devis_id)

        ligne = LigneDevis(
            lot_devis_id=dto.lot_devis_id,
            designation=dto.designation,
            unite=dto.unite,
            quantite=dto.quantite,
            prix_unitaire_ht=dto.prix_unitaire_ht,
            taux_tva=dto.taux_tva,
            ordre=dto.ordre,
            marge_ligne_pct=dto.marge_ligne_pct,
            article_id=dto.article_id,
        )

        ligne = self._ligne_repository.save(ligne)

        # Creer les debourses associes
        debourse_dtos = []
        for deb_dto in dto.debourses:
            debourse = DebourseDetail(
                ligne_devis_id=ligne.id,
                type_debourse=deb_dto.type_debourse,
                designation=deb_dto.designation,
                quantite=deb_dto.quantite,
                prix_unitaire=deb_dto.prix_unitaire,
                unite=deb_dto.unite,
            )
            debourse = self._debourse_repository.save(debourse)
            debourse_dtos.append(DebourseDetailDTO.from_entity(debourse))

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=lot.devis_id,
                action="ajout_ligne",
                details=f"Ajout de la ligne '{dto.designation}' dans le lot '{lot.titre}'",
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return LigneDevisDTO.from_entity(ligne, debourse_dtos)


class UpdateLigneDevisUseCase:
    """Use case pour mettre a jour une ligne de devis."""

    def __init__(
        self,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
        lot_repository: LotDevisRepository,
    ):
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository
        self._lot_repository = lot_repository

    def execute(
        self, ligne_id: int, dto: LigneDevisUpdateDTO, updated_by: int
    ) -> LigneDevisDTO:
        """Met a jour une ligne de devis et remplace ses debourses.

        Raises:
            LigneDevisNotFoundError: Si la ligne n'existe pas.
        """
        ligne = self._ligne_repository.find_by_id(ligne_id)
        if not ligne:
            raise LigneDevisNotFoundError(ligne_id)

        if dto.designation is not None:
            ligne.designation = dto.designation
        if dto.unite is not None:
            ligne.unite = dto.unite
        if dto.quantite is not None:
            ligne.quantite = dto.quantite
        if dto.prix_unitaire_ht is not None:
            ligne.prix_unitaire_ht = dto.prix_unitaire_ht
        if dto.taux_tva is not None:
            ligne.taux_tva = dto.taux_tva
        if dto.ordre is not None:
            ligne.ordre = dto.ordre
        if dto.marge_ligne_pct is not None:
            ligne.marge_ligne_pct = dto.marge_ligne_pct
        if dto.article_id is not None:
            ligne.article_id = dto.article_id

        ligne = self._ligne_repository.save(ligne)

        # Si debourses fournis, remplacer
        debourse_dtos = []
        if dto.debourses is not None:
            self._debourse_repository.delete_by_ligne_id(ligne_id)
            for deb_dto in dto.debourses:
                debourse = DebourseDetail(
                    ligne_devis_id=ligne.id,
                    type_debourse=deb_dto.type_debourse,
                    designation=deb_dto.designation,
                    quantite=deb_dto.quantite,
                    prix_unitaire=deb_dto.prix_unitaire,
                    unite=deb_dto.unite,
                )
                debourse = self._debourse_repository.save(debourse)
                debourse_dtos.append(DebourseDetailDTO.from_entity(debourse))
        else:
            debourses = self._debourse_repository.find_by_ligne_id(ligne_id)
            debourse_dtos = [DebourseDetailDTO.from_entity(d) for d in debourses]

        # Journal
        lot = self._lot_repository.find_by_id(ligne.lot_devis_id)
        if lot:
            self._journal_repository.save(
                JournalDevis(
                    devis_id=lot.devis_id,
                    action="modification_ligne",
                    details=f"Modification de la ligne '{ligne.designation}'",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        return LigneDevisDTO.from_entity(ligne, debourse_dtos)


class DeleteLigneDevisUseCase:
    """Use case pour supprimer une ligne de devis."""

    def __init__(
        self,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
        lot_repository: LotDevisRepository,
    ):
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository
        self._lot_repository = lot_repository

    def execute(self, ligne_id: int, deleted_by: int) -> None:
        """Supprime une ligne et ses debourses.

        Raises:
            LigneDevisNotFoundError: Si la ligne n'existe pas.
        """
        ligne = self._ligne_repository.find_by_id(ligne_id)
        if not ligne:
            raise LigneDevisNotFoundError(ligne_id)

        # Supprimer les debourses d'abord
        self._debourse_repository.delete_by_ligne_id(ligne_id)
        self._ligne_repository.delete(ligne_id)

        # Journal
        lot = self._lot_repository.find_by_id(ligne.lot_devis_id)
        if lot:
            self._journal_repository.save(
                JournalDevis(
                    devis_id=lot.devis_id,
                    action="suppression_ligne",
                    details=f"Suppression de la ligne '{ligne.designation}'",
                    auteur_id=deleted_by,
                    created_at=datetime.utcnow(),
                )
            )
