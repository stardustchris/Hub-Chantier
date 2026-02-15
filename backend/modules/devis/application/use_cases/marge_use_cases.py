"""Use Cases pour la gestion des marges et coefficients.

DEV-06: Gestion marges et coefficients.
Application marges globales / par lot / par ligne.
Regle de priorite: ligne > lot > type debourse > global.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from shared.domain.calcul_financier import arrondir_montant

from ...domain.entities.journal_devis import JournalDevis
from ...domain.services.marge_service import MargeService
from ...domain.services.debourse_service import DebourseService
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.marge_dtos import (
    AppliquerMargeGlobaleDTO,
    AppliquerMargeLotDTO,
    AppliquerMargeLigneDTO,
    MargeResolueDTO,
    MargesDevisDTO,
)


class AppliquerMargeGlobaleUseCase:
    """Use case pour appliquer une marge globale a un devis.

    DEV-06: Marge au niveau global (priorite 4).
    Met a jour la marge globale et optionnellement les marges par type de debourse.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, dto: AppliquerMargeGlobaleDTO, updated_by: int
    ) -> dict:
        """Applique la marge globale au devis.

        Args:
            dto: Les parametres de marge a appliquer.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Dictionnaire avec les marges mises a jour.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            ValueError: Si le taux de marge est negatif.
        """
        from .devis_use_cases import DevisNotFoundError

        if dto.taux_marge_global < Decimal("0"):
            raise ValueError("Le taux de marge global ne peut pas etre negatif")

        devis = self._devis_repository.find_by_id(dto.devis_id)
        if not devis:
            raise DevisNotFoundError(dto.devis_id)

        ancien_taux = devis.taux_marge_global

        devis.taux_marge_global = dto.taux_marge_global
        if dto.coefficient_frais_generaux is not None:
            devis.coefficient_frais_generaux = dto.coefficient_frais_generaux

        # Marges par type de debourse
        if dto.taux_marge_moe is not None:
            devis.taux_marge_moe = dto.taux_marge_moe
        if dto.taux_marge_materiaux is not None:
            devis.taux_marge_materiaux = dto.taux_marge_materiaux
        if dto.taux_marge_sous_traitance is not None:
            devis.taux_marge_sous_traitance = dto.taux_marge_sous_traitance
        if dto.taux_marge_materiel is not None:
            devis.taux_marge_materiel = dto.taux_marge_materiel
        if dto.taux_marge_deplacement is not None:
            devis.taux_marge_deplacement = dto.taux_marge_deplacement

        devis.updated_at = datetime.utcnow()
        self._devis_repository.save(devis)

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=dto.devis_id,
                action="modification",
                details_json={
                    "message": (
                        f"Modification marge globale: {ancien_taux}% -> "
                        f"{dto.taux_marge_global}%"
                    )
                },
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        return {
            "devis_id": dto.devis_id,
            "taux_marge_global": str(devis.taux_marge_global),
            "coefficient_frais_generaux": str(devis.coefficient_frais_generaux),
            "taux_marge_moe": str(devis.taux_marge_moe) if devis.taux_marge_moe is not None else None,
            "taux_marge_materiaux": str(devis.taux_marge_materiaux) if devis.taux_marge_materiaux is not None else None,
            "taux_marge_sous_traitance": str(devis.taux_marge_sous_traitance) if devis.taux_marge_sous_traitance is not None else None,
            "taux_marge_materiel": str(devis.taux_marge_materiel) if devis.taux_marge_materiel is not None else None,
            "taux_marge_deplacement": str(devis.taux_marge_deplacement) if devis.taux_marge_deplacement is not None else None,
        }


