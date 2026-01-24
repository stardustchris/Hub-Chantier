"""Modèle SQLAlchemy pour PhaseChantier."""

from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base


class PhaseChantierModel(Base):
    """
    Modèle SQLAlchemy représentant une phase/étape d'un chantier.

    Permet de découper un chantier en plusieurs phases avec leurs propres dates.
    Utile pour les chantiers en plusieurs étapes.
    """

    __tablename__ = "phases_chantier"
    __table_args__ = {"extend_existing": True}

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Référence au chantier
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Informations de la phase
    nom = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    ordre = Column(Integer, nullable=False, default=1)

    # Dates de la phase
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relation avec le chantier
    chantier = relationship(
        "modules.chantiers.infrastructure.persistence.chantier_model.ChantierModel",
        back_populates="phases"
    )

    def __repr__(self) -> str:
        return f"<PhaseChantierModel(id={self.id}, nom={self.nom}, ordre={self.ordre})>"
