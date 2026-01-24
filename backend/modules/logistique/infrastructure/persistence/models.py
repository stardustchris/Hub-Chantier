"""Modeles SQLAlchemy pour le module Logistique.

CDC Section 11 - LOG-01 a LOG-18.
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    Text,
    ForeignKey,
    Index,
    JSON,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base
from ...domain.value_objects import TypeRessource, StatutReservation


class RessourceModel(Base):
    """
    Modele SQLAlchemy pour les ressources materielles.

    Selon CDC Section 11:
    - LOG-01: Referentiel materiel (Admin uniquement)
    - LOG-02: Fiche ressource (nom, code, photo, couleur, plage horaire)
    - LOG-10: Option validation N+1
    """

    __tablename__ = "ressources"

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identification (LOG-02)
    code = Column(String(20), unique=True, nullable=False, index=True)
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Type de ressource
    type_ressource = Column(
        String(50),
        nullable=False,
        default=TypeRessource.OUTILLAGE.value,
    )

    # Identification visuelle (LOG-02)
    photo_url = Column(String(500), nullable=True)
    couleur = Column(String(7), nullable=False, default="#3498DB")

    # Plage horaire par defaut (LOG-05)
    plage_horaire_debut = Column(String(5), nullable=False, default="08:00")
    plage_horaire_fin = Column(String(5), nullable=False, default="18:00")

    # Option validation N+1 (LOG-10)
    validation_requise = Column(Boolean, nullable=False, default=True)

    # Statut
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # Soft delete (RGPD compliant)
    deleted_at = Column(DateTime, nullable=True, default=None, index=True)

    # Relations
    reservations = relationship(
        "ReservationModel",
        back_populates="ressource",
        cascade="all, delete-orphan",
    )

    # Index composites
    __table_args__ = (
        Index("ix_ressources_type", "type_ressource"),
        Index("ix_ressources_active", "is_active", "deleted_at"),
    )

    def __repr__(self) -> str:
        return f"<RessourceModel(id={self.id}, code={self.code}, nom={self.nom})>"


class ReservationModel(Base):
    """
    Modele SQLAlchemy pour les reservations de ressources.

    Selon CDC Section 11:
    - LOG-07: Demande de reservation
    - LOG-08: Selection chantier (obligatoire)
    - LOG-09: Selection creneau
    - LOG-11, LOG-12: Workflow et statuts
    - LOG-16: Motif de refus
    - LOG-17: Detection conflits (via index)
    """

    __tablename__ = "reservations"

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relations obligatoires
    ressource_id = Column(
        Integer,
        ForeignKey("ressources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    demandeur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    # Valideur (null si pas encore traite)
    valideur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Creneau de reservation (LOG-09)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    heure_debut = Column(String(5), nullable=False)
    heure_fin = Column(String(5), nullable=False)

    # Statut (LOG-11, LOG-12)
    statut = Column(
        String(20),
        nullable=False,
        default=StatutReservation.EN_ATTENTE.value,
        index=True,
    )

    # Motif de refus (LOG-16)
    motif_refus = Column(Text, nullable=True)

    # Note du demandeur
    note = Column(Text, nullable=True)

    # Horodatages des actions
    validated_at = Column(DateTime, nullable=True)
    refused_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # Soft delete (RGPD compliant)
    deleted_at = Column(DateTime, nullable=True, default=None, index=True)

    # Relations
    ressource = relationship("RessourceModel", back_populates="reservations")
    historique = relationship(
        "HistoriqueReservationModel",
        back_populates="reservation",
        cascade="all, delete-orphan",
    )

    # Contraintes et index
    __table_args__ = (
        # Contrainte de coherence des dates
        CheckConstraint("date_fin >= date_debut", name="ck_reservation_dates"),
        # Index pour recherche par ressource et dates (LOG-03)
        Index("ix_reservations_ressource_dates", "ressource_id", "date_debut", "date_fin"),
        # Index pour recherche par chantier
        Index("ix_reservations_chantier_dates", "chantier_id", "date_debut"),
        # Index pour recherche par statut et ressource
        Index("ix_reservations_statut_ressource", "statut", "ressource_id"),
        # Index pour detection de conflits (LOG-17)
        Index(
            "ix_reservations_conflit",
            "ressource_id",
            "statut",
            "date_debut",
            "date_fin",
            "heure_debut",
            "heure_fin",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ReservationModel(id={self.id}, "
            f"ressource_id={self.ressource_id}, "
            f"statut={self.statut})>"
        )


class HistoriqueReservationModel(Base):
    """
    Modele SQLAlchemy pour l'historique des reservations (LOG-18).

    Enregistre toutes les actions effectuees sur une reservation:
    - created: Creation de la demande
    - validated: Validation par chef/conducteur
    - refused: Refus par chef/conducteur
    - cancelled: Annulation par le demandeur
    - modified: Modification du creneau
    """

    __tablename__ = "historique_reservations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Reservation concernee
    reservation_id = Column(
        Integer,
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Action effectuee
    action = Column(String(50), nullable=False, index=True)

    # Utilisateur ayant effectue l'action
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Details de l'action (JSON pour flexibilite)
    details = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)

    # Relations
    reservation = relationship("ReservationModel", back_populates="historique")

    def __repr__(self) -> str:
        return (
            f"<HistoriqueReservationModel(id={self.id}, "
            f"reservation_id={self.reservation_id}, "
            f"action={self.action})>"
        )
