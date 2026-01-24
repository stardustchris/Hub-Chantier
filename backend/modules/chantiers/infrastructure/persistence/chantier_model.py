"""Modèle SQLAlchemy pour Chantier et ContactChantier."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base
from shared.domain.value_objects import Couleur
from ...domain.value_objects import StatutChantierEnum


class ContactChantierModel(Base):
    """
    Modèle SQLAlchemy représentant un contact sur un chantier.

    Selon CDC CHT-07: Contacts sur place avec nom, profession et téléphone.
    """

    __tablename__ = "contacts_chantier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    profession = Column(String(100), nullable=True)
    telephone = Column(String(20), nullable=True)
    ordre = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relation vers le chantier
    chantier = relationship("ChantierModel", back_populates="contacts")

    def __repr__(self) -> str:
        return f"<ContactChantierModel(id={self.id}, nom={self.nom}, chantier_id={self.chantier_id})>"


class ChantierModel(Base):
    """
    Modèle SQLAlchemy représentant un chantier en base.

    Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20).

    Note:
        Ce modèle est dans Infrastructure car il dépend de SQLAlchemy.
        Il est mappé vers/depuis l'entité Chantier du Domain.
    """

    __tablename__ = "chantiers"

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identification (CHT-19)
    code = Column(String(4), unique=True, nullable=False, index=True)

    # Informations générales
    nom = Column(String(255), nullable=False)
    adresse = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Statut (CHT-03)
    statut = Column(
        String(20), nullable=False, default=StatutChantierEnum.OUVERT.value
    )

    # Couleur (CHT-02)
    couleur = Column(String(7), nullable=False, default=Couleur.DEFAULT)

    # Coordonnées GPS (CHT-04)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Photo de couverture (CHT-01)
    photo_couverture = Column(String(500), nullable=True)

    # Contact sur place (CHT-07) - Legacy fields (kept for backward compatibility)
    contact_nom = Column(String(200), nullable=True)
    contact_telephone = Column(String(20), nullable=True)

    # Relation avec les contacts (nouvelle structure multi-contacts)
    contacts = relationship("ContactChantierModel", back_populates="chantier", cascade="all, delete-orphan")

    # Relation avec les phases (chantiers en plusieurs étapes)
    phases = relationship("PhaseChantierModel", back_populates="chantier", cascade="all, delete-orphan", order_by="PhaseChantierModel.ordre")

    # Budget temps (CHT-18)
    heures_estimees = Column(Float, nullable=True)

    # Dates prévisionnelles (CHT-20)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)

    # Responsables (CHT-05, CHT-06) - Stockés en JSON pour simplifier
    conducteur_ids = Column(JSON, nullable=False, default=list)
    chef_chantier_ids = Column(JSON, nullable=False, default=list)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # Relations avec les contacts
    contacts = relationship(
        "ContactChantierModel",
        back_populates="chantier",
        cascade="all, delete-orphan",
        order_by="ContactChantierModel.ordre"
    )

    # Relations avec le module Documents (GED)
    dossiers = relationship("DossierModel", back_populates="chantier", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", back_populates="chantier", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChantierModel(id={self.id}, code={self.code}, nom={self.nom})>"
