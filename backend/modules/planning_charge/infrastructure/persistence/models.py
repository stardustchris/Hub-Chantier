"""Modeles SQLAlchemy pour le module planning_charge."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Index
from sqlalchemy.orm import Mapped

from shared.infrastructure.database_base import Base


class BesoinChargeModel(Base):
    """
    Modele SQLAlchemy pour les besoins de charge.

    Represente un besoin en main d'oeuvre pour un chantier,
    une semaine et un type de metier.
    """

    __tablename__ = "besoins_charge"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id: Mapped[int] = Column(Integer, nullable=False, index=True)
    semaine_annee: Mapped[int] = Column(Integer, nullable=False)
    semaine_numero: Mapped[int] = Column(Integer, nullable=False)
    type_metier: Mapped[str] = Column(String(50), nullable=False)
    besoin_heures: Mapped[float] = Column(Float, nullable=False, default=0.0)
    note: Mapped[str] = Column(Text, nullable=True)
    created_by: Mapped[int] = Column(Integer, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Index composite pour recherche rapide
    __table_args__ = (
        Index(
            "ix_besoins_charge_chantier_semaine",
            "chantier_id",
            "semaine_annee",
            "semaine_numero",
        ),
        Index(
            "ix_besoins_charge_semaine",
            "semaine_annee",
            "semaine_numero",
        ),
        Index(
            "ix_besoins_charge_unique",
            "chantier_id",
            "semaine_annee",
            "semaine_numero",
            "type_metier",
            unique=True,
        ),
    )

    @property
    def semaine_code(self) -> str:
        """Retourne le code semaine au format SXX-YYYY."""
        return f"S{self.semaine_numero:02d}-{self.semaine_annee}"

    def __repr__(self) -> str:
        return (
            f"<BesoinChargeModel(id={self.id}, chantier_id={self.chantier_id}, "
            f"semaine={self.semaine_code}, type={self.type_metier}, "
            f"besoin={self.besoin_heures}h)>"
        )
