"""Implementation SQLAlchemy des repositories Situation de Travaux.

FIN-07: Situations de travaux - persistence SQLAlchemy.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.situation_travaux import SituationTravaux
from ...domain.entities.ligne_situation import LigneSituation
from ...domain.repositories.situation_repository import (
    SituationRepository,
    LigneSituationRepository,
)
from .models import SituationTravauxModel, LigneSituationModel


class SQLAlchemySituationRepository(SituationRepository):
    """Implementation SQLAlchemy du repository SituationTravaux."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: SituationTravauxModel) -> SituationTravaux:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite SituationTravaux correspondante.
        """
        return SituationTravaux(
            id=model.id,
            chantier_id=model.chantier_id,
            budget_id=model.budget_id,
            numero=model.numero,
            periode_debut=model.periode_debut,
            periode_fin=model.periode_fin,
            montant_cumule_precedent_ht=Decimal(str(model.montant_cumule_precedent_ht)),
            montant_periode_ht=Decimal(str(model.montant_periode_ht)),
            montant_cumule_ht=Decimal(str(model.montant_cumule_ht)),
            retenue_garantie_pct=Decimal(str(model.retenue_garantie_pct)),
            taux_tva=Decimal(str(model.taux_tva)),
            statut=model.statut,
            notes=model.notes,
            created_by=model.created_by,
            validated_by=model.validated_by,
            validated_at=model.validated_at,
            emise_at=model.emise_at,
            facturee_at=model.facturee_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _to_model(self, entity: SituationTravaux) -> SituationTravauxModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite SituationTravaux source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return SituationTravauxModel(
            id=entity.id,
            chantier_id=entity.chantier_id,
            budget_id=entity.budget_id,
            numero=entity.numero,
            periode_debut=entity.periode_debut,
            periode_fin=entity.periode_fin,
            montant_cumule_precedent_ht=entity.montant_cumule_precedent_ht,
            montant_periode_ht=entity.montant_periode_ht,
            montant_cumule_ht=entity.montant_cumule_ht,
            retenue_garantie_pct=entity.retenue_garantie_pct,
            taux_tva=entity.taux_tva,
            statut=entity.statut,
            notes=entity.notes,
            created_by=entity.created_by,
            validated_by=entity.validated_by,
            validated_at=entity.validated_at,
            emise_at=entity.emise_at,
            facturee_at=entity.facturee_at,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
        )

    def save(self, situation: SituationTravaux) -> SituationTravaux:
        """Persiste une situation (creation ou mise a jour).

        Args:
            situation: La situation a persister.

        Returns:
            La situation avec son ID attribue.
        """
        if situation.id:
            # Mise a jour
            model = (
                self._session.query(SituationTravauxModel)
                .filter(SituationTravauxModel.id == situation.id)
                .first()
            )
            if model:
                model.periode_debut = situation.periode_debut
                model.periode_fin = situation.periode_fin
                model.montant_cumule_precedent_ht = situation.montant_cumule_precedent_ht
                model.montant_periode_ht = situation.montant_periode_ht
                model.montant_cumule_ht = situation.montant_cumule_ht
                model.retenue_garantie_pct = situation.retenue_garantie_pct
                model.taux_tva = situation.taux_tva
                model.statut = situation.statut
                model.notes = situation.notes
                model.validated_by = situation.validated_by
                model.validated_at = situation.validated_at
                model.emise_at = situation.emise_at
                model.facturee_at = situation.facturee_at
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(situation)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, situation_id: int) -> Optional[SituationTravaux]:
        """Recherche une situation par son ID (exclut les supprimes).

        Args:
            situation_id: L'ID de la situation.

        Returns:
            La situation ou None si non trouvee.
        """
        model = (
            self._session.query(SituationTravauxModel)
            .filter(SituationTravauxModel.id == situation_id)
            .filter(SituationTravauxModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_chantier_id(
        self, chantier_id: int, include_deleted: bool = False
    ) -> List[SituationTravaux]:
        """Liste les situations d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            include_deleted: Inclure les situations supprimees.

        Returns:
            Liste des situations du chantier.
        """
        query = self._session.query(SituationTravauxModel).filter(
            SituationTravauxModel.chantier_id == chantier_id
        )
        if not include_deleted:
            query = query.filter(SituationTravauxModel.deleted_at.is_(None))
        query = query.order_by(SituationTravauxModel.created_at)

        return [self._to_entity(model) for model in query.all()]

    def count_by_chantier_id(self, chantier_id: int) -> int:
        """Compte le nombre de situations pour un chantier (non supprimees).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le nombre de situations.
        """
        return (
            self._session.query(SituationTravauxModel)
            .filter(SituationTravauxModel.chantier_id == chantier_id)
            .filter(SituationTravauxModel.deleted_at.is_(None))
            .count()
        )

    def delete(self, situation_id: int, deleted_by: int) -> None:
        """Supprime une situation (soft delete - H10).

        Args:
            situation_id: L'ID de la situation a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.
        """
        model = (
            self._session.query(SituationTravauxModel)
            .filter(SituationTravauxModel.id == situation_id)
            .filter(SituationTravauxModel.deleted_at.is_(None))
            .first()
        )
        if model:
            model.deleted_at = datetime.utcnow()
            model.deleted_by = deleted_by
            self._session.flush()

    def find_derniere_situation(
        self, chantier_id: int
    ) -> Optional[SituationTravaux]:
        """Recherche la derniere situation d'un chantier (non supprimee).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            La derniere situation ou None si aucune.
        """
        model = (
            self._session.query(SituationTravauxModel)
            .filter(SituationTravauxModel.chantier_id == chantier_id)
            .filter(SituationTravauxModel.deleted_at.is_(None))
            .order_by(SituationTravauxModel.created_at.desc())
            .first()
        )
        return self._to_entity(model) if model else None


class SQLAlchemyLigneSituationRepository(LigneSituationRepository):
    """Implementation SQLAlchemy du repository LigneSituation."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: LigneSituationModel) -> LigneSituation:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite LigneSituation correspondante.
        """
        return LigneSituation(
            id=model.id,
            situation_id=model.situation_id,
            lot_budgetaire_id=model.lot_budgetaire_id,
            pourcentage_avancement=Decimal(str(model.pourcentage_avancement)),
            montant_marche_ht=Decimal(str(model.montant_marche_ht)),
            montant_cumule_precedent_ht=Decimal(str(model.montant_cumule_precedent_ht)),
            montant_periode_ht=Decimal(str(model.montant_periode_ht)),
            montant_cumule_ht=Decimal(str(model.montant_cumule_ht)),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: LigneSituation) -> LigneSituationModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite LigneSituation source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return LigneSituationModel(
            id=entity.id,
            situation_id=entity.situation_id,
            lot_budgetaire_id=entity.lot_budgetaire_id,
            pourcentage_avancement=entity.pourcentage_avancement,
            montant_marche_ht=entity.montant_marche_ht,
            montant_cumule_precedent_ht=entity.montant_cumule_precedent_ht,
            montant_periode_ht=entity.montant_periode_ht,
            montant_cumule_ht=entity.montant_cumule_ht,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
        )

    def save(self, ligne: LigneSituation) -> LigneSituation:
        """Persiste une ligne de situation (creation ou mise a jour).

        Args:
            ligne: La ligne a persister.

        Returns:
            La ligne avec son ID attribue.
        """
        if ligne.id:
            # Mise a jour
            model = (
                self._session.query(LigneSituationModel)
                .filter(LigneSituationModel.id == ligne.id)
                .first()
            )
            if model:
                model.pourcentage_avancement = ligne.pourcentage_avancement
                model.montant_marche_ht = ligne.montant_marche_ht
                model.montant_cumule_precedent_ht = ligne.montant_cumule_precedent_ht
                model.montant_periode_ht = ligne.montant_periode_ht
                model.montant_cumule_ht = ligne.montant_cumule_ht
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(ligne)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def save_all(self, lignes: List[LigneSituation]) -> List[LigneSituation]:
        """Persiste plusieurs lignes de situation.

        Args:
            lignes: Les lignes a persister.

        Returns:
            Les lignes avec leurs IDs attribues.
        """
        result = []
        for ligne in lignes:
            result.append(self.save(ligne))
        return result

    def find_by_situation_id(
        self, situation_id: int
    ) -> List[LigneSituation]:
        """Liste les lignes d'une situation.

        Args:
            situation_id: L'ID de la situation.

        Returns:
            Liste des lignes de la situation.
        """
        models = (
            self._session.query(LigneSituationModel)
            .filter(LigneSituationModel.situation_id == situation_id)
            .order_by(LigneSituationModel.id)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def delete_by_situation_id(self, situation_id: int) -> None:
        """Supprime toutes les lignes d'une situation.

        Args:
            situation_id: L'ID de la situation.
        """
        self._session.query(LigneSituationModel).filter(
            LigneSituationModel.situation_id == situation_id
        ).delete()
        self._session.flush()
