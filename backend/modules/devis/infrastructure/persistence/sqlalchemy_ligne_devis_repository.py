"""Implementation SQLAlchemy du repository LigneDevis.

DEV-03: Creation devis structure - CRUD des lignes dans les lots.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...domain.entities import LigneDevis
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.value_objects import UniteArticle
from .models import LigneDevisModel, LotDevisModel


class SQLAlchemyLigneDevisRepository(LigneDevisRepository):
    """Implementation SQLAlchemy du repository LigneDevis."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: LigneDevisModel) -> LigneDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite LigneDevis correspondante.
        """
        return LigneDevis(
            id=model.id,
            lot_devis_id=model.lot_devis_id,
            article_id=model.article_id,
            libelle=model.designation,
            unite=UniteArticle(model.unite),
            quantite=Decimal(str(model.quantite)),
            prix_unitaire_ht=Decimal(str(model.prix_unitaire_ht)),
            taux_marge_ligne=(
                Decimal(str(model.marge_ligne_pct))
                if model.marge_ligne_pct is not None
                else None
            ),
            ordre=model.ordre,
            verrouille=False,
            total_ht=Decimal(str(model.montant_ht)),
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def save(self, ligne: LigneDevis) -> LigneDevis:
        """Persiste une ligne de devis (creation ou mise a jour).

        Args:
            ligne: La ligne a persister.

        Returns:
            La ligne avec son ID attribue.
        """
        if ligne.id:
            model = (
                self._session.query(LigneDevisModel)
                .filter(LigneDevisModel.id == ligne.id)
                .first()
            )
            if model:
                model.lot_devis_id = ligne.lot_devis_id
                model.article_id = ligne.article_id
                model.designation = ligne.libelle
                model.unite = ligne.unite.value
                model.quantite = ligne.quantite
                model.prix_unitaire_ht = ligne.prix_unitaire_ht
                model.marge_ligne_pct = ligne.taux_marge_ligne
                model.ordre = ligne.ordre
                model.montant_ht = ligne.total_ht
                model.updated_at = datetime.utcnow()
        else:
            model = LigneDevisModel(
                lot_devis_id=ligne.lot_devis_id,
                article_id=ligne.article_id,
                designation=ligne.libelle,
                unite=ligne.unite.value,
                quantite=ligne.quantite,
                prix_unitaire_ht=ligne.prix_unitaire_ht,
                taux_tva=Decimal("20"),
                marge_ligne_pct=ligne.taux_marge_ligne,
                ordre=ligne.ordre,
                montant_ht=ligne.total_ht,
                montant_ttc=Decimal("0"),
                debourse_sec=Decimal("0"),
                prix_revient=Decimal("0"),
                created_at=ligne.created_at or datetime.utcnow(),
                created_by=ligne.created_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, ligne_id: int) -> Optional[LigneDevis]:
        """Recherche une ligne par son ID (exclut les supprimees).

        Args:
            ligne_id: L'ID de la ligne.

        Returns:
            La ligne ou None si non trouvee.
        """
        model = (
            self._session.query(LigneDevisModel)
            .filter(LigneDevisModel.id == ligne_id)
            .filter(LigneDevisModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_lot(
        self,
        lot_devis_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LigneDevis]:
        """Liste les lignes d'un lot de devis (exclut les supprimees).

        Args:
            lot_devis_id: L'ID du lot.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des lignes ordonnee par le champ ordre.
        """
        query = (
            self._session.query(LigneDevisModel)
            .filter(LigneDevisModel.lot_devis_id == lot_devis_id)
            .filter(LigneDevisModel.deleted_at.is_(None))
            .order_by(LigneDevisModel.ordre)
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(model) for model in query.all()]

    def find_by_devis(self, devis_id: int) -> List[LigneDevis]:
        """Liste toutes les lignes d'un devis (tous lots confondus).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des lignes.
        """
        query = (
            self._session.query(LigneDevisModel)
            .join(LotDevisModel, LigneDevisModel.lot_devis_id == LotDevisModel.id)
            .filter(LotDevisModel.devis_id == devis_id)
            .filter(LigneDevisModel.deleted_at.is_(None))
            .filter(LotDevisModel.deleted_at.is_(None))
            .order_by(LotDevisModel.ordre, LigneDevisModel.ordre)
        )
        return [self._to_entity(model) for model in query.all()]

    def somme_by_lot(self, lot_devis_id: int) -> Decimal:
        """Calcule la somme HT des lignes d'un lot.

        Args:
            lot_devis_id: L'ID du lot.

        Returns:
            La somme HT des lignes.
        """
        result = (
            self._session.query(
                func.coalesce(func.sum(LigneDevisModel.montant_ht), 0)
            )
            .filter(LigneDevisModel.lot_devis_id == lot_devis_id)
            .filter(LigneDevisModel.deleted_at.is_(None))
            .scalar()
        )
        return Decimal(str(result))

    def count_by_lot(self, lot_devis_id: int) -> int:
        """Compte le nombre de lignes d'un lot (exclut les supprimees).

        Args:
            lot_devis_id: L'ID du lot.

        Returns:
            Le nombre de lignes.
        """
        return (
            self._session.query(LigneDevisModel)
            .filter(LigneDevisModel.lot_devis_id == lot_devis_id)
            .filter(LigneDevisModel.deleted_at.is_(None))
            .count()
        )

    def delete(self, ligne_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime une ligne (soft delete - H10).

        Args:
            ligne_id: L'ID de la ligne a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimee, False si non trouvee.
        """
        model = (
            self._session.query(LigneDevisModel)
            .filter(LigneDevisModel.id == ligne_id)
            .filter(LigneDevisModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
