"""Migration Pennylane Inbound Integration (CONN-10 to CONN-17)

Ajoute les tables et colonnes pour l'import de donnees comptables depuis Pennylane.
Permet le calcul de la rentabilite reelle des chantiers (Budget vs Realise).

Tables modifiees :
- achats : colonnes Pennylane (montant_ht_reel, date_facture_reelle, pennylane_invoice_id, source_donnee)
- factures_client : colonnes encaissement (date_paiement_reel, montant_encaisse, pennylane_invoice_id)
- fournisseurs : colonnes sync Pennylane (pennylane_supplier_id, delai_paiement_jours, iban, bic, source_donnee, derniere_sync_pennylane)

Nouvelles tables :
- pennylane_mapping_analytique : correspondance code_analytique <-> chantier_id
- pennylane_sync_log : historique des synchronisations
- pennylane_pending_reconciliation : file d'attente factures non matchees

Revision ID: pennylane_inbound_001
Revises: add_devis_id_budget_001
Create Date: 2026-02-03 14:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'pennylane_inbound_001'
down_revision: Union[str, None] = 'add_devis_id_budget_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum pour source_donnee
SOURCE_DONNEE_VALUES = ('HUB', 'PENNYLANE')

# Enum pour statut reconciliation
RECONCILIATION_STATUS_VALUES = ('pending', 'matched', 'rejected', 'manual')

# Enum pour sync status
SYNC_STATUS_VALUES = ('running', 'completed', 'failed', 'partial')


def upgrade() -> None:
    """Ajoute les colonnes et tables pour l'integration Pennylane Inbound."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Enrichissement table 'achats'
    # ─────────────────────────────────────────────────────────────────────────

    existing_columns_achats = [c['name'] for c in inspector.get_columns('achats')]

    # montant_ht_reel : Montant facture reelle (Pennylane)
    if 'montant_ht_reel' not in existing_columns_achats:
        op.add_column(
            'achats',
            sa.Column(
                'montant_ht_reel',
                sa.Numeric(15, 2),
                nullable=True,
                comment='Montant HT facture reelle importee de Pennylane'
            )
        )

    # date_facture_reelle : Date facture Pennylane
    if 'date_facture_reelle' not in existing_columns_achats:
        op.add_column(
            'achats',
            sa.Column(
                'date_facture_reelle',
                sa.Date(),
                nullable=True,
                comment='Date de la facture reelle depuis Pennylane'
            )
        )

    # pennylane_invoice_id : ID externe pour idempotence
    if 'pennylane_invoice_id' not in existing_columns_achats:
        op.add_column(
            'achats',
            sa.Column(
                'pennylane_invoice_id',
                sa.String(255),
                nullable=True,
                comment='ID unique facture Pennylane (idempotence)'
            )
        )
        # Index unique pour idempotence
        op.create_index(
            'ix_achats_pennylane_invoice_id',
            'achats',
            ['pennylane_invoice_id'],
            unique=True,
            postgresql_where=sa.text('pennylane_invoice_id IS NOT NULL')
        )

    # source_donnee : "HUB" | "PENNYLANE"
    if 'source_donnee' not in existing_columns_achats:
        op.add_column(
            'achats',
            sa.Column(
                'source_donnee',
                sa.String(20),
                nullable=False,
                server_default='HUB',
                comment='Source de la donnee: HUB (saisie manuelle) ou PENNYLANE (import)'
            )
        )
        # Index pour filtrer par source
        op.create_index(
            'ix_achats_source_donnee',
            'achats',
            ['source_donnee']
        )

    # Index composite pour recherche factures Pennylane par chantier
    op.create_index(
        'ix_achats_chantier_pennylane',
        'achats',
        ['chantier_id', 'pennylane_invoice_id'],
        postgresql_where=sa.text('pennylane_invoice_id IS NOT NULL')
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Enrichissement table 'factures_client'
    # ─────────────────────────────────────────────────────────────────────────

    existing_columns_factures = [c['name'] for c in inspector.get_columns('factures_client')]

    # date_paiement_reel : Date encaissement constate
    if 'date_paiement_reel' not in existing_columns_factures:
        op.add_column(
            'factures_client',
            sa.Column(
                'date_paiement_reel',
                sa.Date(),
                nullable=True,
                comment='Date de paiement reelle constatee depuis Pennylane'
            )
        )
        # Index pour suivi DSO (Days Sales Outstanding)
        op.create_index(
            'ix_factures_client_date_paiement_reel',
            'factures_client',
            ['date_paiement_reel']
        )

    # montant_encaisse : Montant reellement encaisse
    if 'montant_encaisse' not in existing_columns_factures:
        op.add_column(
            'factures_client',
            sa.Column(
                'montant_encaisse',
                sa.Numeric(15, 2),
                nullable=False,
                server_default='0',
                comment='Montant reellement encaisse (peut differer du montant_ttc)'
            )
        )

    # pennylane_invoice_id : ID externe
    if 'pennylane_invoice_id' not in existing_columns_factures:
        op.add_column(
            'factures_client',
            sa.Column(
                'pennylane_invoice_id',
                sa.String(255),
                nullable=True,
                comment='ID unique facture client Pennylane (idempotence)'
            )
        )
        # Index unique pour idempotence
        op.create_index(
            'ix_factures_client_pennylane_invoice_id',
            'factures_client',
            ['pennylane_invoice_id'],
            unique=True,
            postgresql_where=sa.text('pennylane_invoice_id IS NOT NULL')
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Enrichissement table 'fournisseurs'
    # ─────────────────────────────────────────────────────────────────────────

    existing_columns_fournisseurs = [c['name'] for c in inspector.get_columns('fournisseurs')]

    # pennylane_supplier_id : ID externe
    if 'pennylane_supplier_id' not in existing_columns_fournisseurs:
        op.add_column(
            'fournisseurs',
            sa.Column(
                'pennylane_supplier_id',
                sa.String(255),
                nullable=True,
                comment='ID unique fournisseur Pennylane'
            )
        )
        # Index unique pour idempotence
        op.create_index(
            'ix_fournisseurs_pennylane_supplier_id',
            'fournisseurs',
            ['pennylane_supplier_id'],
            unique=True,
            postgresql_where=sa.text('pennylane_supplier_id IS NOT NULL')
        )

    # delai_paiement_jours : Delai paiement par defaut
    if 'delai_paiement_jours' not in existing_columns_fournisseurs:
        op.add_column(
            'fournisseurs',
            sa.Column(
                'delai_paiement_jours',
                sa.Integer(),
                nullable=False,
                server_default='30',
                comment='Delai de paiement par defaut en jours'
            )
        )

    # iban : Coordonnees bancaires (optionnel)
    if 'iban' not in existing_columns_fournisseurs:
        op.add_column(
            'fournisseurs',
            sa.Column(
                'iban',
                sa.String(34),
                nullable=True,
                comment='IBAN du fournisseur (34 caracteres max)'
            )
        )

    # bic : Code BIC (optionnel)
    if 'bic' not in existing_columns_fournisseurs:
        op.add_column(
            'fournisseurs',
            sa.Column(
                'bic',
                sa.String(11),
                nullable=True,
                comment='Code BIC/SWIFT du fournisseur (8 ou 11 caracteres)'
            )
        )

    # source_donnee : "HUB" | "PENNYLANE"
    if 'source_donnee' not in existing_columns_fournisseurs:
        op.add_column(
            'fournisseurs',
            sa.Column(
                'source_donnee',
                sa.String(20),
                nullable=False,
                server_default='HUB',
                comment='Source de la donnee: HUB (saisie manuelle) ou PENNYLANE (import)'
            )
        )
        # Index pour filtrer par source
        op.create_index(
            'ix_fournisseurs_source_donnee',
            'fournisseurs',
            ['source_donnee']
        )

    # derniere_sync_pennylane : Derniere synchronisation
    if 'derniere_sync_pennylane' not in existing_columns_fournisseurs:
        op.add_column(
            'fournisseurs',
            sa.Column(
                'derniere_sync_pennylane',
                sa.DateTime(),
                nullable=True,
                comment='Date/heure de la derniere synchronisation avec Pennylane'
            )
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Nouvelle table 'pennylane_mapping_analytique'
    # ─────────────────────────────────────────────────────────────────────────

    if 'pennylane_mapping_analytique' not in inspector.get_table_names():
        op.create_table(
            'pennylane_mapping_analytique',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                'code_analytique',
                sa.String(50),
                nullable=False,
                unique=True,
                comment='Code analytique Pennylane (ex: MONTMELIAN, CHT001)'
            ),
            sa.Column(
                'chantier_id',
                sa.Integer(),
                sa.ForeignKey('chantiers.id', ondelete='CASCADE'),
                nullable=False,
                comment='ID du chantier Hub Chantier associe'
            ),
            sa.Column(
                'created_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                comment='Date de creation du mapping'
            ),
            sa.Column(
                'created_by',
                sa.Integer(),
                sa.ForeignKey('users.id', ondelete='SET NULL'),
                nullable=True,
                comment='Utilisateur ayant cree le mapping'
            ),
            comment='Table de correspondance entre codes analytiques Pennylane et chantiers Hub'
        )

        # Index pour recherche par chantier
        op.create_index(
            'ix_pennylane_mapping_analytique_chantier_id',
            'pennylane_mapping_analytique',
            ['chantier_id']
        )

        # Index unique sur code_analytique (deja defini dans la colonne, mais explicite)
        op.create_index(
            'ix_pennylane_mapping_analytique_code',
            'pennylane_mapping_analytique',
            ['code_analytique'],
            unique=True
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Nouvelle table 'pennylane_sync_log'
    # ─────────────────────────────────────────────────────────────────────────

    if 'pennylane_sync_log' not in inspector.get_table_names():
        op.create_table(
            'pennylane_sync_log',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                'sync_type',
                sa.String(50),
                nullable=False,
                comment='Type de sync: supplier_invoices, customer_invoices, suppliers'
            ),
            sa.Column(
                'started_at',
                sa.DateTime(),
                nullable=False,
                comment='Debut de la synchronisation'
            ),
            sa.Column(
                'completed_at',
                sa.DateTime(),
                nullable=True,
                comment='Fin de la synchronisation (NULL si en cours)'
            ),
            sa.Column(
                'records_processed',
                sa.Integer(),
                nullable=False,
                server_default='0',
                comment='Nombre total de records traites'
            ),
            sa.Column(
                'records_created',
                sa.Integer(),
                nullable=False,
                server_default='0',
                comment='Nombre de nouveaux records crees'
            ),
            sa.Column(
                'records_updated',
                sa.Integer(),
                nullable=False,
                server_default='0',
                comment='Nombre de records mis a jour'
            ),
            sa.Column(
                'records_pending',
                sa.Integer(),
                nullable=False,
                server_default='0',
                comment='Nombre de records en attente de reconciliation'
            ),
            sa.Column(
                'error_message',
                sa.Text(),
                nullable=True,
                comment='Message d\'erreur si echec'
            ),
            sa.Column(
                'status',
                sa.String(20),
                nullable=False,
                server_default='running',
                comment='Statut: running, completed, failed, partial'
            ),
            comment='Journal des synchronisations Pennylane (audit trail)'
        )

        # Index pour filtrer par type de sync
        op.create_index(
            'ix_pennylane_sync_log_sync_type',
            'pennylane_sync_log',
            ['sync_type']
        )

        # Index pour filtrer par statut
        op.create_index(
            'ix_pennylane_sync_log_status',
            'pennylane_sync_log',
            ['status']
        )

        # Index pour trier par date
        op.create_index(
            'ix_pennylane_sync_log_started_at',
            'pennylane_sync_log',
            ['started_at']
        )

        # Index composite pour dashboard monitoring
        op.create_index(
            'ix_pennylane_sync_log_type_status',
            'pennylane_sync_log',
            ['sync_type', 'status']
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Nouvelle table 'pennylane_pending_reconciliation'
    # ─────────────────────────────────────────────────────────────────────────

    if 'pennylane_pending_reconciliation' not in inspector.get_table_names():
        op.create_table(
            'pennylane_pending_reconciliation',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                'pennylane_invoice_id',
                sa.String(255),
                nullable=False,
                unique=True,
                comment='ID unique facture Pennylane (idempotence)'
            ),
            sa.Column(
                'supplier_name',
                sa.String(255),
                nullable=True,
                comment='Nom du fournisseur depuis Pennylane'
            ),
            sa.Column(
                'supplier_siret',
                sa.String(14),
                nullable=True,
                comment='SIRET du fournisseur depuis Pennylane'
            ),
            sa.Column(
                'amount_ht',
                sa.Numeric(15, 2),
                nullable=True,
                comment='Montant HT de la facture'
            ),
            sa.Column(
                'code_analytique',
                sa.String(50),
                nullable=True,
                comment='Code analytique Pennylane associe'
            ),
            sa.Column(
                'invoice_date',
                sa.Date(),
                nullable=True,
                comment='Date de la facture'
            ),
            sa.Column(
                'suggested_achat_id',
                sa.Integer(),
                sa.ForeignKey('achats.id', ondelete='SET NULL'),
                nullable=True,
                comment='ID de l\'achat suggere par le matching intelligent'
            ),
            sa.Column(
                'status',
                sa.String(20),
                nullable=False,
                server_default='pending',
                comment='Statut: pending, matched, rejected, manual'
            ),
            sa.Column(
                'resolved_by',
                sa.Integer(),
                sa.ForeignKey('users.id', ondelete='SET NULL'),
                nullable=True,
                comment='Utilisateur ayant resolu la reconciliation'
            ),
            sa.Column(
                'resolved_at',
                sa.DateTime(),
                nullable=True,
                comment='Date/heure de resolution'
            ),
            sa.Column(
                'created_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                comment='Date de creation de la demande'
            ),
            comment='File d\'attente des factures Pennylane non matchees automatiquement'
        )

        # Index unique sur pennylane_invoice_id (deja defini, mais explicite)
        op.create_index(
            'ix_pennylane_pending_invoice_id',
            'pennylane_pending_reconciliation',
            ['pennylane_invoice_id'],
            unique=True
        )

        # Index pour filtrer par statut (dashboard reconciliation)
        op.create_index(
            'ix_pennylane_pending_status',
            'pennylane_pending_reconciliation',
            ['status']
        )

        # Index pour filtrer par code analytique
        op.create_index(
            'ix_pennylane_pending_code_analytique',
            'pennylane_pending_reconciliation',
            ['code_analytique']
        )

        # Index pour trier par date creation
        op.create_index(
            'ix_pennylane_pending_created_at',
            'pennylane_pending_reconciliation',
            ['created_at']
        )

        # Index pour recherche par achat suggere
        op.create_index(
            'ix_pennylane_pending_suggested_achat',
            'pennylane_pending_reconciliation',
            ['suggested_achat_id']
        )

        # Index composite pour dashboard (status + date)
        op.create_index(
            'ix_pennylane_pending_status_created',
            'pennylane_pending_reconciliation',
            ['status', 'created_at']
        )


def downgrade() -> None:
    """Supprime les colonnes et tables ajoutees pour l'integration Pennylane."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Supprimer table 'pennylane_pending_reconciliation'
    # ─────────────────────────────────────────────────────────────────────────

    if 'pennylane_pending_reconciliation' in inspector.get_table_names():
        # Supprimer les index
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('pennylane_pending_reconciliation')]

        if 'ix_pennylane_pending_status_created' in existing_indexes:
            op.drop_index('ix_pennylane_pending_status_created', table_name='pennylane_pending_reconciliation')
        if 'ix_pennylane_pending_suggested_achat' in existing_indexes:
            op.drop_index('ix_pennylane_pending_suggested_achat', table_name='pennylane_pending_reconciliation')
        if 'ix_pennylane_pending_created_at' in existing_indexes:
            op.drop_index('ix_pennylane_pending_created_at', table_name='pennylane_pending_reconciliation')
        if 'ix_pennylane_pending_code_analytique' in existing_indexes:
            op.drop_index('ix_pennylane_pending_code_analytique', table_name='pennylane_pending_reconciliation')
        if 'ix_pennylane_pending_status' in existing_indexes:
            op.drop_index('ix_pennylane_pending_status', table_name='pennylane_pending_reconciliation')
        if 'ix_pennylane_pending_invoice_id' in existing_indexes:
            op.drop_index('ix_pennylane_pending_invoice_id', table_name='pennylane_pending_reconciliation')

        op.drop_table('pennylane_pending_reconciliation')

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Supprimer table 'pennylane_sync_log'
    # ─────────────────────────────────────────────────────────────────────────

    if 'pennylane_sync_log' in inspector.get_table_names():
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('pennylane_sync_log')]

        if 'ix_pennylane_sync_log_type_status' in existing_indexes:
            op.drop_index('ix_pennylane_sync_log_type_status', table_name='pennylane_sync_log')
        if 'ix_pennylane_sync_log_started_at' in existing_indexes:
            op.drop_index('ix_pennylane_sync_log_started_at', table_name='pennylane_sync_log')
        if 'ix_pennylane_sync_log_status' in existing_indexes:
            op.drop_index('ix_pennylane_sync_log_status', table_name='pennylane_sync_log')
        if 'ix_pennylane_sync_log_sync_type' in existing_indexes:
            op.drop_index('ix_pennylane_sync_log_sync_type', table_name='pennylane_sync_log')

        op.drop_table('pennylane_sync_log')

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Supprimer table 'pennylane_mapping_analytique'
    # ─────────────────────────────────────────────────────────────────────────

    if 'pennylane_mapping_analytique' in inspector.get_table_names():
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('pennylane_mapping_analytique')]

        if 'ix_pennylane_mapping_analytique_code' in existing_indexes:
            op.drop_index('ix_pennylane_mapping_analytique_code', table_name='pennylane_mapping_analytique')
        if 'ix_pennylane_mapping_analytique_chantier_id' in existing_indexes:
            op.drop_index('ix_pennylane_mapping_analytique_chantier_id', table_name='pennylane_mapping_analytique')

        op.drop_table('pennylane_mapping_analytique')

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Supprimer colonnes table 'fournisseurs'
    # ─────────────────────────────────────────────────────────────────────────

    existing_columns_fournisseurs = [c['name'] for c in inspector.get_columns('fournisseurs')]
    existing_indexes_fournisseurs = [idx['name'] for idx in inspector.get_indexes('fournisseurs')]

    if 'derniere_sync_pennylane' in existing_columns_fournisseurs:
        op.drop_column('fournisseurs', 'derniere_sync_pennylane')

    if 'source_donnee' in existing_columns_fournisseurs:
        if 'ix_fournisseurs_source_donnee' in existing_indexes_fournisseurs:
            op.drop_index('ix_fournisseurs_source_donnee', table_name='fournisseurs')
        op.drop_column('fournisseurs', 'source_donnee')

    if 'bic' in existing_columns_fournisseurs:
        op.drop_column('fournisseurs', 'bic')

    if 'iban' in existing_columns_fournisseurs:
        op.drop_column('fournisseurs', 'iban')

    if 'delai_paiement_jours' in existing_columns_fournisseurs:
        op.drop_column('fournisseurs', 'delai_paiement_jours')

    if 'pennylane_supplier_id' in existing_columns_fournisseurs:
        if 'ix_fournisseurs_pennylane_supplier_id' in existing_indexes_fournisseurs:
            op.drop_index('ix_fournisseurs_pennylane_supplier_id', table_name='fournisseurs')
        op.drop_column('fournisseurs', 'pennylane_supplier_id')

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Supprimer colonnes table 'factures_client'
    # ─────────────────────────────────────────────────────────────────────────

    existing_columns_factures = [c['name'] for c in inspector.get_columns('factures_client')]
    existing_indexes_factures = [idx['name'] for idx in inspector.get_indexes('factures_client')]

    if 'pennylane_invoice_id' in existing_columns_factures:
        if 'ix_factures_client_pennylane_invoice_id' in existing_indexes_factures:
            op.drop_index('ix_factures_client_pennylane_invoice_id', table_name='factures_client')
        op.drop_column('factures_client', 'pennylane_invoice_id')

    if 'montant_encaisse' in existing_columns_factures:
        op.drop_column('factures_client', 'montant_encaisse')

    if 'date_paiement_reel' in existing_columns_factures:
        if 'ix_factures_client_date_paiement_reel' in existing_indexes_factures:
            op.drop_index('ix_factures_client_date_paiement_reel', table_name='factures_client')
        op.drop_column('factures_client', 'date_paiement_reel')

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Supprimer colonnes table 'achats'
    # ─────────────────────────────────────────────────────────────────────────

    existing_columns_achats = [c['name'] for c in inspector.get_columns('achats')]
    existing_indexes_achats = [idx['name'] for idx in inspector.get_indexes('achats')]

    # Index composite
    if 'ix_achats_chantier_pennylane' in existing_indexes_achats:
        op.drop_index('ix_achats_chantier_pennylane', table_name='achats')

    if 'source_donnee' in existing_columns_achats:
        if 'ix_achats_source_donnee' in existing_indexes_achats:
            op.drop_index('ix_achats_source_donnee', table_name='achats')
        op.drop_column('achats', 'source_donnee')

    if 'pennylane_invoice_id' in existing_columns_achats:
        if 'ix_achats_pennylane_invoice_id' in existing_indexes_achats:
            op.drop_index('ix_achats_pennylane_invoice_id', table_name='achats')
        op.drop_column('achats', 'pennylane_invoice_id')

    if 'date_facture_reelle' in existing_columns_achats:
        op.drop_column('achats', 'date_facture_reelle')

    if 'montant_ht_reel' in existing_columns_achats:
        op.drop_column('achats', 'montant_ht_reel')
