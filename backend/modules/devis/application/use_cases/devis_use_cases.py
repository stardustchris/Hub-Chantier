"""Use Cases pour la gestion des devis.

DEV-03: Creation devis structure.
"""

from datetime import datetime
from typing import Optional, List

from ...domain.entities.devis import Devis
from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.devis_dtos import (
    DevisCreateDTO,
    DevisUpdateDTO,
    DevisDTO,
    DevisDetailDTO,
    DevisListDTO,
)
from ..dtos.lot_dtos import LotDevisDTO
from ..dtos.ligne_dtos import LigneDevisDTO
from ..dtos.debourse_dtos import DebourseDetailDTO


class DevisNotFoundError(Exception):
    """Erreur levee quand un devis n'est pas trouve."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        super().__init__(f"Devis {devis_id} non trouve")


class DevisNotBrouillonError(Exception):
    """Erreur levee quand on essaie de modifier un devis non brouillon."""

    def __init__(self, devis_id: int, statut: str):
        self.devis_id = devis_id
        self.statut = statut
        super().__init__(
            f"Le devis {devis_id} est en statut '{statut}' et ne peut pas etre modifie"
        )


class CreateDevisUseCase:
    """Use case pour creer un devis.

    DEV-03: Creation en statut Brouillon avec numero auto-genere.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, dto: DevisCreateDTO, created_by: int) -> DevisDTO:
        """Cree un nouveau devis en statut Brouillon.

        Args:
            dto: Les donnees du devis a creer.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO du devis cree.
        """
        numero = self._devis_repository.generate_numero()

        devis = Devis(
            numero=numero,
            client_nom=dto.client_nom,
            objet=dto.objet,
            statut="brouillon",
            chantier_id=dto.chantier_id,
            client_adresse=dto.client_adresse,
            client_email=dto.client_email,
            client_telephone=dto.client_telephone,
            date_validite=dto.date_validite,
            taux_tva_defaut=dto.taux_tva_defaut,
            marge_globale_pct=dto.marge_globale_pct,
            marge_moe_pct=dto.marge_moe_pct,
            marge_materiaux_pct=dto.marge_materiaux_pct,
            marge_sous_traitance_pct=dto.marge_sous_traitance_pct,
            coeff_frais_generaux=dto.coeff_frais_generaux,
            retenue_garantie_pct=dto.retenue_garantie_pct,
            notes=dto.notes,
            commercial_id=dto.commercial_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by,
        )

        devis = self._devis_repository.save(devis)

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis.id,
                action="creation",
                details=f"Creation du devis {numero} - {dto.objet}",
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class UpdateDevisUseCase:
    """Use case pour mettre a jour un devis (brouillon uniquement)."""

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, dto: DevisUpdateDTO, updated_by: int
    ) -> DevisDTO:
        """Met a jour un devis.

        Args:
            devis_id: L'ID du devis a mettre a jour.
            dto: Les donnees a mettre a jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO du devis mis a jour.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisNotBrouillonError: Si le devis n'est pas en brouillon.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        if devis.statut != "brouillon":
            raise DevisNotBrouillonError(devis_id, devis.statut)

        modifications = []

        if dto.client_nom is not None:
            devis.client_nom = dto.client_nom
            modifications.append("client_nom")
        if dto.objet is not None:
            devis.objet = dto.objet
            modifications.append("objet")
        if dto.chantier_id is not None:
            devis.chantier_id = dto.chantier_id
            modifications.append("chantier_id")
        if dto.client_adresse is not None:
            devis.client_adresse = dto.client_adresse
            modifications.append("client_adresse")
        if dto.client_email is not None:
            devis.client_email = dto.client_email
            modifications.append("client_email")
        if dto.client_telephone is not None:
            devis.client_telephone = dto.client_telephone
            modifications.append("client_telephone")
        if dto.date_validite is not None:
            devis.date_validite = dto.date_validite
            modifications.append("date_validite")
        if dto.taux_tva_defaut is not None:
            devis.taux_tva_defaut = dto.taux_tva_defaut
            modifications.append("taux_tva_defaut")
        if dto.marge_globale_pct is not None:
            devis.marge_globale_pct = dto.marge_globale_pct
            modifications.append("marge_globale_pct")
        if dto.marge_moe_pct is not None:
            devis.marge_moe_pct = dto.marge_moe_pct
            modifications.append("marge_moe_pct")
        if dto.marge_materiaux_pct is not None:
            devis.marge_materiaux_pct = dto.marge_materiaux_pct
            modifications.append("marge_materiaux_pct")
        if dto.marge_sous_traitance_pct is not None:
            devis.marge_sous_traitance_pct = dto.marge_sous_traitance_pct
            modifications.append("marge_sous_traitance_pct")
        if dto.coeff_frais_generaux is not None:
            devis.coeff_frais_generaux = dto.coeff_frais_generaux
            modifications.append("coeff_frais_generaux")
        if dto.retenue_garantie_pct is not None:
            devis.retenue_garantie_pct = dto.retenue_garantie_pct
            modifications.append("retenue_garantie_pct")
        if dto.notes is not None:
            devis.notes = dto.notes
            modifications.append("notes")
        if dto.commercial_id is not None:
            devis.commercial_id = dto.commercial_id
            modifications.append("commercial_id")

        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        # Journal
        if modifications:
            self._journal_repository.save(
                JournalDevis(
                    devis_id=devis.id,
                    action="modification",
                    details=f"Modification des champs: {', '.join(modifications)}",
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        return DevisDTO.from_entity(devis)


class GetDevisUseCase:
    """Use case pour recuperer un devis avec ses details complets."""

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

    def execute(self, devis_id: int) -> DevisDetailDTO:
        """Recupere un devis avec ses lots, lignes et debourses.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        lots = self._lot_repository.find_by_devis_id(devis_id)
        lot_dtos = []
        for lot in lots:
            lignes = self._ligne_repository.find_by_lot_id(lot.id)
            ligne_dtos = []
            for ligne in lignes:
                debourses = self._debourse_repository.find_by_ligne_id(ligne.id)
                debourse_dtos = [DebourseDetailDTO.from_entity(d) for d in debourses]
                ligne_dtos.append(LigneDevisDTO.from_entity(ligne, debourse_dtos))
            lot_dtos.append(LotDevisDTO.from_entity(lot, ligne_dtos))

        return DevisDetailDTO.from_entity(devis, lot_dtos)


class ListDevisUseCase:
    """Use case pour lister les devis avec pagination."""

    def __init__(self, devis_repository: DevisRepository):
        self._devis_repository = devis_repository

    def execute(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> DevisListDTO:
        """Liste les devis avec pagination."""
        devis_list = self._devis_repository.find_all(skip=offset, limit=limit)
        total = self._devis_repository.count()
        return DevisListDTO(
            items=[DevisDTO.from_entity(d) for d in devis_list],
            total=total,
            limit=limit,
            offset=offset,
        )


class DeleteDevisUseCase:
    """Use case pour supprimer un devis (brouillon uniquement, soft delete)."""

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, deleted_by: int) -> None:
        """Supprime un devis en statut brouillon uniquement.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisNotBrouillonError: Si le devis n'est pas en brouillon.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        if devis.statut != "brouillon":
            raise DevisNotBrouillonError(devis_id, devis.statut)

        self._devis_repository.delete(devis_id)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="suppression",
                details=f"Suppression du devis {devis.numero}",
                auteur_id=deleted_by,
                created_at=datetime.utcnow(),
            )
        )
