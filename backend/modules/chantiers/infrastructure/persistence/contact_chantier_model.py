"""Modèle SQLAlchemy pour ContactChantier."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base


class ContactChantierModel(Base):
    """
    Modèle SQLAlchemy représentant un contact sur un chantier.

    Permet de stocker plusieurs contacts par chantier avec leur profession.
    """

    __tablename__ = "contacts_chantier"
    __table_args__ = {"extend_existing": True}

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Référence au chantier
    chantier_id = Column(Integer, ForeignKey("chantiers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Informations du contact
    nom = Column(String(200), nullable=False)
    telephone = Column(String(20), nullable=False)
    profession = Column(String(100), nullable=True)
    ordre = Column(Integer, nullable=False, default=0)  # Ordre d'affichage

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relation avec le chantier
    chantier = relationship(
        "modules.chantiers.infrastructure.persistence.chantier_model.ChantierModel",
        back_populates="contacts"
    )

    def __repr__(self) -> str:
        return f"<ContactChantierModel(id={self.id}, nom={self.nom}, profession={self.profession})>"
