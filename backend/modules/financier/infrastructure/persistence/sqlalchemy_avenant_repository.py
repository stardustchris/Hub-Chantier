"""Implementation SQLAlchemy du repository AvenantBudgetaire.

FIN-04: Avenants budgetaires - CRUD et somme des avenants valides.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...domain.entities.avenant_budgetaire import AvenantBudgetaire
from ...domain.repositories.avenant_repository import AvenantRepository
from .models import AvenantBudgetaireModel


class SQLAlchemyAvenantRepository(AvenantRepository):
    """Implementation SQLAlchemy du repository AvenantBudgetaire."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: AvenantBudgetaireModel) -> AvenantBudgetaire:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite AvenantBudgetaire correspondante.
        """
        return AvenantBudgetaire(
            id=model.id,
            budget_id=model.budget_id,
            numero=model.numero,
            motif=model.motif,
            montant_ht=Decimal(str(model.montant_ht)),
            impact_description=model.impact_description,
            statut=model.statut,
            created_by=model.created_by,
            validated_by=model.validated_by,
            validated_at=model.validated_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _to_model(self, entity: AvenantBudgetaire) -> AvenantBudgetaireModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite AvenantBudgetaire source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return AvenantBudgetaireModel(
            id=entity.id,
            budget_id=entity.budget_id,
            numero=entity.numero,
            motif=entity.motif,
            montant_ht=entity.montant_ht,
            impact_description=entity.impact_description,
            statut=entity.statut,
            created_by=entity.created_by,
            validated_by=entity.validated_by,
            validated_at=entity.validated_at,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
        )

    def save(self, avenant: AvenantBudgetaire) -> AvenantBudgetaire:
        """Persiste un avenant (creation ou mise a jour).

        Args:
            avenant: L'avenant a persister.

        Returns:
            L'avenant avec son ID attribue.
        """
        if avenant.id:
            # Mise a jour
            model = (
                self._session.query(AvenantBudgetaireModel)
                .filter(AvenantBudgetaireModel.id == avenant.id)
                .first()
            )
            if model:
                model.motif = avenant.motif
                model.montant_ht = avenant.montant_ht
                model.impact_description = avenant.impact_description
                model.statut = avenant.statut
                model.validated_by = avenant.validated_by
                model.validated_at = avenant.validated_at
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(avenant)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, avenant_id: int) -> Optional[AvenantBudgetaire]:
        """Recherche un avenant par son ID (exclut les supprimes).

        Args:
            avenant_id: L'ID de l'avenant.

        Returns:
            L'avenant ou None si non trouve.
        """
        model = (
            self._session.query(AvenantBudgetaireModel)
            .filter(AvenantBudgetaireModel.id == avenant_id)
            .filter(AvenantBudgetaireModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_budget_id(
        self, budget_id: int, include_deleted: bool = False
    ) -> List[AvenantBudgetaire]:
        """Liste les avenants d'un budget.

        Args:
            budget_id: L'ID du budget.
            include_deleted: Inclure les avenants supprimes.

        Returns:
            Liste des avenants du budget.
        """
        query = self._session.query(AvenantBudgetaireModel).filter(
            AvenantBudgetaireModel.budget_id == budget_id
        )
        if not include_deleted:
            query = query.filter(AvenantBudgetaireModel.deleted_at.is_(None))
        query = query.order_by(AvenantBudgetaireModel.created_at)

        return [self._to_entity(model) for model in query.all()]

    def count_by_budget_id(self, budget_id: int) -> int:
        """Compte le nombre d'avenants pour un budget (non supprimes).

        Args:
            budget_id: L'ID du budget.

        Returns:
            Le nombre d'avenants.
        """
        return (
            self._session.query(AvenantBudgetaireModel)
            .filter(AvenantBudgetaireModel.budget_id == budget_id)
            .filter(AvenantBudgetaireModel.deleted_at.is_(None))
            .count()
        )

    def delete(self, avenant_id: int, deleted_by: int) -> None:
        """Supprime un avenant (soft delete - H10).

        Args:
            avenant_id: L'ID de l'avenant a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.
        """
        model = (
            self._session.query(AvenantBudgetaireModel)
            .filter(AvenantBudgetaireModel.id == avenant_id)
            .filter(AvenantBudgetaireModel.deleted_at.is_(None))
            .first()
        )
        if model:
            model.deleted_at = datetime.utcnow()
            model.deleted_by = deleted_by
            self._session.flush()

    def somme_avenants_valides(self, budget_id: int) -> Decimal:
        """Calcule la somme des montants HT des avenants valides d'un budget.

        Args:
            budget_id: L'ID du budget.

        Returns:
            La somme des montants HT des avenants valides.
        """
        result = (
            self._session.query(
                func.coalesce(
                    func.sum(AvenantBudgetaireModel.montant_ht), 0
                )
            )
            .filter(AvenantBudgetaireModel.budget_id == budget_id)
            .filter(AvenantBudgetaireModel.statut == "valide")
            .filter(AvenantBudgetaireModel.deleted_at.is_(None))
            .scalar()
        )
        return Decimal(str(result))
