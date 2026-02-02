"""Implementation SQLAlchemy du repository RelanceDevis.

DEV-24: Relances automatiques de devis.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.relance_devis import RelanceDevis
from ...domain.repositories.relance_devis_repository import RelanceDevisRepository
from .models import RelanceDevisModel


class SQLAlchemyRelanceDevisRepository(RelanceDevisRepository):
    """Implementation SQLAlchemy du repository RelanceDevis."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: RelanceDevisModel) -> RelanceDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite RelanceDevis correspondante.
        """
        return RelanceDevis(
            id=model.id,
            devis_id=model.devis_id,
            numero_relance=model.numero_relance,
            type_relance=model.type_relance,
            date_envoi=model.date_envoi,
            date_prevue=model.date_prevue,
            statut=model.statut,
            message_personnalise=model.message_personnalise,
            created_at=model.created_at or datetime.utcnow(),
        )

    def _to_model(self, relance: RelanceDevis) -> RelanceDevisModel:
        """Convertit une entite domain en modele SQLAlchemy (creation).

        Args:
            relance: L'entite source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return RelanceDevisModel(
            devis_id=relance.devis_id,
            numero_relance=relance.numero_relance,
            type_relance=relance.type_relance,
            date_envoi=relance.date_envoi,
            date_prevue=relance.date_prevue,
            statut=relance.statut,
            message_personnalise=relance.message_personnalise,
            created_at=relance.created_at or datetime.utcnow(),
        )

    def _update_model(
        self, model: RelanceDevisModel, relance: RelanceDevis
    ) -> None:
        """Met a jour les champs modifiables du modele depuis l'entite.

        Args:
            model: Le modele SQLAlchemy a mettre a jour.
            relance: L'entite RelanceDevis source.
        """
        model.statut = relance.statut
        model.date_envoi = relance.date_envoi
        model.message_personnalise = relance.message_personnalise

    def find_by_id(self, relance_id: int) -> Optional[RelanceDevis]:
        """Trouve une relance par son ID.

        Args:
            relance_id: L'ID de la relance.

        Returns:
            La relance ou None si non trouvee.
        """
        model = (
            self._session.query(RelanceDevisModel)
            .filter(RelanceDevisModel.id == relance_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_devis_id(self, devis_id: int) -> List[RelanceDevis]:
        """Trouve toutes les relances d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des relances triees par numero_relance.
        """
        models = (
            self._session.query(RelanceDevisModel)
            .filter(RelanceDevisModel.devis_id == devis_id)
            .order_by(RelanceDevisModel.numero_relance)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_planifiees_avant(self, date_limite: datetime) -> List[RelanceDevis]:
        """Trouve les relances planifiees dont la date prevue est arrivee.

        Args:
            date_limite: Date limite (incluse).

        Returns:
            Liste des relances planifiees a envoyer.
        """
        models = (
            self._session.query(RelanceDevisModel)
            .filter(
                RelanceDevisModel.statut == "planifiee",
                RelanceDevisModel.date_prevue <= date_limite,
            )
            .order_by(RelanceDevisModel.date_prevue)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_planifiees_by_devis_id(self, devis_id: int) -> List[RelanceDevis]:
        """Trouve les relances planifiees d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des relances en attente.
        """
        models = (
            self._session.query(RelanceDevisModel)
            .filter(
                RelanceDevisModel.devis_id == devis_id,
                RelanceDevisModel.statut == "planifiee",
            )
            .order_by(RelanceDevisModel.numero_relance)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, relance: RelanceDevis) -> RelanceDevis:
        """Persiste une relance (creation ou mise a jour).

        Args:
            relance: La relance a persister.

        Returns:
            La relance avec son ID attribue.
        """
        if relance.id:
            model = (
                self._session.query(RelanceDevisModel)
                .filter(RelanceDevisModel.id == relance.id)
                .first()
            )
            if model:
                self._update_model(model, relance)
        else:
            model = self._to_model(relance)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def save_batch(self, relances: List[RelanceDevis]) -> List[RelanceDevis]:
        """Persiste plusieurs relances en batch.

        Args:
            relances: Les relances a persister.

        Returns:
            Les relances avec leurs IDs attribues.
        """
        models = []
        for relance in relances:
            model = self._to_model(relance)
            self._session.add(model)
            models.append(model)

        self._session.flush()
        return [self._to_entity(m) for m in models]

    def delete(self, relance_id: int) -> bool:
        """Supprime une relance.

        Args:
            relance_id: L'ID de la relance a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        model = (
            self._session.query(RelanceDevisModel)
            .filter(RelanceDevisModel.id == relance_id)
            .first()
        )
        if not model:
            return False

        self._session.delete(model)
        self._session.flush()
        return True
