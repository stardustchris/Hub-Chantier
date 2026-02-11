"""Rendre fournisseur_id et date_commande nullable sur achats.

Un achat au stade 'demande' peut ne pas encore avoir de fournisseur
ni de date de commande. Ces champs sont renseignes lors du passage
en statut 'commande'. Aligne la DB avec le domaine et l'API.

Revision ID: nullable_fournisseur_date
Revises: remove_tva_21
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "nullable_fournisseur_date"
down_revision = "remove_tva_21"
branch_labels = None
depends_on = None


def upgrade():
    # Rendre fournisseur_id nullable
    op.alter_column(
        "achats",
        "fournisseur_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    # Rendre date_commande nullable
    op.alter_column(
        "achats",
        "date_commande",
        existing_type=sa.Date(),
        nullable=True,
    )
    # Supprimer la contrainte de coherence date qui reference date_commande
    # car date_commande peut maintenant etre NULL
    op.execute(
        "ALTER TABLE achats DROP CONSTRAINT "
        "IF EXISTS check_achats_date_livraison_coherente"
    )
    op.execute(
        "ALTER TABLE achats ADD CONSTRAINT check_achats_date_livraison_coherente "
        "CHECK (date_commande IS NULL OR date_livraison_prevue IS NULL "
        "OR date_livraison_prevue >= date_commande)"
    )


def downgrade():
    # Restaurer la contrainte originale
    op.execute(
        "ALTER TABLE achats DROP CONSTRAINT "
        "IF EXISTS check_achats_date_livraison_coherente"
    )
    op.execute(
        "ALTER TABLE achats ADD CONSTRAINT check_achats_date_livraison_coherente "
        "CHECK (date_livraison_prevue IS NULL OR date_livraison_prevue >= date_commande)"
    )
    # Remettre NOT NULL (avec valeur par defaut pour les NULL existants)
    op.execute(
        "UPDATE achats SET date_commande = created_at::date "
        "WHERE date_commande IS NULL"
    )
    op.alter_column(
        "achats",
        "date_commande",
        existing_type=sa.Date(),
        nullable=False,
    )
    op.execute(
        "UPDATE achats SET fournisseur_id = 1 "
        "WHERE fournisseur_id IS NULL"
    )
    op.alter_column(
        "achats",
        "fournisseur_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
