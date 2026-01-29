"""Modèles SQLAlchemy pour le module Documents."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base


class DossierModel(Base):
    """Modèle SQLAlchemy pour les dossiers."""

    __tablename__ = "dossiers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False, index=True)
    nom = Column(String(255), nullable=False)
    type_dossier = Column(String(50), nullable=False, default="custom")
    niveau_acces = Column(String(50), nullable=False, default="compagnon")
    parent_id = Column(Integer, ForeignKey("dossiers.id", ondelete="SET NULL"), nullable=True)
    ordre = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations
    chantier = relationship("ChantierModel", back_populates="dossiers")
    documents = relationship("DocumentModel", back_populates="dossier", cascade="all, delete-orphan")
    children = relationship("DossierModel", back_populates="parent", remote_side=[id])
    parent = relationship("DossierModel", back_populates="children", remote_side=[parent_id])
    autorisations = relationship("AutorisationDocumentModel", back_populates="dossier", cascade="all, delete-orphan")


class DocumentModel(Base):
    """Modèle SQLAlchemy pour les documents."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False, index=True)
    dossier_id = Column(Integer, ForeignKey("dossiers.id", ondelete="SET NULL"), nullable=True, index=True)
    nom = Column(String(255), nullable=False)
    nom_original = Column(String(255), nullable=False)
    type_document = Column(String(50), nullable=False, default="autre")
    taille = Column(Integer, nullable=False)
    chemin_stockage = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    niveau_acces = Column(String(50), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations
    chantier = relationship("ChantierModel", back_populates="documents")
    dossier = relationship("DossierModel", back_populates="documents")
    uploader = relationship("UserModel", foreign_keys=[uploaded_by])
    autorisations = relationship("AutorisationDocumentModel", back_populates="document", cascade="all, delete-orphan")


class AutorisationDocumentModel(Base):
    """Modèle SQLAlchemy pour les autorisations nominatives."""

    __tablename__ = "autorisations_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type_autorisation = Column(String(50), nullable=False)
    dossier_id = Column(Integer, ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    accorde_par = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    expire_at = Column(DateTime, nullable=True)

    # Relations
    user = relationship("UserModel", foreign_keys=[user_id])
    accorde_par_user = relationship("UserModel", foreign_keys=[accorde_par])
    dossier = relationship("DossierModel", back_populates="autorisations")
    document = relationship("DocumentModel", back_populates="autorisations")
