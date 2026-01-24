"""Modèles SQLAlchemy pour le module pointages."""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Text,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base


class PointageModel(Base):
    """Modèle SQLAlchemy pour les pointages."""

    __tablename__ = "pointages"

    id = Column(Integer, primary_key=True, index=True)
    # Pas de FK vers users/chantiers - découplage modules Clean Architecture
    utilisateur_id = Column(Integer, nullable=False, index=True)
    chantier_id = Column(Integer, nullable=False, index=True)
    date_pointage = Column(Date, nullable=False, index=True)

    # Heures (stockées en minutes pour précision)
    heures_normales_minutes = Column(Integer, nullable=False, default=0)
    heures_supplementaires_minutes = Column(Integer, nullable=False, default=0)

    # Statut
    statut = Column(String(20), nullable=False, default="brouillon")
    commentaire = Column(Text, nullable=True)

    # Signature électronique (FDH-12)
    signature_utilisateur = Column(Text, nullable=True)
    signature_date = Column(DateTime, nullable=True)

    # Validation (pas de FK - découplage modules)
    validateur_id = Column(Integer, nullable=True)
    validation_date = Column(DateTime, nullable=True)
    motif_rejet = Column(Text, nullable=True)

    # Lien avec planning (FDH-10) - pas de FK pour découplage modules
    affectation_id = Column(Integer, nullable=True, index=True)

    # Métadonnées (pas de FK - découplage modules)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations
    variables_paie = relationship(
        "VariablePaieModel",
        back_populates="pointage",
        cascade="all, delete-orphan",
    )

    # Contraintes
    __table_args__ = (
        UniqueConstraint(
            "utilisateur_id",
            "chantier_id",
            "date_pointage",
            name="uq_pointage_utilisateur_chantier_date",
        ),
        Index("ix_pointage_semaine", "utilisateur_id", "date_pointage"),
        Index("ix_pointage_chantier_semaine", "chantier_id", "date_pointage"),
    )


class FeuilleHeuresModel(Base):
    """Modèle SQLAlchemy pour les feuilles d'heures hebdomadaires."""

    __tablename__ = "feuilles_heures"

    id = Column(Integer, primary_key=True, index=True)
    # Pas de FK vers users - découplage modules Clean Architecture
    utilisateur_id = Column(Integer, nullable=False, index=True)
    semaine_debut = Column(Date, nullable=False, index=True)  # Toujours un lundi
    annee = Column(Integer, nullable=False)
    numero_semaine = Column(Integer, nullable=False)

    # Statut global
    statut_global = Column(String(20), nullable=False, default="brouillon")
    commentaire_global = Column(Text, nullable=True)

    # Métadonnées
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Contraintes
    __table_args__ = (
        UniqueConstraint(
            "utilisateur_id",
            "semaine_debut",
            name="uq_feuille_utilisateur_semaine",
        ),
        Index("ix_feuille_annee_semaine", "annee", "numero_semaine"),
    )


class VariablePaieModel(Base):
    """Modèle SQLAlchemy pour les variables de paie."""

    __tablename__ = "variables_paie"

    id = Column(Integer, primary_key=True, index=True)
    pointage_id = Column(
        Integer,
        ForeignKey("pointages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type_variable = Column(String(50), nullable=False)
    valeur = Column(Numeric(10, 2), nullable=False)
    date_application = Column(Date, nullable=False)
    commentaire = Column(Text, nullable=True)

    # Métadonnées
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations
    pointage = relationship("PointageModel", back_populates="variables_paie")

    # Index
    __table_args__ = (
        Index("ix_variable_type_date", "type_variable", "date_application"),
    )
