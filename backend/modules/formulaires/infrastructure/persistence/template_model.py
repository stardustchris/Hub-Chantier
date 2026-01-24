"""Modele SQLAlchemy pour les templates de formulaire."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from shared.infrastructure.database_base import Base


class ChampTemplateModel(Base):
    """Modele SQLAlchemy pour un champ de template."""

    __tablename__ = "champs_template"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates_formulaire.id", ondelete="CASCADE"))
    nom: Mapped[str] = mapped_column(String(100))
    label: Mapped[str] = mapped_column(String(200))
    type_champ: Mapped[str] = mapped_column(String(50))
    obligatoire: Mapped[bool] = mapped_column(default=False)
    ordre: Mapped[int] = mapped_column(default=0)
    placeholder: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    valeur_defaut: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    validation_regex: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    min_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(nullable=True)


class TemplateFormulaireModel(Base):
    """Modele SQLAlchemy pour un template de formulaire."""

    __tablename__ = "templates_formulaire"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categorie: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relation avec les champs
    champs: Mapped[List[ChampTemplateModel]] = relationship(
        "ChampTemplateModel",
        cascade="all, delete-orphan",
        order_by="ChampTemplateModel.ordre",
    )
