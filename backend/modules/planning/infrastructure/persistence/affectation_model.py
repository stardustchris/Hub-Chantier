"""Modèle SQLAlchemy pour les affectations."""

from datetime import date, time, datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Date, Time, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AffectationModel(Base):
    """
    Modèle SQLAlchemy pour la table des affectations.

    Selon CDC Section 5 - Planning Opérationnel (PLN-01 à PLN-28).
    """

    __tablename__ = "affectations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, nullable=False, index=True)
    chantier_id = Column(Integer, nullable=False, index=True)
    date_affectation = Column(Date, nullable=False, index=True)
    heure_debut = Column(Time, nullable=True)
    heure_fin = Column(Time, nullable=True)
    note = Column(Text, nullable=True)
    recurrence = Column(String(20), nullable=False, default="unique")
    jours_recurrence = Column(JSON, nullable=True, default=list)
    date_fin_recurrence = Column(Date, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now)

    def __repr__(self) -> str:
        """Représentation de l'affectation."""
        return (
            f"<Affectation(id={self.id}, "
            f"utilisateur_id={self.utilisateur_id}, "
            f"chantier_id={self.chantier_id}, "
            f"date={self.date_affectation})>"
        )
