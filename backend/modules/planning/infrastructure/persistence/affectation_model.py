"""Modele SQLAlchemy pour Affectation."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Index, JSON, Float

from shared.infrastructure.database_base import Base
from ...domain.value_objects import TypeAffectation


class AffectationModel(Base):
    """
    Modele SQLAlchemy representant une affectation en base.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

    Note:
        Ce modele est dans Infrastructure car il depend de SQLAlchemy.
        Il est mappe vers/depuis l'entite Affectation du Domain.
    """

    __tablename__ = "affectations"

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relations (references vers autres tables)
    utilisateur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Date de l'affectation
    date = Column(Date, nullable=False, index=True)

    # Heures prevues pour l'affectation (defaut: 8.0 pour journee standard)
    heures_prevues = Column(Float, nullable=False, default=8.0)

    # Horaires (format "HH:MM")
    heure_debut = Column(String(5), nullable=True)
    heure_fin = Column(String(5), nullable=True)

    # Note privee pour l'utilisateur affecte
    note = Column(Text, nullable=True)

    # Type d'affectation (unique ou recurrente)
    type_affectation = Column(
        String(20),
        nullable=False,
        default=TypeAffectation.UNIQUE.value,
    )

    # Jours de recurrence (ex: [0, 1, 2, 3, 4] pour lundi-vendredi)
    # Stocke en JSON pour SQLite/PostgreSQL compatibilite
    jours_recurrence = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    # Index composites pour les recherches frequentes
    __table_args__ = (
        Index("ix_affectations_user_date", "utilisateur_id", "date"),
        Index("ix_affectations_chantier_date", "chantier_id", "date"),
        Index("ix_affectations_date_range", "date"),
    )

    def __repr__(self) -> str:
        return (
            f"<AffectationModel(id={self.id}, "
            f"utilisateur_id={self.utilisateur_id}, "
            f"chantier_id={self.chantier_id}, "
            f"date={self.date})>"
        )
