"""Implémentation SQLAlchemy du repository MacroPaie (FDH-18)."""

import json
import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from .models import MacroPaieModel
from ...domain.entities import MacroPaie
from ...domain.entities.macro_paie import TypeMacroPaie
from ...domain.repositories import MacroPaieRepository

logger = logging.getLogger(__name__)


class SQLAlchemyMacroPaieRepository(MacroPaieRepository):
    """Implémentation SQLAlchemy du repository MacroPaie."""

    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, macro_id: int) -> Optional[MacroPaie]:
        """Trouve une macro par son ID."""
        model = (
            self._session.query(MacroPaieModel)
            .filter(MacroPaieModel.id == macro_id)
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def save(self, macro: MacroPaie) -> MacroPaie:
        """Persiste une macro (création ou mise à jour)."""
        if macro.id is None:
            model = MacroPaieModel(
                nom=macro.nom,
                type_macro=macro.type_macro.value,
                description=macro.description,
                formule=macro.formule,
                parametres=json.dumps(macro.parametres) if macro.parametres else None,
                active=macro.active,
                created_by=macro.created_by,
                created_at=macro.created_at,
                updated_at=macro.updated_at,
            )
            self._session.add(model)
            self._session.commit()
            self._session.refresh(model)
            macro.id = model.id
        else:
            model = (
                self._session.query(MacroPaieModel)
                .filter(MacroPaieModel.id == macro.id)
                .first()
            )
            if model:
                model.nom = macro.nom
                model.type_macro = macro.type_macro.value
                model.description = macro.description
                model.formule = macro.formule
                model.parametres = (
                    json.dumps(macro.parametres) if macro.parametres else None
                )
                model.active = macro.active
                model.updated_at = macro.updated_at
                self._session.commit()

        return macro

    def delete(self, macro_id: int) -> bool:
        """Supprime une macro."""
        model = (
            self._session.query(MacroPaieModel)
            .filter(MacroPaieModel.id == macro_id)
            .first()
        )
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    def find_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[MacroPaie]:
        """Récupère toutes les macros."""
        query = self._session.query(MacroPaieModel)
        if active_only:
            query = query.filter(MacroPaieModel.active.is_(True))
        query = query.order_by(MacroPaieModel.nom)
        models = query.offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_by_type(
        self,
        type_macro: TypeMacroPaie,
        active_only: bool = True,
    ) -> List[MacroPaie]:
        """Récupère les macros d'un type donné."""
        query = self._session.query(MacroPaieModel).filter(
            MacroPaieModel.type_macro == type_macro.value
        )
        if active_only:
            query = query.filter(MacroPaieModel.active.is_(True))
        models = query.all()
        return [self._to_entity(m) for m in models]

    def count(self, active_only: bool = True) -> int:
        """Compte le nombre de macros."""
        query = self._session.query(MacroPaieModel)
        if active_only:
            query = query.filter(MacroPaieModel.active.is_(True))
        return query.count()

    @staticmethod
    def _to_entity(model: MacroPaieModel) -> MacroPaie:
        """Convertit un modèle en entité."""
        parametres = {}
        if model.parametres:
            try:
                parametres = json.loads(model.parametres)
            except (json.JSONDecodeError, TypeError):
                parametres = {}

        return MacroPaie(
            id=model.id,
            nom=model.nom,
            type_macro=TypeMacroPaie.from_string(model.type_macro),
            description=model.description,
            formule=model.formule,
            parametres=parametres,
            active=model.active,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
