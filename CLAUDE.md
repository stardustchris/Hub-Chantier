# Hub Chantier - Instructions Claude

> Ce fichier est lu au debut de chaque session. Les regles ci-dessous sont OBLIGATOIRES.

## ⛔ LECTURE OBLIGATOIRE AVANT TOUTE ACTION

**LIRE ces fichiers AVANT de commencer :**

1. Ce fichier (`CLAUDE.md`) - regles de session
2. `.claude/agents.md` - workflow agents detaille

**NE PAS coder, NE PAS planifier sans avoir lu ces deux fichiers.**

---

## ENVIRONNEMENT DOCKER (mode par defaut)

Le projet tourne sur Docker. Toujours verifier/lancer Docker AVANT de coder.

### Demarrage

```bash
docker compose up -d          # Lance db + api + frontend + adminer
docker compose ps              # Verifier que tout est "running"
```

### Services et ports

| Service | URL | Description |
|---------|-----|-------------|
| **frontend** | http://localhost | Nginx + SPA React (production build) |
| **api** | http://localhost:8000 | FastAPI backend |
| **db** | localhost:5432 | PostgreSQL 16 |
| **adminer** | http://localhost:8080 | Admin BDD |

### Apres modification de code

```bash
# Backend : rebuild + restart
docker compose build api && docker compose up -d api

# Frontend : rebuild + restart + VIDER LE CACHE NAVIGATEUR
docker compose build frontend && docker compose up -d frontend
```

⚠️ **Service Worker (PWA)** : Apres chaque rebuild frontend, le navigateur sert l'ancienne version en cache. Il FAUT vider le Service Worker et les caches du navigateur (via DevTools ou MCP Chrome).

### Logs

```bash
docker compose logs -f api       # Logs backend
docker compose logs -f frontend  # Logs nginx
```

---

## REGLES OBLIGATOIRES

### 1. Debut de session (AVANT tout dev)

**Mode Docker (par defaut)** :
```bash
docker compose ps                # Verifier que les containers tournent
docker compose logs api --tail=20  # Verifier que l'API repond
curl -s http://localhost/api/health  # Health check
```

**Mode local (si Docker non disponible)** :
```bash
cd backend && pip install -r requirements.txt && python -m pytest tests/unit -v --tb=short
cd ../frontend && npm install && npm run build
```

**NE PAS commencer si ces commandes echouent.**

---

### 2. Workflow SYSTEMATIQUE avec agents

⚠️ **REGLE ABSOLUE** : Je (Claude) ne code JAMAIS seul. Les agents m'assistent SYSTEMATIQUEMENT.

Voir `.claude/agents.md` pour le workflow detaille complet (301 lignes).

#### 📖 Étape 0 : Lecture specs
- Lire `docs/SPECIFICATIONS.md` pour comprendre la fonctionnalité

#### 🔨 Étape 1 : IMPLEMENTATION (agents selon contexte)

Je lance les agents d'implémentation **SELON LE CONTEXTE** :

| Si modification de... | Agent à lancer | Commande |
|----------------------|----------------|----------|
| Base de données (nouvelles tables/colonnes) | **sql-pro** | `Task(subagent_type="general-purpose", prompt="Lis .claude/agents/sql-pro.md...")` |
| Code backend (`*.py`) | **python-pro** | `Task(subagent_type="general-purpose", prompt="Lis .claude/agents/python-pro.md...")` |
| Code frontend (`*.ts`, `*.tsx`) | **typescript-pro** | `Task(subagent_type="general-purpose", prompt="Lis .claude/agents/typescript-pro.md...")` |

#### ✅ Étape 2 : VALIDATION (4 agents OBLIGATOIRES avant commit)

Je lance **TOUJOURS** ces 4 agents, dans l'ordre :

1. **architect-reviewer** → Objectif : PASS (0 violation Clean Architecture)
2. **test-automator** → Objectif : >= 90% couverture
3. **code-reviewer** → Objectif : APPROVED (qualité + conventions)
4. **security-auditor** → Objectif : PASS (0 finding CRITICAL/HIGH)

