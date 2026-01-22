"""SQLAlchemy Model pour les feuilles de taches."""

from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Date

from shared.infrastructure.database import Base
from ...domain.entities.feuille_tache import StatutValidation


class FeuilleTacheModel(Base):
    """
    Model SQLAlchemy pour les feuilles de taches.

    Represente la table 'feuilles_taches' en base de donnees.
    Selon CDC Section 13 - TAC-18: Feuilles de taches.
    """

    __tablename__ = "feuilles_taches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tache_id = Column(Integer, nullable=False, index=True)
    utilisateur_id = Column(Integer, nullable=False, index=True)
    chantier_id = Column(Integer, nullable=False, index=True)
    date_travail = Column(Date, nullable=False, index=True)
    heures_travaillees = Column(Float, nullable=False, default=0.0)
    quantite_realisee = Column(Float, nullable=False, default=0.0)
    commentaire = Column(Text, nullable=True)
    statut_validation = Column(
        String(20), nullable=False, default=StatutValidation.EN_ATTENTE.value
    )
    validateur_id = Column(Integer, nullable=True)
    date_validation = Column(DateTime, nullable=True)
    motif_rejet = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_entity(self) -> "FeuilleTache":
        """Convertit le model en entite domain."""
        from ...domain.entities import FeuilleTache
        from ...domain.entities.feuille_tache import StatutValidation

        return FeuilleTache(
            id=self.id,
            tache_id=self.tache_id,
            utilisateur_id=self.utilisateur_id,
            chantier_id=self.chantier_id,
            date_travail=self.date_travail,
            heures_travaillees=self.heures_travaillees or 0.0,
            quantite_realisee=self.quantite_realisee or 0.0,
            commentaire=self.commentaire,
            statut_validation=StatutValidation(self.statut_validation),
            validateur_id=self.validateur_id,
            date_validation=self.date_validation,
            motif_rejet=self.motif_rejet,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, feuille: "FeuilleTache") -> "FeuilleTacheModel":
        """Cree un model depuis une entite domain."""
        return cls(
            id=feuille.id,
            tache_id=feuille.tache_id,
            utilisateur_id=feuille.utilisateur_id,
            chantier_id=feuille.chantier_id,
            date_travail=feuille.date_travail,
            heures_travaillees=feuille.heures_travaillees,
            quantite_realisee=feuille.quantite_realisee,
            commentaire=feuille.commentaire,
            statut_validation=feuille.statut_validation.value,
            validateur_id=feuille.validateur_id,
            date_validation=feuille.date_validation,
            motif_rejet=feuille.motif_rejet,
            created_at=feuille.created_at,
            updated_at=feuille.updated_at,
        )
