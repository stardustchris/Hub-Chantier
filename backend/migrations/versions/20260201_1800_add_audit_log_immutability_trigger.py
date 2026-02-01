"""Add immutability trigger to audit_log table

Revision ID: audit_log_immutability_001
Revises: audit_log_001
Create Date: 2026-02-01 18:00:00.000000

Cette migration ajoute des triggers PostgreSQL pour garantir l'immutabilité
de la table audit_log. Les entrées d'audit ne peuvent jamais être modifiées
ou supprimées après leur création.

Sécurité : Protection contre les altérations malveillantes de l'historique d'audit.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "audit_log_immutability_001"
down_revision = "audit_log_001"
branch_labels = None
depends_on = None


def upgrade():
    """
    Ajoute les triggers d'immutabilité à la table audit_log.

    Crée :
    1. Une fonction PL/pgSQL qui lève une exception
    2. Un trigger BEFORE UPDATE qui empêche toute modification
    3. Un trigger BEFORE DELETE qui empêche toute suppression

    Seul INSERT reste autorisé (table append-only).
    """
    # Création de la fonction de trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Les entrées d''audit sont immuables. Suppression et modification interdites.';
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Trigger pour empêcher les UPDATE
    op.execute("""
        CREATE TRIGGER audit_log_prevent_update
            BEFORE UPDATE ON audit_log
            FOR EACH ROW
            EXECUTE FUNCTION prevent_audit_log_modification();
    """)

    # Trigger pour empêcher les DELETE
    op.execute("""
        CREATE TRIGGER audit_log_prevent_delete
            BEFORE DELETE ON audit_log
            FOR EACH ROW
            EXECUTE FUNCTION prevent_audit_log_modification();
    """)


def downgrade():
    """
    Supprime les triggers et la fonction d'immutabilité.

    Attention : Cette action rend la table audit_log à nouveau modifiable,
    ce qui peut poser des risques de sécurité. À n'utiliser qu'en développement.
    """
    # Suppression des triggers (ordre inverse de création)
    op.execute("DROP TRIGGER IF EXISTS audit_log_prevent_delete ON audit_log;")
    op.execute("DROP TRIGGER IF EXISTS audit_log_prevent_update ON audit_log;")

    # Suppression de la fonction
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_modification();")
