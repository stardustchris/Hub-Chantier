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
