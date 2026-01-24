"""Implementation SQLAlchemy du BesoinChargeRepository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ...domain.entities import BesoinCharge
from ...domain.repositories import BesoinChargeRepository
from ...domain.value_objects import Semaine, TypeMetier
from .models import BesoinChargeModel


class SQLAlchemyBesoinChargeRepository(BesoinChargeRepository):
    """
    Implementation SQLAlchemy du repository des besoins de charge.

    Gere la persistence des besoins en base de donnees.
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
            model = self.session.query(BesoinChargeModel).filter_by(id=besoin.id).first()
            if model:
                model.besoin_heures = besoin.besoin_heures
                model.note = besoin.note
                model.type_metier = besoin.type_metier.value
                model.updated_at = besoin.updated_at

        return besoin

    def find_by_id(self, id: int) -> Optional[BesoinCharge]:
        """Trouve un besoin par son ID."""
        model = self.session.query(BesoinChargeModel).filter_by(id=id).first()
        return self._to_entity(model) if model else None

    def find_by_chantier(
        self,
        chantier_id: int,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[BesoinCharge]:
        """Trouve les besoins d'un chantier sur une plage de semaines."""
        query = self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.chantier_id == chantier_id
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
        ).first()

        return self._to_entity(model) if model else None

    def find_all_in_range(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[BesoinCharge]:
        """Trouve tous les besoins sur une plage de semaines."""
        query = self.session.query(BesoinChargeModel)
        query = self._filter_by_semaine_range(query, semaine_debut, semaine_fin)

        models = query.order_by(
            BesoinChargeModel.chantier_id,
            BesoinChargeModel.semaine_annee,
            BesoinChargeModel.semaine_numero,
        ).all()

        return [self._to_entity(m) for m in models]

    def delete(self, id: int) -> bool:
        """Supprime un besoin."""
        result = self.session.query(BesoinChargeModel).filter_by(id=id).delete()
        return result > 0

    def delete_by_chantier(self, chantier_id: int) -> int:
        """Supprime tous les besoins d'un chantier."""
        return self.session.query(BesoinChargeModel).filter(
            BesoinChargeModel.chantier_id == chantier_id
        ).delete()

    def sum_besoins_by_semaine(self, semaine: Semaine) -> float:
        """Calcule la somme des besoins pour une semaine."""
        result = self.session.query(
            func.sum(BesoinChargeModel.besoin_heures)
        ).filter(
            BesoinChargeModel.semaine_annee == semaine.annee,
            BesoinChargeModel.semaine_numero == semaine.numero,
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
        ).scalar()

        return result or 0.0

    def get_chantiers_with_besoins(
        self,
        semaine_debut: Semaine,
        semaine_fin: Semaine,
    ) -> List[int]:
        """Retourne les IDs des chantiers ayant des besoins."""
        query = self.session.query(BesoinChargeModel.chantier_id).distinct()
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
