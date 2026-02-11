"""Audit constraints financiers: retenue garantie, TVA discrete, autoliquidation ST.

P1-5: La retenue de garantie a 10% est illegale (loi 71-584, plafond 5%).
      Supprime la valeur 10 du CHECK sur devis.retenue_garantie_pct.
P2-6: Les CHECK TVA sur achats et situations_travaux sont trop permissifs (0-100%).
      Remplace par les taux TVA legaux francais: 0, 2.1, 5.5, 10, 20.
P2-7: Autoliquidation sous-traitance: si type_achat = 'sous_traitance',
      alors taux_tva doit etre 0 (art. 283-2 nonies CGI).

Revision ID: audit_financial_constraints
Revises: fix_coeff_fg_unit
Create Date: 2026-02-11
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "audit_financial_constraints"
down_revision = "fix_coeff_fg_unit"
branch_labels = None
depends_on = None


def upgrade():
    # ── P1-5: Retenue de garantie devis - supprimer 10% illegal ──────────
    # Loi 71-584 art. 1 : la retenue de garantie ne peut exceder 5%.
    # Mise a jour des donnees existantes AVANT le nouveau CHECK.
    op.execute(
        "UPDATE devis SET retenue_garantie_pct = 5 "
        "WHERE retenue_garantie_pct = 10"
    )
    op.execute(
        "ALTER TABLE devis DROP CONSTRAINT "
        "IF EXISTS check_devis_retenue_garantie_valeurs"
    )
    op.execute(
        "ALTER TABLE devis ADD CONSTRAINT check_devis_retenue_garantie_valeurs "
        "CHECK (retenue_garantie_pct IN (0, 5))"
    )

    # ── P2-6: TVA valeurs discretes sur achats ───────────────────────────
    # Taux TVA legaux francais (CGI art. 278 et suivants):
    # 0% (exonere/autoliquidation), 2.1% (presse), 5.5% (renovation),
    # 10% (travaux amelioration), 20% (taux normal).
    op.execute(
        "ALTER TABLE achats DROP CONSTRAINT "
        "IF EXISTS check_achats_tva_range"
    )
    op.execute(
        "ALTER TABLE achats ADD CONSTRAINT check_achats_tva_range "
        "CHECK (taux_tva IN (0, 2.1, 5.5, 10, 20))"
    )

    # ── P2-6: TVA valeurs discretes sur situations_travaux ───────────────
    op.execute(
        "ALTER TABLE situations_travaux DROP CONSTRAINT "
        "IF EXISTS check_situations_travaux_tva_range"
    )
    op.execute(
        "ALTER TABLE situations_travaux ADD CONSTRAINT check_situations_travaux_tva_range "
        "CHECK (taux_tva IN (0, 2.1, 5.5, 10, 20))"
    )

    # ── P2-7: Autoliquidation sous-traitance ─────────────────────────────
    # Art. 283-2 nonies CGI : le sous-traitant ne facture pas de TVA,
    # c'est le donneur d'ordre qui l'autoliquide.
    op.execute(
        "ALTER TABLE achats ADD CONSTRAINT check_achats_autoliquidation_st "
        "CHECK (type_achat != 'sous_traitance' OR taux_tva = 0)"
    )


def downgrade():
    # ── P2-7: Supprimer contrainte autoliquidation ───────────────────────
    op.execute(
        "ALTER TABLE achats DROP CONSTRAINT "
        "IF EXISTS check_achats_autoliquidation_st"
    )

    # ── P2-6: Restaurer CHECK TVA permissif sur situations_travaux ───────
    op.execute(
        "ALTER TABLE situations_travaux DROP CONSTRAINT "
        "IF EXISTS check_situations_travaux_tva_range"
    )
    op.execute(
        "ALTER TABLE situations_travaux ADD CONSTRAINT check_situations_travaux_tva_range "
        "CHECK (taux_tva >= 0 AND taux_tva <= 100)"
    )

    # ── P2-6: Restaurer CHECK TVA permissif sur achats ───────────────────
    op.execute(
        "ALTER TABLE achats DROP CONSTRAINT "
        "IF EXISTS check_achats_tva_range"
    )
    op.execute(
        "ALTER TABLE achats ADD CONSTRAINT check_achats_tva_range "
        "CHECK (taux_tva >= 0 AND taux_tva <= 100)"
    )

    # ── P1-5: Restaurer CHECK retenue de garantie avec 10% ──────────────
    op.execute(
        "ALTER TABLE devis DROP CONSTRAINT "
        "IF EXISTS check_devis_retenue_garantie_valeurs"
    )
    op.execute(
        "ALTER TABLE devis ADD CONSTRAINT check_devis_retenue_garantie_valeurs "
        "CHECK (retenue_garantie_pct IN (0, 5, 10))"
    )
