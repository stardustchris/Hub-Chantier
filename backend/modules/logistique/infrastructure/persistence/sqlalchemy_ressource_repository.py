"""Implémentation SQLAlchemy du repository Ressource."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import Ressource
from ...domain.repositories import RessourceRepository
from ...domain.value_objects import CategorieRessource, PlageHoraire
from .models import RessourceModel


class SQLAlchemyRessourceRepository(RessourceRepository):
    """Implémentation SQLAlchemy du repository Ressource."""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: RessourceModel) -> Ressource:
        """Convertit un modèle SQLAlchemy en entité domain."""
        return Ressource(
            id=model.id,
            nom=model.nom,
            code=model.code,
            categorie=model.categorie,
            photo_url=model.photo_url,
            couleur=model.couleur,
            plage_horaire_defaut=PlageHoraire(
                heure_debut=model.heure_debut_defaut,
                heure_fin=model.heure_fin_defaut,
            ),
            validation_requise=model.validation_requise,
            actif=model.actif,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            # H10: Soft delete fields
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _to_model(self, entity: Ressource) -> RessourceModel:
        """Convertit une entité domain en modèle SQLAlchemy."""
        return RessourceModel(
            id=entity.id,
            nom=entity.nom,
            code=entity.code,
            categorie=entity.categorie,
            photo_url=entity.photo_url,
            couleur=entity.couleur,
            heure_debut_defaut=entity.plage_horaire_defaut.heure_debut,
            heure_fin_defaut=entity.plage_horaire_defaut.heure_fin,
            validation_requise=entity.validation_requise,
            actif=entity.actif,
            description=entity.description,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )

    def save(self, ressource: Ressource) -> Ressource:
        """Persiste une ressource."""
        if ressource.id:
            # Mise à jour
            model = (
                self._session.query(RessourceModel)
                .filter(RessourceModel.id == ressource.id)
                .first()
            )
            if model:
                model.nom = ressource.nom
                model.code = ressource.code
                model.categorie = ressource.categorie
                model.photo_url = ressource.photo_url
                model.couleur = ressource.couleur
                model.heure_debut_defaut = ressource.plage_horaire_defaut.heure_debut
                model.heure_fin_defaut = ressource.plage_horaire_defaut.heure_fin
                model.validation_requise = ressource.validation_requise
                model.actif = ressource.actif
                model.description = ressource.description
                model.updated_at = datetime.utcnow()
        else:
            # Création
            model = self._to_model(ressource)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, ressource_id: int) -> Optional[Ressource]:
        """Recherche une ressource par son ID (exclut les supprimées)."""
        model = (
            self._session.query(RessourceModel)
            .filter(RessourceModel.id == ressource_id)
            .filter(RessourceModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_code(self, code: str) -> Optional[Ressource]:
        """Recherche une ressource par son code (exclut les supprimées)."""
        model = (
            self._session.query(RessourceModel)
            .filter(RessourceModel.code == code)
            .filter(RessourceModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all(
        self,
        categorie: Optional[CategorieRessource] = None,
        actif_seulement: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Ressource]:
        """Liste les ressources avec filtres (exclut les supprimées)."""
        query = self._session.query(RessourceModel)
        # H10: Exclure les supprimées
        query = query.filter(RessourceModel.deleted_at.is_(None))

        if categorie:
            query = query.filter(RessourceModel.categorie == categorie)
        if actif_seulement:
            query = query.filter(RessourceModel.actif.is_(True))

        query = query.order_by(RessourceModel.nom)
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def count(
        self,
        categorie: Optional[CategorieRessource] = None,
        actif_seulement: bool = True,
    ) -> int:
        """Compte le nombre de ressources (exclut les supprimées)."""
        query = self._session.query(RessourceModel)
        # H10: Exclure les supprimées
        query = query.filter(RessourceModel.deleted_at.is_(None))

        if categorie:
            query = query.filter(RessourceModel.categorie == categorie)
        if actif_seulement:
            query = query.filter(RessourceModel.actif.is_(True))

        return query.count()

    def delete(self, ressource_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime une ressource (soft delete - H10)."""
        model = (
            self._session.query(RessourceModel)
            .filter(RessourceModel.id == ressource_id)
            .filter(RessourceModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True

    def find_by_categorie(self, categorie: CategorieRessource) -> List[Ressource]:
        """Liste les ressources d'une catégorie."""
        return self.find_all(categorie=categorie, actif_seulement=True)
