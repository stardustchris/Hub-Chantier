# Pre-Commit Checklist pour Claude

> Ce fichier DOIT être lu par Claude AVANT chaque commit de code source.

## Verification obligatoire

Avant de committer, Claude DOIT verifier :

### 1. Types de fichiers modifies

```bash
git status --porcelain | grep -E '\.(py|ts|tsx|sql)$'
```

Si cette commande retourne des resultats → **LANCER LES AGENTS**

### 2. Ordre d'execution des agents (7 agents)

1. **sql-pro** - Schema DB et migrations (si modifications DB)
   - Migrations Alembic reversibles
   - Index sur requetes frequentes
   - Contraintes d'integrite

2. **architect-reviewer** - Validation Clean Architecture
   - Domain layer PURE (aucun import framework)
   - Use cases dependent d'interfaces
   - Pas d'import direct entre modules
   - Communication via Events

3. **test-automator** - Verification couverture tests
   - Identifier les gaps de couverture
   - Proposer les tests manquants
   - Objectif: >= 90% couverture

4. **code-reviewer** - Qualite du code
   - Type hints complets
   - Docstrings Google style
   - Gestion des erreurs appropriee

5. **security-auditor** - Securite et conformite RGPD
   - Zero injection SQL/XSS
   - Validation des entrees (Pydantic)
   - Donnees sensibles chiffrees
   - Conformite RGPD si donnees personnelles

### 3. Correction des violations

Si un agent trouve des violations :
- **CORRIGER** avant de passer a l'agent suivant
- **NE JAMAIS** committer avec des violations critiques

### 4. Commit uniquement si

- [ ] Tous les agents ont valide (PASS ou APPROVED)
- [ ] Les tests passent (>= 85% couverture)
- [ ] Aucune violation architecture critique
- [ ] Aucun finding securite CRITIQUE ou HAUTE

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
2. Si *.py, *.ts, *.tsx, *.sql → Lancer agents:
   - sql-pro (si modifs DB)
   - architect-reviewer
   - test-automator
   - code-reviewer
   - security-auditor
3. Corriger les violations
4. Relancer agents si corrections
5. Commit uniquement apres validation complete
```
