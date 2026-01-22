# Pre-Commit Checklist pour Claude

> Ce fichier DOIT être lu par Claude AVANT chaque commit de code source.

## Verification obligatoire

Avant de committer, Claude DOIT verifier :

### 1. Types de fichiers modifies

```bash
git status --porcelain | grep -E '\.(py|ts|tsx|sql)$'
```

Si cette commande retourne des resultats → **LANCER LES AGENTS**

### 2. Ordre d'execution des agents

1. **architect-reviewer** - Validation Clean Architecture
   - Domain layer PURE (aucun import framework)
   - Use cases dependent d'interfaces
   - Pas d'import direct entre modules
   - Communication via Events

2. **test-automator** - Verification couverture tests
   - Identifier les gaps de couverture
   - Proposer les tests manquants

3. **code-reviewer** - Qualite et securite
   - Zero issues securite critiques
   - Type hints complets
   - Docstrings Google style
   - Gestion des erreurs appropriee

### 3. Correction des violations

Si un agent trouve des violations :
- **CORRIGER** avant de passer a l'agent suivant
- **NE JAMAIS** committer avec des violations critiques

### 4. Commit uniquement si

- [ ] Tous les agents ont valide (PASS ou APPROVED)
- [ ] Les tests passent
- [ ] Aucune violation critique

---

## Fichiers EXCLUS (pas besoin d'agents)

- `*.md` (documentation)
- `.claude/*` (configuration Claude)
- `*.json` / `*.yaml` / `*.toml` (configuration)
- `scripts/*` (scripts simples)

---

## Rappel automatique

Claude DOIT executer cette verification a chaque fois qu'il s'apprete a faire `git commit` sur des fichiers de code source.

```
AVANT git commit:
1. Lister les fichiers modifies
2. Si *.py, *.ts, *.tsx, *.sql → Lancer agents
3. Corriger les violations
4. Relancer agents si corrections
5. Commit uniquement apres validation
```
