"""Implementation SQLAlchemy du repository Ressource.

CDC Section 11 - LOG-01, LOG-02.
"""
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import RessourceModel
from ...domain.entities import Ressource
from ...domain.value_objects import TypeRessource
from ...domain.repositories import RessourceRepository


class SQLAlchemyRessourceRepository(RessourceRepository):
    """Implementation SQLAlchemy du repository Ressource."""

    def __init__(self, session: Session):
        """Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def save(self, ressource: Ressource) -> Ressource:
        """Sauvegarde une ressource.

        Args:
            ressource: Ressource a sauvegarder.

        Returns:
            La ressource sauvegardee avec son ID.
        """
        if ressource.id:
            # Update
            model = self._session.query(RessourceModel).filter(
                RessourceModel.id == ressource.id
            ).first()
            if model:
                self._entity_to_model(ressource, model)
        else:
            # Create
            model = RessourceModel()
            self._entity_to_model(ressource, model)
            self._session.add(model)

        self._session.flush()
        return self._model_to_entity(model)

    def find_by_id(self, ressource_id: int) -> Optional[Ressource]:
        """Trouve une ressource par ID.

        Args:
            ressource_id: ID de la ressource.

        Returns:
            La ressource ou None.
        """
        model = self._session.query(RessourceModel).filter(
            and_(
                RessourceModel.id == ressource_id,
                RessourceModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def find_by_code(self, code: str) -> Optional[Ressource]:
        """Trouve une ressource par code.

        Args:
            code: Code de la ressource.

        Returns:
            La ressource ou None.
        """
        model = self._session.query(RessourceModel).filter(
            and_(
                RessourceModel.code == code,
                RessourceModel.deleted_at.is_(None),
            )
        ).first()

        if not model:
            return None

        return self._model_to_entity(model)

    def find_all(
        self,
        type_ressource: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Ressource]:
        """Liste les ressources.

        Args:
            type_ressource: Filtrer par type.
            is_active: Filtrer par statut actif.
            skip: Offset de pagination.
            limit: Limite de pagination.

        Returns:
            Liste des ressources.
        """
        query = self._session.query(RessourceModel).filter(
            RessourceModel.deleted_at.is_(None)
        )

        if type_ressource:
            query = query.filter(RessourceModel.type_ressource == type_ressource)

        if is_active is not None:
            query = query.filter(RessourceModel.is_active == is_active)

        query = query.order_by(RessourceModel.nom).offset(skip).limit(limit)

        return [self._model_to_entity(m) for m in query.all()]

    def count(
        self,
        type_ressource: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Compte les ressources.

        Args:
            type_ressource: Filtrer par type.
            is_active: Filtrer par statut actif.

        Returns:
            Nombre de ressources.
        """
        query = self._session.query(RessourceModel).filter(
            RessourceModel.deleted_at.is_(None)
        )

        if type_ressource:
            query = query.filter(RessourceModel.type_ressource == type_ressource)

        if is_active is not None:
            query = query.filter(RessourceModel.is_active == is_active)

        return query.count()

    def delete(self, ressource_id: int) -> bool:
        """Supprime une ressource (soft delete).

        Args:
            ressource_id: ID de la ressource.

        Returns:
            True si supprimee.
        """
        ressource = self.find_by_id(ressource_id)
        if ressource:
            ressource.supprimer()
            self.save(ressource)
            return True
        return False

    def _model_to_entity(self, model: RessourceModel) -> Ressource:
        """Convertit un modele en entite."""
        ressource = Ressource(
            code=model.code,
            nom=model.nom,
            description=model.description,
            type_ressource=TypeRessource(model.type_ressource),
            photo_url=model.photo_url,
            couleur=model.couleur,
            plage_horaire_debut=model.plage_horaire_debut,
            plage_horaire_fin=model.plage_horaire_fin,
            validation_requise=model.validation_requise,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
        ressource.id = model.id
        return ressource

    def _entity_to_model(self, entity: Ressource, model: RessourceModel) -> None:
        """Copie les champs d'une entite vers un modele."""
        model.code = entity.code
        model.nom = entity.nom
        model.description = entity.description
        model.type_ressource = entity.type_ressource.value
        model.photo_url = entity.photo_url
        model.couleur = entity.couleur
        model.plage_horaire_debut = entity.plage_horaire_debut
        model.plage_horaire_fin = entity.plage_horaire_fin
        model.validation_requise = entity.validation_requise
        model.is_active = entity.is_active
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
