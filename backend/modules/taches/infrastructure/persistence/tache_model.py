"""SQLAlchemy Model pour les taches."""

from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    Date,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base
from ...domain.value_objects import StatutTache, UniteMesure


class TacheModel(Base):
    """
    Model SQLAlchemy pour les taches.

    Represente la table 'taches' en base de donnees.
    Selon CDC Section 13 - Gestion des Taches (TAC-01 a TAC-20).
    """

    __tablename__ = "taches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chantier_id = Column(Integer, nullable=False, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("taches.id"), nullable=True, index=True)
    ordre = Column(Integer, nullable=False, default=0)
    statut = Column(String(20), nullable=False, default=StatutTache.A_FAIRE.value)
    date_echeance = Column(Date, nullable=True)
    unite_mesure = Column(String(20), nullable=True)
    quantite_estimee = Column(Float, nullable=True)
    quantite_realisee = Column(Float, nullable=False, default=0.0)
    heures_estimees = Column(Float, nullable=True)
    heures_realisees = Column(Float, nullable=False, default=0.0)
    template_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations
    sous_taches = relationship(
        "TacheModel",
        backref="parent",
        remote_side=[id],
        foreign_keys=[parent_id],
        lazy="select",
    )

    def to_entity(self) -> "Tache":
        """Convertit le model en entite domain."""
        from ...domain.entities import Tache
        from ...domain.value_objects import StatutTache, UniteMesure

        unite = None
        if self.unite_mesure:
            unite = UniteMesure.from_string(self.unite_mesure)

        return Tache(
            id=self.id,
            chantier_id=self.chantier_id,
            titre=self.titre,
            description=self.description,
            parent_id=self.parent_id,
            ordre=self.ordre,
            statut=StatutTache.from_string(self.statut),
            date_echeance=self.date_echeance,
            unite_mesure=unite,
            quantite_estimee=self.quantite_estimee,
            quantite_realisee=self.quantite_realisee or 0.0,
            heures_estimees=self.heures_estimees,
            heures_realisees=self.heures_realisees or 0.0,
            template_id=self.template_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, tache: "Tache") -> "TacheModel":
        """Cree un model depuis une entite domain."""
        return cls(
            id=tache.id,
            chantier_id=tache.chantier_id,
            titre=tache.titre,
            description=tache.description,
            parent_id=tache.parent_id,
            ordre=tache.ordre,
            statut=tache.statut.value,
            date_echeance=tache.date_echeance,
            unite_mesure=tache.unite_mesure.value if tache.unite_mesure else None,
            quantite_estimee=tache.quantite_estimee,
            quantite_realisee=tache.quantite_realisee,
            heures_estimees=tache.heures_estimees,
            heures_realisees=tache.heures_realisees,
            template_id=tache.template_id,
            created_at=tache.created_at,
            updated_at=tache.updated_at,
        )