**Commande pour chaque agent** :
```python
Task(subagent_type="general-purpose",
     description="Courte description (3-5 mots)",
     prompt="Lis .claude/agents/NOM_AGENT.md et execute son role. [Détails tâche]")
```

#### 📝 Étape 3 : Documentation
- Mettre à jour `SPECIFICATIONS.md` (statut ✅)
- Mettre à jour `.claude/history.md` (résumé session)

---

### 3. Ce que je fais / ne fais pas

#### ❌ INTERDIT
- Analyser le code moi-même sans lancer les agents
- Dire "je vais vérifier la qualité/sécurité/architecture"
- Committer sans validation des 4 agents
- Sauter un agent d'implémentation si le contexte l'exige

#### ✅ OBLIGATOIRE
- Lancer les agents via `Task(subagent_type="general-purpose")`
- Attendre le retour de chaque agent
- Afficher le rapport complet à l'utilisateur
- Corriger les problèmes trouvés avant de continuer

#### 💡 EXCEPTIONS (validation optionnelle)
- Documentation seule (`*.md`)
- Configuration (`*.json`, `*.yaml`, `*.toml`)
- Scripts utilitaires simples

---

### 4. Note technique : Agents personnalisés

⚠️ **IMPORTANT** : Les agents `sql-pro`, `python-pro`, etc. ne sont PAS des `subagent_type` natifs de Claude Code.

**Syntaxe correcte** :
```python
# ✅ BON
Task(subagent_type="general-purpose",
     description="Validation architecture",
     prompt="Lis .claude/agents/architect-reviewer.md et execute son role. Valide le module auth.")

# ❌ MAUVAIS (n'existe pas dans Claude Code)
Task(subagent_type="architect-reviewer", prompt="...")
```

---

### 5. Apres validation

Committer, pousser, puis **proposer automatiquement** merge/PR vers main.

---

## AGENTS DISPONIBLES (7)

| Agent | Role | Quand utiliser |
|-------|------|----------------|
| **sql-pro** | Expert PostgreSQL | Nouvelles tables/colonnes/migrations |
| **python-pro** | Expert FastAPI/SQLAlchemy | Implementation backend |
| **typescript-pro** | Expert React/TypeScript | Implementation frontend |
| **architect-reviewer** | Validation Clean Architecture | AVANT commit code |
| **test-automator** | Generation tests pytest/vitest | AVANT commit code |
| **code-reviewer** | Qualite + conventions code | AVANT commit code |
| **security-auditor** | Audit securite + RGPD | AVANT commit code |

---

## Projet

- **Client** : Greg Construction (20 employes, 4.3M EUR CA)
- **Type** : SaaS gestion chantiers BTP
- **Depuis** : 21 janvier 2026

## Architecture

Clean Architecture 4 layers : `Domain -> Application -> Adapters -> Infrastructure`

**Regle d'or** : Dependances vers l'interieur uniquement. Module `auth` = reference.

## References

| Fichier | Description |
|---------|-------------|
| `.claude/agents.md` | Workflow agents (7 agents detailles) |
| `docs/SPECIFICATIONS.md` | CDC fonctionnel (177 features) |
| `.claude/project-status.md` | Etat modules + prochaines taches |
| `.claude/history.md` | Historique sessions |
| `CONTRIBUTING.md` | Conventions code |
| `docs/architecture/CLEAN_ARCHITECTURE.md` | Architecture detaillee |

## Commandes utiles

### Docker
```bash
docker compose up -d                 # Demarrer la stack
docker compose ps                    # Etat des containers
docker compose build api frontend    # Rebuild apres modifs
docker compose up -d api frontend    # Relancer apres rebuild
docker compose logs -f api           # Logs backend temps reel
docker compose exec api bash         # Shell dans le container API
docker compose exec db psql -U hubchantier hub_chantier  # Acces BDD
```

### Local
```bash
./scripts/start-dev.sh              # Dev
pytest backend/tests/unit -v        # Tests
./scripts/check-architecture.sh     # Verif archi
./scripts/generate-module.sh X      # Nouveau module
```

## Blocages / Questions en suspens

(Aucun pour l'instant)
