"""Implémentation SQLAlchemy du PointageRepository."""

from datetime import date, timedelta
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ...domain.value_objects import StatutPointage, Duree
from .models import PointageModel

# Imports pour enrichissement (JOIN sans FK - Clean Architecture)
from modules.auth.infrastructure.persistence.user_model import UserModel
from modules.chantiers.infrastructure.persistence.chantier_model import ChantierModel


class SQLAlchemyPointageRepository(PointageRepository):
    """Implémentation SQLAlchemy du repository des pointages."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def find_by_id(self, pointage_id: int) -> Optional[Pointage]:
        """Trouve un pointage par son ID."""
        result = self._query_with_joins().filter(
            PointageModel.id == pointage_id
        ).first()
        return self._to_entity_enriched(result) if result else None

    def save(self, pointage: Pointage) -> Pointage:
        """Persiste un pointage."""
        if pointage.id:
            # Mise à jour
            model = self.session.query(PointageModel).filter(
                PointageModel.id == pointage.id
            ).first()
            if model:
                self._update_model(model, pointage)
        else:
            # Création
            model = self._to_model(pointage)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, pointage_id: int) -> bool:
        """Supprime un pointage."""
        model = self.session.query(PointageModel).filter(
            PointageModel.id == pointage_id
        ).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def find_by_utilisateur_and_date(
        self, utilisateur_id: int, date_pointage: date
    ) -> List[Pointage]:
        """Trouve les pointages d'un utilisateur pour une date."""
        results = self._query_with_joins().filter(
            PointageModel.utilisateur_id == utilisateur_id,
            PointageModel.date_pointage == date_pointage,
        ).all()
        return [self._to_entity_enriched(r) for r in results]

    def find_by_utilisateur_and_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> List[Pointage]:
        """Trouve les pointages d'un utilisateur pour une semaine."""
        semaine_fin = semaine_debut + timedelta(days=6)
        results = self._query_with_joins().filter(
            PointageModel.utilisateur_id == utilisateur_id,
            PointageModel.date_pointage >= semaine_debut,
            PointageModel.date_pointage <= semaine_fin,
        ).order_by(PointageModel.date_pointage).all()
        return [self._to_entity_enriched(r) for r in results]

    def find_by_chantier_and_date(
        self, chantier_id: int, date_pointage: date
    ) -> List[Pointage]:
        """Trouve les pointages d'un chantier pour une date."""
        results = self._query_with_joins().filter(
            PointageModel.chantier_id == chantier_id,
            PointageModel.date_pointage == date_pointage,
        ).all()
        return [self._to_entity_enriched(r) for r in results]

    def find_by_chantier_and_semaine(
        self, chantier_id: int, semaine_debut: date
    ) -> List[Pointage]:
        """Trouve les pointages d'un chantier pour une semaine."""
        semaine_fin = semaine_debut + timedelta(days=6)
        results = self._query_with_joins().filter(
            PointageModel.chantier_id == chantier_id,
            PointageModel.date_pointage >= semaine_debut,
            PointageModel.date_pointage <= semaine_fin,
        ).order_by(PointageModel.date_pointage).all()
        return [self._to_entity_enriched(r) for r in results]

    def find_by_utilisateur_chantier_date(
        self, utilisateur_id: int, chantier_id: int, date_pointage: date
    ) -> Optional[Pointage]:
        """Trouve un pointage unique par utilisateur, chantier et date."""
        result = self._query_with_joins().filter(
            PointageModel.utilisateur_id == utilisateur_id,
            PointageModel.chantier_id == chantier_id,
            PointageModel.date_pointage == date_pointage,
        ).first()
        return self._to_entity_enriched(result) if result else None

    def find_by_affectation(self, affectation_id: int) -> Optional[Pointage]:
        """Trouve un pointage par son affectation source."""
        result = self._query_with_joins().filter(
            PointageModel.affectation_id == affectation_id
        ).first()
        return self._to_entity_enriched(result) if result else None

    def find_pending_validation(
        self,
        validateur_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Pointage], int]:
        """Trouve les pointages en attente de validation."""
        query = self._query_with_joins().filter(
            PointageModel.statut == StatutPointage.SOUMIS.value
        )

        # Count total (sur la sous-query pour optimiser)
        total = self.session.query(PointageModel).filter(
            PointageModel.statut == StatutPointage.SOUMIS.value
        ).count()

        results = query.offset(skip).limit(limit).all()
        return [self._to_entity_enriched(r) for r in results], total

    def search(
        self,
        utilisateur_id: Optional[int] = None,
        chantier_id: Optional[int] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statut: Optional[StatutPointage] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Pointage], int]:
        """Recherche des pointages avec filtres (ENRICHIS avec noms users/chantiers)."""
        query = self._query_with_joins()

        if utilisateur_id:
            query = query.filter(PointageModel.utilisateur_id == utilisateur_id)
        if chantier_id:
            query = query.filter(PointageModel.chantier_id == chantier_id)
        if date_debut:
            query = query.filter(PointageModel.date_pointage >= date_debut)
        if date_fin:
            query = query.filter(PointageModel.date_pointage <= date_fin)
        if statut:
            query = query.filter(PointageModel.statut == statut.value)

        # Count total (sur une query simple pour optimiser)
        count_query = self.session.query(PointageModel)
        if utilisateur_id:
            count_query = count_query.filter(PointageModel.utilisateur_id == utilisateur_id)
        if chantier_id:
            count_query = count_query.filter(PointageModel.chantier_id == chantier_id)
        if date_debut:
            count_query = count_query.filter(PointageModel.date_pointage >= date_debut)
        if date_fin:
            count_query = count_query.filter(PointageModel.date_pointage <= date_fin)
        if statut:
            count_query = count_query.filter(PointageModel.statut == statut.value)
        total = count_query.count()

        results = query.order_by(PointageModel.date_pointage.desc()).offset(skip).limit(limit).all()
        return [self._to_entity_enriched(r) for r in results], total

    def count_by_utilisateur_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> int:
        """Compte les pointages d'un utilisateur pour une semaine."""
        semaine_fin = semaine_debut + timedelta(days=6)
        return self.session.query(PointageModel).filter(
            PointageModel.utilisateur_id == utilisateur_id,
            PointageModel.date_pointage >= semaine_debut,
            PointageModel.date_pointage <= semaine_fin,
        ).count()

    def bulk_save(self, pointages: List[Pointage]) -> List[Pointage]:
        """Sauvegarde plusieurs pointages."""
        models = []
        for pointage in pointages:
            model = self._to_model(pointage)
            self.session.add(model)
            models.append(model)

        self.session.commit()

        for model in models:
            self.session.refresh(model)

        return [self._to_entity(m) for m in models]

    # ===== Helpers =====

    def _query_with_joins(self):
        """
        Crée une query avec JOINs sur users et chantiers pour enrichir les pointages.

        IMPORTANT: Respecte la Clean Architecture - pas de FK en base,
        mais JOIN en lecture pour enrichir les entités avec les noms.

        Returns:
            Query SQLAlchemy avec JOINs sur UserModel et ChantierModel.
        """
        return (
            self.session.query(
                PointageModel,
                UserModel.prenom,
                UserModel.nom,
                ChantierModel.nom.label('chantier_nom'),
                ChantierModel.couleur
            )
            .outerjoin(UserModel, PointageModel.utilisateur_id == UserModel.id)
            .outerjoin(ChantierModel, PointageModel.chantier_id == ChantierModel.id)
        )

    def _to_entity_enriched(self, result: tuple) -> Pointage:
        """
        Convertit un résultat de query avec JOINs en entité enrichie.

        Args:
            result: Tuple (PointageModel, user_prenom, user_nom, chantier_nom, chantier_couleur)

        Returns:
            Entité Pointage avec champs enrichis (utilisateur_nom, chantier_nom, chantier_couleur).
        """
        model, user_prenom, user_nom, chantier_nom, chantier_couleur = result

        # Construire le nom complet de l'utilisateur
        utilisateur_nom = None
        if user_prenom and user_nom:
            utilisateur_nom = f"{user_prenom} {user_nom}"

        # Créer l'entité
        entity = Pointage(
            id=model.id,
            utilisateur_id=model.utilisateur_id,
            chantier_id=model.chantier_id,
            date_pointage=model.date_pointage,
            heures_normales=Duree.from_minutes(model.heures_normales_minutes),
            heures_supplementaires=Duree.from_minutes(model.heures_supplementaires_minutes),
            statut=StatutPointage.from_string(model.statut),
            commentaire=model.commentaire,
            signature_utilisateur=model.signature_utilisateur,
            signature_date=model.signature_date,
            validateur_id=model.validateur_id,
            validation_date=model.validation_date,
            motif_rejet=model.motif_rejet,
            affectation_id=model.affectation_id,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

        # Enrichir avec les données chargées via JOIN
        entity.utilisateur_nom = utilisateur_nom
        entity.chantier_nom = chantier_nom
        entity.chantier_couleur = chantier_couleur

        return entity

    def _to_entity(self, model: PointageModel) -> Pointage:
        """Convertit un modèle en entité."""
        return Pointage(
            id=model.id,
            utilisateur_id=model.utilisateur_id,
            chantier_id=model.chantier_id,
            date_pointage=model.date_pointage,
            heures_normales=Duree.from_minutes(model.heures_normales_minutes),
            heures_supplementaires=Duree.from_minutes(model.heures_supplementaires_minutes),
            statut=StatutPointage.from_string(model.statut),
            commentaire=model.commentaire,
            signature_utilisateur=model.signature_utilisateur,
            signature_date=model.signature_date,
            validateur_id=model.validateur_id,
            validation_date=model.validation_date,
            motif_rejet=model.motif_rejet,
            affectation_id=model.affectation_id,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Pointage) -> PointageModel:
        """Convertit une entité en modèle."""
        return PointageModel(
            id=entity.id,
            utilisateur_id=entity.utilisateur_id,
            chantier_id=entity.chantier_id,
            date_pointage=entity.date_pointage,
            heures_normales_minutes=entity.heures_normales.total_minutes,
            heures_supplementaires_minutes=entity.heures_supplementaires.total_minutes,
            statut=entity.statut.value,
            commentaire=entity.commentaire,
            signature_utilisateur=entity.signature_utilisateur,
            signature_date=entity.signature_date,
            validateur_id=entity.validateur_id,
            validation_date=entity.validation_date,
            motif_rejet=entity.motif_rejet,
            affectation_id=entity.affectation_id,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model(self, model: PointageModel, entity: Pointage) -> None:
        """Met à jour un modèle depuis une entité."""
        model.heures_normales_minutes = entity.heures_normales.total_minutes
        model.heures_supplementaires_minutes = entity.heures_supplementaires.total_minutes
        model.statut = entity.statut.value
        model.commentaire = entity.commentaire
        model.signature_utilisateur = entity.signature_utilisateur
        model.signature_date = entity.signature_date
        model.validateur_id = entity.validateur_id
        model.validation_date = entity.validation_date
        model.motif_rejet = entity.motif_rejet
        model.updated_at = entity.updated_at
