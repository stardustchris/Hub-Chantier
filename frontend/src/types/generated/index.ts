/**
 * Types générés automatiquement depuis le schéma OpenAPI de l'API FastAPI
 *
 * ⚠️ NE PAS MODIFIER CE FICHIER MANUELLEMENT ⚠️
 *
 * Ce fichier est regénéré automatiquement à partir du schéma OpenAPI de l'API.
 * Toute modification manuelle sera écrasée lors de la prochaine génération.
 *
 * ---
 *
 * ## Comment regénérer les types
 *
 * 1. Assurez-vous que Docker Compose est démarré:
 *    ```bash
 *    docker compose up -d
 *    ```
 *
 * 2. Depuis le dossier frontend, exécutez:
 *    ```bash
 *    npm run generate:types
 *    ```
 *
 * Ou directement depuis la racine du projet:
 *    ```bash
 *    ./scripts/generate-api-types.sh
 *    ```
 *
 * ---
 *
 * ## Migration progressive
 *
 * Les types manuels actuels dans `types/index.ts` seront progressivement
 * migrés vers l'utilisation des types générés automatiquement.
 *
 * Cela garantit:
 * - Cohérence totale entre backend et frontend
 * - Détection automatique des breaking changes d'API
 * - Réduction de la duplication de code
 * - Auto-complétion améliorée dans l'IDE
 *
 * ---
 *
 * @packageDocumentation
 */

// Re-export all types from the generated API schema
export * from './api'
