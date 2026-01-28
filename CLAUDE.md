# Hub Chantier - Instructions Claude

> Ce fichier est lu au debut de chaque session. Les regles ci-dessous sont OBLIGATOIRES.

## ⛔ LECTURE OBLIGATOIRE AVANT TOUTE ACTION

**LIRE ces fichiers AVANT de commencer :**

1. Ce fichier (`CLAUDE.md`) - regles de session
2. `.claude/agents.md` - workflow agents detaille

**NE PAS coder, NE PAS planifier sans avoir lu ces deux fichiers.**

---

## REGLES OBLIGATOIRES

### 1. Debut de session (AVANT tout dev)

```bash
cd backend && pip install -r requirements.txt && python -m pytest tests/unit -v --tb=short
cd ../frontend && npm install && npm run build
```

**NE PAS commencer si ces commandes echouent.**

### 2. Workflow fonctionnalite (7 agents)

Voir `.claude/agents.md` pour le workflow detaille complet.

**Resume** :
1. Lire SPECIFICATIONS.md (specs feature)
2. sql-pro : schema DB (si nouvelles tables)
3. python-pro/typescript-pro : implementer
4. architect-reviewer, test-automator, code-reviewer, security-auditor : valider
5. Mettre a jour SPECIFICATIONS.md + .claude/history.md

### 3. Validation AVANT commit (code *.py, *.ts, *.tsx, *.sql)

**CRITIQUE : Utiliser `Task(subagent_type="...")` pour TOUS les agents**

**Checklist obligatoire** :
- [ ] sql-pro : migrations OK (si modifs DB)
- [ ] architect-reviewer : PASS
- [ ] test-automator : tests generes (>= 85% couverture)
- [ ] code-reviewer : APPROVED
- [ ] security-auditor : PASS (0 finding critique/haute)
- [ ] SPECIFICATIONS.md mis a jour
- [ ] .claude/history.md mis a jour

**NE JAMAIS** :
- ❌ Analyser le code soi-meme sans les agents
- ❌ Dire "je vais verifier la qualite"
- ❌ Committer sans validation agents

**TOUJOURS** :
- ✅ `Task(subagent_type="architect-reviewer", prompt="...")`
- ✅ `Task(subagent_type="code-reviewer", prompt="...")`
- ✅ `Task(subagent_type="security-auditor", prompt="...")`
- ✅ Attendre le retour agent
- ✅ Afficher le rapport

**Exceptions** (validation optionnelle) :
- Documentation seule (*.md)
- Configuration (*.json, *.yaml, *.toml)
- Scripts utilitaires simples

### 4. Apres validation

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

**Workflow complet** : Voir `.claude/agents.md` (301 lignes)

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

```bash
./scripts/start-dev.sh              # Dev
pytest backend/tests/unit -v        # Tests
./scripts/check-architecture.sh     # Verif archi
./scripts/generate-module.sh X      # Nouveau module
```

## Blocages / Questions en suspens

(Aucun pour l'instant)
