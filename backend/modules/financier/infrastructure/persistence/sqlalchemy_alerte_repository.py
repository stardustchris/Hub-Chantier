"""Implementation SQLAlchemy du repository AlerteDepassement.

FIN-12: Alertes depassements - CRUD et acquittement.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.alerte_depassement import AlerteDepassement
from ...domain.repositories.alerte_repository import AlerteRepository
from .models import AlerteDepassementModel


class SQLAlchemyAlerteRepository(AlerteRepository):
    """Implementation SQLAlchemy du repository AlerteDepassement."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: AlerteDepassementModel) -> AlerteDepassement:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite AlerteDepassement correspondante.
        """
        return AlerteDepassement(
            id=model.id,
            chantier_id=model.chantier_id,
            budget_id=model.budget_id,
            type_alerte=model.type_alerte,
            message=model.message,
            pourcentage_atteint=Decimal(str(model.pourcentage_atteint)),
            seuil_configure=Decimal(str(model.seuil_configure)),
            montant_budget_ht=Decimal(str(model.montant_budget_ht)),
            montant_atteint_ht=Decimal(str(model.montant_atteint_ht)),
            est_acquittee=model.est_acquittee,
            acquittee_par=model.acquittee_par,
            acquittee_at=model.acquittee_at,
            created_at=model.created_at,
        )

    def _to_model(self, entity: AlerteDepassement) -> AlerteDepassementModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite AlerteDepassement source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return AlerteDepassementModel(
            id=entity.id,
            chantier_id=entity.chantier_id,
            budget_id=entity.budget_id,
            type_alerte=entity.type_alerte,
            message=entity.message,
            pourcentage_atteint=entity.pourcentage_atteint,
            seuil_configure=entity.seuil_configure,
            montant_budget_ht=entity.montant_budget_ht,
            montant_atteint_ht=entity.montant_atteint_ht,
            est_acquittee=entity.est_acquittee,
            acquittee_par=entity.acquittee_par,
            acquittee_at=entity.acquittee_at,
            created_at=entity.created_at or datetime.utcnow(),
        )

    def save(self, alerte: AlerteDepassement) -> AlerteDepassement:
        """Persiste une alerte (creation ou mise a jour).

        Args:
            alerte: L'alerte a persister.

        Returns:
            L'alerte avec son ID attribue.
        """
        if alerte.id:
            # Mise a jour
            model = (
                self._session.query(AlerteDepassementModel)
                .filter(AlerteDepassementModel.id == alerte.id)
                .first()
            )
            if model:
                model.est_acquittee = alerte.est_acquittee
                model.acquittee_par = alerte.acquittee_par
                model.acquittee_at = alerte.acquittee_at
        else:
            # Creation
            model = self._to_model(alerte)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, alerte_id: int) -> Optional[AlerteDepassement]:
        """Recherche une alerte par son ID.

        Args:
            alerte_id: L'ID de l'alerte.

        Returns:
            L'alerte ou None si non trouvee.
        """
        model = (
            self._session.query(AlerteDepassementModel)
            .filter(AlerteDepassementModel.id == alerte_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_chantier_id(
        self, chantier_id: int
    ) -> List[AlerteDepassement]:
        """Liste les alertes d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des alertes du chantier.
        """
        query = (
            self._session.query(AlerteDepassementModel)
            .filter(AlerteDepassementModel.chantier_id == chantier_id)
            .order_by(AlerteDepassementModel.created_at.desc())
        )
        return [self._to_entity(model) for model in query.all()]

    def find_non_acquittees(
        self, chantier_id: int
    ) -> List[AlerteDepassement]:
        """Liste les alertes non acquittees d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des alertes non acquittees.
        """
        query = (
            self._session.query(AlerteDepassementModel)
            .filter(AlerteDepassementModel.chantier_id == chantier_id)
            .filter(AlerteDepassementModel.est_acquittee.is_(False))
            .order_by(AlerteDepassementModel.created_at.desc())
        )
        return [self._to_entity(model) for model in query.all()]

    def acquitter(self, alerte_id: int, user_id: int) -> None:
        """Acquitte une alerte.

        Args:
            alerte_id: L'ID de l'alerte a acquitter.
            user_id: L'ID de l'utilisateur qui acquitte.
        """
        model = (
            self._session.query(AlerteDepassementModel)
            .filter(AlerteDepassementModel.id == alerte_id)
            .first()
        )
        if model:
            model.est_acquittee = True
            model.acquittee_par = user_id
            model.acquittee_at = datetime.utcnow()
            self._session.flush()
