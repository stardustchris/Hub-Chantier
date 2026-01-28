"""Implementation SQLAlchemy du BesoinChargeRepository."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ...domain.entities import BesoinCharge
from ...domain.repositories import BesoinChargeRepository
from ...domain.value_objects import Semaine, TypeMetier
from .besoin_charge_model import BesoinChargeModel


class SQLAlchemyBesoinChargeRepository(BesoinChargeRepository):
    """
    Implementation SQLAlchemy du repository des besoins de charge.

    Gere la persistence des besoins en base de donnees.
    Utilise le soft delete pour conserver l'historique.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def save(self, besoin: BesoinCharge) -> BesoinCharge:
        """Persiste un besoin (creation ou mise a jour)."""
        if besoin.id is None:
            # Creation
            model = self._to_model(besoin)
            self.session.add(model)
            self.session.flush()
            besoin.id = model.id
        else:
            # Mise a jour
            model = self.session.query(BesoinChargeModel).filter(
                BesoinChargeModel.id == besoin.id,
                BesoinChargeModel.is_deleted == False,
            ).first()
            if model:
                model.besoin_heures = besoin.besoin_heures
                model.note = besoin.note
                model.type_metier = besoin.type_metier.value
                model.updated_at = besoin.updated_at

        return besoin

    def find_by_id(self, id: int) -> Optional[BesoinCharge]:
        """Trouve un besoin par son ID (non supprime)."""
        model = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.id == id,
            BesoinChargeModel.is_deleted == False,
        ).first()
        return self._to_entity(model) if model else None

    def find_by_id_including_deleted(self, id: int) -> Optional[BesoinCharge]:
        """Trouve un besoin par son ID, y compris supprime."""
        model = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.id == id,
        ).first()
        return self._to_entity(model) if model else None

    def find_by_chantier(
        self,
        chantier_id: int,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[BesoinCharge]:
        """Trouve les besoins d'un chantier sur une plage de semaines."""
        query = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.chantier_id == chantier_id,
            BesoinChargeModel.is_deleted == False,
        )

        # Filtrer par plage de semaines
        query = self._filter_by_semaine_range(query, semaine_debut, semaine_fin)

        models = query.order_by(
            BesoinChargeModel.semaine_annee,
            BesoinChargeModel.semaine_numero,
        ).all()

        return [self._to_entity(m) for m in models]

    def find_by_semaine(self, semaine: Semaine) -> List[BesoinCharge]:
        """Trouve tous les besoins pour une semaine."""
        models = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.semaine_annee == semaine.annee,
            BesoinChargeModel.semaine_numero == semaine.numero,
            BesoinChargeModel.is_deleted == False,
        ).all()

        return [self._to_entity(m) for m in models]

    def find_by_chantier_and_semaine(
        self,
        chantier_id: int,
        semaine: Semaine,
    ) -> List[BesoinCharge]:
        """Trouve les besoins d'un chantier pour une semaine."""
        models = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.chantier_id == chantier_id,
            BesoinChargeModel.semaine_annee == semaine.annee,
            BesoinChargeModel.semaine_numero == semaine.numero,
            BesoinChargeModel.is_deleted == False,
        ).all()

        return [self._to_entity(m) for m in models]

    def find_by_chantier_semaine_and_type(
        self,
        chantier_id: int,
        semaine: Semaine,
        type_metier: TypeMetier,
    ) -> Optional[BesoinCharge]:
        """Trouve un besoin specifique."""
        model = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.chantier_id == chantier_id,
            BesoinChargeModel.semaine_annee == semaine.annee,
            BesoinChargeModel.semaine_numero == semaine.numero,
            BesoinChargeModel.type_metier == type_metier.value,
            BesoinChargeModel.is_deleted == False,
        ).first()

        return self._to_entity(model) if model else None

    def find_all_in_range(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[BesoinCharge]:
        """Trouve tous les besoins sur une plage de semaines."""
        query = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.is_deleted == False,
        )
        query = self._filter_by_semaine_range(query, semaine_debut, semaine_fin)

        models = query.order_by(
            BesoinChargeModel.chantier_id,
            BesoinChargeModel.semaine_annee,
            BesoinChargeModel.semaine_numero,
        ).all()

        return [self._to_entity(m) for m in models]

    def delete(self, id: int, deleted_by: Optional[int] = None) -> bool:
        """
        Supprime un besoin (soft delete).

        Args:
            id: ID du besoin.
            deleted_by: ID de l'utilisateur effectuant la suppression.

        Returns:
            True si supprime, False si non trouve.
        """
        model = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.id == id,
            BesoinChargeModel.is_deleted == False,
        ).first()

        if not model:
            return False

        model.soft_delete(deleted_by or 0)
        return True

    def delete_by_chantier(self, chantier_id: int, deleted_by: Optional[int] = None) -> int:
        """
        Supprime tous les besoins d'un chantier (soft delete).

        Args:
            chantier_id: ID du chantier.
            deleted_by: ID de l'utilisateur.

        Returns:
            Nombre de besoins supprimes.
        """
        models = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.chantier_id == chantier_id,
            BesoinChargeModel.is_deleted == False,
        ).all()

        count = 0
        for model in models:
            model.soft_delete(deleted_by or 0)
            count += 1

        return count

    def restore(self, id: int) -> bool:
        """
        Restaure un besoin supprime.

        Args:
            id: ID du besoin.

        Returns:
            True si restaure, False si non trouve.
        """
        model = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.id == id,
            BesoinChargeModel.is_deleted == True,
        ).first()

        if not model:
            return False

        model.restore()
        return True

    def sum_besoins_by_semaine(self, semaine: Semaine) -> float:
        """Calcule la somme des besoins pour une semaine."""
        result = self.session.query(
            func.sum(BesoinChargeModel.besoin_heures)
        ).filter(
            BesoinChargeModel.semaine_annee == semaine.annee,
            BesoinChargeModel.semaine_numero == semaine.numero,
            BesoinChargeModel.is_deleted == False,
        ).scalar()

        return result or 0.0

    def sum_besoins_by_type_and_semaine(
        self,
        type_metier: TypeMetier,
        semaine: Semaine,
    ) -> float:
        """Calcule la somme des besoins par type pour une semaine."""
        result = self.session.query(
            func.sum(BesoinChargeModel.besoin_heures)
        ).filter(
            BesoinChargeModel.type_metier == type_metier.value,
            BesoinChargeModel.semaine_annee == semaine.annee,
            BesoinChargeModel.semaine_numero == semaine.numero,
            BesoinChargeModel.is_deleted == False,
        ).scalar()

        return result or 0.0

    def get_chantiers_with_besoins(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[int]:
        """Retourne les IDs des chantiers ayant des besoins."""
        query = self.session.query(BesoinChargeModel.chantier_id).filter(
            BesoinChargeModel.is_deleted == False,
        ).distinct()
        query = self._filter_by_semaine_range(query, semaine_debut, semaine_fin)

        results = query.all()
        return [r[0] for r in results]

    def exists(
        self,
        chantier_id: int,
        semaine: Semaine,
        type_metier: TypeMetier,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Verifie si un besoin existe deja."""
        query = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.chantier_id == chantier_id,
            BesoinChargeModel.semaine_annee == semaine.annee,
            BesoinChargeModel.semaine_numero == semaine.numero,
            BesoinChargeModel.type_metier == type_metier.value,
            BesoinChargeModel.is_deleted == False,
        )

        if exclude_id:
            query = query.filter(BesoinChargeModel.id != exclude_id)

        return query.first() is not None

    # --- Methodes privees ---

    def _to_model(self, entity: BesoinCharge) -> BesoinChargeModel:
        """Convertit une entite en modele."""
        return BesoinChargeModel(
            id=entity.id,
            chantier_id=entity.chantier_id,
            semaine_annee=entity.semaine.annee,
            semaine_numero=entity.semaine.numero,
            type_metier=entity.type_metier.value,
            besoin_heures=entity.besoin_heures,
            note=entity.note,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=False,
        )

    def _to_entity(self, model: BesoinChargeModel) -> BesoinCharge:
        """Convertit un modele en entite."""
        return BesoinCharge(
            id=model.id,
            chantier_id=model.chantier_id,
            semaine=Semaine(annee=model.semaine_annee, numero=model.semaine_numero),
            type_metier=TypeMetier.from_string(model.type_metier),
            besoin_heures=model.besoin_heures,
            note=model.note,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _filter_by_semaine_range(self, query, debut: Semaine, fin: Semaine):
        """Ajoute un filtre par plage de semaines."""
        # Gestion du cas ou la plage traverse une annee
        if debut.annee == fin.annee:
            return query.filter(
                BesoinChargeModel.semaine_annee == debut.annee,
                BesoinChargeModel.semaine_numero >= debut.numero,
                BesoinChargeModel.semaine_numero <= fin.numero,
            )
        else:
            # Cas multi-annees
            return query.filter(
                (
                    (BesoinChargeModel.semaine_annee == debut.annee) &
                    (BesoinChargeModel.semaine_numero >= debut.numero)
                ) |
                (
                    (BesoinChargeModel.semaine_annee > debut.annee) &
                    (BesoinChargeModel.semaine_annee < fin.annee)
                ) |
                (
                    (BesoinChargeModel.semaine_annee == fin.annee) &
                    (BesoinChargeModel.semaine_numero <= fin.numero)
                )
            )
