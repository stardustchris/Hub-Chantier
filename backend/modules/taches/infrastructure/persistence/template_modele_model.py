"""SQLAlchemy Models pour les templates de modeles."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .tache_model import Base


class TemplateModeleModel(Base):
    """
    Model SQLAlchemy pour les templates de taches.

    Represente la table 'templates_modeles' en base de donnees.
    Selon CDC Section 13 - TAC-04: Bibliotheque de modeles.
    """

    __tablename__ = "templates_modeles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    categorie = Column(String(100), nullable=True, index=True)
    unite_mesure = Column(String(20), nullable=True)
    heures_estimees_defaut = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relations
    sous_taches = relationship(
        "SousTacheModeleModel",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="SousTacheModeleModel.ordre",
    )

    def to_entity(self) -> "TemplateModele":
        """Convertit le model en entite domain."""
        from ...domain.entities import TemplateModele, SousTacheModele
        from ...domain.value_objects import UniteMesure

        unite = None
        if self.unite_mesure:
            unite = UniteMesure.from_string(self.unite_mesure)

        template = TemplateModele(
            id=self.id,
            nom=self.nom,
            description=self.description,
            categorie=self.categorie,
            unite_mesure=unite,
            heures_estimees_defaut=self.heures_estimees_defaut,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

        # Convertir les sous-taches
        for st_model in self.sous_taches:
            st_unite = None
            if st_model.unite_mesure:
                st_unite = UniteMesure.from_string(st_model.unite_mesure)

            sous_tache = SousTacheModele(
                titre=st_model.titre,
                description=st_model.description,
                ordre=st_model.ordre,
                unite_mesure=st_unite,
                heures_estimees_defaut=st_model.heures_estimees_defaut,
            )
            template.sous_taches.append(sous_tache)

        return template

    @classmethod
    def from_entity(cls, template: "TemplateModele") -> "TemplateModeleModel":
        """Cree un model depuis une entite domain."""
        model = cls(
            id=template.id,
            nom=template.nom,
            description=template.description,
            categorie=template.categorie,
            unite_mesure=template.unite_mesure.value if template.unite_mesure else None,
            heures_estimees_defaut=template.heures_estimees_defaut,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

        # Convertir les sous-taches
        for i, st in enumerate(template.sous_taches):
            st_model = SousTacheModeleModel(
                titre=st.titre,
                description=st.description,
                ordre=st.ordre if st.ordre else i,
                unite_mesure=st.unite_mesure.value if st.unite_mesure else None,
                heures_estimees_defaut=st.heures_estimees_defaut,
            )
            model.sous_taches.append(st_model)

        return model


class SousTacheModeleModel(Base):
    """
    Model SQLAlchemy pour les sous-taches de modeles.

    Represente la table 'sous_taches_modeles' en base de donnees.
    """

    __tablename__ = "sous_taches_modeles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("templates_modeles.id"), nullable=False)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ordre = Column(Integer, nullable=False, default=0)
    unite_mesure = Column(String(20), nullable=True)
    heures_estimees_defaut = Column(Float, nullable=True)

    # Relations
    template = relationship("TemplateModeleModel", back_populates="sous_taches")
