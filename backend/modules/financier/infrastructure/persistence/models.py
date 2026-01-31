"""SQLAlchemy models pour le module Financier.

FIN-01: Budget chantier
FIN-02: Lots budgetaires (decomposition)
FIN-05: Achats et commandes
FIN-06: Workflow validation achats
FIN-11: Suivi depenses
FIN-14: Gestion fournisseurs
FIN-15: Journal financier (audit trail)
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
    text,
)

from shared.infrastructure.database_base import Base


# Alias pour compatibilite
FinancierBase = Base


# ─────────────────────────────────────────────────────────────────────────────
# Enums (definis localement, a migrer dans domain/value_objects plus tard)
# ─────────────────────────────────────────────────────────────────────────────

FOURNISSEUR_TYPES = (
    "negoce_materiaux",
    "loueur",
    "sous_traitant",
    "service",
)

ACHAT_TYPES = (
    "materiau",
    "materiel",
    "sous_traitance",
    "service",
)

ACHAT_STATUTS = (
    "demande",
    "valide",
    "refuse",
    "commande",
    "livre",
    "facture",
)

JOURNAL_ACTIONS = (
    "creation",
    "modification",
    "suppression",
    "validation",
    "refus",
)

JOURNAL_ENTITE_TYPES = (
    "budget",
    "lot_budgetaire",
    "achat",
    "fournisseur",
)


# ─────────────────────────────────────────────────────────────────────────────
# FIN-14: Fournisseurs
# ─────────────────────────────────────────────────────────────────────────────

class FournisseurModel(FinancierBase):
    """Modele SQLAlchemy pour les fournisseurs.

    FIN-14: Gestion fournisseurs - raison sociale, SIRET, contacts,
    conditions de paiement.
    """

    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raison_sociale = Column(String(200), nullable=False, index=True)
    type = Column(
        SQLEnum(*FOURNISSEUR_TYPES, name="fournisseur_type_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    siret = Column(String(14), nullable=True, unique=True, index=True)
    adresse = Column(Text, nullable=True)
    contact_principal = Column(String(200), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    conditions_paiement = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
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
        Index("ix_fournisseurs_type_actif", "type", "actif"),
        Index("ix_fournisseurs_raison_sociale_actif", "raison_sociale", "actif"),
        CheckConstraint(
            "siret IS NULL OR length(siret) = 14",
            name="check_fournisseurs_siret_length",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Fournisseur(id={self.id}, raison_sociale='{self.raison_sociale}', "
            f"type='{self.type}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-01: Budget chantier
# ─────────────────────────────────────────────────────────────────────────────

class BudgetModel(FinancierBase):
    """Modele SQLAlchemy pour les budgets chantier.

    FIN-01: Budget chantier - enveloppe budgetaire globale par chantier.
    Un budget unique par chantier (contrainte unique sur chantier_id).
    """

    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    montant_initial_ht = Column(Numeric(12, 2), nullable=False, default=0)
    montant_avenants_ht = Column(Numeric(12, 2), nullable=False, default=0)
    retenue_garantie_pct = Column(Numeric(5, 2), nullable=False, default=5.0)
    seuil_alerte_pct = Column(Numeric(5, 2), nullable=False, default=110.0)
    seuil_validation_achat = Column(Numeric(10, 2), nullable=False, default=5000.0)
    notes = Column(Text, nullable=True)

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
        CheckConstraint(
            "montant_initial_ht >= 0",
            name="check_budgets_montant_initial_positif",
        ),
        CheckConstraint(
            "retenue_garantie_pct >= 0 AND retenue_garantie_pct <= 100",
            name="check_budgets_retenue_garantie_range",
        ),
        CheckConstraint(
            "seuil_alerte_pct >= 0",
            name="check_budgets_seuil_alerte_positif",
        ),
        CheckConstraint(
            "seuil_validation_achat >= 0",
            name="check_budgets_seuil_validation_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Budget(id={self.id}, chantier_id={self.chantier_id}, "
            f"montant_initial_ht={self.montant_initial_ht})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-02: Lots budgetaires
# ─────────────────────────────────────────────────────────────────────────────

class LotBudgetaireModel(FinancierBase):
    """Modele SQLAlchemy pour les lots budgetaires.

    FIN-02: Decomposition du budget en lots avec arborescence (parent_lot_id).
    Chaque lot a un code unique par budget.
    """

    __tablename__ = "lots_budgetaires"

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(
        Integer,
        ForeignKey("budgets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code_lot = Column(String(20), nullable=False)
    libelle = Column(String(200), nullable=False)
    unite = Column(String(20), nullable=True)
    quantite_prevue = Column(Numeric(12, 3), nullable=False, default=0)
    prix_unitaire_ht = Column(Numeric(12, 2), nullable=False, default=0)
    parent_lot_id = Column(
        Integer,
        ForeignKey("lots_budgetaires.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ordre = Column(Integer, nullable=False, default=0)

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
        UniqueConstraint("budget_id", "code_lot", name="uq_lots_budgetaires_budget_code"),
        Index("ix_lots_budgetaires_budget_ordre", "budget_id", "ordre"),
        Index("ix_lots_budgetaires_parent", "parent_lot_id"),
        CheckConstraint(
            "quantite_prevue >= 0",
            name="check_lots_budgetaires_quantite_positive",
        ),
        CheckConstraint(
            "prix_unitaire_ht >= 0",
            name="check_lots_budgetaires_prix_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<LotBudgetaire(id={self.id}, code_lot='{self.code_lot}', "
            f"libelle='{self.libelle}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-05 / FIN-06: Achats et workflow validation
# ─────────────────────────────────────────────────────────────────────────────

class AchatModel(FinancierBase):
    """Modele SQLAlchemy pour les achats.

    FIN-05: Saisie achats et commandes
    FIN-06: Workflow de validation des achats
    """

    __tablename__ = "achats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fournisseur_id = Column(
        Integer,
        ForeignKey("fournisseurs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    lot_budgetaire_id = Column(
        Integer,
        ForeignKey("lots_budgetaires.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type_achat = Column(
        SQLEnum(*ACHAT_TYPES, name="achat_type_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    libelle = Column(String(300), nullable=False)
    quantite = Column(Numeric(12, 3), nullable=False)
    unite = Column(String(20), nullable=True)
    prix_unitaire_ht = Column(Numeric(12, 2), nullable=False)
    taux_tva = Column(Numeric(5, 2), nullable=False, default=20.0)
    date_commande = Column(Date, nullable=False, index=True)
    date_livraison_prevue = Column(Date, nullable=True)
    statut = Column(
        SQLEnum(*ACHAT_STATUTS, name="achat_statut_enum", native_enum=False),
        nullable=False,
        default="demande",
        index=True,
    )
    numero_facture = Column(String(100), nullable=True)
    motif_refus = Column(Text, nullable=True)
    commentaire = Column(Text, nullable=True)

    # Validation
    valideur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    validated_at = Column(DateTime, nullable=True)

    # Demandeur
    demandeur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
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
        # Recherche achats par chantier et statut
        Index("ix_achats_chantier_statut", "chantier_id", "statut"),
        # Recherche achats par fournisseur et date
        Index("ix_achats_fournisseur_date", "fournisseur_id", "date_commande"),
        # Recherche achats par chantier et type
        Index("ix_achats_chantier_type", "chantier_id", "type_achat"),
        # Recherche achats par lot budgetaire
        Index("ix_achats_lot_statut", "lot_budgetaire_id", "statut"),
        # Recherche achats en attente de validation par demandeur
        Index("ix_achats_demandeur_statut", "demandeur_id", "statut"),
        # Recherche par numero facture
        Index("ix_achats_numero_facture", "numero_facture"),
        # CHECK constraints
        CheckConstraint(
            "quantite > 0",
            name="check_achats_quantite_positive",
        ),
        CheckConstraint(
            "prix_unitaire_ht >= 0",
            name="check_achats_prix_positif",
        ),
        CheckConstraint(
            "taux_tva >= 0 AND taux_tva <= 100",
            name="check_achats_tva_range",
        ),
        CheckConstraint(
            "date_livraison_prevue IS NULL OR date_livraison_prevue >= date_commande",
            name="check_achats_date_livraison_coherente",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Achat(id={self.id}, libelle='{self.libelle}', "
            f"statut='{self.statut}', montant_ht="
            f"{self.quantite * self.prix_unitaire_ht if self.quantite and self.prix_unitaire_ht else 0})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-15: Journal financier (audit trail)
# ─────────────────────────────────────────────────────────────────────────────

class JournalFinancierModel(FinancierBase):
    """Modele SQLAlchemy pour le journal financier.

    FIN-15: Audit trail pour toutes les modifications financieres.
    Table append-only (pas de soft delete, pas de modification).
    """

    __tablename__ = "journal_financier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entite_type = Column(
        SQLEnum(*JOURNAL_ENTITE_TYPES, name="journal_entite_type_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    entite_id = Column(Integer, nullable=False)
    action = Column(
        SQLEnum(*JOURNAL_ACTIONS, name="journal_action_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    champ_modifie = Column(String(100), nullable=True)
    ancienne_valeur = Column(Text, nullable=True)
    nouvelle_valeur = Column(Text, nullable=True)
    motif = Column(Text, nullable=True)

    # Auteur
    auteur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Timestamp (append-only, pas de updated_at)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        # Recherche par entite
        Index("ix_journal_financier_entite", "entite_type", "entite_id"),
        # Recherche par auteur et date
        Index("ix_journal_financier_auteur_date", "auteur_id", "created_at"),
        # Recherche par action et date
        Index("ix_journal_financier_action_date", "action", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<JournalFinancier(id={self.id}, entite_type='{self.entite_type}', "
            f"entite_id={self.entite_id}, action='{self.action}')>"
        )
