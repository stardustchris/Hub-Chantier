-- Migration: DEV-03, DEV-05, DEV-06 - Structure devis, debourses, marges
-- Date: 2026-02-15
-- Description:
--   DEV-03: Ensure arborescence lots/chapitres/lignes avec numerotation
--   DEV-05: Ensure debourses detailles par ligne
--   DEV-06: Ensure marges multi-niveaux (ligne > lot > type debourse > global)
--
-- Note: Les tables et colonnes existent deja via les modeles SQLAlchemy.
-- Cette migration ajoute des index et contraintes supplementaires pour
-- la performance et l'integrite des nouvelles features.

-- ─────────────────────────────────────────────────────────────────────────────
-- DEV-03: Index pour la recherche d'arborescence (lots avec parent)
-- ─────────────────────────────────────────────────────────────────────────────

-- Index composite pour la recherche des sous-chapitres d'un lot parent
CREATE INDEX IF NOT EXISTS ix_lots_devis_parent_ordre
    ON lots_devis (parent_id, ordre)
    WHERE deleted_at IS NULL;

-- Index partiel pour les lots racine (parent_id IS NULL) d'un devis
CREATE INDEX IF NOT EXISTS ix_lots_devis_devis_racine
    ON lots_devis (devis_id, ordre)
    WHERE parent_id IS NULL AND deleted_at IS NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- DEV-05: Index pour les debourses detailles
-- ─────────────────────────────────────────────────────────────────────────────

-- Index pour la somme des debourses par ligne (debourse sec)
CREATE INDEX IF NOT EXISTS ix_debourses_detail_ligne_montant
    ON debourses_detail (ligne_devis_id, montant);

-- ─────────────────────────────────────────────────────────────────────────────
-- DEV-06: Contraintes pour les marges par type de debourse
-- ─────────────────────────────────────────────────────────────────────────────

-- Valider que les marges par type sont positives ou nulles
ALTER TABLE devis
    ADD CONSTRAINT IF NOT EXISTS check_devis_marge_moe_positive
        CHECK (marge_moe_pct IS NULL OR marge_moe_pct >= 0);

ALTER TABLE devis
    ADD CONSTRAINT IF NOT EXISTS check_devis_marge_materiaux_positive
        CHECK (marge_materiaux_pct IS NULL OR marge_materiaux_pct >= 0);

ALTER TABLE devis
    ADD CONSTRAINT IF NOT EXISTS check_devis_marge_st_positive
        CHECK (marge_sous_traitance_pct IS NULL OR marge_sous_traitance_pct >= 0);

ALTER TABLE devis
    ADD CONSTRAINT IF NOT EXISTS check_devis_marge_materiel_positive
        CHECK (marge_materiel_pct IS NULL OR marge_materiel_pct >= 0);

ALTER TABLE devis
    ADD CONSTRAINT IF NOT EXISTS check_devis_marge_deplacement_positive
        CHECK (marge_deplacement_pct IS NULL OR marge_deplacement_pct >= 0);

-- ─────────────────────────────────────────────────────────────────────────────
-- DEV-05: Contrainte pour le taux_horaire MOE coherent
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE debourses_detail
    ADD CONSTRAINT IF NOT EXISTS check_debourses_moe_taux_horaire
        CHECK (
            type_debourse != 'moe'
            OR taux_horaire IS NOT NULL
        );

-- ─────────────────────────────────────────────────────────────────────────────
-- Commentaires documentation
-- ─────────────────────────────────────────────────────────────────────────────

COMMENT ON INDEX ix_lots_devis_parent_ordre IS
    'DEV-03: Recherche rapide des sous-chapitres par parent, ordonnee';

COMMENT ON INDEX ix_lots_devis_devis_racine IS
    'DEV-03: Recherche rapide des lots racine d''un devis';

COMMENT ON INDEX ix_debourses_detail_ligne_montant IS
    'DEV-05: Calcul rapide du debourse sec par ligne';
