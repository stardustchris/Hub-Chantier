"""Implementation SQLAlchemy du repository FactureClient.

FIN-08: Facturation client - CRUD et workflow.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from ...domain.entities.facture_client import FactureClient
from ...domain.repositories.facture_repository import FactureRepository
from .models import FactureClientModel


class SQLAlchemyFactureRepository(FactureRepository):
    """Implementation SQLAlchemy du repository FactureClient."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: FactureClientModel) -> FactureClient:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite FactureClient correspondante.
        """
        return FactureClient(
            id=model.id,
            chantier_id=model.chantier_id,
            situation_id=model.situation_id,
            numero_facture=model.numero_facture,
            type_facture=model.type_facture,
            montant_ht=Decimal(str(model.montant_ht)),
            taux_tva=Decimal(str(model.taux_tva)),
            montant_tva=Decimal(str(model.montant_tva)),
            montant_ttc=Decimal(str(model.montant_ttc)),
            retenue_garantie_montant=Decimal(str(model.retenue_garantie_montant)),
            montant_net=Decimal(str(model.montant_net)),
            date_emission=model.date_emission,
            date_echeance=model.date_echeance,
            statut=model.statut,
            notes=model.notes,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _to_model(self, entity: FactureClient) -> FactureClientModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite FactureClient source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return FactureClientModel(
            id=entity.id,
            chantier_id=entity.chantier_id,
            situation_id=entity.situation_id,
            numero_facture=entity.numero_facture,
            type_facture=entity.type_facture,
            montant_ht=entity.montant_ht,
            taux_tva=entity.taux_tva,
            montant_tva=entity.montant_tva,
            montant_ttc=entity.montant_ttc,
            retenue_garantie_montant=entity.retenue_garantie_montant,
            montant_net=entity.montant_net,
            date_emission=entity.date_emission,
            date_echeance=entity.date_echeance,
            statut=entity.statut,
            notes=entity.notes,
            created_by=entity.created_by,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
        )

    def save(self, facture: FactureClient) -> FactureClient:
        """Persiste une facture (creation ou mise a jour).

        Args:
            facture: La facture a persister.

        Returns:
            La facture avec son ID attribue.
        """
        if facture.id:
            # Mise a jour
            model = (
                self._session.query(FactureClientModel)
                .filter(FactureClientModel.id == facture.id)
                .first()
            )
            if model:
                model.montant_ht = facture.montant_ht
                model.taux_tva = facture.taux_tva
                model.montant_tva = facture.montant_tva
                model.montant_ttc = facture.montant_ttc
                model.retenue_garantie_montant = facture.retenue_garantie_montant
                model.montant_net = facture.montant_net
                model.date_emission = facture.date_emission
                model.date_echeance = facture.date_echeance
                model.statut = facture.statut
                model.notes = facture.notes
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(facture)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, facture_id: int) -> Optional[FactureClient]:
        """Recherche une facture par son ID (exclut les supprimees).

        Args:
            facture_id: L'ID de la facture.

        Returns:
            La facture ou None si non trouvee.
        """
        model = (
            self._session.query(FactureClientModel)
            .filter(FactureClientModel.id == facture_id)
            .filter(FactureClientModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_chantier_id(
        self, chantier_id: int, include_deleted: bool = False
    ) -> List[FactureClient]:
        """Liste les factures d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            include_deleted: Inclure les factures supprimees.

        Returns:
            Liste des factures du chantier.
        """
        query = self._session.query(FactureClientModel).filter(
            FactureClientModel.chantier_id == chantier_id
        )
        if not include_deleted:
            query = query.filter(FactureClientModel.deleted_at.is_(None))
        query = query.order_by(FactureClientModel.created_at)

        return [self._to_entity(model) for model in query.all()]

    def find_by_situation_id(
        self, situation_id: int
    ) -> Optional[FactureClient]:
        """Recherche une facture par son ID de situation.

        Args:
            situation_id: L'ID de la situation.

        Returns:
            La facture ou None si non trouvee.
        """
        model = (
            self._session.query(FactureClientModel)
            .filter(FactureClientModel.situation_id == situation_id)
            .filter(FactureClientModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def count_factures_year(self, year: int) -> int:
        """Compte le nombre de factures pour une annee (non supprimees).

        Args:
            year: L'annee.

        Returns:
            Le nombre de factures.
        """
        return (
            self._session.query(FactureClientModel)
            .filter(
                extract("year", FactureClientModel.created_at) == year
            )
            .filter(FactureClientModel.deleted_at.is_(None))
            .count()
        )

    def next_numero_facture(self, year: int) -> int:
        """Prochain numero facture atomique via count + 1.

        NOTE: Pour une atomicite parfaite en production haute concurrence,
        utiliser une table de compteurs avec SELECT FOR UPDATE.
        En l'etat, count_factures_year + 1 est conserve mais la methode
        est isolee pour faciliter la migration vers une sequence.
        """
        return self.count_factures_year(year) + 1

    def delete(self, facture_id: int, deleted_by: int) -> None:
        """Supprime une facture (soft delete - H10).

        Args:
            facture_id: L'ID de la facture a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.
        """
        model = (
            self._session.query(FactureClientModel)
            .filter(FactureClientModel.id == facture_id)
            .filter(FactureClientModel.deleted_at.is_(None))
            .first()
        )
        if model:
            model.deleted_at = datetime.utcnow()
            model.deleted_by = deleted_by
            self._session.flush()
