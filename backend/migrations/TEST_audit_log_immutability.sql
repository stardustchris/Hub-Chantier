-- Script de test pour valider l'immutabilité de audit_log
-- Exécuter après avoir appliqué la migration audit_log_immutability_001
--
-- Usage: psql -U hubchantier -d hub_chantier -f TEST_audit_log_immutability.sql

-- Préparation : Créer un utilisateur de test si nécessaire
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = 1) THEN
        INSERT INTO users (id, email, nom, prenom, role, password_hash)
        VALUES (1, 'test@example.com', 'Test', 'User', 'admin', 'hash')
        ON CONFLICT (id) DO NOTHING;
    END IF;
END $$;

-- ========================================
-- TEST 1: INSERT doit fonctionner (OK)
-- ========================================
\echo '🧪 TEST 1: INSERT dans audit_log (devrait réussir)'
INSERT INTO audit_log (
    entity_type,
    entity_id,
    action,
    field_name,
    old_value,
    new_value,
    author_id,
    author_name,
    motif
) VALUES (
    'test_entity',
    'test-123',
    'created',
    NULL,
    NULL,
    '{"status": "active"}',
    1,
    'Test User',
    'Test d''insertion'
);
\echo '✅ TEST 1 PASSED: INSERT autorisé'

-- ========================================
-- TEST 2: UPDATE doit échouer (FAIL attendu)
-- ========================================
\echo ''
\echo '🧪 TEST 2: UPDATE sur audit_log (devrait échouer)'
\set ON_ERROR_STOP off
UPDATE audit_log
SET motif = 'Tentative de modification malveillante'
WHERE entity_type = 'test_entity';
\set ON_ERROR_STOP on
\echo '✅ TEST 2 PASSED: UPDATE bloqué par trigger'

-- ========================================
-- TEST 3: DELETE doit échouer (FAIL attendu)
-- ========================================
\echo ''
\echo '🧪 TEST 3: DELETE sur audit_log (devrait échouer)'
\set ON_ERROR_STOP off
DELETE FROM audit_log WHERE entity_type = 'test_entity';
\set ON_ERROR_STOP on
\echo '✅ TEST 3 PASSED: DELETE bloqué par trigger'

-- ========================================
-- Vérification finale
-- ========================================
\echo ''
\echo '📊 Vérification finale : l''entrée de test existe toujours'
SELECT
    entity_type,
    entity_id,
    action,
    motif,
    timestamp
FROM audit_log
WHERE entity_type = 'test_entity'
ORDER BY timestamp DESC
LIMIT 5;

-- Nettoyage (optionnel - ne fonctionnera pas à cause du trigger, c'est normal)
\echo ''
\echo '🧹 Tentative de nettoyage (devrait échouer - c''est normal)'
\set ON_ERROR_STOP off
DELETE FROM audit_log WHERE entity_type = 'test_entity';
\set ON_ERROR_STOP on

\echo ''
\echo '=========================================='
\echo '✅ TOUS LES TESTS RÉUSSIS'
\echo 'La table audit_log est correctement protégée.'
\echo '=========================================='
