"""Modèle SQLAlchemy pour Chantier."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base
from shared.domain.value_objects import Couleur
from ...domain.value_objects import StatutChantierEnum


class ChantierModel(Base):
    """
    Modèle SQLAlchemy représentant un chantier en base.

    Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20).

    Note:
        Ce modèle est dans Infrastructure car il dépend de SQLAlchemy.
        Il est mappé vers/depuis l'entité Chantier du Domain.
    """

    __tablename__ = "chantiers"
    __table_args__ = {"extend_existing": True}

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

    # Maître d'ouvrage
    maitre_ouvrage = Column(String(200), nullable=True)

    # Relation avec les phases (chantiers en plusieurs étapes) - utilise backref
    phases = relationship(
        "PhaseChantierModel",
        backref="chantier",
        cascade="all, delete-orphan"
    )

    # Budget temps (CHT-18)
    heures_estimees = Column(Float, nullable=True)

    # Dates prévisionnelles (CHT-20)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)

    # Responsables (CHT-05, CHT-06) - DEPRECATED: Utiliser conducteurs_rel/chefs_rel
    # Ces colonnes JSON sont conservées pour backward compatibility mais les tables
    # de jointure (chantier_conducteurs, chantier_chefs) sont la source de vérité.
    conducteur_ids = Column(JSON, nullable=False, default=list)  # DEPRECATED
    chef_chantier_ids = Column(JSON, nullable=False, default=list)  # DEPRECATED

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # Traçabilité devis -> chantier (DEV-16)
    source_devis_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Soft delete - permet de "supprimer" sans perdre les données (RGPD compliant)
    deleted_at = Column(DateTime, nullable=True, default=None, index=True)

    # Relations avec les contacts - utilise backref pour éviter la résolution bidirectionnelle
    contacts = relationship(
        "ContactChantierModel",
        backref="chantier",
        cascade="all, delete-orphan"
    )

    # Relations avec le module Documents (GED)
    dossiers = relationship("DossierModel", back_populates="chantier", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", back_populates="chantier", cascade="all, delete-orphan")

    # Relations via tables de jointure (optimisation N+1)
    conducteurs_rel = relationship(
        "ChantierConducteurModel",
        backref="chantier",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    chefs_rel = relationship(
        "ChantierChefModel",
        backref="chantier",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<ChantierModel(id={self.id}, code={self.code}, nom={self.nom})>"
