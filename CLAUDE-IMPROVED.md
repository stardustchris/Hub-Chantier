# Hub Chantier - Instructions Claude (VERSION AMÉLIORÉE)

> ⚠️ **CE FICHIER REMPLACE `CLAUDE.md` APRÈS VALIDATION**

## 🛑 STOP ! INSTRUCTION CRITIQUE #1

**Avant TOUTE action, Claude DOIT:**

1. ✅ Lire ce fichier en entier
2. ✅ Lire `.claude/agents.md` en entier
3. ✅ Afficher explicitement : "✅ Instructions obligatoires lues"

**Si ces 3 étapes ne sont PAS visibles dans la réponse, l'utilisateur doit ARRÊTER Claude immédiatement.**

---

## 🛑 INSTRUCTION CRITIQUE #2 - Détection Auto

**Claude doit exécuter ce code Python AU DÉBUT de chaque session:**

```python
import os
import sys

def verify_claude_setup():
    """Vérifie que Claude a bien compris les instructions."""

    # Vérifier fichiers obligatoires
    required_files = [
        "CLAUDE.md",
        ".claude/agents.md",
        "docs/SPECIFICATIONS.md"
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        print(f"❌ ERREUR: Fichiers manquants: {missing}")
        sys.exit(1)

    print("✅ Fichiers obligatoires trouvés")
    print("✅ Claude est prêt à travailler")
    return True

# Exécuter la vérification
verify_claude_setup()
```

**Si ce code n'est PAS exécuté au début, ARRÊTER Claude.**

---

## 🛑 INSTRUCTION CRITIQUE #3 - Workflow OBLIGATOIRE

**Pour TOUT commit contenant du code (.py, .ts, .tsx, .sql), Claude DOIT:**

### Checklist AVANT le premier `git add`

```bash
# 1. Lancer architect-reviewer
echo "🏗️ [1/4] Lancement architect-reviewer..."
# Claude DOIT utiliser: Task(subagent_type="architect-reviewer", ...)

# 2. Lancer test-automator
echo "🧪 [2/4] Lancement test-automator..."
# Claude DOIT utiliser: Task(subagent_type="test-automator", ...)

# 3. Lancer code-reviewer
echo "📝 [3/4] Lancement code-reviewer..."
# Claude DOIT utiliser: Task(subagent_type="code-reviewer", ...)

# 4. Lancer security-auditor
echo "🔒 [4/4] Lancement security-auditor..."
# Claude DOIT utiliser: Task(subagent_type="security-auditor", ...)
```

### Vérification Automatique

**Claude DOIT créer ce fichier `.claude-validation-{session_id}.json` avec:**

```json
{
  "session_id": "claude/feature-xxx",
  "agents_run": {
    "architect_reviewer": {"status": "pass", "timestamp": "..."},
    "test_automator": {"status": "pass", "coverage": 92.5},
    "code_reviewer": {"status": "approved", "findings": 0},
    "security_auditor": {"status": "pass", "critical": 0}
  },
  "commit_authorized": true
}
```

**Si ce fichier n'existe PAS, le commit est INTERDIT.**

---

## 🛑 INSTRUCTION CRITIQUE #4 - Agents = Tool `Task`

**Claude NE DOIT JAMAIS:**
- ❌ Faire la review lui-même
- ❌ Dire "je vais vérifier la qualité"
- ❌ Analyser le code sans les agents

**Claude DOIT TOUJOURS:**
- ✅ Utiliser `Task(subagent_type="code-reviewer", ...)`
- ✅ Utiliser `Task(subagent_type="architect-reviewer", ...)`
- ✅ Attendre le retour de l'agent
- ✅ Afficher le rapport JSON de l'agent

### Exemple CORRECT

```python
# Claude exécute ceci:
from anthropic import Task

result = Task(
    subagent_type="code-reviewer",
    description="Review code quality",
    prompt=f"""
    Review les fichiers suivants selon code-reviewer.md:
    - {file1}
    - {file2}

    Retourne le rapport JSON avec findings.
    """
)

# Claude affiche le résultat
print(result)
```

---

## 🔧 Hook Git Automatique

**Un hook git pre-commit vérifie automatiquement:**

```bash
#!/bin/bash
if [ ! -f ".claude-validation-$(git branch --show-current).json" ]; then
    echo "❌ ERREUR: Fichier de validation manquant"
    echo "Les agents n'ont pas été exécutés."
    exit 1
fi

echo "✅ Validation agents OK"
exit 0
```

---

## 📊 Dashboard de Conformité

**Claude doit afficher CE TABLEAU après chaque session:**

```
╔═══════════════════════════════════════════════════════╗
║         CONFORMITÉ INSTRUCTIONS CLAUDE.md            ║
╠═══════════════════════════════════════════════════════╣
║ ✅ CLAUDE.md lu                                       ║
║ ✅ .claude/agents.md lu                               ║
║ ✅ Workflow 7 agents respecté                         ║
║ ✅ architect-reviewer : PASS                          ║
║ ✅ test-automator : 92.5% coverage                    ║
║ ✅ code-reviewer : APPROVED (0 findings)              ║
║ ✅ security-auditor : PASS (0 critical)               ║
║ ✅ SPECIFICATIONS.md mis à jour                       ║
║ ✅ .claude/history.md mis à jour                      ║
╠═══════════════════════════════════════════════════════╣
║ SCORE: 9/9 (100%)                                     ║
║ STATUS: ✅ COMMIT AUTORISÉ                            ║
╚═══════════════════════════════════════════════════════╝
```

**Si le score < 100%, le commit est INTERDIT.**

---

## 🚨 Que Faire Si Claude Viole Ces Règles

### Détection

Si vous voyez Claude:
- ❌ Commencer à coder sans lire les instructions
- ❌ Commit sans lancer les agents
- ❌ Dire "j'ai vérifié" sans utiliser `Task(...)`

### Action Immédiate

```bash
# 1. STOPPER Claude
Ctrl+C

# 2. Reset le commit
git reset HEAD~1

# 3. Relancer Claude avec:
"Tu as violé CLAUDE.md. Recommence en suivant les 4 instructions critiques."
```

---

## ✅ Checklist Utilisateur (Vous!)

**Après chaque réponse de Claude, vérifiez:**

- [ ] Claude a affiché "✅ Instructions obligatoires lues"
- [ ] Claude a exécuté `verify_claude_setup()`
- [ ] Pour chaque commit de code:
  - [ ] Claude a lancé `Task(subagent_type="architect-reviewer")`
  - [ ] Claude a lancé `Task(subagent_type="test-automator")`
  - [ ] Claude a lancé `Task(subagent_type="code-reviewer")`
  - [ ] Claude a lancé `Task(subagent_type="security-auditor")`
  - [ ] Claude a affiché le tableau de conformité avec score 100%
- [ ] Fichier `.claude-validation-*.json` existe

**Si UN SEUL item manque, STOP et faites recommencer Claude.**

---

## 🎯 Résumé des 4 Instructions Critiques

1. **Lire obligatoire**: CLAUDE.md + agents.md AVANT toute action
2. **Détection auto**: Exécuter `verify_claude_setup()` au début
3. **Workflow agents**: Lancer les 4 agents AVANT `git add`
4. **Tool Task**: Utiliser `Task(subagent_type=...)`, JAMAIS analyser soi-même

**Ces 4 règles sont NON-NÉGOCIABLES.**

---

*Version: 2.0 - 28 janvier 2026*
*Amélioration suite à violation lors de session refactor-backend-functions-zhaHE*
