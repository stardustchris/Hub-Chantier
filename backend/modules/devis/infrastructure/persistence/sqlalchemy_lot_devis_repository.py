"""Implementation SQLAlchemy du repository LotDevis.

DEV-03: Creation devis structure - CRUD des lots/chapitres.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import LotDevis
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from .models import LotDevisModel


class SQLAlchemyLotDevisRepository(LotDevisRepository):
    """Implementation SQLAlchemy du repository LotDevis."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: LotDevisModel) -> LotDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite LotDevis correspondante.
        """
        return LotDevis(
            id=model.id,
            devis_id=model.devis_id,
            code_lot=model.numero or "",
            libelle=model.titre,
            ordre=model.ordre,
            taux_marge_lot=(
                Decimal(str(model.marge_lot_pct))
                if model.marge_lot_pct is not None
                else None
            ),
            parent_id=model.parent_id,
            montant_debourse_ht=Decimal(str(model.debourse_sec)),
            montant_vente_ht=Decimal(str(model.total_ht)),
            montant_vente_ttc=Decimal(str(model.total_ttc)),
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def save(self, lot: LotDevis) -> LotDevis:
        """Persiste un lot de devis (creation ou mise a jour).

        Args:
            lot: Le lot a persister.

        Returns:
            Le lot avec son ID attribue.
        """
        if lot.id:
            model = (
                self._session.query(LotDevisModel)
                .filter(LotDevisModel.id == lot.id)
                .first()
            )
            if model:
                model.devis_id = lot.devis_id
                model.titre = lot.libelle
                model.numero = lot.code_lot
                model.ordre = lot.ordre
                model.parent_id = lot.parent_id
                model.marge_lot_pct = lot.taux_marge_lot
                model.total_ht = lot.montant_vente_ht
                model.total_ttc = lot.montant_vente_ttc
                model.debourse_sec = lot.montant_debourse_ht
                model.updated_at = datetime.utcnow()
        else:
            model = LotDevisModel(
                devis_id=lot.devis_id,
                titre=lot.libelle,
                numero=lot.code_lot,
                ordre=lot.ordre,
                parent_id=lot.parent_id,
                marge_lot_pct=lot.taux_marge_lot,
                total_ht=lot.montant_vente_ht,
                total_ttc=lot.montant_vente_ttc,
                debourse_sec=lot.montant_debourse_ht,
                created_at=lot.created_at or datetime.utcnow(),
                created_by=lot.created_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, lot_id: int) -> Optional[LotDevis]:
        """Recherche un lot par son ID (exclut les supprimes).

        Args:
            lot_id: L'ID du lot.

        Returns:
            Le lot ou None si non trouve.
        """
        model = (
            self._session.query(LotDevisModel)
            .filter(LotDevisModel.id == lot_id)
            .filter(LotDevisModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_devis(
        self,
        devis_id: int,
        parent_id: Optional[int] = None,
    ) -> List[LotDevis]:
        """Liste les lots d'un devis, optionnellement filtres par parent.

        Args:
            devis_id: L'ID du devis.
            parent_id: Filtrer par lot parent (None = lots racine).

        Returns:
            Liste des lots ordonnee par le champ ordre.
        """
        query = (
            self._session.query(LotDevisModel)
            .filter(LotDevisModel.devis_id == devis_id)
            .filter(LotDevisModel.deleted_at.is_(None))
        )

        if parent_id is not None:
            query = query.filter(LotDevisModel.parent_id == parent_id)
        else:
            query = query.filter(LotDevisModel.parent_id.is_(None))

        query = query.order_by(LotDevisModel.ordre)
        return [self._to_entity(model) for model in query.all()]

    def find_children(self, parent_id: int) -> List[LotDevis]:
        """Liste les sous-chapitres d'un lot.

        Args:
            parent_id: L'ID du lot parent.

        Returns:
            Liste des sous-chapitres ordonnee par le champ ordre.
        """
        query = (
            self._session.query(LotDevisModel)
            .filter(LotDevisModel.parent_id == parent_id)
            .filter(LotDevisModel.deleted_at.is_(None))
            .order_by(LotDevisModel.ordre)
        )
        return [self._to_entity(model) for model in query.all()]

    def count_by_devis(self, devis_id: int) -> int:
        """Compte le nombre de lots d'un devis (exclut les supprimes).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le nombre de lots.
        """
        return (
            self._session.query(LotDevisModel)
            .filter(LotDevisModel.devis_id == devis_id)
            .filter(LotDevisModel.deleted_at.is_(None))
            .count()
        )

    def delete(self, lot_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un lot (soft delete - H10).

        Args:
            lot_id: L'ID du lot a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(LotDevisModel)
            .filter(LotDevisModel.id == lot_id)
            .filter(LotDevisModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
