"""Implémentation SQLAlchemy du DocumentRepository."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...domain.entities import Document
from ...domain.repositories import DocumentRepository
from ...domain.value_objects import NiveauAcces, TypeDocument
from .models import DocumentModel


class SQLAlchemyDocumentRepository(DocumentRepository):
    """Implémentation SQLAlchemy du repository documents."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def find_by_id(self, document_id: int) -> Optional[Document]:
        """Trouve un document par son ID."""
        model = self._session.query(DocumentModel).filter_by(id=document_id).first()
        return self._to_entity(model) if model else None

    def save(self, document: Document) -> Document:
        """Persiste un document."""
        if document.id:
            model = self._session.query(DocumentModel).filter_by(id=document.id).first()
            if model:
                model.nom = document.nom
                model.dossier_id = document.dossier_id
                model.description = document.description
                model.niveau_acces = document.niveau_acces.value if document.niveau_acces else None
                model.version = document.version
                model.updated_at = document.updated_at
        else:
            model = DocumentModel(
                chantier_id=document.chantier_id,
                dossier_id=document.dossier_id,
                nom=document.nom,
                nom_original=document.nom_original,
                type_document=document.type_document.value,
                taille=document.taille,
                chemin_stockage=document.chemin_stockage,
                mime_type=document.mime_type,
                niveau_acces=document.niveau_acces.value if document.niveau_acces else None,
                uploaded_by=document.uploaded_by,
                description=document.description,
                version=document.version,
                uploaded_at=document.uploaded_at,
                updated_at=document.updated_at,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def delete(self, document_id: int) -> bool:
        """Supprime un document."""
        model = self._session.query(DocumentModel).filter_by(id=document_id).first()
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False

    def find_by_dossier(
        self, dossier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Récupère les documents d'un dossier."""
        models = (
            self._session.query(DocumentModel)
            .filter_by(dossier_id=dossier_id)
            .order_by(DocumentModel.nom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_chantier(
        self, chantier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Récupère tous les documents d'un chantier."""
        models = (
            self._session.query(DocumentModel)
            .filter_by(chantier_id=chantier_id)
            .order_by(DocumentModel.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_dossier(self, dossier_id: int) -> int:
        """Compte les documents d'un dossier."""
        return (
            self._session.query(DocumentModel)
            .filter_by(dossier_id=dossier_id)
            .count()
        )

    def count_by_chantier(self, chantier_id: int) -> int:
        """Compte les documents d'un chantier."""
        return (
            self._session.query(DocumentModel)
            .filter_by(chantier_id=chantier_id)
            .count()
        )

    def search(
        self,
        chantier_id: int,
        query: Optional[str] = None,
        type_document: Optional[TypeDocument] = None,
        dossier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Document], int]:
        """Recherche des documents."""
        q = self._session.query(DocumentModel).filter_by(chantier_id=chantier_id)

        if query:
            q = q.filter(DocumentModel.nom.ilike(f"%{query}%"))

        if type_document:
            q = q.filter_by(type_document=type_document.value)

        if dossier_id:
            q = q.filter_by(dossier_id=dossier_id)

        total = q.count()
        models = q.order_by(DocumentModel.nom).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def exists_by_nom_in_dossier(self, nom: str, dossier_id: int) -> bool:
        """Vérifie si un nom existe déjà."""
        return (
            self._session.query(DocumentModel)
            .filter_by(dossier_id=dossier_id, nom=nom)
            .first()
            is not None
        )

    def get_total_size_by_chantier(self, chantier_id: int) -> int:
        """Calcule la taille totale."""
        result = (
            self._session.query(func.sum(DocumentModel.taille))
            .filter_by(chantier_id=chantier_id)
            .scalar()
        )
        return result or 0

    def _to_entity(self, model: DocumentModel) -> Document:
        """Convertit un modèle en entité."""
        return Document(
            id=model.id,
            chantier_id=model.chantier_id,
            dossier_id=model.dossier_id,
            nom=model.nom,
            nom_original=model.nom_original,
            type_document=TypeDocument(model.type_document),
            taille=model.taille,
            chemin_stockage=model.chemin_stockage,
            mime_type=model.mime_type,
            niveau_acces=NiveauAcces.from_string(model.niveau_acces) if model.niveau_acces else None,
            uploaded_by=model.uploaded_by,
            description=model.description,
            version=model.version,
            uploaded_at=model.uploaded_at,
            updated_at=model.updated_at,
        )
