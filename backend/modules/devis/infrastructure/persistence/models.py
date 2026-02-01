"""SQLAlchemy models pour le module Devis.

DEV-01: Bibliotheque d'articles
DEV-03: Creation devis structure (lots, lignes)
DEV-05: Detail debourses avances
DEV-06: Gestion marges et coefficients
DEV-15: Workflow statut devis
DEV-18: Historique modifications (journal)
DEV-22: Retenue de garantie
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    Text,
    Index,
    Enum as SQLEnum,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)

from shared.infrastructure.database_base import Base


# Alias pour compatibilite
DevisBase = Base


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

DEVIS_STATUTS = (
    "brouillon",
    "en_validation",
    "envoye",
    "vu",
    "en_negociation",
    "accepte",
    "refuse",
    "perdu",
    "expire",
)

CATEGORIE_ARTICLES = (
    "gros_oeuvre",
    "second_oeuvre",
    "electricite",
    "plomberie",
    "chauffage_clim",
    "menuiserie",
    "peinture",
    "couverture",
    "terrassement",
    "vrd",
    "charpente",
    "isolation",
    "carrelage",
    "main_oeuvre",
    "materiel",
    "divers",
)

UNITE_ARTICLES = (
    "m2",
    "m3",
    "ml",
    "u",
    "kg",
    "t",
    "heure",
    "jour",
    "forfait",
    "l",
    "ens",
)

TYPE_DEBOURSES = (
    "moe",
    "materiaux",
    "materiel",
    "sous_traitance",
    "deplacement",
)

JOURNAL_DEVIS_ACTIONS = (
    "creation",
    "modification",
    "suppression",
    "soumission",
    "validation",
    "envoi",
    "acceptation",
    "refus",
    "perdu",
    "ajout_lot",
    "modification_lot",
    "suppression_lot",
    "ajout_ligne",
    "modification_ligne",
    "suppression_ligne",
    "recalcul_totaux",
    "reordonnement_lots",
)


# ─────────────────────────────────────────────────────────────────────────────
# DEV-01: Articles (bibliotheque de prix)
# ─────────────────────────────────────────────────────────────────────────────

class ArticleDevisModel(DevisBase):
    """Modele SQLAlchemy pour les articles de la bibliotheque de prix.

    DEV-01: Bibliotheque d'articles et bordereaux.
    """

    __tablename__ = "articles_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=True, unique=True, index=True)
    designation = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    unite = Column(
        SQLEnum(*UNITE_ARTICLES, name="article_devis_unite_enum", native_enum=False),
        nullable=False,
        default="u",
    )
    prix_unitaire_ht = Column(Numeric(12, 4), nullable=False, default=0)
    categorie = Column(
        SQLEnum(*CATEGORIE_ARTICLES, name="article_devis_categorie_enum", native_enum=False),
        nullable=True,
        index=True,
    )
    taux_tva = Column(Numeric(5, 2), nullable=False, default=20.0)
    actif = Column(Boolean, nullable=False, default=True, index=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_articles_devis_categorie_actif", "categorie", "actif"),
        Index("ix_articles_devis_designation", "designation"),
        CheckConstraint(
            "prix_unitaire_ht >= 0",
            name="check_articles_devis_prix_positif",
        ),
        CheckConstraint(
            "taux_tva >= 0 AND taux_tva <= 100",
            name="check_articles_devis_tva_range",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ArticleDevis(id={self.id}, code='{self.code}', "
            f"designation='{self.designation}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-03: Devis (document principal)
# ─────────────────────────────────────────────────────────────────────────────

class DevisModel(DevisBase):
    """Modele SQLAlchemy pour les devis.

    DEV-03: Creation devis structure.
    DEV-06: Gestion marges et coefficients.
    DEV-15: Workflow statut devis.
    DEV-22: Retenue de garantie.
    """

    __tablename__ = "devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(30), nullable=False, unique=True, index=True)
    client_nom = Column(String(200), nullable=False, index=True)
    client_adresse = Column(Text, nullable=True)
    client_telephone = Column(String(30), nullable=True)
    client_email = Column(String(255), nullable=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    objet = Column(String(500), nullable=True)
    date_validite = Column(Date, nullable=True)
    statut = Column(
        SQLEnum(*DEVIS_STATUTS, name="devis_statut_enum", native_enum=False),
        nullable=False,
        default="brouillon",
        index=True,
    )

    # Montants calcules
    total_ht = Column(Numeric(14, 2), nullable=False, default=0)
    total_ttc = Column(Numeric(14, 2), nullable=False, default=0)
    debourse_sec_total = Column(Numeric(14, 2), nullable=False, default=0)

    # Parametres de marge (DEV-06)
    marge_globale_pct = Column(Numeric(5, 2), nullable=False, default=15.0)
    marge_moe_pct = Column(Numeric(5, 2), nullable=True)
    marge_materiaux_pct = Column(Numeric(5, 2), nullable=True)
    marge_sous_traitance_pct = Column(Numeric(5, 2), nullable=True)
    coeff_frais_generaux = Column(Numeric(5, 4), nullable=False, default=0.12)
    taux_tva_defaut = Column(Numeric(5, 2), nullable=False, default=20.0)

    # Retenue de garantie (DEV-22)
    retenue_garantie_pct = Column(Numeric(5, 2), nullable=False, default=0)

    notes = Column(Text, nullable=True)

    # References utilisateurs
    commercial_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_devis_statut_created", "statut", "created_at"),
        Index("ix_devis_client_nom_statut", "client_nom", "statut"),
        Index("ix_devis_commercial_statut", "commercial_id", "statut"),
        CheckConstraint(
            "total_ht >= 0",
            name="check_devis_total_ht_positif",
        ),
        CheckConstraint(
            "total_ttc >= 0",
            name="check_devis_total_ttc_positif",
        ),
        CheckConstraint(
            "marge_globale_pct >= 0",
            name="check_devis_marge_globale_positive",
        ),
        CheckConstraint(
            "coeff_frais_generaux >= 0",
            name="check_devis_coeff_fg_positif",
        ),
        CheckConstraint(
            "taux_tva_defaut >= 0 AND taux_tva_defaut <= 100",
            name="check_devis_tva_range",
        ),
        CheckConstraint(
            "retenue_garantie_pct >= 0 AND retenue_garantie_pct <= 100",
            name="check_devis_retenue_garantie_range",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Devis(id={self.id}, numero='{self.numero}', "
            f"client='{self.client_nom}', statut='{self.statut}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-03: Lots de devis (arborescence par lots/chapitres)
# ─────────────────────────────────────────────────────────────────────────────

class LotDevisModel(DevisBase):
    """Modele SQLAlchemy pour les lots de devis.

    DEV-03: Arborescence par lots/chapitres.
    DEV-06: Marge par lot.
    """

    __tablename__ = "lots_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    titre = Column(String(300), nullable=False)
    numero = Column(String(20), nullable=True)
    ordre = Column(Integer, nullable=False, default=0)
    marge_lot_pct = Column(Numeric(5, 2), nullable=True)

    # Montants calcules
    total_ht = Column(Numeric(14, 2), nullable=False, default=0)
    total_ttc = Column(Numeric(14, 2), nullable=False, default=0)
    debourse_sec = Column(Numeric(14, 2), nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_lots_devis_devis_ordre", "devis_id", "ordre"),
        CheckConstraint(
            "total_ht >= 0",
            name="check_lots_devis_total_ht_positif",
        ),
        CheckConstraint(
            "marge_lot_pct IS NULL OR marge_lot_pct >= 0",
            name="check_lots_devis_marge_positive",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<LotDevis(id={self.id}, devis_id={self.devis_id}, "
            f"titre='{self.titre}', ordre={self.ordre})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-03 + DEV-05: Lignes de devis
# ─────────────────────────────────────────────────────────────────────────────

class LigneDevisModel(DevisBase):
    """Modele SQLAlchemy pour les lignes de devis.

    DEV-03: Lignes avec quantites et prix.
    DEV-05: Debourses detailles.
    DEV-06: Marge par ligne.
    """

    __tablename__ = "lignes_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_devis_id = Column(
        Integer,
        ForeignKey("lots_devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    article_id = Column(
        Integer,
        ForeignKey("articles_devis.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    designation = Column(String(500), nullable=False)
    unite = Column(
        SQLEnum(*UNITE_ARTICLES, name="ligne_devis_unite_enum", native_enum=False),
        nullable=False,
        default="u",
    )
    quantite = Column(Numeric(12, 4), nullable=False, default=0)
    prix_unitaire_ht = Column(Numeric(12, 4), nullable=False, default=0)
    taux_tva = Column(Numeric(5, 2), nullable=False, default=20.0)
    ordre = Column(Integer, nullable=False, default=0)
    marge_ligne_pct = Column(Numeric(5, 2), nullable=True)

    # Montants calcules
    montant_ht = Column(Numeric(14, 2), nullable=False, default=0)
    montant_ttc = Column(Numeric(14, 2), nullable=False, default=0)
    debourse_sec = Column(Numeric(14, 2), nullable=False, default=0)
    prix_revient = Column(Numeric(14, 2), nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_lignes_devis_lot_ordre", "lot_devis_id", "ordre"),
        CheckConstraint(
            "quantite >= 0",
            name="check_lignes_devis_quantite_positive",
        ),
        CheckConstraint(
            "prix_unitaire_ht >= 0",
            name="check_lignes_devis_prix_positif",
        ),
        CheckConstraint(
            "taux_tva >= 0 AND taux_tva <= 100",
            name="check_lignes_devis_tva_range",
        ),
        CheckConstraint(
            "marge_ligne_pct IS NULL OR marge_ligne_pct >= 0",
            name="check_lignes_devis_marge_positive",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<LigneDevis(id={self.id}, lot_devis_id={self.lot_devis_id}, "
            f"designation='{self.designation}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-05: Debourses detailles
# ─────────────────────────────────────────────────────────────────────────────

class DebourseDetailModel(DevisBase):
    """Modele SQLAlchemy pour les debourses detailles.

    DEV-05: Detail debourses avances - Breakdown par ligne.
    """

    __tablename__ = "debourses_detail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ligne_devis_id = Column(
        Integer,
        ForeignKey("lignes_devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type_debourse = Column(
        SQLEnum(*TYPE_DEBOURSES, name="debourse_type_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    designation = Column(String(300), nullable=False)
    quantite = Column(Numeric(12, 4), nullable=False, default=0)
    prix_unitaire = Column(Numeric(12, 4), nullable=False, default=0)
    unite = Column(
        SQLEnum(*UNITE_ARTICLES, name="debourse_unite_enum", native_enum=False),
        nullable=False,
        default="u",
    )
    montant = Column(Numeric(14, 2), nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_debourses_detail_ligne_type", "ligne_devis_id", "type_debourse"),
        CheckConstraint(
            "quantite >= 0",
            name="check_debourses_detail_quantite_positive",
        ),
        CheckConstraint(
            "prix_unitaire >= 0",
            name="check_debourses_detail_prix_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<DebourseDetail(id={self.id}, ligne_devis_id={self.ligne_devis_id}, "
            f"type='{self.type_debourse}', montant={self.montant})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-18: Journal devis (historique modifications)
# ─────────────────────────────────────────────────────────────────────────────

class JournalDevisModel(DevisBase):
    """Modele SQLAlchemy pour le journal d'audit des devis.

    DEV-18: Historique modifications - Table append-only.
    """

    __tablename__ = "journal_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action = Column(String(50), nullable=False, index=True)
    details = Column(Text, nullable=True)
    auteur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Timestamp (append-only, pas de updated_at)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_journal_devis_devis_created", "devis_id", "created_at"),
        Index("ix_journal_devis_auteur_created", "auteur_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<JournalDevis(id={self.id}, devis_id={self.devis_id}, "
            f"action='{self.action}')>"
        )
