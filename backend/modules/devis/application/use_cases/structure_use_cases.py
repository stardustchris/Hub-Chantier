"""Use Cases pour la creation de devis structure.

DEV-03: Creation devis structure - Arborescence lots/chapitres/sous-chapitres/lignes
avec numerotation automatique, quantites, prix unitaires, totaux automatiques
et reorganisation par drag (ordre_affichage).
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ...domain.entities.lot_devis import LotDevis
from ...domain.entities.ligne_devis import LigneDevis
from ...domain.entities.debourse_detail import DebourseDetail
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects import TypeDebourse, UniteArticle
from ...domain.services.numerotation_service import NumerotationService
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.structure_dtos import (
    CreateDevisStructureDTO,
    LotStructureDTO,
    SousChapitreStructureDTO,
    LigneStructureDTO,
    ReorderRequestDTO,
    StructureDevisDTO,
)
from ..dtos.lot_dtos import LotDevisDTO
from ..dtos.ligne_dtos import LigneDevisDTO
from ..dtos.debourse_dtos import DebourseDetailDTO


class CreateDevisStructureUseCase:
    """Use case pour creer une arborescence complete de devis.

    DEV-03: Cree en batch lots, sous-chapitres, lignes et debourses
    avec numerotation automatique hierarchique.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository

    def execute(
        self, dto: CreateDevisStructureDTO, created_by: int
    ) -> StructureDevisDTO:
        """Cree la structure complete du devis.

        Args:
            dto: La structure a creer (lots, sous-chapitres, lignes, debourses).
            created_by: L'ID de l'utilisateur createur.

        Returns:
            StructureDevisDTO avec la structure creee et les totaux.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(dto.devis_id)
        if not devis:
            raise DevisNotFoundError(dto.devis_id)

        lot_dtos: List[LotDevisDTO] = []
        total_lignes = 0

        for lot_idx, lot_dto in enumerate(dto.lots):
            # Creer le lot racine avec numerotation automatique
            code_lot = NumerotationService.generer_code_lot(lot_idx)
            lot = self._create_lot(
                devis_id=dto.devis_id,
                titre=lot_dto.titre,
                code_lot=code_lot,
                ordre=lot_idx,
                marge_lot_pct=lot_dto.marge_lot_pct,
                parent_id=None,
                created_by=created_by,
            )

            # Creer les lignes directes du lot
            ligne_dtos = self._create_lignes(
                lot_id=lot.id,
                lignes=lot_dto.lignes,
                lot_code=code_lot,
                start_ordre=0,
                created_by=created_by,
            )
            total_lignes += len(ligne_dtos)

            # Creer les sous-chapitres
            for sc_idx, sc_dto in enumerate(lot_dto.sous_chapitres):
                sc_code = NumerotationService.generer_code_lot(sc_idx, parent_code=code_lot)
                sous_chapitre = self._create_lot(
                    devis_id=dto.devis_id,
                    titre=sc_dto.titre,
                    code_lot=sc_code,
                    ordre=sc_idx,
                    marge_lot_pct=sc_dto.marge_lot_pct,
                    parent_id=lot.id,
                    created_by=created_by,
                )

                sc_ligne_dtos = self._create_lignes(
                    lot_id=sous_chapitre.id,
                    lignes=sc_dto.lignes,
                    lot_code=sc_code,
                    start_ordre=0,
                    created_by=created_by,
                )
                total_lignes += len(sc_ligne_dtos)

            lot_dtos.append(LotDevisDTO.from_entity(lot, ligne_dtos))

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=dto.devis_id,
                action="creation",
                details_json={
                    "message": (
                        f"Creation structure: {len(dto.lots)} lot(s), "
                        f"{total_lignes} ligne(s)"
                    )
                },
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return StructureDevisDTO(
            devis_id=dto.devis_id,
            lots=lot_dtos,
            nombre_lots=len(dto.lots),
            nombre_lignes=total_lignes,
            total_debourse_sec="0",
            total_ht="0",
            total_ttc="0",
        )

    def _create_lot(
        self,
        devis_id: int,
        titre: str,
        code_lot: str,
        ordre: int,
        marge_lot_pct: Optional[Decimal],
        parent_id: Optional[int],
        created_by: int,
    ) -> LotDevis:
        """Cree et persiste un lot."""
        lot = LotDevis(
            devis_id=devis_id,
            code_lot=code_lot,
            libelle=titre,
            ordre=ordre,
            taux_marge_lot=marge_lot_pct,
            parent_id=parent_id,
            created_by=created_by,
        )
        return self._lot_repository.save(lot)

    def _create_lignes(
        self,
        lot_id: int,
        lignes: List[LigneStructureDTO],
        lot_code: str,
        start_ordre: int,
        created_by: int,
    ) -> List[LigneDevisDTO]:
        """Cree et persiste une liste de lignes avec leurs debourses."""
        result: List[LigneDevisDTO] = []

        for idx, ligne_dto in enumerate(lignes):
            ordre = start_ordre + idx

            try:
                unite_enum = UniteArticle(ligne_dto.unite.lower()) if ligne_dto.unite else UniteArticle.U
            except ValueError:
                unite_enum = UniteArticle.U

            ligne = LigneDevis(
                lot_devis_id=lot_id,
                libelle=ligne_dto.designation,
                unite=unite_enum,
                quantite=ligne_dto.quantite,
                prix_unitaire_ht=ligne_dto.prix_unitaire_ht,
                taux_tva=ligne_dto.taux_tva,
                ordre=ordre,
                taux_marge_ligne=ligne_dto.marge_ligne_pct,
                article_id=ligne_dto.article_id,
                created_by=created_by,
            )
            ligne = self._ligne_repository.save(ligne)

            # Creer les debourses
            debourse_dtos: List[DebourseDetailDTO] = []
            for deb_dto in ligne_dto.debourses:
                try:
                    type_enum = TypeDebourse(deb_dto.type_debourse)
                except ValueError:
                    type_enum = TypeDebourse.MATERIAUX

                debourse = DebourseDetail(
                    ligne_devis_id=ligne.id,
                    type_debourse=type_enum,
                    libelle=deb_dto.designation,
                    quantite=deb_dto.quantite,
                    prix_unitaire=deb_dto.prix_unitaire,
                    total=deb_dto.quantite * deb_dto.prix_unitaire,
                )
                debourse = self._debourse_repository.save(debourse)
                debourse_dtos.append(DebourseDetailDTO.from_entity(debourse))

            result.append(LigneDevisDTO.from_entity(ligne, debourse_dtos))

        return result


class RenumeroterDevisUseCase:
    """Use case pour renumeroter automatiquement l'arborescence d'un devis.

    DEV-03: Regenere les codes hierarchiques de tous les lots et lignes
    apres un reordonnement.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, updated_by: int) -> List[LotDevisDTO]:
        """Renumerote toute l'arborescence du devis.

        Args:
            devis_id: L'ID du devis.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Liste des lots renumerotes.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # Recuperer les lots racine
        lots_racine = self._lot_repository.find_by_devis(devis_id, parent_id=None)

        result: List[LotDevisDTO] = []
        for lot_idx, lot in enumerate(lots_racine):
            new_code = NumerotationService.generer_code_lot(lot_idx)
            lot.code_lot = new_code
            lot.ordre = lot_idx
            lot = self._lot_repository.save(lot)

            # Renumeroter les sous-chapitres
            self._renumeroter_enfants(lot.id, new_code)

            result.append(LotDevisDTO.from_entity(lot))

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="reordonnement_lots",
                details_json={"message": "Renumerotation automatique de l'arborescence"},
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        return result

    def _renumeroter_enfants(self, parent_id: int, parent_code: str) -> None:
        """Renumerote recursivement les sous-chapitres."""
        enfants = self._lot_repository.find_children(parent_id)
        for idx, enfant in enumerate(enfants):
            new_code = NumerotationService.generer_code_lot(idx, parent_code)
            enfant.code_lot = new_code
            enfant.ordre = idx
            self._lot_repository.save(enfant)
            # Recursion
            self._renumeroter_enfants(enfant.id, new_code)


class GetStructureDevisUseCase:
    """Use case pour recuperer la structure complete d'un devis.

    DEV-03: Arborescence lots/chapitres/lignes avec totaux.
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

    def execute(self, devis_id: int) -> StructureDevisDTO:
        """Recupere la structure complete du devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            StructureDevisDTO avec l'arborescence et totaux.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        lots = self._lot_repository.find_by_devis(devis_id, parent_id=None)

        lot_dtos: List[LotDevisDTO] = []
        total_lignes = 0
        total_debourse_sec = Decimal("0")
        total_ht = Decimal("0")
        total_ttc = Decimal("0")

        for lot in lots:
            lignes = self._ligne_repository.find_by_lot(lot.id)
            ligne_dtos: List[LigneDevisDTO] = []

            for ligne in lignes:
                debourses = self._debourse_repository.find_by_ligne(ligne.id)
                debourse_dtos = [DebourseDetailDTO.from_entity(d) for d in debourses]
                ligne_dtos.append(LigneDevisDTO.from_entity(ligne, debourse_dtos))

            total_lignes += len(ligne_dtos)
            total_debourse_sec += lot.montant_debourse_ht
            total_ht += lot.montant_vente_ht
            total_ttc += lot.montant_vente_ttc

            lot_dtos.append(LotDevisDTO.from_entity(lot, ligne_dtos))

        return StructureDevisDTO(
            devis_id=devis_id,
            lots=lot_dtos,
            nombre_lots=len(lots),
            nombre_lignes=total_lignes,
            total_debourse_sec=str(total_debourse_sec),
            total_ht=str(total_ht),
            total_ttc=str(total_ttc),
        )
