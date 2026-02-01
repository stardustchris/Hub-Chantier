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
            "retenue_garantie_pct >= 0 AND retenue_garantie_pct <= 100",
            name="check_situations_travaux_retenue_range",
        ),
        CheckConstraint(
            "taux_tva >= 0 AND taux_tva <= 100",
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
