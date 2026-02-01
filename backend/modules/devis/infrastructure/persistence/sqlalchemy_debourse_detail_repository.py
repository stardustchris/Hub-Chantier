"""Implementation SQLAlchemy du repository DebourseDetail.

DEV-05: Detail debourses avances - CRUD des sous-details par ligne.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...domain.entities import DebourseDetail
from ...domain.repositories.debourse_detail_repository import (
    DebourseDetailRepository,
)
from ...domain.value_objects import TypeDebourse
from .models import DebourseDetailModel


class SQLAlchemyDebourseDetailRepository(DebourseDetailRepository):
    """Implementation SQLAlchemy du repository DebourseDetail.

    Note: DebourseDetailModel n'a pas de soft delete (deleted_at).
    Les suppressions sont physiques.
    """

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: DebourseDetailModel) -> DebourseDetail:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite DebourseDetail correspondante.
        """
        return DebourseDetail(
            id=model.id,
            ligne_devis_id=model.ligne_devis_id,
            type_debourse=TypeDebourse(model.type_debourse),
            libelle=model.designation,
            quantite=Decimal(str(model.quantite)),
            prix_unitaire=Decimal(str(model.prix_unitaire)),
            metier=None,
            taux_horaire=None,
            total=Decimal(str(model.montant)),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, debourse: DebourseDetail) -> DebourseDetail:
        """Persiste un debourse detaille (creation ou mise a jour).

        Args:
            debourse: Le debourse a persister.

        Returns:
            Le debourse avec son ID attribue.
        """
        if debourse.id:
            model = (
                self._session.query(DebourseDetailModel)
                .filter(DebourseDetailModel.id == debourse.id)
                .first()
            )
            if model:
                model.ligne_devis_id = debourse.ligne_devis_id
                model.type_debourse = debourse.type_debourse.value
                model.designation = debourse.libelle
                model.quantite = debourse.quantite
                model.prix_unitaire = debourse.prix_unitaire
                model.montant = debourse.total
                model.updated_at = datetime.utcnow()
        else:
            model = DebourseDetailModel(
                ligne_devis_id=debourse.ligne_devis_id,
                type_debourse=debourse.type_debourse.value,
                designation=debourse.libelle,
                quantite=debourse.quantite,
                prix_unitaire=debourse.prix_unitaire,
                unite="u",
                montant=debourse.total,
                created_at=debourse.created_at or datetime.utcnow(),
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, debourse_id: int) -> Optional[DebourseDetail]:
        """Recherche un debourse par son ID.

        Args:
            debourse_id: L'ID du debourse.

        Returns:
            Le debourse ou None si non trouve.
        """
        model = (
            self._session.query(DebourseDetailModel)
            .filter(DebourseDetailModel.id == debourse_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_ligne(self, ligne_devis_id: int) -> List[DebourseDetail]:
        """Liste les debourses d'une ligne de devis.

        Args:
            ligne_devis_id: L'ID de la ligne.

        Returns:
            Liste des debourses.
        """
        query = (
            self._session.query(DebourseDetailModel)
            .filter(DebourseDetailModel.ligne_devis_id == ligne_devis_id)
            .order_by(DebourseDetailModel.id)
        )
        return [self._to_entity(model) for model in query.all()]

    def find_by_ligne_and_type(
        self,
        ligne_devis_id: int,
        type_debourse: TypeDebourse,
    ) -> List[DebourseDetail]:
        """Liste les debourses d'une ligne par type.

        Args:
            ligne_devis_id: L'ID de la ligne.
            type_debourse: Le type de debourse.

        Returns:
            Liste des debourses du type specifie.
        """
        query = (
            self._session.query(DebourseDetailModel)
            .filter(DebourseDetailModel.ligne_devis_id == ligne_devis_id)
            .filter(DebourseDetailModel.type_debourse == type_debourse.value)
            .order_by(DebourseDetailModel.id)
        )
        return [self._to_entity(model) for model in query.all()]

    def somme_by_ligne(self, ligne_devis_id: int) -> Decimal:
        """Calcule la somme des debourses d'une ligne (debourse sec).

        Args:
            ligne_devis_id: L'ID de la ligne.

        Returns:
            La somme des debourses.
        """
        result = (
            self._session.query(
                func.coalesce(func.sum(DebourseDetailModel.montant), 0)
            )
            .filter(DebourseDetailModel.ligne_devis_id == ligne_devis_id)
            .scalar()
        )
        return Decimal(str(result))

    def somme_by_ligne_and_type(
        self,
        ligne_devis_id: int,
        type_debourse: TypeDebourse,
    ) -> Decimal:
        """Calcule la somme des debourses d'une ligne par type.

        Args:
            ligne_devis_id: L'ID de la ligne.
            type_debourse: Le type de debourse.

        Returns:
            La somme des debourses du type specifie.
        """
        result = (
            self._session.query(
                func.coalesce(func.sum(DebourseDetailModel.montant), 0)
            )
            .filter(DebourseDetailModel.ligne_devis_id == ligne_devis_id)
            .filter(DebourseDetailModel.type_debourse == type_debourse.value)
            .scalar()
        )
        return Decimal(str(result))

    def delete(self, debourse_id: int) -> bool:
        """Supprime un debourse (suppression physique).

        Args:
            debourse_id: L'ID du debourse a supprimer.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(DebourseDetailModel)
            .filter(DebourseDetailModel.id == debourse_id)
            .first()
        )
        if not model:
            return False

        self._session.delete(model)
        self._session.flush()
        return True

    def delete_by_ligne(self, ligne_devis_id: int) -> int:
        """Supprime tous les debourses d'une ligne (suppression physique).

        Args:
            ligne_devis_id: L'ID de la ligne.

        Returns:
            Le nombre de debourses supprimes.
        """
        count = (
            self._session.query(DebourseDetailModel)
            .filter(DebourseDetailModel.ligne_devis_id == ligne_devis_id)
            .delete(synchronize_session="fetch")
        )
        self._session.flush()
        return count
