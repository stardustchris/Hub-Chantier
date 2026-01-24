"""Implementation SQLAlchemy du AffectationRepository."""

from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, not_

from ...domain.entities import Affectation
from ...domain.repositories import AffectationRepository
from ...domain.value_objects import HeureAffectation, TypeAffectation, JourSemaine
from .affectation_model import AffectationModel


class SQLAlchemyAffectationRepository(AffectationRepository):
    """
    Implementation du AffectationRepository utilisant SQLAlchemy.

    Fait le mapping entre l'entite Affectation (Domain) et AffectationModel (Infrastructure).

    Attributes:
        session: Session SQLAlchemy pour les operations DB.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy active.
        """
        self.session = session

    def save(self, affectation: Affectation) -> Affectation:
        """
        Persiste une affectation (creation ou mise a jour).

        Args:
            affectation: L'entite Affectation a sauvegarder.

        Returns:
            L'entite Affectation avec ID (si creation).
        """
        if affectation.id:
            # Update
            model = (
                self.session.query(AffectationModel)
                .filter(AffectationModel.id == affectation.id)
                .first()
            )
            if model:
                model.utilisateur_id = affectation.utilisateur_id
                model.chantier_id = affectation.chantier_id
                model.date = affectation.date
                model.heure_debut = (
                    str(affectation.heure_debut) if affectation.heure_debut else None
                )
                model.heure_fin = (
                    str(affectation.heure_fin) if affectation.heure_fin else None
                )
                model.note = affectation.note
                model.type_affectation = affectation.type_affectation.value
                model.jours_recurrence = (
                    [j.value for j in affectation.jours_recurrence]
                    if affectation.jours_recurrence
                    else None
                )
                model.updated_at = affectation.updated_at
        else:
            # Create
            model = self._to_model(affectation)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, id: int) -> Optional[Affectation]:
        """
        Trouve une affectation par son ID.

        Args:
            id: L'identifiant unique de l'affectation.

        Returns:
            L'affectation trouvee ou None.
        """
        model = (
            self.session.query(AffectationModel)
            .filter(AffectationModel.id == id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations d'un utilisateur sur une periode.

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste des affectations de l'utilisateur sur la periode.
        """
        models = (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.utilisateur_id == utilisateur_id,
                    AffectationModel.date >= date_debut,
                    AffectationModel.date <= date_fin,
                )
            )
            .order_by(AffectationModel.date, AffectationModel.heure_debut)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_chantier(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations pour un chantier sur une periode.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste des affectations pour ce chantier sur la periode.
        """
        models = (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.chantier_id == chantier_id,
                    AffectationModel.date >= date_debut,
                    AffectationModel.date <= date_fin,
                )
            )
            .order_by(AffectationModel.date, AffectationModel.utilisateur_id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_date_range(
        self,
        date_debut: date,
        date_fin: date,
    ) -> List[Affectation]:
        """
        Trouve toutes les affectations sur une periode.

        Args:
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste de toutes les affectations sur la periode.
        """
        models = (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.date >= date_debut,
                    AffectationModel.date <= date_fin,
                )
            )
            .order_by(
                AffectationModel.date,
                AffectationModel.utilisateur_id,
                AffectationModel.heure_debut,
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_utilisateur_and_date(
        self,
        utilisateur_id: int,
        date_affectation: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations d'un utilisateur pour une date specifique.

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_affectation: La date recherchee.

        Returns:
            Liste des affectations (peut etre multiple si multi-chantiers).
        """
        models = (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.utilisateur_id == utilisateur_id,
                    AffectationModel.date == date_affectation,
                )
            )
            .order_by(AffectationModel.heure_debut)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_chantier_and_date(
        self,
        chantier_id: int,
        date_affectation: date,
    ) -> List[Affectation]:
        """
        Trouve les affectations pour un chantier a une date specifique.

        Args:
            chantier_id: L'ID du chantier.
            date_affectation: La date recherchee.

        Returns:
            Liste des utilisateurs affectes ce jour-la.
        """
        models = (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.chantier_id == chantier_id,
                    AffectationModel.date == date_affectation,
                )
            )
            .order_by(AffectationModel.utilisateur_id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_non_planifies(
        self,
        date_debut: date,
        date_fin: date,
    ) -> List[int]:
        """
        Trouve les utilisateurs sans affectation sur une periode.

        ARCHITECTURE: Cette methode retourne une liste vide pour forcer
        le Use Case a utiliser le calcul via EntityInfoService.
        Cela evite l'import direct de UserModel (violation Clean Architecture).

        Le calcul reel est fait dans GetNonPlanifiesUseCase._calculate_non_planifies()
        qui utilise get_active_user_ids() du service shared.

        Args:
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Liste vide - le Use Case utilise le fallback via EntityInfoService.
        """
        # Retourne vide pour forcer le Use Case a utiliser EntityInfoService
        # via get_active_user_ids() injecte dans le constructeur.
        # Cela respecte Clean Architecture (pas d'import modules.auth).
        return []

    def find_utilisateurs_disponibles(
        self,
        date_cible: date,
    ) -> List[int]:
        """
        Trouve les utilisateurs disponibles pour une date donnee.

        Args:
            date_cible: La date pour laquelle chercher les disponibilites.

        Returns:
            Liste des IDs utilisateurs disponibles ce jour-la.
        """
        # Utilise find_non_planifies avec la meme date pour debut et fin
        return self.find_non_planifies(date_cible, date_cible)

    def delete(self, id: int) -> bool:
        """
        Supprime une affectation.

        Args:
            id: L'identifiant de l'affectation a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        model = (
            self.session.query(AffectationModel)
            .filter(AffectationModel.id == id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def delete_by_utilisateur_and_date_range(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Supprime les affectations d'un utilisateur sur une periode.

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations supprimees.
        """
        count = (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.utilisateur_id == utilisateur_id,
                    AffectationModel.date >= date_debut,
                    AffectationModel.date <= date_fin,
                )
            )
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return count

    def delete_by_chantier_and_date_range(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Supprime les affectations d'un chantier sur une periode.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations supprimees.
        """
        count = (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.chantier_id == chantier_id,
                    AffectationModel.date >= date_debut,
                    AffectationModel.date <= date_fin,
                )
            )
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return count

    def count_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Compte les affectations d'un utilisateur sur une periode.

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations.
        """
        return (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.utilisateur_id == utilisateur_id,
                    AffectationModel.date >= date_debut,
                    AffectationModel.date <= date_fin,
                )
            )
            .count()
        )

    def count_by_chantier(
        self,
        chantier_id: int,
        date_debut: date,
        date_fin: date,
    ) -> int:
        """
        Compte les affectations pour un chantier sur une periode.

        Args:
            chantier_id: L'ID du chantier.
            date_debut: Date de debut de la periode (incluse).
            date_fin: Date de fin de la periode (incluse).

        Returns:
            Nombre d'affectations.
        """
        return (
            self.session.query(AffectationModel)
            .filter(
                and_(
                    AffectationModel.chantier_id == chantier_id,
                    AffectationModel.date >= date_debut,
                    AffectationModel.date <= date_fin,
                )
            )
            .count()
        )

    def exists_for_utilisateur_and_date(
        self,
        utilisateur_id: int,
        date_affectation: date,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Verifie si un utilisateur a deja une affectation pour une date.

        Args:
            utilisateur_id: L'ID de l'utilisateur.
            date_affectation: La date a verifier.
            exclude_id: ID d'affectation a exclure (pour les mises a jour).

        Returns:
            True si une affectation existe deja.
        """
        query = self.session.query(AffectationModel).filter(
            and_(
                AffectationModel.utilisateur_id == utilisateur_id,
                AffectationModel.date == date_affectation,
            )
        )

        if exclude_id:
            query = query.filter(AffectationModel.id != exclude_id)

        return query.first() is not None

    def find_recurrentes_actives(
        self,
        utilisateur_id: Optional[int] = None,
        chantier_id: Optional[int] = None,
    ) -> List[Affectation]:
        """
        Trouve les affectations recurrentes actives.

        Args:
            utilisateur_id: Filtrer par utilisateur (optionnel).
            chantier_id: Filtrer par chantier (optionnel).

        Returns:
            Liste des affectations recurrentes.
        """
        query = self.session.query(AffectationModel).filter(
            AffectationModel.type_affectation == TypeAffectation.RECURRENTE.value
        )

        if utilisateur_id:
            query = query.filter(AffectationModel.utilisateur_id == utilisateur_id)

        if chantier_id:
            query = query.filter(AffectationModel.chantier_id == chantier_id)

        models = query.order_by(AffectationModel.date).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: AffectationModel) -> Affectation:
        """
        Convertit un modele SQLAlchemy en entite Domain.

        Args:
            model: Le modele SQLAlchemy.

        Returns:
            L'entite Affectation.
        """
        # Reconstruire HeureAffectation depuis les strings
        heure_debut = None
        if model.heure_debut:
            heure_debut = HeureAffectation.from_string(model.heure_debut)

        heure_fin = None
        if model.heure_fin:
            heure_fin = HeureAffectation.from_string(model.heure_fin)

        # Reconstruire les jours de recurrence
        jours_recurrence = None
        if model.jours_recurrence:
            jours_recurrence = [
                JourSemaine.from_int(j) for j in model.jours_recurrence
            ]

        return Affectation(
            id=model.id,
            utilisateur_id=model.utilisateur_id,
            chantier_id=model.chantier_id,
            date=model.date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            note=model.note,
            type_affectation=TypeAffectation.from_string(model.type_affectation),
            jours_recurrence=jours_recurrence,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, affectation: Affectation) -> AffectationModel:
        """
        Convertit une entite Domain en modele SQLAlchemy.

        Args:
            affectation: L'entite Affectation.

        Returns:
            Le modele AffectationModel.
        """
        return AffectationModel(
            id=affectation.id,
            utilisateur_id=affectation.utilisateur_id,
            chantier_id=affectation.chantier_id,
            date=affectation.date,
            heure_debut=(
                str(affectation.heure_debut) if affectation.heure_debut else None
            ),
            heure_fin=(
                str(affectation.heure_fin) if affectation.heure_fin else None
            ),
            note=affectation.note,
            type_affectation=affectation.type_affectation.value,
            jours_recurrence=(
                [j.value for j in affectation.jours_recurrence]
                if affectation.jours_recurrence
                else None
            ),
            created_by=affectation.created_by,
            created_at=affectation.created_at,
            updated_at=affectation.updated_at,
        )
