"""Implémentation SQLAlchemy du DossierRepository."""

from typing import Optional, List
from sqlalchemy.orm import Session

from ...domain.entities import Dossier
from ...domain.repositories import DossierRepository
from ...domain.value_objects import NiveauAcces, DossierType
from .models import DossierModel, DocumentModel


class SQLAlchemyDossierRepository(DossierRepository):
    """Implémentation SQLAlchemy du repository dossiers."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def find_by_id(self, dossier_id: int) -> Optional[Dossier]:
        """Trouve un dossier par son ID."""
        model = self._session.query(DossierModel).filter_by(id=dossier_id).first()
        return self._to_entity(model) if model else None

    def save(self, dossier: Dossier) -> Dossier:
        """Persiste un dossier."""
        if dossier.id:
            model = self._session.query(DossierModel).filter_by(id=dossier.id).first()
            if model:
                model.nom = dossier.nom
                model.type_dossier = dossier.type_dossier.value
                model.niveau_acces = dossier.niveau_acces.value
                model.parent_id = dossier.parent_id
                model.ordre = dossier.ordre
                model.updated_at = dossier.updated_at
        else:
            model = DossierModel(
                chantier_id=dossier.chantier_id,
                nom=dossier.nom,
                type_dossier=dossier.type_dossier.value,
                niveau_acces=dossier.niveau_acces.value,
                parent_id=dossier.parent_id,
                ordre=dossier.ordre,
                created_at=dossier.created_at,
                updated_at=dossier.updated_at,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def delete(self, dossier_id: int) -> bool:
        """Supprime un dossier."""
        model = self._session.query(DossierModel).filter_by(id=dossier_id).first()
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False

    def find_by_chantier(
        self, chantier_id: int, parent_id: Optional[int] = None
    ) -> List[Dossier]:
        """Récupère les dossiers d'un chantier."""
        query = self._session.query(DossierModel).filter_by(chantier_id=chantier_id)

        if parent_id is None:
            query = query.filter(DossierModel.parent_id.is_(None))
        else:
            query = query.filter_by(parent_id=parent_id)

        models = query.order_by(DossierModel.ordre, DossierModel.nom).all()
        return [self._to_entity(m) for m in models]

    def find_children(self, dossier_id: int) -> List[Dossier]:
        """Récupère les sous-dossiers."""
        models = (
            self._session.query(DossierModel)
            .filter_by(parent_id=dossier_id)
            .order_by(DossierModel.ordre, DossierModel.nom)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_chantier(self, chantier_id: int) -> int:
        """Compte les dossiers d'un chantier."""
        return (
            self._session.query(DossierModel)
            .filter_by(chantier_id=chantier_id)
            .count()
        )

    def exists_by_nom_in_parent(
        self, nom: str, chantier_id: int, parent_id: Optional[int] = None
    ) -> bool:
        """Vérifie si un nom existe déjà."""
        query = self._session.query(DossierModel).filter_by(
            chantier_id=chantier_id, nom=nom
        )

        if parent_id is None:
            query = query.filter(DossierModel.parent_id.is_(None))
        else:
            query = query.filter_by(parent_id=parent_id)

        return query.first() is not None

    def find_by_type(
        self, chantier_id: int, type_dossier: DossierType
    ) -> Optional[Dossier]:
        """Trouve un dossier par type."""
        model = (
            self._session.query(DossierModel)
            .filter_by(chantier_id=chantier_id, type_dossier=type_dossier.value)
            .first()
        )
        return self._to_entity(model) if model else None

    def get_arborescence(self, chantier_id: int) -> List[Dossier]:
        """Récupère toute l'arborescence."""
        models = (
            self._session.query(DossierModel)
            .filter_by(chantier_id=chantier_id)
            .order_by(DossierModel.ordre, DossierModel.nom)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def has_documents(self, dossier_id: int) -> bool:
        """Vérifie si un dossier contient des documents."""
        return (
            self._session.query(DocumentModel)
            .filter_by(dossier_id=dossier_id)
            .first()
            is not None
        )

    def has_children(self, dossier_id: int) -> bool:
        """Vérifie si un dossier a des sous-dossiers."""
        return (
            self._session.query(DossierModel)
            .filter_by(parent_id=dossier_id)
            .first()
            is not None
        )

    def _to_entity(self, model: DossierModel) -> Dossier:
        """Convertit un modèle en entité."""
        return Dossier(
            id=model.id,
            chantier_id=model.chantier_id,
            nom=model.nom,
            type_dossier=DossierType.from_string(model.type_dossier),
            niveau_acces=NiveauAcces.from_string(model.niveau_acces),
            parent_id=model.parent_id,
            ordre=model.ordre,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
