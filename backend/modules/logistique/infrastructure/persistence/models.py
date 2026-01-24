"""SQLAlchemy models pour le module Logistique.

LOG-01: Référentiel matériel
LOG-02: Fiche ressource
LOG-07 à LOG-18: Réservations et workflow
"""

from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Time,
    Text,
    Index,
    Enum as SQLEnum,
)

from shared.infrastructure.database_base import Base
from ...domain.value_objects import CategorieRessource, StatutReservation


# Alias pour compatibilité
LogistiqueBase = Base


class RessourceModel(LogistiqueBase):
    """Modèle SQLAlchemy pour les ressources.

    LOG-01: Référentiel matériel
    LOG-02: Fiche ressource - Nom, code, photo, couleur, plage horaire
    """

    __tablename__ = "ressources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(200), nullable=False)
    code = Column(String(20), nullable=False, unique=True, index=True)
    categorie = Column(
        SQLEnum(CategorieRessource, native_enum=False, length=50),
        nullable=False,
        index=True,
    )
    photo_url = Column(String(500), nullable=True)
    couleur = Column(String(7), nullable=False, default="#3B82F6")
    heure_debut_defaut = Column(Time, nullable=False, default=time(8, 0))
    heure_fin_defaut = Column(Time, nullable=False, default=time(18, 0))
    validation_requise = Column(Boolean, nullable=False, default=True)
    actif = Column(Boolean, nullable=False, default=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_ressources_categorie_actif", "categorie", "actif"),
    )

    def __repr__(self) -> str:
        return f"<Ressource(id={self.id}, code='{self.code}', nom='{self.nom}')>"


class ReservationModel(LogistiqueBase):
    """Modèle SQLAlchemy pour les réservations.

    LOG-07: Demande de réservation
    LOG-08: Sélection chantier
    LOG-09: Sélection créneau
    LOG-11: Workflow validation
    LOG-12: Statuts réservation
    """

    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ressource_id = Column(Integer, nullable=False, index=True)
    chantier_id = Column(Integer, nullable=False, index=True)
    demandeur_id = Column(Integer, nullable=False, index=True)
    date_reservation = Column(Date, nullable=False, index=True)
    heure_debut = Column(Time, nullable=False)
    heure_fin = Column(Time, nullable=False)
    statut = Column(
        SQLEnum(StatutReservation, native_enum=False, length=20),
        nullable=False,
        default=StatutReservation.EN_ATTENTE,
        index=True,
    )
    motif_refus = Column(Text, nullable=True)
    commentaire = Column(Text, nullable=True)
    valideur_id = Column(Integer, nullable=True)
    validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    __table_args__ = (
        # Index pour le planning par ressource et date
        Index("ix_reservations_ressource_date", "ressource_id", "date_reservation"),
        # Index pour les réservations en attente
        Index("ix_reservations_statut_date", "statut", "date_reservation"),
        # Index pour les réservations par chantier
        Index("ix_reservations_chantier_date", "chantier_id", "date_reservation"),
        # Index pour les réservations par demandeur
        Index("ix_reservations_demandeur_statut", "demandeur_id", "statut"),
    )

    def __repr__(self) -> str:
        return (
            f"<Reservation(id={self.id}, ressource={self.ressource_id}, "
            f"date={self.date_reservation}, statut={self.statut.value})>"
        )