class AppliquerMargeLotUseCase:
    """Use case pour appliquer une marge sur un lot.

    DEV-06: Marge au niveau lot (priorite 2).
    """

    def __init__(
        self,
        lot_repository: LotDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository

    def execute(
        self, dto: AppliquerMargeLotDTO, updated_by: int
    ) -> dict:
        """Applique la marge sur un lot.

        Args:
            dto: Le lot et la marge a appliquer.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Dictionnaire avec la marge mise a jour.

        Raises:
            LotDevisNotFoundError: Si le lot n'existe pas.
        """
        from .lot_use_cases import LotDevisNotFoundError

        lot = self._lot_repository.find_by_id(dto.lot_id)
        if not lot:
            raise LotDevisNotFoundError(dto.lot_id)

        if dto.taux_marge_lot is not None and dto.taux_marge_lot < Decimal("0"):
            raise ValueError("Le taux de marge du lot ne peut pas etre negatif")

        ancien_taux = lot.taux_marge_lot
        lot.taux_marge_lot = dto.taux_marge_lot
        lot = self._lot_repository.save(lot)

        # Journal
        ancien_str = str(ancien_taux) if ancien_taux is not None else "heritee"
        nouveau_str = str(dto.taux_marge_lot) if dto.taux_marge_lot is not None else "heritee"
        self._journal_repository.save(
            JournalDevis(
                devis_id=lot.devis_id,
                action="modification_lot",
                details_json={
                    "message": (
                        f"Modification marge lot '{lot.libelle}': "
                        f"{ancien_str}% -> {nouveau_str}%"
                    )
                },
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        return {
            "lot_id": lot.id,
            "libelle": lot.libelle,
            "taux_marge_lot": str(lot.taux_marge_lot) if lot.taux_marge_lot is not None else None,
        }


class AppliquerMargeLigneUseCase:
    """Use case pour appliquer une marge sur une ligne.

    DEV-06: Marge au niveau ligne (priorite 1 - maximale).
    """

    def __init__(
        self,
        ligne_repository: LigneDevisRepository,
        lot_repository: LotDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._ligne_repository = ligne_repository
        self._lot_repository = lot_repository
        self._journal_repository = journal_repository

    def execute(
        self, dto: AppliquerMargeLigneDTO, updated_by: int
    ) -> dict:
        """Applique la marge sur une ligne.

        Args:
            dto: La ligne et la marge a appliquer.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Dictionnaire avec la marge mise a jour.

        Raises:
            LigneDevisNotFoundError: Si la ligne n'existe pas.
        """
        from .ligne_use_cases import LigneDevisNotFoundError

        ligne = self._ligne_repository.find_by_id(dto.ligne_id)
        if not ligne:
            raise LigneDevisNotFoundError(dto.ligne_id)

        if dto.taux_marge_ligne is not None and dto.taux_marge_ligne < Decimal("0"):
            raise ValueError("Le taux de marge de la ligne ne peut pas etre negatif")

        ancien_taux = ligne.taux_marge_ligne
        ligne.taux_marge_ligne = dto.taux_marge_ligne
        ligne = self._ligne_repository.save(ligne)

        # Journal
        lot = self._lot_repository.find_by_id(ligne.lot_devis_id)
        if lot:
            ancien_str = str(ancien_taux) if ancien_taux is not None else "heritee"
            nouveau_str = str(dto.taux_marge_ligne) if dto.taux_marge_ligne is not None else "heritee"
            self._journal_repository.save(
                JournalDevis(
                    devis_id=lot.devis_id,
                    action="modification_ligne",
                    details_json={
                        "message": (
                            f"Modification marge ligne '{ligne.libelle}': "
                            f"{ancien_str}% -> {nouveau_str}%"
                        )
                    },
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        return {
            "ligne_id": ligne.id,
            "libelle": ligne.libelle,
            "taux_marge_ligne": str(ligne.taux_marge_ligne) if ligne.taux_marge_ligne is not None else None,
        }


class ConsulterMargesDevisUseCase:
    """Use case pour consulter les marges resolues de tout un devis.

    DEV-06: Vue Debours (interne uniquement) - affiche les marges
    resolues a chaque niveau avec tracabilite.
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

    def execute(self, devis_id: int) -> MargesDevisDTO:
        """Consulte les marges resolues de tout le devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            MargesDevisDTO avec les marges resolues pour chaque ligne.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        lots = self._lot_repository.find_by_devis(devis_id)

        ligne_marges: List[MargeResolueDTO] = []
        total_debourse_sec = Decimal("0")
        total_prix_revient = Decimal("0")
        total_prix_vente_ht = Decimal("0")

        for lot in lots:
            lignes = self._ligne_repository.find_by_lot(lot.id)

            for ligne in lignes:
                debourses = self._debourse_repository.find_by_ligne(ligne.id)

                # Debourse sec
                debourse_sec = DebourseService.calculer_debourse_sec(debourses)

                # Prix de revient
                prix_revient = arrondir_montant(
                    MargeService.calculer_prix_revient(
                        debourse_sec, devis.coefficient_frais_generaux
                    )
                )

                # Resoudre la marge
                marge_resolue = MargeService.resoudre_marge(
                    ligne_marge=ligne.taux_marge_ligne,
                    lot_marge=lot.taux_marge_lot,
                    devis=devis,
                    debourses=debourses,
                )

                # Prix de vente HT
                prix_vente_ht = arrondir_montant(
                    MargeService.calculer_prix_vente_ht(
                        prix_revient, marge_resolue.taux
                    )
                )

                total_debourse_sec += debourse_sec
                total_prix_revient += prix_revient
                total_prix_vente_ht += prix_vente_ht

                ligne_marges.append(
                    MargeResolueDTO(
                        ligne_id=ligne.id,
                        taux_marge=str(marge_resolue.taux),
                        niveau=marge_resolue.niveau,
                        debourse_sec=str(debourse_sec),
                        prix_revient=str(prix_revient),
                        prix_vente_ht=str(prix_vente_ht),
                    )
                )

        marge_globale_montant = total_prix_vente_ht - total_prix_revient

        return MargesDevisDTO(
            devis_id=devis_id,
            taux_marge_global=str(devis.taux_marge_global),
            coefficient_frais_generaux=str(devis.coefficient_frais_generaux),
            taux_marge_moe=str(devis.taux_marge_moe) if devis.taux_marge_moe is not None else None,
            taux_marge_materiaux=str(devis.taux_marge_materiaux) if devis.taux_marge_materiaux is not None else None,
            taux_marge_sous_traitance=str(devis.taux_marge_sous_traitance) if devis.taux_marge_sous_traitance is not None else None,
            taux_marge_materiel=str(devis.taux_marge_materiel) if devis.taux_marge_materiel is not None else None,
            taux_marge_deplacement=str(devis.taux_marge_deplacement) if devis.taux_marge_deplacement is not None else None,
            total_debourse_sec=str(total_debourse_sec),
            total_prix_revient=str(total_prix_revient),
            total_prix_vente_ht=str(total_prix_vente_ht),
            marge_globale_montant=str(marge_globale_montant),
            lignes=ligne_marges,
        )
