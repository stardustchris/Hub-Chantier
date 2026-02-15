# Types générés automatiquement depuis l'API

Ce dossier contient les types TypeScript générés automatiquement depuis le schéma OpenAPI de l'API FastAPI.

## 🔄 Génération

### Prérequis

1. Docker Compose démarré:
   ```bash
   docker compose up -d
   ```

2. Vérifier que l'API est accessible:
   ```bash
   curl http://localhost:8000/api/health
   ```

### Commande

Depuis le dossier `frontend/`:
```bash
npm run generate:types
```

Ou depuis la racine du projet:
```bash
./scripts/generate-api-types.sh
```

## 📁 Structure

```
types/generated/
├── README.md         # Ce fichier
├── .gitignore        # Exclut api.ts du versioning
├── index.ts          # Barrel export (versionné)
└── api.ts            # Types générés (non versionné)
```

## ⚠️ Règles importantes

### NE PAS modifier manuellement

- `api.ts` est regénéré à chaque exécution du script
- Toute modification manuelle sera écrasée
- Le fichier n'est **pas versionné** (.gitignore)

### Quand regénérer

Regénérez les types après:
- Modification des modèles Pydantic dans le backend
- Ajout de nouveaux endpoints
- Modification des schémas de réponse/requête
- Pull de changements API depuis Git

### Usage dans le code

```typescript
// Import des types générés
import { components } from '@/types/generated'

// Exemple d'utilisation
type User = components['schemas']['User']
type ChantierCreate = components['schemas']['ChantierCreate']
type APIError = components['schemas']['HTTPValidationError']
```

## 🔗 Intégration

### Structure OpenAPI

Les types suivent la structure OpenAPI standard:

- `components.schemas` - Schémas de données (modèles Pydantic)
- `paths['/endpoint'].get.responses['200'].content` - Réponses par endpoint
- `paths['/endpoint'].post.requestBody` - Corps de requête

### Exemple complet

```typescript
import { paths, components } from '@/types/generated'

// Type d'une réponse endpoint
type GetChantiersResponse = paths['/v1/chantiers']['get']['responses']['200']['content']['application/json']

// Type d'un schéma
type Chantier = components['schemas']['Chantier']

// Type d'une requête
type CreateChantierBody = paths['/v1/chantiers']['post']['requestBody']['content']['application/json']
```

## 🚀 Migration progressive

Les types manuels actuels dans `types/index.ts` seront progressivement remplacés.

### Avantages

✅ Cohérence totale frontend/backend
✅ Détection automatique des breaking changes
✅ Réduction de la duplication de code
✅ Auto-complétion améliorée dans l'IDE
✅ Documentation inline depuis les docstrings Python

### Stratégie

1. **Phase 1** (Actuelle): Pipeline de génération en place
2. **Phase 2**: Migration des composants critiques
3. **Phase 3**: Dépréciation progressive des types manuels
4. **Phase 4**: Suppression complète des duplications

## 🛠️ Troubleshooting

### Erreur: "API non accessible"

```bash
# Vérifier que Docker est démarré
docker compose ps

# Vérifier les logs de l'API
docker compose logs -f api

# Redémarrer si nécessaire
docker compose restart api
```

### Erreur: "openapi-typescript not found"

```bash
cd frontend
npm install --save-dev openapi-typescript
```

### Types incomplets ou incorrects

1. Vérifier le schéma OpenAPI dans le navigateur:
   ```
   http://localhost:8000/openapi.json
   ```

2. Vérifier la documentation interactive:
   ```
   http://localhost:8000/docs
   ```

3. Regénérer après rebuild du backend:
   ```bash
   docker compose build api
   docker compose up -d api
   npm run generate:types
   ```

## 📚 Ressources

- [Documentation openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [OpenAPI Specification](https://swagger.io/specification/)
- [FastAPI Schema Generation](https://fastapi.tiangolo.com/advanced/extending-openapi/)
