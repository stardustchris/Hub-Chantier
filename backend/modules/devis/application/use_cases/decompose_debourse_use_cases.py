"""Use Cases pour la decomposition des debourses.

DEV-05: Detail debourses avances - Vue decomposee par type.
"""

from decimal import Decimal
from typing import List

from ...domain.services.debourse_service import DebourseService, DecomposeDebourse
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ..dtos.decompose_debourse_dtos import (
    DecomposeDebourseDTO,
    DecomposeLotDTO,
    DecomposeDevisDTO,
)


class DecomposerDebourseLigneUseCase:
    """Use case pour decomposer les debourses d'une ligne.

    DEV-05: Breakdown par ligne : MOE, materiaux, sous-traitance,
    materiel, deplacement.
    """

    def __init__(
        self,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
    ):
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository

    def execute(self, ligne_id: int) -> DecomposeDebourseDTO:
        """Decompose les debourses d'une ligne par type.

        Args:
            ligne_id: L'ID de la ligne.

        Returns:
            DecomposeDebourseDTO avec les totaux par type.

        Raises:
            LigneDevisNotFoundError: Si la ligne n'existe pas.
        """
        from .ligne_use_cases import LigneDevisNotFoundError

        ligne = self._ligne_repository.find_by_id(ligne_id)
        if not ligne:
            raise LigneDevisNotFoundError(ligne_id)

        debourses = self._debourse_repository.find_by_ligne(ligne_id)
        decompose = DebourseService.decomposer(ligne_id, debourses)

        return self._to_dto(decompose)

    @staticmethod
    def _to_dto(decompose: DecomposeDebourse) -> DecomposeDebourseDTO:
        """Convertit un DecomposeDebourse en DTO."""
        return DecomposeDebourseDTO(
            ligne_devis_id=decompose.ligne_devis_id,
            total_moe=str(decompose.total_moe),
            total_materiaux=str(decompose.total_materiaux),
            total_sous_traitance=str(decompose.total_sous_traitance),
            total_materiel=str(decompose.total_materiel),
            total_deplacement=str(decompose.total_deplacement),
            debourse_sec=str(decompose.debourse_sec),
            details_par_type=decompose.details_par_type,
        )


class DecomposerDebourseDevisUseCase:
    """Use case pour decomposer les debourses de tout un devis.

    DEV-05: Vue interne complete des debourses par type,
    par lot et par ligne.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository

    def execute(self, devis_id: int) -> DecomposeDevisDTO:
        """Decompose les debourses de tout le devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            DecomposeDevisDTO avec les totaux par type a chaque niveau.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        lots = self._lot_repository.find_by_devis(devis_id)

        # Accumulateurs globaux
        global_moe = Decimal("0")
        global_materiaux = Decimal("0")
        global_sous_traitance = Decimal("0")
        global_materiel = Decimal("0")
        global_deplacement = Decimal("0")

        lot_dtos: List[DecomposeLotDTO] = []

        for lot in lots:
            lignes = self._ligne_repository.find_by_lot(lot.id)

            # Accumulateurs lot
            lot_moe = Decimal("0")
            lot_materiaux = Decimal("0")
            lot_sous_traitance = Decimal("0")
            lot_materiel = Decimal("0")
            lot_deplacement = Decimal("0")

            ligne_dtos: List[DecomposeDebourseDTO] = []

            for ligne in lignes:
                debourses = self._debourse_repository.find_by_ligne(ligne.id)
                decompose = DebourseService.decomposer(ligne.id, debourses)

                lot_moe += decompose.total_moe
                lot_materiaux += decompose.total_materiaux
                lot_sous_traitance += decompose.total_sous_traitance
                lot_materiel += decompose.total_materiel
                lot_deplacement += decompose.total_deplacement

                ligne_dtos.append(
                    DecomposeDebourseDTO(
                        ligne_devis_id=decompose.ligne_devis_id,
                        total_moe=str(decompose.total_moe),
                        total_materiaux=str(decompose.total_materiaux),
                        total_sous_traitance=str(decompose.total_sous_traitance),
                        total_materiel=str(decompose.total_materiel),
                        total_deplacement=str(decompose.total_deplacement),
                        debourse_sec=str(decompose.debourse_sec),
                        details_par_type=decompose.details_par_type,
                    )
                )

            lot_debourse_sec = lot_moe + lot_materiaux + lot_sous_traitance + lot_materiel + lot_deplacement

            lot_dtos.append(
                DecomposeLotDTO(
                    lot_id=lot.id,
                    lot_titre=lot.libelle,
                    total_moe=str(lot_moe),
                    total_materiaux=str(lot_materiaux),
                    total_sous_traitance=str(lot_sous_traitance),
                    total_materiel=str(lot_materiel),
                    total_deplacement=str(lot_deplacement),
                    debourse_sec=str(lot_debourse_sec),
                    lignes=ligne_dtos,
                )
            )

            global_moe += lot_moe
            global_materiaux += lot_materiaux
            global_sous_traitance += lot_sous_traitance
            global_materiel += lot_materiel
            global_deplacement += lot_deplacement

        global_debourse_sec = (
            global_moe + global_materiaux + global_sous_traitance
            + global_materiel + global_deplacement
        )

        return DecomposeDevisDTO(
            devis_id=devis_id,
            total_moe=str(global_moe),
            total_materiaux=str(global_materiaux),
            total_sous_traitance=str(global_sous_traitance),
            total_materiel=str(global_materiel),
            total_deplacement=str(global_deplacement),
            debourse_sec_total=str(global_debourse_sec),
            lots=lot_dtos,
        )
