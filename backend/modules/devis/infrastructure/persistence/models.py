"""SQLAlchemy models pour le module Devis.

DEV-01: Bibliotheque d'articles
DEV-03: Creation devis structure (lots, lignes)
DEV-05: Detail debourses avances
DEV-06: Gestion marges et coefficients
DEV-08: Variantes et revisions
DEV-11: Personnalisation presentation
DEV-14: Signature electronique client
DEV-15: Workflow statut devis
DEV-18: Historique modifications (journal)
DEV-22: Retenue de garantie
DEV-23: Attestation TVA reglementaire
DEV-24: Relances automatiques
DEV-25: Frais de chantier
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
    JSON,
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
    "converti",
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

# DEV-08: Types de version
TYPE_VERSIONS = (
    "originale",
    "revision",
    "variante",
)

# DEV-08: Types d'ecart pour comparatifs
TYPE_ECARTS = (
    "ajout",
    "suppression",
    "modification",
    "identique",
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
    "conversion",
    "ajout_lot",
    "modification_lot",
    "suppression_lot",
    "ajout_ligne",
    "modification_ligne",
    "suppression_ligne",
    "recalcul_totaux",
    "reordonnement_lots",
    # DEV-08: Actions de versioning
    "creation_revision",
    "creation_variante",
    "gel_version",
    "comparatif_genere",
    # DEV-23: Attestation TVA
    "generation_attestation_tva",
    # DEV-24: Relances automatiques
    "planification_relances",
    "envoi_relance",
    "annulation_relances",
    "modification_config_relances",
    # DEV-25: Frais de chantier
    "ajout_frais_chantier",
    "modification_frais_chantier",
    "suppression_frais_chantier",
    # DEV-11: Options de presentation
    "modification_options_presentation",
    # DEV-14: Signature electronique
    "signature_client",
    "revocation_signature",
    # DEV-16: Conversion en chantier
    "conversion_chantier",
)

# DEV-24: Types et statuts de relances
TYPES_RELANCE = (
    "email",
    "push",
    "email_push",
)

STATUTS_RELANCE = (
    "planifiee",
    "envoyee",
    "annulee",
)

# DEV-23: Natures d'immeuble pour attestation TVA
NATURES_IMMEUBLE = (
    "maison",
    "appartement",
    "immeuble",
)

# DEV-23: Natures de travaux pour attestation TVA
NATURES_TRAVAUX = (
    "amelioration",
    "entretien",
    "transformation",
)

# DEV-23: Types de CERFA
TYPES_CERFA = (
    "1300-SD",
    "1301-SD",
)

# DEV-25: Types de frais de chantier
TYPE_FRAIS_CHANTIER = (
    "compte_prorata",
    "frais_generaux",
    "installation_chantier",
    "autre",
)

# DEV-25: Modes de repartition des frais
MODE_REPARTITION_FRAIS = (
    "global",
    "prorata_lots",
)

# DEV-14: Types de signature electronique
TYPE_SIGNATURES = (
    "dessin_tactile",
    "upload_scan",
    "nom_prenom",
)

# DEV-14: Statuts de devis autorisant la signature
STATUTS_SIGNABLES = (
    "envoye",
    "vu",
    "en_negociation",
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
    composants_json = Column(JSON, nullable=True)
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

    # Marges par type de debourse supplementaires (DEV-06)
    marge_materiel_pct = Column(Numeric(5, 2), nullable=True)
    marge_deplacement_pct = Column(Numeric(5, 2), nullable=True)

    notes = Column(Text, nullable=True)
    conditions_generales = Column(Text, nullable=True)

    # Date de creation metier (distincte de created_at technique)
    date_creation = Column(Date, nullable=True)

    # References utilisateurs
    commercial_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    conducteur_id = Column(
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

    # Conversion devis -> chantier (DEV-16)
    converti_at = Column(DateTime, nullable=True)
    converti_by = Column(
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

    # DEV-08: Versioning
    devis_parent_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    numero_version = Column(Integer, nullable=False, default=1)
    type_version = Column(
        SQLEnum(*TYPE_VERSIONS, name="devis_type_version_enum", native_enum=False),
        nullable=False,
        default="originale",
    )
    label_variante = Column(String(50), nullable=True)
    version_commentaire = Column(Text, nullable=True)
    version_figee = Column(Boolean, nullable=False, default=False)
    version_figee_at = Column(DateTime, nullable=True)
    version_figee_par = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # DEV-11: Options de presentation
    options_presentation_json = Column(JSON, nullable=True)

    # DEV-24: Configuration des relances automatiques
    config_relances_json = Column(JSON, nullable=True)

    # DEV-16: Conversion en chantier
    converti_en_chantier_id = Column(Integer, nullable=True, index=True)

    __table_args__ = (
        Index("ix_devis_statut_created", "statut", "created_at"),
        Index("ix_devis_client_nom_statut", "client_nom", "statut"),
        Index("ix_devis_commercial_statut", "commercial_id", "statut"),
        Index("ix_devis_conducteur_statut", "conducteur_id", "statut"),
        Index("ix_devis_date_validite", "date_validite"),
        Index("ix_devis_parent_version", "devis_parent_id", "numero_version"),
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
            "retenue_garantie_pct IN (0, 5, 10)",
            name="check_devis_retenue_garantie_valeurs",
        ),
        CheckConstraint(
            "numero_version >= 1",
            name="check_devis_numero_version_positif",
        ),
        CheckConstraint(
            "(type_version != 'variante') OR (label_variante IS NOT NULL)",
            name="check_devis_label_variante_obligatoire",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Devis(id={self.id}, numero='{self.numero}', "
            f"client='{self.client_nom}', statut='{self.statut}', "
            f"type_version='{self.type_version}', v{self.numero_version})>"
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
    parent_id = Column(
        Integer,
        ForeignKey("lots_devis.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
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
    verrouille = Column(Boolean, nullable=False, default=False)
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
    # Champs specifiques MOE (DEV-05)
    metier = Column(String(100), nullable=True)
    taux_horaire = Column(Numeric(10, 2), nullable=True)
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
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
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


# ─────────────────────────────────────────────────────────────────────────────
# DEV-08: Comparatifs de devis
# ─────────────────────────────────────────────────────────────────────────────

class ComparatifDevisModel(DevisBase):
    """Modele SQLAlchemy pour les comparatifs globaux entre devis.

    DEV-08: Variantes et revisions - Ecarts globaux entre 2 versions.
    """

    __tablename__ = "comparatifs_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_source_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    devis_cible_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Ecarts globaux
    ecart_montant_ht = Column(Numeric(14, 2), nullable=False, default=0)
    ecart_montant_ttc = Column(Numeric(14, 2), nullable=False, default=0)
    ecart_marge_pct = Column(Numeric(5, 2), nullable=False, default=0)
    ecart_debourse_total = Column(Numeric(14, 2), nullable=False, default=0)

    # Compteurs
    nb_lignes_ajoutees = Column(Integer, nullable=False, default=0)
    nb_lignes_supprimees = Column(Integer, nullable=False, default=0)
    nb_lignes_modifiees = Column(Integer, nullable=False, default=0)
    nb_lignes_identiques = Column(Integer, nullable=False, default=0)

    # Metadonnees
    genere_par = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_comparatifs_devis_source_cible", "devis_source_id", "devis_cible_id"),
        UniqueConstraint(
            "devis_source_id", "devis_cible_id",
            name="uq_comparatifs_devis_source_cible",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ComparatifDevis(id={self.id}, "
            f"source={self.devis_source_id}, cible={self.devis_cible_id})>"
        )


class ComparatifLigneModel(DevisBase):
    """Modele SQLAlchemy pour les lignes de comparatif.

    DEV-08: Variantes et revisions - Detail ligne a ligne des ecarts.
    """

    __tablename__ = "comparatifs_devis_lignes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    comparatif_id = Column(
        Integer,
        ForeignKey("comparatifs_devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type_ecart = Column(
        SQLEnum(*TYPE_ECARTS, name="comparatif_type_ecart_enum", native_enum=False),
        nullable=False,
        index=True,
    )

    # Identification
    lot_titre = Column(String(300), nullable=False)
    designation = Column(String(500), nullable=False)
    article_id = Column(Integer, nullable=True)

    # Valeurs source
    source_quantite = Column(Numeric(12, 4), nullable=True)
    source_prix_unitaire = Column(Numeric(12, 4), nullable=True)
    source_montant_ht = Column(Numeric(14, 2), nullable=True)
    source_debourse_sec = Column(Numeric(14, 2), nullable=True)

    # Valeurs cible
    cible_quantite = Column(Numeric(12, 4), nullable=True)
    cible_prix_unitaire = Column(Numeric(12, 4), nullable=True)
    cible_montant_ht = Column(Numeric(14, 2), nullable=True)
    cible_debourse_sec = Column(Numeric(14, 2), nullable=True)

    # Ecarts calcules
    ecart_quantite = Column(Numeric(12, 4), nullable=True)
    ecart_prix_unitaire = Column(Numeric(12, 4), nullable=True)
    ecart_montant_ht = Column(Numeric(14, 2), nullable=True)
    ecart_debourse_sec = Column(Numeric(14, 2), nullable=True)

    __table_args__ = (
        Index("ix_comparatifs_lignes_comparatif_type", "comparatif_id", "type_ecart"),
    )

    def __repr__(self) -> str:
        return (
            f"<ComparatifLigne(id={self.id}, comparatif_id={self.comparatif_id}, "
            f"type='{self.type_ecart}', designation='{self.designation}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-23: Attestations TVA
# ─────────────────────────────────────────────────────────────────────────────

class AttestationTVAModel(DevisBase):
    """Modele SQLAlchemy pour les attestations TVA reglementaires.

    DEV-23: Generation attestation TVA selon taux applique.
    Un devis avec TVA reduite (5.5% ou 10%) necessite une attestation
    CERFA (1300-SD pour travaux simples, 1301-SD pour travaux lourds).
    """

    __tablename__ = "attestations_tva"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    type_cerfa = Column(
        SQLEnum(*TYPES_CERFA, name="attestation_tva_type_cerfa_enum", native_enum=False),
        nullable=False,
    )
    taux_tva = Column(Numeric(5, 2), nullable=False)

    # Informations client / maitre d'ouvrage
    nom_client = Column(String(200), nullable=False)
    adresse_client = Column(Text, nullable=False)
    telephone_client = Column(String(30), nullable=True)

    # Informations immeuble
    adresse_immeuble = Column(Text, nullable=False)
    nature_immeuble = Column(
        SQLEnum(*NATURES_IMMEUBLE, name="attestation_tva_nature_immeuble_enum", native_enum=False),
        nullable=False,
        default="maison",
    )
    date_construction_plus_2ans = Column(Boolean, nullable=False, default=True)

    # Nature des travaux
    description_travaux = Column(Text, nullable=False)
    nature_travaux = Column(
        SQLEnum(*NATURES_TRAVAUX, name="attestation_tva_nature_travaux_enum", native_enum=False),
        nullable=False,
        default="amelioration",
    )

    # Attestation
    atteste_par = Column(String(200), nullable=False, default="")
    date_attestation = Column(DateTime, nullable=True)
    generee_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "taux_tva IN (5.5, 10.0)",
            name="check_attestation_tva_taux_reduit",
        ),
        CheckConstraint(
            "date_construction_plus_2ans = true",
            name="check_attestation_tva_immeuble_plus_2ans",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AttestationTVA(id={self.id}, devis_id={self.devis_id}, "
            f"cerfa='{self.type_cerfa}', taux={self.taux_tva}%)>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-25: Frais de chantier
# ─────────────────────────────────────────────────────────────────────────────

class FraisChantierDevisModel(DevisBase):
    """Modele SQLAlchemy pour les frais de chantier.

    DEV-25: Compte prorata, frais generaux, installations de chantier
    avec repartition globale ou par lot.
    """

    __tablename__ = "frais_chantier_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type_frais = Column(
        SQLEnum(
            *TYPE_FRAIS_CHANTIER,
            name="frais_chantier_type_enum",
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )
    libelle = Column(String(300), nullable=False)
    montant_ht = Column(Numeric(14, 2), nullable=False, default=0)
    mode_repartition = Column(
        SQLEnum(
            *MODE_REPARTITION_FRAIS,
            name="frais_chantier_repartition_enum",
            native_enum=False,
        ),
        nullable=False,
        default="global",
    )
    taux_tva = Column(Numeric(5, 2), nullable=False, default=20.0)
    ordre = Column(Integer, nullable=False, default=0)
    lot_devis_id = Column(
        Integer,
        ForeignKey("lots_devis.id", ondelete="SET NULL"),
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
        Index("ix_frais_chantier_devis_ordre", "devis_id", "ordre"),
        Index("ix_frais_chantier_devis_type", "devis_id", "type_frais"),
        CheckConstraint(
            "montant_ht >= 0",
            name="check_frais_chantier_montant_positif",
        ),
        CheckConstraint(
            "taux_tva >= 0 AND taux_tva <= 100",
            name="check_frais_chantier_tva_range",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<FraisChantierDevis(id={self.id}, devis_id={self.devis_id}, "
            f"type='{self.type_frais}', montant={self.montant_ht})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-14: Signatures electroniques devis
# ─────────────────────────────────────────────────────────────────────────────

class SignatureDevisModel(DevisBase):
    """Modele SQLAlchemy pour les signatures electroniques de devis.

    DEV-14: Signature electronique client.
    Signature simple conforme eIDAS avec tracabilite complete
    (horodatage, IP, user-agent, hash document).

    Contraintes metier :
    - Un devis ne peut etre signe que s'il est en statut 'envoye', 'vu' ou 'en_negociation'.
    - Une seule signature active par devis (UNIQUE sur devis_id).
    - Hash SHA-512 du document PDF pour preuve d'integrite.
    """

    __tablename__ = "signatures_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Type de signature
    type_signature = Column(
        SQLEnum(
            *TYPE_SIGNATURES,
            name="signature_devis_type_enum",
            native_enum=False,
        ),
        nullable=False,
    )

    # Identite du signataire
    signataire_nom = Column(String(200), nullable=False)
    signataire_email = Column(String(255), nullable=False)
    signataire_telephone = Column(String(30), nullable=True)

    # Donnees de signature (base64 PNG pour dessin, path pour scan, texte pour nom_prenom)
    signature_data = Column(Text, nullable=False)

    # Tracabilite eIDAS (signature simple)
    ip_adresse = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=False)
    horodatage = Column(DateTime, nullable=False)

    # Integrite document
    hash_document = Column(String(128), nullable=False)

    # Etat de la signature
    valide = Column(Boolean, nullable=False, default=True, index=True)

    # Revocation
    revoquee_at = Column(DateTime, nullable=True)
    revoquee_par = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    motif_revocation = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        # Index composite pour rechercher les signatures valides par devis
        Index("ix_signatures_devis_devis_valide", "devis_id", "valide"),
        # Index sur horodatage pour requetes chronologiques / audit
        Index("ix_signatures_devis_horodatage", "horodatage"),
        # Hash SHA-512 = 128 caracteres hexadecimaux
        CheckConstraint(
            "length(hash_document) = 128",
            name="check_signatures_devis_hash_sha512",
        ),
        # IP obligatoire et non vide
        CheckConstraint(
            "length(ip_adresse) >= 7",
            name="check_signatures_devis_ip_non_vide",
        ),
        # Coherence revocation : si revoquee_at renseigne, motif obligatoire
        CheckConstraint(
            "(revoquee_at IS NULL) OR (motif_revocation IS NOT NULL AND motif_revocation != '')",
            name="check_signatures_devis_revocation_coherente",
        ),
        # Si revoquee, valide doit etre FALSE
        CheckConstraint(
            "(revoquee_at IS NULL) OR (valide = false)",
            name="check_signatures_devis_revoquee_invalide",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<SignatureDevis(id={self.id}, devis_id={self.devis_id}, "
            f"type='{self.type_signature}', signataire='{self.signataire_nom}', "
            f"valide={self.valide})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEV-24: Relances automatiques de devis
# ─────────────────────────────────────────────────────────────────────────────

class RelanceDevisModel(DevisBase):
    """Modele SQLAlchemy pour les relances automatiques de devis.

    DEV-24: Relances automatiques - Notifications push/email
    si delai de reponse depasse (configurable : 7j, 15j, 30j).
    """

    __tablename__ = "relances_devis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    devis_id = Column(
        Integer,
        ForeignKey("devis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    numero_relance = Column(Integer, nullable=False)
    type_relance = Column(
        SQLEnum(
            *TYPES_RELANCE,
            name="relance_devis_type_enum",
            native_enum=False,
        ),
        nullable=False,
        default="email",
    )
    date_envoi = Column(DateTime, nullable=True)
    date_prevue = Column(DateTime, nullable=False)
    statut = Column(
        SQLEnum(
            *STATUTS_RELANCE,
            name="relance_devis_statut_enum",
            native_enum=False,
        ),
        nullable=False,
        default="planifiee",
        index=True,
    )
    message_personnalise = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_relances_devis_devis_statut", "devis_id", "statut"),
        Index("ix_relances_devis_statut_date_prevue", "statut", "date_prevue"),
        Index("ix_relances_devis_devis_numero", "devis_id", "numero_relance"),
        CheckConstraint(
            "numero_relance >= 1",
            name="check_relances_devis_numero_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<RelanceDevis(id={self.id}, devis_id={self.devis_id}, "
            f"numero={self.numero_relance}, statut='{self.statut}')>"
        )
