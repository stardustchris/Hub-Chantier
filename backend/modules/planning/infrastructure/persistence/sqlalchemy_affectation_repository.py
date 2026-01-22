"""Implémentation SQLAlchemy du AffectationRepository."""

from datetime import date, time
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.value_objects import CreneauHoraire, TypeRecurrence
from .affectation_model import AffectationModel


class SQLAlchemyAffectationRepository(AffectationRepository):
    """
    Implémentation SQLAlchemy du repository des affectations.

    Fournit l'accès aux données via SQLAlchemy ORM.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy pour les opérations DB.
        """
        self.session = session

    def _to_entity(self, model: AffectationModel) -> Affectation:
        """Convertit un modèle SQLAlchemy en entité domain."""
        creneau = None
        if model.heure_debut or model.heure_fin:
            creneau = CreneauHoraire(
                heure_debut=model.heure_debut,
                heure_fin=model.heure_fin,
            )

        jours = model.jours_recurrence if model.jours_recurrence else []

        return Affectation(
            id=model.id,
            utilisateur_id=model.utilisateur_id,
            chantier_id=model.chantier_id,
            date_affectation=model.date_affectation,
            creneau=creneau,
            note=model.note,
            recurrence=TypeRecurrence.from_string(model.recurrence),
            jours_recurrence=jours,
            date_fin_recurrence=model.date_fin_recurrence,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Affectation) -> AffectationModel:
        """Convertit une entité domain en modèle SQLAlchemy."""
        heure_debut = None
        heure_fin = None
        if entity.creneau:
            heure_debut = entity.creneau.heure_debut
            heure_fin = entity.creneau.heure_fin

        return AffectationModel(
            id=entity.id,
            utilisateur_id=entity.utilisateur_id,
            chantier_id=entity.chantier_id,
            date_affectation=entity.date_affectation,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            note=entity.note,
            recurrence=entity.recurrence.value,
            jours_recurrence=list(entity.jours_recurrence),
            date_fin_recurrence=entity.date_fin_recurrence,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def find_by_id(self, affectation_id: int) -> Optional[Affectation]:
        """Trouve une affectation par son ID."""
        model = self.session.query(AffectationModel).filter(
            AffectationModel.id == affectation_id
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def save(self, affectation: Affectation) -> Affectation:
        """Persiste une affectation (création ou mise à jour)."""
        if affectation.id:
            # Mise à jour
            model = self.session.query(AffectationModel).filter(
                AffectationModel.id == affectation.id
            ).first()

            if model:
                model.chantier_id = affectation.chantier_id
                model.date_affectation = affectation.date_affectation
                model.heure_debut = (
                    affectation.creneau.heure_debut if affectation.creneau else None
                )
                model.heure_fin = (
                    affectation.creneau.heure_fin if affectation.creneau else None
                )
                model.note = affectation.note
                model.recurrence = affectation.recurrence.value
                model.jours_recurrence = list(affectation.jours_recurrence)
                model.date_fin_recurrence = affectation.date_fin_recurrence
                model.updated_at = affectation.updated_at
        else:
            # Création
            model = self._to_model(affectation)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)

        return self._to_entity(model)

    def delete(self, affectation_id: int) -> bool:
        """Supprime une affectation."""
        model = self.session.query(AffectationModel).filter(
            AffectationModel.id == affectation_id
        ).first()

        if not model:
            return False

        self.session.delete(model)
        self.session.commit()
        return True

    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """Trouve les affectations d'un utilisateur sur une période."""
        models = self.session.query(AffectationModel).filter(
            and_(
                AffectationModel.utilisateur_id == utilisateur_id,
                AffectationModel.date_affectation >= date_debut,
                AffectationModel.date_affectation <= date_fin,
            )
        ).order_by(AffectationModel.date_affectation).all()

        return [self._to_entity(m) for m in models]

    def find_by_chantier(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """Trouve les affectations d'un chantier sur une période."""
        models = self.session.query(AffectationModel).filter(
            and_(
                AffectationModel.chantier_id == chantier_id,
                AffectationModel.date_affectation >= date_debut,
                AffectationModel.date_affectation <= date_fin,
            )
        ).order_by(AffectationModel.date_affectation).all()

        return [self._to_entity(m) for m in models]

    def find_by_date(self, date_affectation: date) -> List[Affectation]:
        """Trouve toutes les affectations pour une date donnée."""
        models = self.session.query(AffectationModel).filter(
            AffectationModel.date_affectation == date_affectation
        ).order_by(
            AffectationModel.utilisateur_id,
            AffectationModel.heure_debut,
        ).all()

        return [self._to_entity(m) for m in models]

    def find_by_periode(
        self,
        date_debut: date,
        date_fin: date,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Affectation], int]:
        """Trouve les affectations sur une période avec pagination."""
        query = self.session.query(AffectationModel).filter(
            and_(
                AffectationModel.date_affectation >= date_debut,
                AffectationModel.date_affectation <= date_fin,
            )
        )

        total = query.count()

        models = query.order_by(
            AffectationModel.date_affectation,
            AffectationModel.utilisateur_id,
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def find_utilisateurs_non_planifies(self, date_affectation: date) -> List[int]:
        """
        Trouve les IDs des utilisateurs non planifiés pour une date.

        Note: Cette méthode nécessite une jointure avec la table users.
        Pour l'instant, on retourne une liste vide.
        L'implémentation complète nécessiterait une dépendance vers le module auth.
        """
        # TODO: Implémenter avec jointure vers users
        # Pour l'instant, on récupère tous les utilisateurs affectés ce jour
        # et on laisse le frontend calculer la différence
        return []

    def count_by_utilisateur_and_date(
        self,
        utilisateur_id: int,
        date_affectation: date,
    ) -> int:
        """Compte les affectations d'un utilisateur pour une date."""
        return self.session.query(AffectationModel).filter(
            and_(
                AffectationModel.utilisateur_id == utilisateur_id,
                AffectationModel.date_affectation == date_affectation,
            )
        ).count()

    def exists_for_utilisateur_chantier_date(
        self,
        utilisateur_id: int,
        chantier_id: int,
        date_affectation: date,
    ) -> bool:
        """Vérifie si une affectation existe déjà pour cet utilisateur/chantier/date."""
        return self.session.query(AffectationModel).filter(
            and_(
                AffectationModel.utilisateur_id == utilisateur_id,
                AffectationModel.chantier_id == chantier_id,
                AffectationModel.date_affectation == date_affectation,
            )
        ).count() > 0

    def delete_by_utilisateur_and_periode(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """Supprime les affectations d'un utilisateur sur une période."""
        deleted = self.session.query(AffectationModel).filter(
            and_(
                AffectationModel.utilisateur_id == utilisateur_id,
                AffectationModel.date_affectation >= date_debut,
                AffectationModel.date_affectation <= date_fin,
            )
        ).delete()

        self.session.commit()
        return deleted
