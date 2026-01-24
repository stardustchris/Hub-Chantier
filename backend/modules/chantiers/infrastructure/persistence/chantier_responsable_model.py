"""Tables de jointure pour les responsables de chantier.

Ces tables permettent des requetes SQL efficaces (evitant les N+1)
pour trouver les chantiers d'un conducteur ou chef de chantier.
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Index
from shared.infrastructure.database_base import Base


class ChantierConducteurModel(Base):
    """
    Table de jointure Chantier <-> Conducteur.

    Permet de recuperer efficacement les chantiers d'un conducteur
    via une requete SQL avec JOIN au lieu de charger tous les chantiers.

    Attributes:
        chantier_id: FK vers le chantier.
        user_id: FK vers l'utilisateur (conducteur).
    """

    __tablename__ = "chantier_conducteurs"
    __table_args__ = (
        UniqueConstraint("chantier_id", "user_id", name="uq_chantier_conducteur"),
        Index("ix_chantier_conducteurs_user_id", "user_id"),
        Index("ix_chantier_conducteurs_chantier_id", "chantier_id"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )


class ChantierChefModel(Base):
    """
    Table de jointure Chantier <-> Chef de chantier.

    Permet de recuperer efficacement les chantiers d'un chef de chantier
    via une requete SQL avec JOIN au lieu de charger tous les chantiers.

    Attributes:
        chantier_id: FK vers le chantier.
        user_id: FK vers l'utilisateur (chef de chantier).
    """

    __tablename__ = "chantier_chefs"
    __table_args__ = (
        UniqueConstraint("chantier_id", "user_id", name="uq_chantier_chef"),
        Index("ix_chantier_chefs_user_id", "user_id"),
        Index("ix_chantier_chefs_chantier_id", "chantier_id"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
