"""Modèle SQLAlchemy pour User."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import declarative_base

from ...domain.value_objects import Role

Base = declarative_base()


class UserModel(Base):
    """
    Modèle SQLAlchemy représentant un utilisateur en base.

    Note:
        Ce modèle est dans Infrastructure car il dépend de SQLAlchemy.
        Il est mappé vers/depuis l'entité User du Domain.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False, default=Role.EMPLOYE.value)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"
