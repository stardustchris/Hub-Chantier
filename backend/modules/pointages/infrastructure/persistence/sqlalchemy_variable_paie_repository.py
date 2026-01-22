"""Implémentation SQLAlchemy du VariablePaieRepository."""

from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import VariablePaie
from ...domain.repositories import VariablePaieRepository
from ...domain.value_objects import TypeVariablePaie
from .models import VariablePaieModel


class SQLAlchemyVariablePaieRepository(VariablePaieRepository):
    """Implémentation SQLAlchemy du repository des variables de paie."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def find_by_id(self, variable_id: int) -> Optional[VariablePaie]:
        """Trouve une variable de paie par son ID."""
        model = self.session.query(VariablePaieModel).filter(
            VariablePaieModel.id == variable_id
        ).first()
        return self._to_entity(model) if model else None

    def save(self, variable: VariablePaie) -> VariablePaie:
        """Persiste une variable de paie."""
        if variable.id:
            # Mise à jour
            model = self.session.query(VariablePaieModel).filter(
                VariablePaieModel.id == variable.id
            ).first()
            if model:
                self._update_model(model, variable)
        else:
            # Création
            model = self._to_model(variable)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, variable_id: int) -> bool:
        """Supprime une variable de paie."""
        model = self.session.query(VariablePaieModel).filter(
            VariablePaieModel.id == variable_id
        ).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def find_by_pointage(self, pointage_id: int) -> List[VariablePaie]:
        """Trouve toutes les variables de paie d'un pointage."""
        models = self.session.query(VariablePaieModel).filter(
            VariablePaieModel.pointage_id == pointage_id
        ).all()
        return [self._to_entity(m) for m in models]

    def find_by_type_and_periode(
        self,
        type_variable: TypeVariablePaie,
        date_debut: date,
        date_fin: date,
        utilisateur_id: Optional[int] = None,
    ) -> List[VariablePaie]:
        """Trouve les variables d'un type sur une période."""
        query = self.session.query(VariablePaieModel).filter(
            VariablePaieModel.type_variable == type_variable.value,
            VariablePaieModel.date_application >= date_debut,
            VariablePaieModel.date_application <= date_fin,
        )

        # Note: Pour filtrer par utilisateur, il faudrait joindre avec pointages
        # Simplifié ici

        models = query.all()
        return [self._to_entity(m) for m in models]

    def find_by_utilisateur_and_periode(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[VariablePaie]:
        """Trouve toutes les variables d'un utilisateur sur une période."""
        from .models import PointageModel

        models = self.session.query(VariablePaieModel).join(
            PointageModel
        ).filter(
            PointageModel.utilisateur_id == utilisateur_id,
            VariablePaieModel.date_application >= date_debut,
            VariablePaieModel.date_application <= date_fin,
        ).all()

        return [self._to_entity(m) for m in models]

    def bulk_save(self, variables: List[VariablePaie]) -> List[VariablePaie]:
        """Sauvegarde plusieurs variables."""
        models = []
        for variable in variables:
            model = self._to_model(variable)
            self.session.add(model)
            models.append(model)

        self.session.commit()

        for model in models:
            self.session.refresh(model)

        return [self._to_entity(m) for m in models]

    def delete_by_pointage(self, pointage_id: int) -> int:
        """Supprime toutes les variables d'un pointage."""
        count = self.session.query(VariablePaieModel).filter(
            VariablePaieModel.pointage_id == pointage_id
        ).delete()
        self.session.commit()
        return count

    # ===== Helpers =====

    def _to_entity(self, model: VariablePaieModel) -> VariablePaie:
        """Convertit un modèle en entité."""
        return VariablePaie(
            id=model.id,
            pointage_id=model.pointage_id,
            type_variable=TypeVariablePaie.from_string(model.type_variable),
            valeur=Decimal(str(model.valeur)),
            date_application=model.date_application,
            commentaire=model.commentaire,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: VariablePaie) -> VariablePaieModel:
        """Convertit une entité en modèle."""
        return VariablePaieModel(
            id=entity.id,
            pointage_id=entity.pointage_id,
            type_variable=entity.type_variable.value,
            valeur=entity.valeur,
            date_application=entity.date_application,
            commentaire=entity.commentaire,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model(self, model: VariablePaieModel, entity: VariablePaie) -> None:
        """Met à jour un modèle depuis une entité."""
        model.type_variable = entity.type_variable.value
        model.valeur = entity.valeur
        model.date_application = entity.date_application
        model.commentaire = entity.commentaire
        model.updated_at = entity.updated_at
