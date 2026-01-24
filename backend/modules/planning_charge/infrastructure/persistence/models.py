"""Modeles SQLAlchemy pour le module planning_charge."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, relationship

from shared.infrastructure.database_base import Base


class BesoinChargeModel(Base):
    """
    Modele SQLAlchemy pour les besoins de charge.

    Represente un besoin en main d'oeuvre pour un chantier,
    une semaine et un type de metier.

    Inclut soft delete pour conservation historique.
    """

    __tablename__ = "besoins_charge"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    chantier_id: Mapped[int] = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[int] = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Semaine
    semaine_annee: Mapped[int] = Column(Integer, nullable=False)
    semaine_numero: Mapped[int] = Column(Integer, nullable=False)

    # Besoin
    type_metier: Mapped[str] = Column(String(50), nullable=False)
    besoin_heures: Mapped[float] = Column(Float, nullable=False, default=0.0)
    note: Mapped[Optional[str]] = Column(Text, nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    deleted_by: Mapped[Optional[int]] = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

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
        Index(
            "ix_besoins_charge_not_deleted",
            "is_deleted",
        ),
    )

    @property
    def semaine_code(self) -> str:
        """Retourne le code semaine au format SXX-YYYY."""
        return f"S{self.semaine_numero:02d}-{self.semaine_annee}"

    def soft_delete(self, deleted_by: int) -> None:
        """Marque l'enregistrement comme supprime."""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.deleted_by = deleted_by

    def restore(self) -> None:
        """Restaure un enregistrement supprime."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

    def __repr__(self) -> str:
        status = " [DELETED]" if self.is_deleted else ""
        return (
            f"<BesoinChargeModel(id={self.id}, chantier_id={self.chantier_id}, "
            f"semaine={self.semaine_code}, type={self.type_metier}, "
            f"besoin={self.besoin_heures}h){status}>"
        )
