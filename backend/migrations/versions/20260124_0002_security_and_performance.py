"""Security and performance improvements.

- Add chantier_conducteurs and chantier_chefs join tables (N+1 fix)
- Add soft delete to users (RGPD compliance)
- Add missing indexes for performance
- Add foreign keys for data integrity

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-24 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply security and performance improvements."""

    # =========================================================================
    # 1. CHANTIER RESPONSABLES - Tables de jointure (fix N+1)
    # =========================================================================

    # Table chantier_conducteurs
    op.create_table(
        'chantier_conducteurs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chantier_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['chantier_id'], ['chantiers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('chantier_id', 'user_id', name='uq_chantier_conducteur'),
    )
    op.create_index('ix_chantier_conducteurs_user_id', 'chantier_conducteurs', ['user_id'])
    op.create_index('ix_chantier_conducteurs_chantier_id', 'chantier_conducteurs', ['chantier_id'])

    # Table chantier_chefs
    op.create_table(
        'chantier_chefs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chantier_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['chantier_id'], ['chantiers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('chantier_id', 'user_id', name='uq_chantier_chef'),
    )
    op.create_index('ix_chantier_chefs_user_id', 'chantier_chefs', ['user_id'])
    op.create_index('ix_chantier_chefs_chantier_id', 'chantier_chefs', ['chantier_id'])

    # =========================================================================
    # 2. USERS - Soft delete (RGPD Art. 17)
    # =========================================================================

    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])

    # =========================================================================
    # 3. POSTS - Index manquants pour performance feed
    # =========================================================================

    # Index sur author_id pour recuperer les posts d'un utilisateur
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_posts_author_id ON posts(author_id);
    """)

    # Index sur created_at pour tri chronologique du feed
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_posts_created_at ON posts(created_at DESC);
    """)

    # Index composite pour filtrage par chantier + date
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_posts_chantier_created
        ON posts(chantier_id, created_at DESC) WHERE chantier_id IS NOT NULL;
    """)

    # =========================================================================
    # 4. COMMENTS - Index et FK manquantes
    # =========================================================================

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_comments_post_id ON comments(post_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_comments_author_id ON comments(author_id);
    """)

    # =========================================================================
    # 5. AFFECTATIONS - Index pour planning
    # =========================================================================

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_affectations_date ON affectations(date);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_affectations_user_date
        ON affectations(utilisateur_id, date);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_affectations_chantier_date
        ON affectations(chantier_id, date);
    """)

    # =========================================================================
    # 6. POINTAGES - Index pour feuilles d'heures
    # =========================================================================

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_pointages_user_date
        ON pointages(utilisateur_id, date_pointage);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_pointages_chantier_date
        ON pointages(chantier_id, date_pointage);
    """)

    # =========================================================================
    # 7. DOCUMENTS - Index pour GED
    # =========================================================================

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_documents_chantier_id ON documents(chantier_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_documents_dossier_id ON documents(dossier_id);
    """)

    # =========================================================================
    # 8. TACHES - Index pour suivi
    # =========================================================================

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_taches_chantier_id ON taches(chantier_id);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_taches_parent_id ON taches(parent_id);
    """)


def downgrade() -> None:
    """Revert security and performance improvements."""

    # Drop taches indexes
    op.execute("DROP INDEX IF EXISTS ix_taches_parent_id;")
    op.execute("DROP INDEX IF EXISTS ix_taches_chantier_id;")

    # Drop documents indexes
    op.execute("DROP INDEX IF EXISTS ix_documents_dossier_id;")
    op.execute("DROP INDEX IF EXISTS ix_documents_chantier_id;")

    # Drop pointages indexes
    op.execute("DROP INDEX IF EXISTS ix_pointages_chantier_date;")
    op.execute("DROP INDEX IF EXISTS ix_pointages_user_date;")

    # Drop affectations indexes
    op.execute("DROP INDEX IF EXISTS ix_affectations_chantier_date;")
    op.execute("DROP INDEX IF EXISTS ix_affectations_user_date;")
    op.execute("DROP INDEX IF EXISTS ix_affectations_date;")

    # Drop comments indexes
    op.execute("DROP INDEX IF EXISTS ix_comments_author_id;")
    op.execute("DROP INDEX IF EXISTS ix_comments_post_id;")

    # Drop posts indexes
    op.execute("DROP INDEX IF EXISTS ix_posts_chantier_created;")
    op.execute("DROP INDEX IF EXISTS ix_posts_created_at;")
    op.execute("DROP INDEX IF EXISTS ix_posts_author_id;")

    # Drop users soft delete
    op.drop_index('ix_users_deleted_at', table_name='users')
    op.drop_column('users', 'deleted_at')

    # Drop chantier_chefs
    op.drop_index('ix_chantier_chefs_chantier_id')
    op.drop_index('ix_chantier_chefs_user_id')
    op.drop_table('chantier_chefs')

    # Drop chantier_conducteurs
    op.drop_index('ix_chantier_conducteurs_chantier_id')
    op.drop_index('ix_chantier_conducteurs_user_id')
    op.drop_table('chantier_conducteurs')
