"""Modele SQLAlchemy pour les formulaires remplis."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .template_model import Base


class PhotoFormulaireModel(Base):
    """Modele SQLAlchemy pour une photo de formulaire."""

    __tablename__ = "photos_formulaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    formulaire_id: Mapped[int] = mapped_column(ForeignKey("formulaires_remplis.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    nom_fichier: Mapped[str] = mapped_column(String(200))
    champ_nom: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)


class ChampRempliModel(Base):
    """Modele SQLAlchemy pour un champ rempli."""

    __tablename__ = "champs_remplis"

    id: Mapped[int] = mapped_column(primary_key=True)
    formulaire_id: Mapped[int] = mapped_column(ForeignKey("formulaires_remplis.id", ondelete="CASCADE"))
    nom: Mapped[str] = mapped_column(String(100))
    type_champ: Mapped[str] = mapped_column(String(50))
    valeur: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class FormulaireRempliModel(Base):
    """Modele SQLAlchemy pour un formulaire rempli."""

    __tablename__ = "formulaires_remplis"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates_formulaire.id", ondelete="SET NULL"), nullable=True)
    chantier_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    statut: Mapped[str] = mapped_column(String(50), default="brouillon")

    # Signature (FOR-05)
    signature_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    signature_nom: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    signature_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Localisation (FOR-03)
    localisation_latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    localisation_longitude: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Soumission (FOR-07)
    soumis_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Validation
    valide_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    valide_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Historique (FOR-08)
    version: Mapped[int] = mapped_column(default=1)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("formulaires_remplis.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relations
    champs: Mapped[List[ChampRempliModel]] = relationship(
        "ChampRempliModel",
        cascade="all, delete-orphan",
    )
    photos: Mapped[List[PhotoFormulaireModel]] = relationship(
        "PhotoFormulaireModel",
        cascade="all, delete-orphan",
    )
