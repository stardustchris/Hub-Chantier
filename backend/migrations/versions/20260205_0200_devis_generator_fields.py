"""Ajout champs generateur de devis.

Nouveaux champs: acompte_pct, echeance, moyens_paiement,
date_visite, date_debut_travaux, duree_estimee_jours,
notes_bas_page, nom_interne.

Revision ID: devis_generator_fields
Revises: tva_context_chantier_001
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "devis_generator_fields"
down_revision = "tva_context_chantier_001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("devis", sa.Column("acompte_pct", sa.Numeric(5, 2), nullable=False, server_default="30"))
    op.add_column("devis", sa.Column("echeance", sa.String(50), nullable=False, server_default="30_jours_fin_mois"))
    op.add_column("devis", sa.Column("moyens_paiement", postgresql.JSON(), nullable=True))
    op.add_column("devis", sa.Column("date_visite", sa.Date(), nullable=True))
    op.add_column("devis", sa.Column("date_debut_travaux", sa.Date(), nullable=True))
    op.add_column("devis", sa.Column("duree_estimee_jours", sa.Integer(), nullable=True))
    op.add_column("devis", sa.Column("notes_bas_page", sa.Text(), nullable=True))
    op.add_column("devis", sa.Column("nom_interne", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("devis", "nom_interne")
    op.drop_column("devis", "notes_bas_page")
    op.drop_column("devis", "duree_estimee_jours")
    op.drop_column("devis", "date_debut_travaux")
    op.drop_column("devis", "date_visite")
    op.drop_column("devis", "moyens_paiement")
    op.drop_column("devis", "echeance")
    op.drop_column("devis", "acompte_pct")
