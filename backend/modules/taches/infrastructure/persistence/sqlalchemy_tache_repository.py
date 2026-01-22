"""Implementation SQLAlchemy du TacheRepository."""

from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from ...domain.entities import Tache
from ...domain.repositories import TacheRepository
from ...domain.value_objects import StatutTache
from .tache_model import TacheModel


class SQLAlchemyTacheRepository(TacheRepository):
    """
    Implementation SQLAlchemy du repository Tache.

    Gere la persistence des taches en base de donnees.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def find_by_id(self, tache_id: int) -> Optional[Tache]:
        """Trouve une tache par son ID."""
        model = self.session.query(TacheModel).filter(TacheModel.id == tache_id).first()
        return model.to_entity() if model else None

    def find_by_chantier(
        self,
        chantier_id: int,
        include_sous_taches: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tache]:
        """Trouve les taches racines d'un chantier (TAC-01)."""
        query = (
            self.session.query(TacheModel)
            .filter(TacheModel.chantier_id == chantier_id)
            .filter(TacheModel.parent_id.is_(None))  # Taches racines
            .order_by(TacheModel.ordre)
            .offset(skip)
            .limit(limit)
        )

        models = query.all()
        return [m.to_entity() for m in models]

    def find_children(self, parent_id: int) -> List[Tache]:
        """Trouve les sous-taches d'une tache (TAC-02)."""
        models = (
            self.session.query(TacheModel)
            .filter(TacheModel.parent_id == parent_id)
            .order_by(TacheModel.ordre)
            .all()
        )
        return [m.to_entity() for m in models]

    def save(self, tache: Tache) -> Tache:
        """Persiste une tache."""
        if tache.id:
            # Mise a jour
            model = self.session.query(TacheModel).filter(TacheModel.id == tache.id).first()
            if model:
                model.chantier_id = tache.chantier_id
                model.titre = tache.titre
                model.description = tache.description
                model.parent_id = tache.parent_id
                model.ordre = tache.ordre
                model.statut = tache.statut.value
                model.date_echeance = tache.date_echeance
                model.unite_mesure = tache.unite_mesure.value if tache.unite_mesure else None
                model.quantite_estimee = tache.quantite_estimee
                model.quantite_realisee = tache.quantite_realisee
                model.heures_estimees = tache.heures_estimees
                model.heures_realisees = tache.heures_realisees
                model.template_id = tache.template_id
                model.updated_at = tache.updated_at
        else:
            # Creation
            model = TacheModel.from_entity(tache)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, tache_id: int) -> bool:
        """Supprime une tache et ses sous-taches."""
        model = self.session.query(TacheModel).filter(TacheModel.id == tache_id).first()
        if not model:
            return False

        # Supprimer recursement les sous-taches
        self._delete_children(tache_id)

        self.session.delete(model)
        self.session.commit()
        return True

    def _delete_children(self, parent_id: int) -> None:
        """Supprime recursement les sous-taches."""
        children = (
            self.session.query(TacheModel)
            .filter(TacheModel.parent_id == parent_id)
            .all()
        )
        for child in children:
            self._delete_children(child.id)
            self.session.delete(child)

    def count_by_chantier(self, chantier_id: int) -> int:
        """Compte les taches d'un chantier."""
        return (
            self.session.query(func.count(TacheModel.id))
            .filter(TacheModel.chantier_id == chantier_id)
            .scalar()
        )

    def search(
        self,
        chantier_id: int,
        query: Optional[str] = None,
        statut: Optional[StatutTache] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Tache], int]:
        """Recherche des taches avec filtres (TAC-14)."""
        base_query = self.session.query(TacheModel).filter(
            TacheModel.chantier_id == chantier_id
        )

        if query:
            search_term = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    TacheModel.titre.ilike(search_term),
                    TacheModel.description.ilike(search_term),
                )
            )

        if statut:
            base_query = base_query.filter(TacheModel.statut == statut.value)

        # Compter le total
        total = base_query.count()

        # Appliquer pagination
        models = base_query.order_by(TacheModel.ordre).offset(skip).limit(limit).all()

        return [m.to_entity() for m in models], total

    def reorder(self, tache_id: int, nouvel_ordre: int) -> None:
        """Reordonne une tache (TAC-15)."""
        model = self.session.query(TacheModel).filter(TacheModel.id == tache_id).first()
        if model:
            model.ordre = nouvel_ordre
            self.session.commit()

    def find_by_template(self, template_id: int) -> List[Tache]:
        """Trouve les taches creees depuis un template."""
        models = (
            self.session.query(TacheModel)
            .filter(TacheModel.template_id == template_id)
            .all()
        )
        return [m.to_entity() for m in models]

    def get_stats_chantier(self, chantier_id: int) -> dict:
        """Obtient les statistiques des taches d'un chantier."""
        # Total
        total = (
            self.session.query(func.count(TacheModel.id))
            .filter(TacheModel.chantier_id == chantier_id)
            .scalar()
        )

        # Terminees
        terminees = (
            self.session.query(func.count(TacheModel.id))
            .filter(TacheModel.chantier_id == chantier_id)
            .filter(TacheModel.statut == StatutTache.TERMINE.value)
            .scalar()
        )

        # En cours (non terminees)
        en_cours = total - terminees

        # En retard
        today = date.today()
        en_retard = (
            self.session.query(func.count(TacheModel.id))
            .filter(TacheModel.chantier_id == chantier_id)
            .filter(TacheModel.statut == StatutTache.A_FAIRE.value)
            .filter(TacheModel.date_echeance < today)
            .scalar()
        )

        # Heures
        heures = (
            self.session.query(
                func.sum(TacheModel.heures_estimees),
                func.sum(TacheModel.heures_realisees),
            )
            .filter(TacheModel.chantier_id == chantier_id)
            .first()
        )

        return {
            "total": total or 0,
            "terminees": terminees or 0,
            "en_cours": en_cours or 0,
            "en_retard": en_retard or 0,
            "heures_estimees_total": heures[0] or 0 if heures else 0,
            "heures_realisees_total": heures[1] or 0 if heures else 0,
        }
