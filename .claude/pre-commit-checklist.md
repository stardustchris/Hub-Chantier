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

### 4. Mise a jour documentation OBLIGATOIRE

**AVANT de committer**, mettre a jour :

1. **`docs/SPECIFICATIONS.md`** - TOUJOURS
   - Ajouter colonne Status si absente dans le tableau
   - Marquer les fonctionnalites implementees : ✅ Backend / ✅ Complet
   - Marquer les fonctionnalites en attente : ⏳ Frontend / ⏳ Infra

2. **`CLAUDE.md`** - Si module change de statut
   - Mettre a jour le tableau "Etat des modules"
   - Cocher les taches prioritaires completees

3. **`.claude/history.md`** - Toujours en fin de session
   - Ajouter le resume de la session

### 5. Commit uniquement si

- [ ] Tous les agents ont valide (PASS ou APPROVED)
- [ ] Les tests passent
- [ ] Aucune violation critique
- [ ] **SPECIFICATIONS.md mis a jour avec Status**
- [ ] **CLAUDE.md mis a jour si necessaire**

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
5. METTRE A JOUR SPECIFICATIONS.md (Status des fonctionnalites)
6. METTRE A JOUR CLAUDE.md (si module change de statut)
7. Commit uniquement apres validation + docs a jour
```

## RAPPEL CRITIQUE

> **SPECIFICATIONS.md = source de verite vivante**
>
> Chaque fonctionnalite implementee DOIT avoir son Status mis a jour.
> Ne JAMAIS oublier cette etape. C'est la trace de ce qui est fait.
