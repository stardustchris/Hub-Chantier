"""Implémentation SQLAlchemy du FeuilleHeuresRepository."""

from datetime import date, timedelta
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from ...domain.entities import FeuilleHeures
from ...domain.repositories import FeuilleHeuresRepository
from ...domain.value_objects import StatutPointage
from .models import FeuilleHeuresModel


class SQLAlchemyFeuilleHeuresRepository(FeuilleHeuresRepository):
    """Implémentation SQLAlchemy du repository des feuilles d'heures."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def find_by_id(self, feuille_id: int) -> Optional[FeuilleHeures]:
        """Trouve une feuille d'heures par son ID."""
        model = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.id == feuille_id
        ).first()
        return self._to_entity(model) if model else None

    def save(self, feuille: FeuilleHeures) -> FeuilleHeures:
        """Persiste une feuille d'heures."""
        if feuille.id:
            # Mise à jour
            model = self.session.query(FeuilleHeuresModel).filter(
                FeuilleHeuresModel.id == feuille.id
            ).first()
            if model:
                self._update_model(model, feuille)
        else:
            # Création
            model = self._to_model(feuille)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, feuille_id: int) -> bool:
        """Supprime une feuille d'heures."""
        model = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.id == feuille_id
        ).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def find_by_utilisateur_and_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> Optional[FeuilleHeures]:
        """Trouve la feuille d'un utilisateur pour une semaine donnée."""
        model = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.utilisateur_id == utilisateur_id,
            FeuilleHeuresModel.semaine_debut == semaine_debut,
        ).first()
        return self._to_entity(model) if model else None

    def find_by_utilisateur_and_week_number(
        self, utilisateur_id: int, annee: int, numero_semaine: int
    ) -> Optional[FeuilleHeures]:
        """Trouve la feuille d'un utilisateur par numéro de semaine."""
        model = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.utilisateur_id == utilisateur_id,
            FeuilleHeuresModel.annee == annee,
            FeuilleHeuresModel.numero_semaine == numero_semaine,
        ).first()
        return self._to_entity(model) if model else None

    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[FeuilleHeures], int]:
        """Trouve toutes les feuilles d'un utilisateur."""
        query = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.utilisateur_id == utilisateur_id
        )

        total = query.count()
        models = query.order_by(
            FeuilleHeuresModel.semaine_debut.desc()
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def find_by_semaine(
        self,
        semaine_debut: date,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[FeuilleHeures], int]:
        """Trouve toutes les feuilles pour une semaine donnée."""
        query = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.semaine_debut == semaine_debut
        )

        total = query.count()
        models = query.offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def find_by_statut(
        self,
        statut: StatutPointage,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[FeuilleHeures], int]:
        """Trouve les feuilles par statut global."""
        query = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.statut_global == statut.value
        )

        total = query.count()
        models = query.offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def search(
        self,
        utilisateur_id: Optional[int] = None,
        annee: Optional[int] = None,
        numero_semaine: Optional[int] = None,
        statut: Optional[StatutPointage] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[FeuilleHeures], int]:
        """Recherche des feuilles d'heures avec filtres."""
        query = self.session.query(FeuilleHeuresModel)

        if utilisateur_id:
            query = query.filter(FeuilleHeuresModel.utilisateur_id == utilisateur_id)
        if annee:
            query = query.filter(FeuilleHeuresModel.annee == annee)
        if numero_semaine:
            query = query.filter(FeuilleHeuresModel.numero_semaine == numero_semaine)
        if statut:
            query = query.filter(FeuilleHeuresModel.statut_global == statut.value)
        if date_debut:
            query = query.filter(FeuilleHeuresModel.semaine_debut >= date_debut)
        if date_fin:
            query = query.filter(FeuilleHeuresModel.semaine_debut <= date_fin)

        total = query.count()
        models = query.order_by(
            FeuilleHeuresModel.semaine_debut.desc()
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def get_or_create(
        self, utilisateur_id: int, semaine_debut: date
    ) -> Tuple[FeuilleHeures, bool]:
        """Récupère ou crée une feuille pour un utilisateur/semaine."""
        existing = self.find_by_utilisateur_and_semaine(utilisateur_id, semaine_debut)
        if existing:
            return existing, False

        # Crée une nouvelle feuille
        feuille = FeuilleHeures.for_week(utilisateur_id, semaine_debut)
        saved = self.save(feuille)
        return saved, True

    def count_by_periode(
        self, date_debut: date, date_fin: date, statut: Optional[StatutPointage] = None
    ) -> int:
        """Compte les feuilles sur une période."""
        query = self.session.query(FeuilleHeuresModel).filter(
            FeuilleHeuresModel.semaine_debut >= date_debut,
            FeuilleHeuresModel.semaine_debut <= date_fin,
        )

        if statut:
            query = query.filter(FeuilleHeuresModel.statut_global == statut.value)

        return query.count()

    # ===== Helpers =====

    def _to_entity(self, model: FeuilleHeuresModel) -> FeuilleHeures:
        """Convertit un modèle en entité."""
        return FeuilleHeures(
            id=model.id,
            utilisateur_id=model.utilisateur_id,
            semaine_debut=model.semaine_debut,
            annee=model.annee,
            numero_semaine=model.numero_semaine,
            statut_global=StatutPointage.from_string(model.statut_global),
            commentaire_global=model.commentaire_global,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: FeuilleHeures) -> FeuilleHeuresModel:
        """Convertit une entité en modèle."""
        return FeuilleHeuresModel(
            id=entity.id,
            utilisateur_id=entity.utilisateur_id,
            semaine_debut=entity.semaine_debut,
            annee=entity.annee,
            numero_semaine=entity.numero_semaine,
            statut_global=entity.statut_global.value,
            commentaire_global=entity.commentaire_global,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model(self, model: FeuilleHeuresModel, entity: FeuilleHeures) -> None:
        """Met à jour un modèle depuis une entité."""
        model.statut_global = entity.statut_global.value
        model.commentaire_global = entity.commentaire_global
        model.updated_at = entity.updated_at
