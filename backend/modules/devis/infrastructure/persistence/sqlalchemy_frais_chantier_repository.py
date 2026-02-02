"""Implementation SQLAlchemy du repository FraisChantier.

DEV-25: Frais de chantier - Compte prorata, frais generaux, installations.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.frais_chantier_devis import FraisChantierDevis
from ...domain.value_objects.type_frais_chantier import TypeFraisChantier
from ...domain.value_objects.mode_repartition import ModeRepartition
from ...domain.repositories.frais_chantier_repository import FraisChantierRepository
from .models import FraisChantierDevisModel


class SQLAlchemyFraisChantierRepository(FraisChantierRepository):
    """Implementation SQLAlchemy du repository FraisChantier."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: FraisChantierDevisModel) -> FraisChantierDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite FraisChantierDevis correspondante.
        """
        return FraisChantierDevis(
            id=model.id,
            devis_id=model.devis_id,
            type_frais=TypeFraisChantier(model.type_frais),
            libelle=model.libelle,
            montant_ht=Decimal(str(model.montant_ht)) if model.montant_ht is not None else Decimal("0"),
            mode_repartition=ModeRepartition(model.mode_repartition),
            taux_tva=Decimal(str(model.taux_tva)) if model.taux_tva is not None else Decimal("20"),
            ordre=model.ordre or 0,
            lot_devis_id=model.lot_devis_id,
            created_at=model.created_at or datetime.utcnow(),
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _update_model(
        self, model: FraisChantierDevisModel, frais: FraisChantierDevis
    ) -> None:
        """Met a jour les champs du modele depuis l'entite.

        Args:
            model: Le modele SQLAlchemy a mettre a jour.
            frais: L'entite FraisChantierDevis source.
        """
        model.type_frais = frais.type_frais.value
        model.libelle = frais.libelle
        model.montant_ht = frais.montant_ht
        model.mode_repartition = frais.mode_repartition.value
        model.taux_tva = frais.taux_tva
        model.ordre = frais.ordre
        model.lot_devis_id = frais.lot_devis_id
        model.updated_at = datetime.utcnow()
        model.deleted_at = frais.deleted_at
        model.deleted_by = frais.deleted_by

    def find_by_id(self, frais_id: int) -> Optional[FraisChantierDevis]:
        """Trouve un frais de chantier par son ID.

        Args:
            frais_id: L'ID du frais de chantier.

        Returns:
            Le frais de chantier ou None si non trouve.
        """
        model = (
            self._session.query(FraisChantierDevisModel)
            .filter(FraisChantierDevisModel.id == frais_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_devis(self, devis_id: int) -> List[FraisChantierDevis]:
        """Liste les frais de chantier d'un devis (non supprimes).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des frais de chantier, triee par ordre.
        """
        models = (
            self._session.query(FraisChantierDevisModel)
            .filter(
                FraisChantierDevisModel.devis_id == devis_id,
                FraisChantierDevisModel.deleted_at.is_(None),
            )
            .order_by(FraisChantierDevisModel.ordre)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, frais: FraisChantierDevis) -> FraisChantierDevis:
        """Persiste un frais de chantier (creation ou mise a jour).

        Args:
            frais: Le frais de chantier a persister.

        Returns:
            Le frais avec son ID attribue.
        """
        if frais.id:
            model = (
                self._session.query(FraisChantierDevisModel)
                .filter(FraisChantierDevisModel.id == frais.id)
                .first()
            )
            if model:
                self._update_model(model, frais)
        else:
            model = FraisChantierDevisModel(
                devis_id=frais.devis_id,
                type_frais=frais.type_frais.value,
                libelle=frais.libelle,
                montant_ht=frais.montant_ht,
                mode_repartition=frais.mode_repartition.value,
                taux_tva=frais.taux_tva,
                ordre=frais.ordre,
                lot_devis_id=frais.lot_devis_id,
                created_at=frais.created_at or datetime.utcnow(),
                created_by=frais.created_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def delete(self, frais_id: int, deleted_by: int) -> bool:
        """Supprime un frais de chantier (soft delete).

        Args:
            frais_id: L'ID du frais a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(FraisChantierDevisModel)
            .filter(FraisChantierDevisModel.id == frais_id)
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
