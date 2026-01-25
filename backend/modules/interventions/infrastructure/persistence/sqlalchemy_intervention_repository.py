"""Implementation SQLAlchemy du repository Intervention."""

from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

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

    def __init__(self, session: AsyncSession):
        """Initialise le repository.

        Args:
            session: Session SQLAlchemy async.
        """
        self._session = session

    async def save(self, intervention: Intervention) -> Intervention:
        """Sauvegarde une intervention."""
        if intervention.id is None:
            # Creation
            if not intervention.code:
                intervention.code = await self.generate_code()

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
            await self._session.flush()
            intervention.id = model.id
            intervention.code = model.code
        else:
            # Mise a jour
            stmt = select(InterventionModel).where(
                InterventionModel.id == intervention.id
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

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

                await self._session.flush()

        return intervention

    async def get_by_id(self, intervention_id: int) -> Optional[Intervention]:
        """Recupere une intervention par son ID."""
        stmt = select(InterventionModel).where(InterventionModel.id == intervention_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def get_by_code(self, code: str) -> Optional[Intervention]:
        """Recupere une intervention par son code."""
        stmt = select(InterventionModel).where(InterventionModel.code == code)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def list_all(
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
        stmt = select(InterventionModel)

        conditions = []

        if not include_deleted:
            conditions.append(InterventionModel.deleted_at.is_(None))

        if statut:
            conditions.append(InterventionModel.statut == statut)

        if priorite:
            conditions.append(InterventionModel.priorite == priorite)

        if type_intervention:
            conditions.append(InterventionModel.type_intervention == type_intervention)

        if date_debut:
            conditions.append(InterventionModel.date_planifiee >= date_debut)

        if date_fin:
            conditions.append(InterventionModel.date_planifiee <= date_fin)

        if chantier_origine_id:
            conditions.append(
                InterventionModel.chantier_origine_id == chantier_origine_id
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(
            InterventionModel.priorite.desc(),
            InterventionModel.date_planifiee.asc(),
            InterventionModel.created_at.desc(),
        )
        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def count(
        self,
        statut: Optional[StatutIntervention] = None,
        priorite: Optional[PrioriteIntervention] = None,
        type_intervention: Optional[TypeIntervention] = None,
        include_deleted: bool = False,
    ) -> int:
        """Compte les interventions."""
        stmt = select(func.count(InterventionModel.id))

        conditions = []

        if not include_deleted:
            conditions.append(InterventionModel.deleted_at.is_(None))

        if statut:
            conditions.append(InterventionModel.statut == statut)

        if priorite:
            conditions.append(InterventionModel.priorite == priorite)

        if type_intervention:
            conditions.append(InterventionModel.type_intervention == type_intervention)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def list_by_utilisateur(
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
            select(AffectationInterventionModel.intervention_id)
            .where(
                and_(
                    AffectationInterventionModel.utilisateur_id == utilisateur_id,
                    AffectationInterventionModel.deleted_at.is_(None),
                )
            )
            .scalar_subquery()
        )

        stmt = select(InterventionModel).where(InterventionModel.id.in_(subq))

        conditions = []

        if not include_deleted:
            conditions.append(InterventionModel.deleted_at.is_(None))

        if date_debut:
            conditions.append(InterventionModel.date_planifiee >= date_debut)

        if date_fin:
            conditions.append(InterventionModel.date_planifiee <= date_fin)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(InterventionModel.date_planifiee.asc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def list_by_date_range(
        self,
        date_debut: date,
        date_fin: date,
        include_deleted: bool = False,
    ) -> List[Intervention]:
        """Liste les interventions pour une periode."""
        stmt = select(InterventionModel).where(
            and_(
                InterventionModel.date_planifiee >= date_debut,
                InterventionModel.date_planifiee <= date_fin,
            )
        )

        if not include_deleted:
            stmt = stmt.where(InterventionModel.deleted_at.is_(None))

        stmt = stmt.order_by(
            InterventionModel.date_planifiee.asc(),
            InterventionModel.heure_debut.asc(),
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def delete(self, intervention_id: int, deleted_by: int) -> bool:
        """Supprime une intervention (soft delete)."""
        stmt = select(InterventionModel).where(
            and_(
                InterventionModel.id == intervention_id,
                InterventionModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        await self._session.flush()

        return True

    async def generate_code(self) -> str:
        """Genere un nouveau code unique."""
        year = datetime.utcnow().year

        # Compte les interventions de l'annee
        stmt = select(func.count(InterventionModel.id)).where(
            InterventionModel.code.like(f"INT-{year}-%")
        )
        result = await self._session.execute(stmt)
        count = result.scalar() or 0

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
