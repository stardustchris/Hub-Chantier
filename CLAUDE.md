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

```
1. Lire .claude/agents.md (workflow agents)
2. Lire docs/SPECIFICATIONS.md (specs de la feature)
3. sql-pro : schema DB et migrations (si nouvelles tables)
4. python-pro/typescript-pro : implementer
5. architect-reviewer : valider architecture
6. test-automator : generer tests (couverture >= 85%)
7. code-reviewer : valider qualite
8. security-auditor : audit securite/RGPD
9. Mettre a jour SPECIFICATIONS.md (statut -> done)
10. Mettre a jour .claude/history.md (resume session)
```

### 3. Avant commit (code *.py, *.ts, *.tsx, *.sql)

- [ ] sql-pro : migrations OK (si modifs DB)
- [ ] architect-reviewer : PASS
- [ ] test-automator : tests generes
- [ ] code-reviewer : APPROVED
- [ ] security-auditor : PASS (aucun finding critique/haute)
- [ ] Couverture >= 90% sur code modifie
- [ ] SPECIFICATIONS.md mis a jour
- [ ] .claude/history.md mis a jour

### 4. Apres validation

Committer, pousser, puis **proposer automatiquement** merge/PR vers main.

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
| `docs/SPECIFICATIONS.md` | CDC fonctionnel (177 features) |
| `.claude/agents.md` | Workflow agents detaille |
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
