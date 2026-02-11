"""SQLAlchemy models pour le module Financier.

FIN-01: Budget chantier
FIN-02: Lots budgetaires (decomposition)
FIN-03: Affectation budgets aux taches
FIN-04: Avenants budgetaires
FIN-05: Achats et commandes
FIN-06: Workflow validation achats
FIN-07: Situations de travaux
FIN-08: Factures client
FIN-11: Suivi depenses
FIN-12: Alertes depassement budgetaire
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
    "main_oeuvre",
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
    "emission",
    "facturation",
    "acquittement",
)

JOURNAL_ENTITE_TYPES = (
    "budget",
    "lot_budgetaire",
    "achat",
    "fournisseur",
    "avenant",
    "situation",
    "facture",
    "alerte",
)

# Phase 2 enums
AVENANT_STATUTS = (
    "brouillon",
    "valide",
)

SITUATION_STATUTS = (
    "brouillon",
    "en_validation",
    "emise",
    "validee",
    "facturee",
)

FACTURE_TYPES = (
    "acompte",
    "situation",
    "solde",
)

FACTURE_STATUTS = (
    "brouillon",
    "emise",
    "envoyee",
    "payee",
    "annulee",
)

ALERTE_TYPES = (
    "seuil_engage",
    "seuil_realise",
    "depassement_lot",
    "perte_terminaison",
)

# CONN-10 to CONN-15: Pennylane Inbound enums
SYNC_TYPES = (
    "supplier_invoices",
    "customer_invoices",
    "suppliers",
)

SYNC_STATUS = (
    "running",
    "completed",
    "failed",
    "partial",
)

RECONCILIATION_STATUS = (
    "pending",
    "matched",
    "rejected",
    "manual",
)

SOURCE_DONNEE = (
    "HUB",
    "PENNYLANE",
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

    # CONN-12: Champs Pennylane Inbound
    pennylane_supplier_id = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="ID unique fournisseur Pennylane",
    )
    delai_paiement_jours = Column(
        Integer,
        nullable=False,
        default=30,
        comment="Delai de paiement par defaut en jours",
    )
    iban = Column(
        String(34),
        nullable=True,
        comment="IBAN du fournisseur (34 caracteres max)",
    )
    bic = Column(
        String(11),
        nullable=True,
        comment="Code BIC/SWIFT du fournisseur (8 ou 11 caracteres)",
    )
    source_donnee = Column(
        SQLEnum(*SOURCE_DONNEE, name="fournisseur_source_donnee_enum", native_enum=False),
        nullable=False,
        default="HUB",
        index=True,
        comment="Source de la donnee: HUB (saisie manuelle) ou PENNYLANE (import)",
    )
    derniere_sync_pennylane = Column(
        DateTime,
        nullable=True,
        comment="Date/heure de la derniere synchronisation avec Pennylane",
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
    seuil_alerte_pct = Column(Numeric(5, 2), nullable=False, default=90.0)
    seuil_validation_achat = Column(Numeric(10, 2), nullable=False, default=5000.0)
    notes = Column(Text, nullable=True)

    # Tracabilite devis source (pas de FK pour eviter couplage cross-module)
    devis_id = Column(Integer, nullable=True, index=True)

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

    # A5: Lock optimiste
    version = Column(Integer, nullable=False, default=1, server_default=text("1"))

    __table_args__ = (
        CheckConstraint(
            "montant_initial_ht >= 0",
            name="check_budgets_montant_initial_positif",
        ),
        CheckConstraint(
            "retenue_garantie_pct >= 0 AND retenue_garantie_pct <= 5",
            name="check_budgets_retenue_garantie_range",
        ),
        CheckConstraint(
            "seuil_alerte_pct >= 0 AND seuil_alerte_pct <= 200",
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
    Chaque lot a un code unique par budget (phase chantier) ou par devis (phase commerciale).

    Phase Devis:
        - devis_id est renseigné, budget_id est NULL
        - Les champs déboursés détaillés sont utilisés
        - marge_pct et prix_vente_ht sont calculés

    Phase Chantier:
        - budget_id est renseigné, devis_id est NULL
        - Les champs déboursés sont optionnels
    """

    __tablename__ = "lots_budgetaires"

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(
        Integer,
        ForeignKey("budgets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    devis_id = Column(
        String(36),  # UUID stocké comme string
        nullable=True,
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

    # Champs déboursés détaillés (phase devis)
    debourse_main_oeuvre = Column(Numeric(12, 2), nullable=True)
    debourse_materiaux = Column(Numeric(12, 2), nullable=True)
    debourse_sous_traitance = Column(Numeric(12, 2), nullable=True)
    debourse_materiel = Column(Numeric(12, 2), nullable=True)
    debourse_divers = Column(Numeric(12, 2), nullable=True)

    # Marge (phase devis)
    marge_pct = Column(Numeric(5, 2), nullable=True)
    prix_vente_ht = Column(Numeric(12, 2), nullable=True)

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
        # Contrainte XOR: soit devis_id, soit budget_id (pas les deux, pas aucun)
        CheckConstraint(
            "(devis_id IS NULL AND budget_id IS NOT NULL) OR (devis_id IS NOT NULL AND budget_id IS NULL)",
            name="check_lots_budgetaires_devis_xor_budget",
        ),
        # Contraintes sur les valeurs
        CheckConstraint(
            "quantite_prevue >= 0",
            name="check_lots_budgetaires_quantite_positive",
        ),
        CheckConstraint(
            "prix_unitaire_ht >= 0",
            name="check_lots_budgetaires_prix_positif",
        ),
        CheckConstraint(
            "debourse_main_oeuvre IS NULL OR debourse_main_oeuvre >= 0",
            name="check_lots_budgetaires_debourse_mo_positive",
        ),
        CheckConstraint(
            "debourse_materiaux IS NULL OR debourse_materiaux >= 0",
            name="check_lots_budgetaires_debourse_mat_positive",
        ),
        CheckConstraint(
            "debourse_sous_traitance IS NULL OR debourse_sous_traitance >= 0",
            name="check_lots_budgetaires_debourse_st_positive",
        ),
        CheckConstraint(
            "debourse_materiel IS NULL OR debourse_materiel >= 0",
            name="check_lots_budgetaires_debourse_materiel_positive",
        ),
        CheckConstraint(
            "debourse_divers IS NULL OR debourse_divers >= 0",
            name="check_lots_budgetaires_debourse_divers_positive",
        ),
        CheckConstraint(
            "marge_pct IS NULL OR marge_pct >= 0",
            name="check_lots_budgetaires_marge_positive",
        ),
        CheckConstraint(
            "prix_vente_ht IS NULL OR prix_vente_ht >= 0",
            name="check_lots_budgetaires_prix_vente_positive",
        ),
        # Index composés
        Index("ix_lots_budgetaires_budget_ordre", "budget_id", "ordre"),
        Index("ix_lots_budgetaires_devis_ordre", "devis_id", "ordre"),
        Index("ix_lots_budgetaires_parent", "parent_lot_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<LotBudgetaire(id={self.id}, code_lot='{self.code_lot}', "
            f"libelle='{self.libelle}', devis_id={self.devis_id}, budget_id={self.budget_id})>"
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

    # CONN-10: Champs Pennylane Inbound
    montant_ht_reel = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Montant HT facture reelle importee de Pennylane",
    )
    date_facture_reelle = Column(
        Date,
        nullable=True,
        comment="Date de la facture reelle depuis Pennylane",
    )
    pennylane_invoice_id = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="ID unique facture Pennylane (idempotence)",
    )
    source_donnee = Column(
        SQLEnum(*SOURCE_DONNEE, name="achat_source_donnee_enum", native_enum=False),
        nullable=False,
        default="HUB",
        index=True,
        comment="Source de la donnee: HUB (saisie manuelle) ou PENNYLANE (import)",
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
            "taux_tva IN (0, 2.1, 5.5, 10, 20)",
            name="check_achats_tva_range",
        ),
        CheckConstraint(
            "date_livraison_prevue IS NULL OR date_livraison_prevue >= date_commande",
            name="check_achats_date_livraison_coherente",
        ),
        CheckConstraint(
            "type_achat != 'sous_traitance' OR taux_tva = 0",
            name="check_achats_autoliquidation_st",
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


# ─────────────────────────────────────────────────────────────────────────────
# FIN-04: Avenants budgetaires
# ─────────────────────────────────────────────────────────────────────────────

class AvenantBudgetaireModel(FinancierBase):
    """Modele SQLAlchemy pour les avenants budgetaires.

    FIN-04: Avenants budgetaires - modifications du budget initial.
    Le montant peut etre negatif (reduction de budget).
    Numerotation automatique AVN-YYYY-NN par budget.
    """

    __tablename__ = "avenants_budgetaires"

    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(
        Integer,
        ForeignKey("budgets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    numero = Column(String(20), nullable=False)
    motif = Column(Text, nullable=False)
    montant_ht = Column(Numeric(12, 2), nullable=False)
    impact_description = Column(Text, nullable=True)
    statut = Column(
        SQLEnum(*AVENANT_STATUTS, name="avenant_statut_enum", native_enum=False),
        nullable=False,
        default="brouillon",
        index=True,
    )

    # Auteur / Validation
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    validated_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    validated_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("budget_id", "numero", name="uq_avenants_budgetaires_budget_numero"),
        Index("ix_avenants_budgetaires_budget_statut", "budget_id", "statut"),
        CheckConstraint(
            "length(motif) > 0",
            name="check_avenants_budgetaires_motif_non_vide",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AvenantBudgetaire(id={self.id}, numero='{self.numero}', "
            f"montant_ht={self.montant_ht}, statut='{self.statut}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-07: Situations de travaux
# ─────────────────────────────────────────────────────────────────────────────

class SituationTravauxModel(FinancierBase):
    """Modele SQLAlchemy pour les situations de travaux.

    FIN-07: Situations de travaux - etats d'avancement periodiques.
    Numerotation automatique SIT-YYYY-NN par chantier.
    montant_cumule_ht = montant_cumule_precedent_ht + montant_periode_ht.
    """

    __tablename__ = "situations_travaux"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    budget_id = Column(
        Integer,
        ForeignKey("budgets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    numero = Column(String(20), nullable=False)
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    montant_cumule_precedent_ht = Column(Numeric(12, 2), nullable=False, default=0)
    montant_periode_ht = Column(Numeric(12, 2), nullable=False, default=0)
    montant_cumule_ht = Column(Numeric(12, 2), nullable=False, default=0)
    retenue_garantie_pct = Column(Numeric(5, 2), nullable=False, default=5.0)
    taux_tva = Column(Numeric(5, 2), nullable=False, default=20.0)
    statut = Column(
        SQLEnum(*SITUATION_STATUTS, name="situation_statut_enum", native_enum=False),
        nullable=False,
        default="brouillon",
        index=True,
    )
    notes = Column(Text, nullable=True)

    # Auteur / Validation / Workflow dates
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    validated_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    validated_at = Column(DateTime, nullable=True)
    emise_at = Column(DateTime, nullable=True)
    facturee_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # A5: Lock optimiste
    version = Column(Integer, nullable=False, default=1, server_default=text("1"))

    __table_args__ = (
        UniqueConstraint("chantier_id", "numero", name="uq_situations_travaux_chantier_numero"),
        Index("ix_situations_travaux_chantier_statut", "chantier_id", "statut"),
        Index("ix_situations_travaux_budget", "budget_id"),
        Index("ix_situations_travaux_periode", "chantier_id", "periode_debut", "periode_fin"),
        CheckConstraint(
            "periode_fin >= periode_debut",
            name="check_situations_travaux_periode_coherente",
        ),
        CheckConstraint(
            "montant_cumule_precedent_ht >= 0",
            name="check_situations_travaux_cumule_precedent_positif",
        ),
        CheckConstraint(
            "montant_cumule_ht >= 0",
            name="check_situations_travaux_cumule_positif",
        ),
        CheckConstraint(
            "retenue_garantie_pct >= 0 AND retenue_garantie_pct <= 5",
            name="check_situations_travaux_retenue_range",
        ),
        CheckConstraint(
            "taux_tva IN (0, 2.1, 5.5, 10, 20)",
            name="check_situations_travaux_tva_range",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<SituationTravaux(id={self.id}, numero='{self.numero}', "
            f"statut='{self.statut}', montant_cumule_ht={self.montant_cumule_ht})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-07 (sub-table): Lignes de situation
# ─────────────────────────────────────────────────────────────────────────────

class LigneSituationModel(FinancierBase):
    """Modele SQLAlchemy pour les lignes de situation.

    Sub-table de situations_travaux: avancement par lot budgetaire.
    montant_cumule_ht = montant_marche_ht * pourcentage_avancement / 100.
    montant_periode_ht = montant_cumule_ht - montant_cumule_precedent_ht.
    """

    __tablename__ = "lignes_situation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    situation_id = Column(
        Integer,
        ForeignKey("situations_travaux.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lot_budgetaire_id = Column(
        Integer,
        ForeignKey("lots_budgetaires.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    pourcentage_avancement = Column(Numeric(5, 2), nullable=False, default=0)
    montant_marche_ht = Column(Numeric(12, 2), nullable=False, default=0)
    montant_cumule_precedent_ht = Column(Numeric(12, 2), nullable=False, default=0)
    montant_periode_ht = Column(Numeric(12, 2), nullable=False, default=0)
    montant_cumule_ht = Column(Numeric(12, 2), nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "situation_id", "lot_budgetaire_id",
            name="uq_lignes_situation_situation_lot",
        ),
        Index("ix_lignes_situation_lot", "lot_budgetaire_id"),
        CheckConstraint(
            "pourcentage_avancement >= 0 AND pourcentage_avancement <= 100",
            name="check_lignes_situation_avancement_range",
        ),
        CheckConstraint(
            "montant_marche_ht >= 0",
            name="check_lignes_situation_montant_marche_positif",
        ),
        CheckConstraint(
            "montant_cumule_precedent_ht >= 0",
            name="check_lignes_situation_cumule_precedent_positif",
        ),
        CheckConstraint(
            "montant_cumule_ht >= 0",
            name="check_lignes_situation_cumule_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<LigneSituation(id={self.id}, situation_id={self.situation_id}, "
            f"lot_budgetaire_id={self.lot_budgetaire_id}, "
            f"avancement={self.pourcentage_avancement}%)>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-08: Factures client
# ─────────────────────────────────────────────────────────────────────────────

class FactureClientModel(FinancierBase):
    """Modele SQLAlchemy pour les factures client.

    FIN-08: Factures client - generees a partir des situations de travaux.
    Numerotation automatique FAC-YYYY-NN (unique globale).
    montant_net = montant_ttc - retenue_garantie_montant.
    """

    __tablename__ = "factures_client"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    situation_id = Column(
        Integer,
        ForeignKey("situations_travaux.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    numero_facture = Column(String(20), nullable=False, unique=True, index=True)
    type_facture = Column(
        SQLEnum(*FACTURE_TYPES, name="facture_type_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    montant_ht = Column(Numeric(12, 2), nullable=False)
    taux_tva = Column(Numeric(5, 2), nullable=False, default=20.0)
    montant_tva = Column(Numeric(12, 2), nullable=False)
    montant_ttc = Column(Numeric(12, 2), nullable=False)
    retenue_garantie_montant = Column(Numeric(12, 2), nullable=False, default=0)
    montant_net = Column(Numeric(12, 2), nullable=False)
    date_emission = Column(Date, nullable=True)
    date_echeance = Column(Date, nullable=True)
    statut = Column(
        SQLEnum(*FACTURE_STATUTS, name="facture_statut_enum", native_enum=False),
        nullable=False,
        default="brouillon",
        index=True,
    )
    notes = Column(Text, nullable=True)

    # Auteur
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # CONN-11: Champs Pennylane encaissements
    date_paiement_reel = Column(
        Date,
        nullable=True,
        index=True,
        comment="Date de paiement reelle constatee depuis Pennylane",
    )
    montant_encaisse = Column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        comment="Montant reellement encaisse (peut differer du montant_ttc)",
    )
    pennylane_invoice_id = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="ID unique facture client Pennylane (idempotence)",
    )

    __table_args__ = (
        Index("ix_factures_client_chantier_statut", "chantier_id", "statut"),
        Index("ix_factures_client_chantier_type", "chantier_id", "type_facture"),
        Index("ix_factures_client_date_emission", "date_emission"),
        Index("ix_factures_client_date_echeance_statut", "date_echeance", "statut"),
        CheckConstraint(
            "montant_ht >= 0",
            name="check_factures_client_montant_ht_positif",
        ),
        CheckConstraint(
            "taux_tva >= 0 AND taux_tva <= 100",
            name="check_factures_client_tva_range",
        ),
        CheckConstraint(
            "montant_tva >= 0",
            name="check_factures_client_montant_tva_positif",
        ),
        CheckConstraint(
            "montant_ttc >= 0",
            name="check_factures_client_montant_ttc_positif",
        ),
        CheckConstraint(
            "retenue_garantie_montant >= 0",
            name="check_factures_client_retenue_positive",
        ),
        CheckConstraint(
            "montant_net >= 0",
            name="check_factures_client_montant_net_positif",
        ),
        CheckConstraint(
            "date_echeance IS NULL OR date_emission IS NULL OR date_echeance >= date_emission",
            name="check_factures_client_echeance_coherente",
        ),
        CheckConstraint(
            "montant_encaisse >= 0",
            name="check_factures_client_montant_encaisse_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<FactureClient(id={self.id}, numero='{self.numero_facture}', "
            f"type='{self.type_facture}', statut='{self.statut}', "
            f"montant_ttc={self.montant_ttc})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-12: Alertes depassement budgetaire
# ─────────────────────────────────────────────────────────────────────────────

class AlerteDepassementModel(FinancierBase):
    """Modele SQLAlchemy pour les alertes de depassement budgetaire.

    FIN-12: Alertes automatiques quand un seuil budgetaire est atteint.
    Table append-only (pas de soft delete, acquittement uniquement).
    """

    __tablename__ = "alertes_depassement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    budget_id = Column(
        Integer,
        ForeignKey("budgets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    type_alerte = Column(
        SQLEnum(*ALERTE_TYPES, name="alerte_type_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    message = Column(Text, nullable=False)
    pourcentage_atteint = Column(Numeric(7, 2), nullable=False)
    seuil_configure = Column(Numeric(5, 2), nullable=False)
    montant_budget_ht = Column(Numeric(12, 2), nullable=False)
    montant_atteint_ht = Column(Numeric(12, 2), nullable=False)
    est_acquittee = Column(Boolean, nullable=False, default=False, index=True)

    # Acquittement
    acquittee_par = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    acquittee_at = Column(DateTime, nullable=True)

    # Timestamp (append-only, pas de updated_at)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_alertes_depassement_chantier_acquittee", "chantier_id", "est_acquittee"),
        Index("ix_alertes_depassement_budget_type", "budget_id", "type_alerte"),
        Index("ix_alertes_depassement_created", "created_at"),
        CheckConstraint(
            "pourcentage_atteint >= 0",
            name="check_alertes_depassement_pourcentage_positif",
        ),
        CheckConstraint(
            "seuil_configure >= 0",
            name="check_alertes_depassement_seuil_positif",
        ),
        CheckConstraint(
            "montant_budget_ht >= 0",
            name="check_alertes_depassement_montant_budget_positif",
        ),
        CheckConstraint(
            "montant_atteint_ht >= 0",
            name="check_alertes_depassement_montant_atteint_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AlerteDepassement(id={self.id}, type='{self.type_alerte}', "
            f"pourcentage={self.pourcentage_atteint}%, "
            f"acquittee={self.est_acquittee})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FIN-03: Affectation budgets aux taches
# ─────────────────────────────────────────────────────────────────────────────

class AffectationBudgetTacheModel(FinancierBase):
    """Modele SQLAlchemy pour les affectations budget-tache.

    FIN-03: Affectation budgets aux taches - Lien entre un lot budgetaire
    et une tache avec un pourcentage d'allocation.
    tache_id est un Integer simple (pas de FK cross-module).
    """

    __tablename__ = "financier_affectations_budget_tache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_budgetaire_id = Column(
        Integer,
        ForeignKey("lots_budgetaires.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tache_id = Column(
        Integer,
        nullable=False,
        index=True,
    )
    pourcentage_allocation = Column(
        Numeric(5, 2),
        nullable=False,
        default=0,
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "lot_budgetaire_id", "tache_id",
            name="uq_affectations_budget_tache_lot_tache",
        ),
        Index(
            "ix_affectations_budget_tache_lot",
            "lot_budgetaire_id",
        ),
        Index(
            "ix_affectations_budget_tache_tache",
            "tache_id",
        ),
        CheckConstraint(
            "pourcentage_allocation >= 0 AND pourcentage_allocation <= 100",
            name="check_affectations_budget_tache_pourcentage_range",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AffectationBudgetTache(id={self.id}, "
            f"lot_budgetaire_id={self.lot_budgetaire_id}, "
            f"tache_id={self.tache_id}, "
            f"pourcentage={self.pourcentage_allocation}%)>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-14: Pennylane Mapping Analytique
# ─────────────────────────────────────────────────────────────────────────────

class PennylaneMappingAnalytiqueModel(FinancierBase):
    """Modele SQLAlchemy pour le mapping codes analytiques Pennylane.

    CONN-14: Table de correspondance entre les codes analytiques utilises
    dans Pennylane et les ID de chantiers dans Hub Chantier.
    """

    __tablename__ = "pennylane_mapping_analytique"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code_analytique = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Code analytique Pennylane (ex: MONTMELIAN, CHT001)",
    )
    chantier_id = Column(
        Integer,
        ForeignKey("chantiers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID du chantier Hub Chantier associe",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Date de creation du mapping",
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Utilisateur ayant cree le mapping",
    )

    __table_args__ = (
        {"comment": "Table de correspondance entre codes analytiques Pennylane et chantiers Hub"},
    )

    def __repr__(self) -> str:
        return (
            f"<PennylaneMappingAnalytique(id={self.id}, "
            f"code_analytique='{self.code_analytique}', "
            f"chantier_id={self.chantier_id})>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-10/11/12: Pennylane Sync Log
# ─────────────────────────────────────────────────────────────────────────────

class PennylaneSyncLogModel(FinancierBase):
    """Modele SQLAlchemy pour le journal des synchronisations Pennylane.

    CONN-10/11/12: Audit trail des synchronisations periodiques avec Pennylane.
    Table append-only (pas de modification, pas de suppression).
    """

    __tablename__ = "pennylane_sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_type = Column(
        SQLEnum(*SYNC_TYPES, name="sync_type_enum", native_enum=False),
        nullable=False,
        index=True,
        comment="Type de sync: supplier_invoices, customer_invoices, suppliers",
    )
    started_at = Column(
        DateTime,
        nullable=False,
        index=True,
        comment="Debut de la synchronisation",
    )
    completed_at = Column(
        DateTime,
        nullable=True,
        comment="Fin de la synchronisation (NULL si en cours)",
    )
    records_processed = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Nombre total de records traites",
    )
    records_created = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Nombre de nouveaux records crees",
    )
    records_updated = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Nombre de records mis a jour",
    )
    records_pending = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Nombre de records en attente de reconciliation",
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="Message d'erreur si echec",
    )
    status = Column(
        SQLEnum(*SYNC_STATUS, name="sync_status_enum", native_enum=False),
        nullable=False,
        default="running",
        index=True,
        comment="Statut: running, completed, failed, partial",
    )

    __table_args__ = (
        Index("ix_pennylane_sync_log_type_status", "sync_type", "status"),
        {"comment": "Journal des synchronisations Pennylane (audit trail)"},
    )

    def __repr__(self) -> str:
        return (
            f"<PennylaneSyncLog(id={self.id}, "
            f"sync_type='{self.sync_type}', "
            f"status='{self.status}')>"
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-15: Pennylane Pending Reconciliation
# ─────────────────────────────────────────────────────────────────────────────

class PennylanePendingReconciliationModel(FinancierBase):
    """Modele SQLAlchemy pour la file d'attente de reconciliation Pennylane.

    CONN-15: Stocke les factures Pennylane importees qui n'ont pas pu
    etre matchees automatiquement avec un achat existant.
    """

    __tablename__ = "pennylane_pending_reconciliation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pennylane_invoice_id = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="ID unique facture Pennylane (idempotence)",
    )
    supplier_name = Column(
        String(255),
        nullable=True,
        comment="Nom du fournisseur depuis Pennylane",
    )
    supplier_siret = Column(
        String(14),
        nullable=True,
        comment="SIRET du fournisseur depuis Pennylane",
    )
    amount_ht = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Montant HT de la facture",
    )
    code_analytique = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Code analytique Pennylane associe",
    )
    invoice_date = Column(
        Date,
        nullable=True,
        comment="Date de la facture",
    )
    suggested_achat_id = Column(
        Integer,
        ForeignKey("achats.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de l'achat suggere par le matching intelligent",
    )
    status = Column(
        SQLEnum(*RECONCILIATION_STATUS, name="reconciliation_status_enum", native_enum=False),
        nullable=False,
        default="pending",
        index=True,
        comment="Statut: pending, matched, rejected, manual",
    )
    resolved_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Utilisateur ayant resolu la reconciliation",
    )
    resolved_at = Column(
        DateTime,
        nullable=True,
        comment="Date/heure de resolution",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Date de creation de la demande",
    )

    __table_args__ = (
        Index("ix_pennylane_pending_status_created", "status", "created_at"),
        {"comment": "File d'attente des factures Pennylane non matchees automatiquement"},
    )

    def __repr__(self) -> str:
        return (
            f"<PennylanePendingReconciliation(id={self.id}, "
            f"pennylane_invoice_id='{self.pennylane_invoice_id}', "
            f"status='{self.status}')>"
        )
