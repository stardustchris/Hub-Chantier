"""Modele SQLAlchemy pour User."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base
from shared.infrastructure.security import EncryptedString
from ...domain.value_objects import Role, TypeUtilisateur, Couleur


class UserModel(Base):
    """
    Modèle SQLAlchemy représentant un utilisateur en base.

    Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 à USR-13).

    Note:
        Ce modèle est dans Infrastructure car il dépend de SQLAlchemy.
        Il est mappé vers/depuis l'entité User du Domain.
    """

    __tablename__ = "users"

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Authentification
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Informations personnelles
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    telephone = Column(EncryptedString(20), nullable=True)  # USR-08 - Chiffre RGPD

    # Rôle et type
    role = Column(String(50), nullable=False, default=Role.COMPAGNON.value)  # USR-06
    type_utilisateur = Column(
        String(50), nullable=False, default=TypeUtilisateur.EMPLOYE.value
    )  # USR-05

    # Statut
    is_active = Column(Boolean, nullable=False, default=True)  # USR-04, USR-10

    # Identification visuelle
    couleur = Column(String(7), nullable=False, default=Couleur.DEFAULT)  # USR-03
    photo_profil = Column(String(500), nullable=True)  # USR-02

    # Informations professionnelles
    code_utilisateur = Column(String(50), nullable=True, index=True)  # USR-07 (matricule)
    metier = Column(String(100), nullable=True)  # USR-11

    # Contact d'urgence (USR-13) - Donnees chiffrees RGPD Art. 32
    contact_urgence_nom = Column(EncryptedString(200), nullable=True)
    contact_urgence_tel = Column(EncryptedString(20), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # Soft delete - RGPD Art. 17 (Droit a l'oubli) avec conservation audit
    deleted_at = Column(DateTime, nullable=True, default=None, index=True)

    # Consentements RGPD Art. 7 (preuve du consentement)
    consent_geolocation = Column(Boolean, nullable=False, default=False)
    consent_notifications = Column(Boolean, nullable=False, default=False)
    consent_analytics = Column(Boolean, nullable=False, default=False)
    consent_timestamp = Column(DateTime, nullable=True, index=True)  # Date du consentement
    consent_ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    consent_user_agent = Column(String(500), nullable=True)  # User agent navigateur

    # Relations
    api_keys = relationship("APIKeyModel", back_populates="user", cascade="all, delete-orphan")
    # webhooks = relationship("WebhookModel", back_populates="user", cascade="all, delete-orphan")  # Temporairement désactivé

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"
