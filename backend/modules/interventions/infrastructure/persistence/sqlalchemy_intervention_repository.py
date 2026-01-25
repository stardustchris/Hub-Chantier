"""Implementation SQLAlchemy du repository Intervention."""

from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from ...domain.entities import Intervention
from ...domain.repositories import InterventionRepository
from ...domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)
from .models import InterventionModel


class SQLAlchemyInterventionRepository(InterventionRepository):
    """Implementation SQLAlchemy du repository des interventions."""

    def __init__(self, session: Session):
        """Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def save(self, intervention: Intervention) -> Intervention:
        """Sauvegarde une intervention."""
        if intervention.id is None:
            # Creation
            if not intervention.code:
                intervention.code = self.generate_code()

            model = InterventionModel(
                code=intervention.code,
                type_intervention=intervention.type_intervention,
                statut=intervention.statut,
                priorite=intervention.priorite,
                client_nom=intervention.client_nom,
                client_adresse=intervention.client_adresse,
                client_telephone=intervention.client_telephone,
                client_email=intervention.client_email,
                description=intervention.description,
                travaux_realises=intervention.travaux_realises,
                anomalies=intervention.anomalies,
                date_souhaitee=intervention.date_souhaitee,
                date_planifiee=intervention.date_planifiee,
                heure_debut=intervention.heure_debut,
                heure_fin=intervention.heure_fin,
                heure_debut_reelle=intervention.heure_debut_reelle,
                heure_fin_reelle=intervention.heure_fin_reelle,
                chantier_origine_id=intervention.chantier_origine_id,
                rapport_genere=intervention.rapport_genere,
                rapport_url=intervention.rapport_url,
                created_by=intervention.created_by,
                created_at=intervention.created_at,
            )
            self._session.add(model)
            self._session.flush()
            intervention.id = model.id
            intervention.code = model.code
        else:
            # Mise a jour
            model = self._session.query(InterventionModel).filter(
                InterventionModel.id == intervention.id
            ).first()

            if model:
                model.type_intervention = intervention.type_intervention
                model.statut = intervention.statut
                model.priorite = intervention.priorite
                model.client_nom = intervention.client_nom
                model.client_adresse = intervention.client_adresse
                model.client_telephone = intervention.client_telephone
                model.client_email = intervention.client_email
                model.description = intervention.description
                model.travaux_realises = intervention.travaux_realises
                model.anomalies = intervention.anomalies
                model.date_souhaitee = intervention.date_souhaitee
                model.date_planifiee = intervention.date_planifiee
                model.heure_debut = intervention.heure_debut
                model.heure_fin = intervention.heure_fin
                model.heure_debut_reelle = intervention.heure_debut_reelle
                model.heure_fin_reelle = intervention.heure_fin_reelle
                model.chantier_origine_id = intervention.chantier_origine_id
                model.rapport_genere = intervention.rapport_genere
                model.rapport_url = intervention.rapport_url
                model.updated_at = datetime.utcnow()

                if intervention.deleted_at:
                    model.deleted_at = intervention.deleted_at
                    model.deleted_by = intervention.deleted_by

                self._session.flush()

        return intervention

    def get_by_id(self, intervention_id: int) -> Optional[Intervention]:
        """Recupere une intervention par son ID."""
        model = self._session.query(InterventionModel).filter(
            InterventionModel.id == intervention_id
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def get_by_code(self, code: str) -> Optional[Intervention]:
        """Recupere une intervention par son code."""
        model = self._session.query(InterventionModel).filter(
            InterventionModel.code == code
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def list_all(
        self,
        statut: Optional[StatutIntervention] = None,
        priorite: Optional[PrioriteIntervention] = None,
        type_intervention: Optional[TypeIntervention] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        chantier_origine_id: Optional[int] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Intervention]:
        """Liste les interventions avec filtres."""
        query = self._session.query(InterventionModel)

        if not include_deleted:
            query = query.filter(InterventionModel.deleted_at.is_(None))

        if statut:
            query = query.filter(InterventionModel.statut == statut)

        if priorite:
            query = query.filter(InterventionModel.priorite == priorite)

        if type_intervention:
            query = query.filter(InterventionModel.type_intervention == type_intervention)

        if date_debut:
            query = query.filter(InterventionModel.date_planifiee >= date_debut)

        if date_fin:
            query = query.filter(InterventionModel.date_planifiee <= date_fin)

        if chantier_origine_id:
            query = query.filter(
                InterventionModel.chantier_origine_id == chantier_origine_id
            )

        query = query.order_by(
            InterventionModel.priorite.desc(),
            InterventionModel.date_planifiee.asc(),
            InterventionModel.created_at.desc(),
        )
        query = query.limit(limit).offset(offset)

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def count(
        self,
        statut: Optional[StatutIntervention] = None,
        priorite: Optional[PrioriteIntervention] = None,
        type_intervention: Optional[TypeIntervention] = None,
        include_deleted: bool = False,
    ) -> int:
        """Compte les interventions."""
        query = self._session.query(func.count(InterventionModel.id))

        if not include_deleted:
            query = query.filter(InterventionModel.deleted_at.is_(None))

        if statut:
            query = query.filter(InterventionModel.statut == statut)

        if priorite:
            query = query.filter(InterventionModel.priorite == priorite)

        if type_intervention:
            query = query.filter(InterventionModel.type_intervention == type_intervention)

        return query.scalar() or 0

    def list_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        include_deleted: bool = False,
    ) -> List[Intervention]:
        """Liste les interventions d'un technicien."""
        from .models import AffectationInterventionModel

        # Sous-requete pour les IDs d'interventions du technicien
        subq = (
            self._session.query(AffectationInterventionModel.intervention_id)
            .filter(
                and_(
                    AffectationInterventionModel.utilisateur_id == utilisateur_id,
                    AffectationInterventionModel.deleted_at.is_(None),
                )
            )
            .subquery()
        )

        query = self._session.query(InterventionModel).filter(
            InterventionModel.id.in_(subq)
        )

        if not include_deleted:
            query = query.filter(InterventionModel.deleted_at.is_(None))

        if date_debut:
            query = query.filter(InterventionModel.date_planifiee >= date_debut)

        if date_fin:
            query = query.filter(InterventionModel.date_planifiee <= date_fin)

        query = query.order_by(InterventionModel.date_planifiee.asc())

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def list_by_date_range(
        self,
        date_debut: date,
        date_fin: date,
        include_deleted: bool = False,
    ) -> List[Intervention]:
        """Liste les interventions pour une periode."""
        query = self._session.query(InterventionModel).filter(
            and_(
                InterventionModel.date_planifiee >= date_debut,
                InterventionModel.date_planifiee <= date_fin,
            )
        )

        if not include_deleted:
            query = query.filter(InterventionModel.deleted_at.is_(None))

        query = query.order_by(
            InterventionModel.date_planifiee.asc(),
            InterventionModel.heure_debut.asc(),
        )

        models = query.all()

        return [self._model_to_entity(m) for m in models]

    def delete(self, intervention_id: int, deleted_by: int) -> bool:
        """Supprime une intervention (soft delete)."""
        model = self._session.query(InterventionModel).filter(
            and_(
                InterventionModel.id == intervention_id,
                InterventionModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()

        return True

    def generate_code(self) -> str:
        """Genere un nouveau code unique."""
        year = datetime.utcnow().year

        # Compte les interventions de l'annee
        count = self._session.query(func.count(InterventionModel.id)).filter(
            InterventionModel.code.like(f"INT-{year}-%")
        ).scalar() or 0

        return f"INT-{year}-{count + 1:04d}"

    def _model_to_entity(self, model: InterventionModel) -> Intervention:
        """Convertit un modele SQLAlchemy en entite de domaine."""
        return Intervention(
            id=model.id,
            code=model.code,
            type_intervention=model.type_intervention,
            statut=model.statut,
            priorite=model.priorite,
            client_nom=model.client_nom,
            client_adresse=model.client_adresse,
            client_telephone=model.client_telephone,
            client_email=model.client_email,
            description=model.description,
            travaux_realises=model.travaux_realises,
            anomalies=model.anomalies,
            date_souhaitee=model.date_souhaitee,
            date_planifiee=model.date_planifiee,
            heure_debut=model.heure_debut,
            heure_fin=model.heure_fin,
            heure_debut_reelle=model.heure_debut_reelle,
            heure_fin_reelle=model.heure_fin_reelle,
            chantier_origine_id=model.chantier_origine_id,
            rapport_genere=model.rapport_genere,
            rapport_url=model.rapport_url,
            created_by=model.created_by or 0,
            created_at=model.created_at,
            updated_at=model.updated_at or model.created_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )
