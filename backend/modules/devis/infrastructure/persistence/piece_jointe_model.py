"""Modele SQLAlchemy pour les pieces jointes de devis.

DEV-07: Insertion multimedia.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)

from shared.infrastructure.database_base import Base


class PieceJointeDevisModel(Base):
    """Table des pieces jointes associees aux devis."""

    __tablename__ = "pieces_jointes_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_id = Column(Integer, ForeignKey("devis.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    lot_devis_id = Column(Integer, ForeignKey("lots_devis.id", ondelete="SET NULL"), nullable=True)
    ligne_devis_id = Column(Integer, ForeignKey("lignes_devis.id", ondelete="SET NULL"), nullable=True)
    visible_client = Column(Boolean, nullable=False, default=True)
    ordre = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)

    # Champs denormalises depuis le document GED
    nom_fichier = Column(String(255), nullable=True)
    type_fichier = Column(String(50), nullable=True)
    taille_octets = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint("devis_id", "document_id", name="uq_devis_document"),
        Index("ix_pieces_jointes_devis_id", "devis_id"),
        Index("ix_pieces_jointes_devis_ordre", "devis_id", "ordre"),
    )

    def __repr__(self) -> str:
        return (
            f"<PieceJointeDevis(id={self.id}, devis_id={self.devis_id}, "
            f"document_id={self.document_id}, nom='{self.nom_fichier}')>"
        )
