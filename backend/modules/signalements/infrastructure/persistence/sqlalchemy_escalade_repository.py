"""Implémentation SQLAlchemy du repository EscaladeHistorique (SIG-17)."""

import json
import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from .models import EscaladeHistoriqueModel
from ...domain.entities import EscaladeHistorique
from ...domain.repositories import EscaladeRepository

logger = logging.getLogger(__name__)


class SQLAlchemyEscaladeRepository(EscaladeRepository):
    """Implémentation SQLAlchemy du repository EscaladeHistorique."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, escalade: EscaladeHistorique) -> EscaladeHistorique:
        """Persiste une escalade."""
        model = EscaladeHistoriqueModel(
            signalement_id=escalade.signalement_id,
            niveau=escalade.niveau,
            pourcentage_temps=int(escalade.pourcentage_temps),
            destinataires_roles=json.dumps(escalade.destinataires_roles),
            message=escalade.message,
            created_at=escalade.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        escalade.id = model.id
        return escalade

    def find_by_signalement(
        self,
        signalement_id: int,
    ) -> List[EscaladeHistorique]:
        """Récupère l'historique des escalades d'un signalement."""
        models = (
            self._session.query(EscaladeHistoriqueModel)
            .filter(EscaladeHistoriqueModel.signalement_id == signalement_id)
            .order_by(EscaladeHistoriqueModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_last_by_signalement(
        self,
        signalement_id: int,
    ) -> Optional[EscaladeHistorique]:
        """Récupère la dernière escalade d'un signalement."""
        model = (
            self._session.query(EscaladeHistoriqueModel)
            .filter(EscaladeHistoriqueModel.signalement_id == signalement_id)
            .order_by(EscaladeHistoriqueModel.created_at.desc())
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def count_by_signalement(self, signalement_id: int) -> int:
        """Compte le nombre d'escalades d'un signalement."""
        return (
            self._session.query(EscaladeHistoriqueModel)
            .filter(EscaladeHistoriqueModel.signalement_id == signalement_id)
            .count()
        )

    @staticmethod
    def _to_entity(model: EscaladeHistoriqueModel) -> EscaladeHistorique:
        """Convertit un modèle en entité."""
        destinataires = []
        if model.destinataires_roles:
            try:
                destinataires = json.loads(model.destinataires_roles)
            except (json.JSONDecodeError, TypeError):
                destinataires = []

        return EscaladeHistorique(
            id=model.id,
            signalement_id=model.signalement_id,
            niveau=model.niveau,
            pourcentage_temps=float(model.pourcentage_temps),
            destinataires_roles=destinataires,
            message=model.message,
            created_at=model.created_at,
        )
