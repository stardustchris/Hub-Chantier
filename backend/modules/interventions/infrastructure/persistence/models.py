"""SQLAlchemy models pour le module Interventions.

INT-01 a INT-17: Gestion des interventions ponctuelles.
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
    ForeignKey,
    CheckConstraint,
    JSON,
    text,
)
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base
from ...domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)
from ...domain.entities import TypeMessage, TypeSignataire


class InterventionModel(Base):
    """Modele SQLAlchemy pour les interventions.

    INT-01 a INT-05: Gestion de base des interventions
    """

    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True, index=True)
    type_intervention = Column(
        SQLEnum(TypeIntervention, native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    statut = Column(
        SQLEnum(StatutIntervention, native_enum=False, length=20),
        nullable=False,
        default=StatutIntervention.A_PLANIFIER,
        index=True,
    )
    priorite = Column(
        SQLEnum(PrioriteIntervention, native_enum=False, length=20),
        nullable=False,
        default=PrioriteIntervention.NORMALE,
        index=True,
    )

    # Informations client (INT-04)
    client_nom = Column(String(200), nullable=False)
    client_adresse = Column(Text, nullable=False)
    client_telephone = Column(String(20), nullable=True)
    client_email = Column(String(200), nullable=True)

    # Description et travaux
    description = Column(Text, nullable=False)
    travaux_realises = Column(Text, nullable=True)
    anomalies = Column(Text, nullable=True)

    # Planification (INT-05, INT-06, INT-07)
    date_souhaitee = Column(Date, nullable=True)
    date_planifiee = Column(Date, nullable=True, index=True)
    heure_debut = Column(Time, nullable=True)
    heure_fin = Column(Time, nullable=True)
    heure_debut_reelle = Column(Time, nullable=True)
    heure_fin_reelle = Column(Time, nullable=True)

    # Lien optionnel avec chantier d'origine (pour SAV)
    chantier_origine_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Rapport PDF (INT-14, INT-16)
    rapport_genere = Column(Boolean, nullable=False, default=False)
    rapport_url = Column(String(500), nullable=True)

    # Audit
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relations
    affectations = relationship(
        "AffectationInterventionModel",
        back_populates="intervention",
        cascade="all, delete-orphan",
    )
    messages = relationship(
        "InterventionMessageModel",
        back_populates="intervention",
        cascade="all, delete-orphan",
    )
    signatures = relationship(
        "SignatureInterventionModel",
        back_populates="intervention",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Index pour le planning hebdomadaire (INT-06)
        Index("ix_interventions_date_statut", "date_planifiee", "statut"),
        # Index pour la recherche par client
        Index("ix_interventions_client_nom", "client_nom"),
        # Index pour les interventions actives
        Index(
            "ix_interventions_statut_priorite_date",
            "statut",
            "priorite",
            "date_planifiee",
        ),
        # Index composite pour soft delete
        Index(
            "ix_interventions_deleted_statut",
            "deleted_at",
            "statut",
        ),
        # CHECK: heure_fin > heure_debut si les deux sont definis
        CheckConstraint(
            "heure_fin IS NULL OR heure_debut IS NULL OR heure_fin > heure_debut",
            name="check_interventions_plage_horaire",
        ),
    )

    def __repr__(self) -> str:
        return f"<Intervention(id={self.id}, code='{self.code}', statut={self.statut.value})>"


class AffectationInterventionModel(Base):
    """Modele SQLAlchemy pour les affectations de techniciens.

    INT-10: Affectation technicien
    INT-17: Affectation sous-traitants
    """

    __tablename__ = "affectations_interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(
        Integer,
        ForeignKey("interventions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    utilisateur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    est_principal = Column(Boolean, nullable=False, default=False)
    commentaire = Column(Text, nullable=True)

    # Audit
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relations
    intervention = relationship("InterventionModel", back_populates="affectations")

    __table_args__ = (
        # Index pour les recherches par utilisateur
        Index("ix_affectations_interventions_user_deleted", "utilisateur_id", "deleted_at"),
        # Contrainte unique: un utilisateur ne peut etre affecte qu'une fois par intervention
        Index(
            "ix_affectations_interventions_unique",
            "intervention_id",
            "utilisateur_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AffectationIntervention(id={self.id}, intervention={self.intervention_id}, "
            f"user={self.utilisateur_id}, principal={self.est_principal})>"
        )


class InterventionMessageModel(Base):
    """Modele SQLAlchemy pour les messages/fil d'activite.

    INT-11: Fil d'actualite
    INT-12: Chat intervention
    INT-15: Selection posts pour rapport
    """

    __tablename__ = "interventions_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(
        Integer,
        ForeignKey("interventions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    auteur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # Peut etre null pour messages systeme
        index=True,
    )
    type_message = Column(
        SQLEnum(TypeMessage, native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    contenu = Column(Text, nullable=False)
    photos_urls = Column(JSON, nullable=True, default=list)
    extra_data = Column(JSON, nullable=True)  # metadata is reserved in SQLAlchemy
    inclure_rapport = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relations
    intervention = relationship("InterventionModel", back_populates="messages")

    __table_args__ = (
        # Index pour le fil d'activite
        Index("ix_interventions_messages_chrono", "intervention_id", "created_at"),
        # Index pour les messages a inclure dans le rapport
        Index(
            "ix_interventions_messages_rapport",
            "intervention_id",
            "inclure_rapport",
            postgresql_where=text("deleted_at IS NULL AND inclure_rapport = true"),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<InterventionMessage(id={self.id}, intervention={self.intervention_id}, "
            f"type={self.type_message.value})>"
        )


class SignatureInterventionModel(Base):
    """Modele SQLAlchemy pour les signatures.

    INT-13: Signature client
    INT-14: Signatures dans rapport PDF
    """

    __tablename__ = "interventions_signatures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(
        Integer,
        ForeignKey("interventions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type_signataire = Column(
        SQLEnum(TypeSignataire, native_enum=False, length=20),
        nullable=False,
    )
    nom_signataire = Column(String(200), nullable=False)
    signature_data = Column(Text, nullable=False)  # Base64 ou URL

    # Pour les techniciens
    utilisateur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Tracabilite
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)

    # Horodatage
    signed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relations
    intervention = relationship("InterventionModel", back_populates="signatures")

    __table_args__ = (
        # Index pour retrouver les signatures par intervention et type
        Index(
            "ix_interventions_signatures_type",
            "intervention_id",
            "type_signataire",
        ),
        # Contrainte: une seule signature client par intervention
        Index(
            "ix_interventions_signatures_client_unique",
            "intervention_id",
            unique=True,
            postgresql_where=text("type_signataire = 'client' AND deleted_at IS NULL"),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<SignatureIntervention(id={self.id}, intervention={self.intervention_id}, "
            f"type={self.type_signataire.value}, nom='{self.nom_signataire}')>"
        )
