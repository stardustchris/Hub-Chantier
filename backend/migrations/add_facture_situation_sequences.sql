-- Migration: Sequences PostgreSQL pour numerotation atomique
-- Resout la race condition sur FAC-YYYY-NNNN et SIT-YYYY-NNNN
--
-- Usage:
--   INSERT INTO numero_compteurs (prefixe, annee, chantier_id, dernier_numero)
--   VALUES ('FAC', 2026, 0, 0)
--   ON CONFLICT (prefixe, annee, chantier_id) DO UPDATE
--   SET dernier_numero = numero_compteurs.dernier_numero + 1
--   RETURNING dernier_numero;
--
-- Pour les factures : chantier_id = 0 (numerotation globale)
-- Pour les situations : chantier_id = <id_chantier> (numerotation par chantier)

-- Table de compteurs atomiques pour la numerotation
CREATE TABLE IF NOT EXISTS numero_compteurs (
    prefixe VARCHAR(10) NOT NULL,       -- 'FAC' ou 'SIT'
    annee INTEGER NOT NULL,
    chantier_id INTEGER NOT NULL DEFAULT 0,  -- 0 pour factures (globales), >0 pour situations (par chantier)
    dernier_numero INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (prefixe, annee, chantier_id)
);

-- Index pour les requetes frequentes
CREATE INDEX IF NOT EXISTS idx_numero_compteurs_prefixe_annee
    ON numero_compteurs (prefixe, annee);

-- Commentaires
COMMENT ON TABLE numero_compteurs IS 'Compteurs atomiques pour numerotation factures (FAC-YYYY-NNNN) et situations (SIT-YYYY-NNNN)';
COMMENT ON COLUMN numero_compteurs.prefixe IS 'Prefixe du numero: FAC pour factures, SIT pour situations';
COMMENT ON COLUMN numero_compteurs.annee IS 'Annee du compteur';
COMMENT ON COLUMN numero_compteurs.chantier_id IS '0 pour factures (globales), ID chantier pour situations (par chantier)';
COMMENT ON COLUMN numero_compteurs.dernier_numero IS 'Dernier numero attribue';
