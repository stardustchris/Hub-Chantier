# Hub Chantier - Instructions Claude

> Ce fichier est lu au debut de chaque session. Les regles ci-dessous sont OBLIGATOIRES.

## LECTURE OBLIGATOIRE

1. Ce fichier (`CLAUDE.md`) - regles de session
2. `.claude/agents.md` - workflow agents detaille (16 agents)

**NE PAS coder sans avoir lu ces deux fichiers.**

---

## Projet

| | |
|---|---|
| **Client** | Greg Construction (20 employes, 4.3M EUR CA) |
| **Type** | SaaS gestion chantiers BTP |
| **Stack** | FastAPI + React + PostgreSQL 16 + Docker |
| **Architecture** | Clean Architecture 4 layers |

---

## Environnement Docker

```bash
# Demarrage
docker compose up -d && docker compose ps

# Health check
curl -s http://localhost/api/health

# Rebuild apres modifs
docker compose build api frontend && docker compose up -d api frontend

# Logs
docker compose logs -f api
```

| Service | URL |
|---------|-----|
| frontend | http://localhost |
| api | http://localhost:8000 |
| db | localhost:5432 |
| adminer | http://localhost:8080 |

> **PWA** : Apres rebuild frontend, vider le cache navigateur (Service Worker).

---

## Workflow agents (OBLIGATOIRE)

**Regle absolue** : Je ne code JAMAIS seul. Les agents m'assistent SYSTEMATIQUEMENT.

### Etapes

1. **Specs** : Lire `docs/SPECIFICATIONS.md`
2. **Implementation** : Lancer l'agent selon contexte (voir tableau ci-dessous)
3. **Validation** : 4 agents OBLIGATOIRES avant commit
4. **Documentation** : Mettre a jour SPECIFICATIONS.md + history.md

### Agents disponibles (16)

| Categorie | Agents |
|-----------|--------|
| **Implementation** | sql-pro, postgres-pro, python-pro, typescript-pro, react-specialist, api-designer |
| **Validation** | architect-reviewer, test-automator, code-reviewer, security-auditor, compliance-auditor |
| **Specialises** | performance-engineer, accessibility-tester, business-analyst, documentation-engineer, devops-engineer |

### Validation obligatoire (4 agents)

| # | Agent | Objectif |
|---|-------|----------|
| 1 | architect-reviewer | PASS (0 violation Clean Architecture) |
| 2 | test-automator | >= 90% couverture |
| 3 | code-reviewer | APPROVED |
| 4 | security-auditor | PASS (0 finding CRITICAL/HIGH) |

### Syntaxe d'appel

```python
Task(subagent_type="general-purpose",
     description="Description 3-5 mots",
     prompt="Lis .claude/agents/NOM_AGENT.md et execute son role. [Details]")
```

> **Detail complet** : Voir `.claude/agents.md` pour les declencheurs et cas d'usage de chaque agent.

---

## Exceptions (validation optionnelle)

- Documentation seule (`*.md`)
- Configuration (`*.json`, `*.yaml`, `*.toml`)
- Scripts utilitaires simples

---

## References

| Fichier | Description |
|---------|-------------|
| `.claude/agents.md` | Workflow agents (16 agents) |
| `docs/SPECIFICATIONS.md` | CDC fonctionnel (177 features) |
| `.claude/project-status.md` | Etat modules |
| `.claude/history.md` | Historique sessions |
| `docs/architecture/CLEAN_ARCHITECTURE.md` | Architecture detaillee |

---

## Blocages / Questions en suspens

(Aucun pour l'instant)
