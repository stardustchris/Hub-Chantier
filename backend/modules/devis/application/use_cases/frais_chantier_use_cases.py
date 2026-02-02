"""Use Cases pour les frais de chantier.

DEV-25: Frais de chantier - CRUD + repartition prorata.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ...domain.entities.frais_chantier_devis import (
    FraisChantierDevis,
    FraisChantierValidationError,
)
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects.type_frais_chantier import TypeFraisChantier
from ...domain.value_objects.mode_repartition import ModeRepartition
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.frais_chantier_repository import FraisChantierRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.frais_chantier_dtos import (
    FraisChantierCreateDTO,
    FraisChantierUpdateDTO,
    FraisChantierDTO,
)


class FraisChantierNotFoundError(Exception):
    """Exception levee quand un frais de chantier n'est pas trouve."""

    def __init__(self, frais_id: int):
        self.frais_id = frais_id
        self.message = f"Frais de chantier {frais_id} non trouve"
        super().__init__(self.message)


class DevisNonModifiableError(Exception):
    """Exception levee quand le devis n'est pas modifiable."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        self.message = f"Le devis {devis_id} n'est pas modifiable"
        super().__init__(self.message)


class CreateFraisChantierUseCase:
    """Cas d'utilisation : Creer un frais de chantier.

    Verifie que le devis existe et est modifiable avant de creer le frais.

    Attributes:
        _frais_repo: Repository pour les frais de chantier.
        _devis_repo: Repository pour les devis.
        _journal_repo: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        frais_repo: FraisChantierRepository,
        devis_repo: DevisRepository,
        journal_repo: JournalDevisRepository,
    ):
        """Initialise le use case.

        Args:
            frais_repo: Repository frais de chantier (interface).
            devis_repo: Repository devis (interface).
            journal_repo: Repository journal (interface).
        """
        self._frais_repo = frais_repo
        self._devis_repo = devis_repo
        self._journal_repo = journal_repo

    def execute(
        self, dto: FraisChantierCreateDTO, created_by: int
    ) -> FraisChantierDTO:
        """Cree un frais de chantier.

        Args:
            dto: Les donnees de creation.
            created_by: ID de l'utilisateur createur.

        Returns:
            Le DTO du frais cree.

        Raises:
            DevisNonModifiableError: Si le devis n'est pas modifiable.
            FraisChantierValidationError: Si les donnees sont invalides.
        """
        from .devis_use_cases import DevisNotFoundError

        # 1. Verifier que le devis existe
        devis = self._devis_repo.find_by_id(dto.devis_id)
        if not devis:
            raise DevisNotFoundError(dto.devis_id)

        # 2. Verifier que le devis est modifiable
        if not devis.est_modifiable:
            raise DevisNonModifiableError(dto.devis_id)

        # 3. Convertir les enums
        type_frais = TypeFraisChantier(dto.type_frais)
        mode_repartition = ModeRepartition(dto.mode_repartition)

        # 4. Creer l'entite
        frais = FraisChantierDevis(
            devis_id=dto.devis_id,
            type_frais=type_frais,
            libelle=dto.libelle,
            montant_ht=dto.montant_ht,
            mode_repartition=mode_repartition,
            taux_tva=dto.taux_tva,
            ordre=dto.ordre,
            lot_devis_id=dto.lot_devis_id,
            created_by=created_by,
            created_at=datetime.utcnow(),
        )

        # 5. Persister
        frais = self._frais_repo.save(frais)

        # 6. Journal
        self._journal_repo.save(
            JournalDevis(
                devis_id=dto.devis_id,
                action="ajout_frais_chantier",
                details_json={
                    "message": (
                        f"Ajout frais de chantier: {frais.libelle} "
                        f"({type_frais.label}) - {frais.montant_ht} EUR HT"
                    ),
                    "frais_id": frais.id,
                    "type_frais": type_frais.value,
                },
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return FraisChantierDTO.from_entity(frais)


class UpdateFraisChantierUseCase:
    """Cas d'utilisation : Modifier un frais de chantier.

    Attributes:
        _frais_repo: Repository pour les frais de chantier.
        _devis_repo: Repository pour les devis.
        _journal_repo: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        frais_repo: FraisChantierRepository,
        devis_repo: DevisRepository,
        journal_repo: JournalDevisRepository,
    ):
        self._frais_repo = frais_repo
        self._devis_repo = devis_repo
        self._journal_repo = journal_repo

    def execute(
        self, frais_id: int, dto: FraisChantierUpdateDTO, updated_by: int
    ) -> FraisChantierDTO:
        """Met a jour un frais de chantier.

        Args:
            frais_id: L'ID du frais a modifier.
            dto: Les donnees de mise a jour.
            updated_by: ID de l'utilisateur.

        Returns:
            Le DTO du frais mis a jour.

        Raises:
            FraisChantierNotFoundError: Si le frais n'existe pas.
            DevisNonModifiableError: Si le devis n'est pas modifiable.
        """
        from .devis_use_cases import DevisNotFoundError

        # 1. Trouver le frais
        frais = self._frais_repo.find_by_id(frais_id)
        if not frais or frais.est_supprime:
            raise FraisChantierNotFoundError(frais_id)

        # 2. Verifier que le devis est modifiable
        devis = self._devis_repo.find_by_id(frais.devis_id)
        if not devis:
            raise DevisNotFoundError(frais.devis_id)
        if not devis.est_modifiable:
            raise DevisNonModifiableError(frais.devis_id)

        # 3. Appliquer les modifications
        if dto.type_frais is not None:
            frais.type_frais = TypeFraisChantier(dto.type_frais)
        if dto.libelle is not None:
            frais.libelle = dto.libelle
        if dto.montant_ht is not None:
            frais.montant_ht = dto.montant_ht
        if dto.mode_repartition is not None:
            frais.mode_repartition = ModeRepartition(dto.mode_repartition)
        if dto.taux_tva is not None:
            frais.taux_tva = dto.taux_tva
        if dto.ordre is not None:
            frais.ordre = dto.ordre
        if dto.lot_devis_id is not None:
            frais.lot_devis_id = dto.lot_devis_id

        frais.updated_at = datetime.utcnow()

        # 4. Persister
        frais = self._frais_repo.save(frais)

        # 5. Journal
        self._journal_repo.save(
            JournalDevis(
                devis_id=frais.devis_id,
                action="modification_frais_chantier",
                details_json={
                    "message": f"Modification frais de chantier: {frais.libelle}",
                    "frais_id": frais.id,
                },
                auteur_id=updated_by,
                created_at=datetime.utcnow(),
            )
        )

        return FraisChantierDTO.from_entity(frais)


class DeleteFraisChantierUseCase:
    """Cas d'utilisation : Supprimer un frais de chantier (soft delete).

    Attributes:
        _frais_repo: Repository pour les frais de chantier.
        _devis_repo: Repository pour les devis.
        _journal_repo: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        frais_repo: FraisChantierRepository,
        devis_repo: DevisRepository,
        journal_repo: JournalDevisRepository,
    ):
        self._frais_repo = frais_repo
        self._devis_repo = devis_repo
        self._journal_repo = journal_repo

    def execute(self, frais_id: int, deleted_by: int) -> None:
        """Supprime un frais de chantier.

        Args:
            frais_id: L'ID du frais a supprimer.
            deleted_by: ID de l'utilisateur.

        Raises:
            FraisChantierNotFoundError: Si le frais n'existe pas.
            DevisNonModifiableError: Si le devis n'est pas modifiable.
        """
        from .devis_use_cases import DevisNotFoundError

        # 1. Trouver le frais
        frais = self._frais_repo.find_by_id(frais_id)
        if not frais or frais.est_supprime:
            raise FraisChantierNotFoundError(frais_id)

        # 2. Verifier que le devis est modifiable
        devis = self._devis_repo.find_by_id(frais.devis_id)
        if not devis:
            raise DevisNotFoundError(frais.devis_id)
        if not devis.est_modifiable:
            raise DevisNonModifiableError(frais.devis_id)

        # 3. Soft delete
        libelle = frais.libelle
        devis_id = frais.devis_id
        self._frais_repo.delete(frais_id, deleted_by)

        # 4. Journal
        self._journal_repo.save(
            JournalDevis(
                devis_id=devis_id,
                action="suppression_frais_chantier",
                details_json={
                    "message": f"Suppression frais de chantier: {libelle}",
                    "frais_id": frais_id,
                },
                auteur_id=deleted_by,
                created_at=datetime.utcnow(),
            )
        )


class ListFraisChantierUseCase:
    """Cas d'utilisation : Lister les frais de chantier d'un devis.

    Attributes:
        _frais_repo: Repository pour les frais de chantier.
        _devis_repo: Repository pour les devis.
    """

    def __init__(
        self,
        frais_repo: FraisChantierRepository,
        devis_repo: DevisRepository,
    ):
        self._frais_repo = frais_repo
        self._devis_repo = devis_repo

    def execute(self, devis_id: int) -> List[FraisChantierDTO]:
        """Liste les frais de chantier d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des DTOs de frais de chantier.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repo.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        frais_list = self._frais_repo.find_by_devis(devis_id)
        return [FraisChantierDTO.from_entity(f) for f in frais_list]


class CalculerRepartitionFraisUseCase:
    """Cas d'utilisation : Calculer la repartition des frais prorata sur les lots.

    Calcule pour chaque lot du devis la part de chaque frais de chantier
    en mode PRORATA_LOTS.

    Attributes:
        _frais_repo: Repository pour les frais de chantier.
        _devis_repo: Repository pour les devis.
        _lot_repo: Repository pour les lots.
    """

    def __init__(
        self,
        frais_repo: FraisChantierRepository,
        devis_repo: DevisRepository,
        lot_repo: LotDevisRepository,
    ):
        self._frais_repo = frais_repo
        self._devis_repo = devis_repo
        self._lot_repo = lot_repo

    def execute(self, devis_id: int) -> dict:
        """Calcule la repartition des frais de chantier par lot.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Dictionnaire avec:
                - total_frais_ht: Total des frais HT
                - total_frais_ttc: Total des frais TTC
                - frais: Liste des frais avec details
                - repartition_par_lot: Repartition par lot

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repo.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        frais_list = self._frais_repo.find_by_devis(devis_id)
        lots = self._lot_repo.find_by_devis(devis_id)

        # Calculer le total HT du devis (somme des lots)
        devis_total_ht = sum(
            lot.montant_vente_ht for lot in lots
        ) if lots else Decimal("0")

        # Totaux des frais
        total_frais_ht = sum(f.montant_ht for f in frais_list)
        total_frais_ttc = sum(f.montant_ttc for f in frais_list)

        # Calculer la repartition par lot
        repartition_par_lot = []
        for lot in lots:
            lot_frais = []
            lot_total_frais = Decimal("0")

            for frais in frais_list:
                part = frais.calculer_repartition_lot(
                    lot.montant_vente_ht, devis_total_ht
                )
                lot_frais.append({
                    "frais_id": frais.id,
                    "libelle": frais.libelle,
                    "type_frais": frais.type_frais.value,
                    "mode_repartition": frais.mode_repartition.value,
                    "montant_reparti": str(part),
                })
                lot_total_frais += part

            repartition_par_lot.append({
                "lot_id": lot.id,
                "lot_libelle": lot.libelle,
                "lot_code": lot.code_lot,
                "lot_total_ht": str(lot.montant_vente_ht),
                "frais_repartis": lot_frais,
                "total_frais_lot": str(lot_total_frais),
            })

        return {
            "devis_id": devis_id,
            "total_frais_ht": str(total_frais_ht),
            "total_frais_ttc": str(total_frais_ttc),
            "nb_frais": len(frais_list),
            "frais": [FraisChantierDTO.from_entity(f).to_dict() for f in frais_list],
            "repartition_par_lot": repartition_par_lot,
        }
