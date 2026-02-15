# Lessons Learned

## 2026-02-08 - Session modest-liskov

### VIOLATION: Agents non lancés

**Contexte**: 6 thèmes de changements (~3500 lignes) ont été codés sans lancer les agents d'implémentation ni de validation.

**Règle violée**: CLAUDE.md § "Workflow agents (OBLIGATOIRE)" - "Je ne code JAMAIS seul. Les agents m'assistent SYSTÉMATIQUEMENT."

**Ce qui aurait dû se passer**:
1. Agents d'implémentation AVANT de coder: `python-pro`, `react-specialist`, `postgres-pro`, `devops-engineer`
2. Agents de validation AVANT de commit: `architect-reviewer`, `test-automator`, `code-reviewer`, `security-auditor`

**Action corrective**: Les 4 agents de validation ont été lancés en rattrapage.

**Règle pour le futur**:
- TOUJOURS lancer les agents d'implémentation AVANT d'écrire du code non-trivial
- TOUJOURS lancer les 4 agents de validation AVANT tout commit
- Ne JAMAIS demander "veux-tu que je lance les agents?" — c'est obligatoire, les lancer d'office

## 2026-02-11 - Session audit ConfigurationEntreprise

### PROBLEME: Agents background instables

**Contexte**: Les 3 agents de validation (architect-reviewer, code-reviewer, security-auditor) ont ete lances en `run_in_background=true` et ont plante 2 fois de suite (fichiers output non crees).

**Impact**: Perte de temps, relance x2, frustration utilisateur.

**Cause probable**: Les agents background avec des prompts longs ou beaucoup de lectures de fichiers peuvent planter silencieusement.

**Solution appliquee**: Faire les reviews directement dans le contexte principal au lieu de les deleguer a des agents background. Plus fiable, plus rapide.

**Regle pour le futur**:
- Pour la VALIDATION (architect, code-reviewer, security): faire directement dans le contexte principal (lire les fichiers + rendre le verdict)
- Pour l'IMPLEMENTATION (python-pro, react-specialist): les agents background restent utiles car ils produisent du code de maniere autonome
- Ne pas relancer un agent background qui a plante — basculer sur execution directe

## 2026-02-15 - Session plan-hub-ux-improvements

### CONFIRMATION: Agents background TOUS cassés (3e occurrence)

**Contexte**: Les 4 agents de validation lancés en `run_in_background=true` ont ENCORE planté. Fichiers output vides (0 bytes). 3e session consécutive avec le même problème.

**Impact**: Perte de 15+ min à attendre et vérifier, frustration utilisateur ("je vais aller sur Codex").

**Cause confirmée**: `run_in_background: true` ne fonctionne PAS dans cet environnement. Les processus agents meurent silencieusement sans écrire de sortie.

**Solution définitive** (ajoutée dans CLAUDE.md):
- **JAMAIS** de `run_in_background: true` — point final
- Validations = Grep/Read directs dans le contexte principal (~30s, 100% fiable)
- Agents foreground synchrones OK si vraiment nécessaire
- **Règle persistée dans CLAUDE.md** pour survivre au compactage
