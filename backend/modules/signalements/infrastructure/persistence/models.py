"""Modèles SQLAlchemy pour le module Signalements."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base


class SignalementModel(Base):
    """Modèle SQLAlchemy pour les signalements."""

    __tablename__ = "signalements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(Integer, ForeignKey("chantiers.id"), nullable=False, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priorite = Column(String(50), nullable=False, default="moyenne")
    statut = Column(String(50), nullable=False, default="ouvert")
    cree_par = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assigne_a = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    date_resolution_souhaitee = Column(DateTime, nullable=True)
    date_traitement = Column(DateTime, nullable=True)
    date_cloture = Column(DateTime, nullable=True)
    commentaire_traitement = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    localisation = Column(String(255), nullable=True)
    nb_escalades = Column(Integer, nullable=False, default=0)
    derniere_escalade_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations (interne au module uniquement)
    # Note: Les relations vers ChantierModel et UserModel sont gérées par ForeignKey
    # mais pas par ORM relationship car ils utilisent un Base différent
    reponses = relationship("ReponseModel", back_populates="signalement", cascade="all, delete-orphan")


class ReponseModel(Base):
    """Modèle SQLAlchemy pour les réponses aux signalements."""

    __tablename__ = "reponses_signalements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signalement_id = Column(Integer, ForeignKey("signalements.id"), nullable=False, index=True)
    contenu = Column(Text, nullable=False)
    auteur_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    photo_url = Column(String(500), nullable=True)
    est_resolution = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations (interne au module uniquement)
    signalement = relationship("SignalementModel", back_populates="reponses")
