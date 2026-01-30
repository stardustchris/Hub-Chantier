# Orchestration Périodique des Agents - Proposition Pédagogique

> 💡 **Question du user** : "Faudra aussi que cet orchestrateur d'agents sache intervenir périodiquement et avec le contexte qui s'élargit, ce ne sera pas toujours le cas. Comment faire ?"

## 📚 Compréhension du Problème

### Contexte actuel (ce qu'on vient de créer)
- ✅ Système de validation **manuel** : `python .claude/scripts/validate.py auth`
- ✅ Exécution **à la demande** avant un commit
- ✅ Validation **complète** du module (fail-fast)

### Nouvelle exigence
Le système doit pouvoir **intervenir automatiquement** de manière périodique, mais avec deux contraintes importantes :

1. **Périodicité** : Validation automatique à intervalles réguliers
2. **Contexte élargi** : Pas toujours valider tout le module, mais s'adapter au contexte

---

## 🎯 3 Stratégies Proposées

Je vous présente 3 approches, de la plus simple à la plus sophistiquée.

---

## Stratégie A : Hooks Git + CI/CD (Simple) ⭐

### Principe
Exécuter les agents automatiquement sur les **événements Git** :
- Pre-commit : avant chaque commit local
- Pre-push : avant chaque push
- CI/CD : sur GitHub Actions à chaque PR

### Avantages
✅ Simple à mettre en place
✅ Intégration native avec le workflow dev
✅ Bloque les commits/pushs non conformes
✅ Zéro configuration côté dev

### Mise en œuvre

#### 1. Hook pre-commit (validation avant commit)
```bash
# .git/hooks/pre-commit

#!/bin/bash
# Détecte les modules modifiés et valide uniquement ceux-là

MODULES_CHANGED=$(git diff --cached --name-only | grep 'backend/modules/' | cut -d'/' -f3 | sort -u)

if [ -z "$MODULES_CHANGED" ]; then
  echo "✅ Aucun module modifié, skip validation"
  exit 0
fi

for MODULE in $MODULES_CHANGED; do
  echo "🔍 Validation du module $MODULE..."
  python .claude/scripts/validate.py "$MODULE" --agents architect-reviewer code-reviewer security-auditor

  if [ $? -ne 0 ]; then
    echo "❌ Validation échouée pour $MODULE"
    echo "💡 Corrigez les erreurs ou utilisez git commit --no-verify pour forcer"
    exit 1
  fi
done

echo "✅ Tous les modules modifiés sont valides"
exit 0
```

#### 2. GitHub Actions (validation sur PR)
```yaml
# .github/workflows/validation.yml

name: Validation Modules

on:
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'backend/modules/**'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r backend/requirements.txt

      - name: Detect changed modules
        id: changed-modules
        run: |
          MODULES=$(git diff --name-only origin/main...HEAD | grep 'backend/modules/' | cut -d'/' -f3 | sort -u)
          echo "modules=$MODULES" >> $GITHUB_OUTPUT

      - name: Validate modules
        run: |
          for MODULE in ${{ steps.changed-modules.outputs.modules }}; do
            echo "Validating $MODULE..."
            python .claude/scripts/validate.py "$MODULE"
          done
```

### Quand c'est suffisant
- ✅ Équipe < 10 personnes
- ✅ Commits fréquents (plusieurs fois par jour)
- ✅ Workflow Git bien établi

---

## Stratégie B : Validation Incrémentale Intelligente (Recommandé) ⭐⭐⭐

### Principe
Valider **uniquement ce qui a changé** depuis la dernière validation, avec différents niveaux de profondeur.

### Avantages
✅ Très rapide (valide uniquement les changements)
✅ S'adapte automatiquement au contexte
✅ Peut tourner en arrière-plan pendant le dev
✅ Historique des validations

### Architecture

```
.claude/scripts/
├── orchestrator.py          (existant)
├── validate.py              (existant)
└── incremental_validator.py (NOUVEAU)

.claude/validation_state/
└── {module}/
    ├── last_validation.json
    ├── file_checksums.json
    └── history/
        └── 2026-01-30_14-30-00.json
```

### Mise en œuvre

```python
# .claude/scripts/incremental_validator.py

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
from orchestrator import validate_module


class IncrementalValidator:
    """
    Valide uniquement les fichiers modifiés depuis la dernière validation.

    Niveaux de validation :
    - QUICK   : Uniquement les fichiers modifiés (architect + code)
    - STANDARD: Fichiers modifiés + use cases dépendants (+ test + security)
    - FULL    : Tout le module (tous les agents)
    """

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module_path = Path.cwd() / 'backend' / 'modules' / module_name
        self.state_dir = Path.cwd() / '.claude' / 'validation_state' / module_name
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.last_validation_file = self.state_dir / 'last_validation.json'
        self.checksums_file = self.state_dir / 'file_checksums.json'

    def detect_changes(self) -> Dict[str, Set[str]]:
        """
        Détecte les fichiers modifiés depuis la dernière validation.

        Returns:
            Dict avec les catégories de changements :
            {
                'domain': {'user.py', 'pointage.py'},
                'application': {'login.py'},
                'infrastructure': {'user_repository.py'},
                'tests': {'test_login.py'}
            }
        """
        changes = {
            'domain': set(),
            'application': set(),
            'infrastructure': set(),
            'tests': set(),
        }

        # Charger les checksums précédents
        old_checksums = self._load_checksums()

        # Calculer les checksums actuels
        new_checksums = {}
        for py_file in self.module_path.rglob('*.py'):
            rel_path = str(py_file.relative_to(self.module_path))
            checksum = self._file_checksum(py_file)
            new_checksums[rel_path] = checksum

            # Comparer avec l'ancien
            if rel_path not in old_checksums or old_checksums[rel_path] != checksum:
                # Fichier modifié ou nouveau
                if '/domain/' in rel_path:
                    changes['domain'].add(py_file.name)
                elif '/application/' in rel_path:
                    changes['application'].add(py_file.name)
                elif '/infrastructure/' in rel_path:
                    changes['infrastructure'].add(py_file.name)
                elif '/tests/' in rel_path:
                    changes['tests'].add(py_file.name)

        # Sauvegarder les nouveaux checksums
        self._save_checksums(new_checksums)

        return changes

    def select_agents(self, changes: Dict[str, Set[str]], level: str = 'STANDARD') -> List[str]:
        """
        Sélectionne les agents à exécuter selon les changements et le niveau.

        Args:
            changes: Dictionnaire des fichiers modifiés par catégorie.
            level: Niveau de validation (QUICK | STANDARD | FULL).

        Returns:
            Liste des noms d'agents à exécuter.
        """
        if level == 'FULL':
            # Tous les agents
            return [
                'sql-pro',
                'python-pro',
                'architect-reviewer',
                'test-automator',
                'code-reviewer',
                'security-auditor',
            ]

        agents = set()

        # Toujours inclure architect-reviewer et code-reviewer
        agents.add('architect-reviewer')
        agents.add('code-reviewer')

        # Selon les changements
        if changes['domain']:
            agents.add('python-pro')
            if level == 'STANDARD':
                agents.add('test-automator')  # Domain change = tests requis

        if changes['application']:
            agents.add('python-pro')
            if level == 'STANDARD':
                agents.add('test-automator')
                agents.add('security-auditor')  # Use cases = risque sécurité

        if changes['infrastructure']:
            agents.add('sql-pro')  # Peut impacter DB
            if level == 'STANDARD':
                agents.add('security-auditor')

        if changes['tests']:
            agents.add('test-automator')

        if level == 'QUICK':
            # Mode rapide : enlever test-automator et security
            agents.discard('test-automator')
            agents.discard('security-auditor')

        return list(agents)

    def validate(self, level: str = 'STANDARD') -> Dict:
        """
        Valide le module de manière incrémentale.

        Args:
            level: Niveau de validation (QUICK | STANDARD | FULL).

        Returns:
            Rapport de validation.
        """
        print(f"🔍 Détection des changements dans {self.module_name}...")
        changes = self.detect_changes()

        total_changes = sum(len(files) for files in changes.values())

        if total_changes == 0:
            print(f"✅ Aucun changement détecté, skip validation")
            return {
                'status': 'SKIP',
                'message': 'No changes detected',
                'timestamp': datetime.now().isoformat()
            }

        print(f"📝 {total_changes} fichier(s) modifié(s) :")
        for category, files in changes.items():
            if files:
                print(f"   • {category}: {len(files)} fichier(s)")

        # Sélectionner les agents
        agents = self.select_agents(changes, level)

        print(f"\n🤖 Agents sélectionnés ({level}) : {', '.join(agents)}")

        # Exécuter la validation
        report = validate_module(
            module_name=self.module_name,
            agents=agents,
            fail_fast=True
        )

        # Sauvegarder l'historique
        self._save_validation_history(report, level, changes)

        return report

    def _file_checksum(self, file_path: Path) -> str:
        """Calcule le checksum MD5 d'un fichier."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _load_checksums(self) -> Dict[str, str]:
        """Charge les checksums sauvegardés."""
        if not self.checksums_file.exists():
            return {}
        with open(self.checksums_file, 'r') as f:
            return json.load(f)

    def _save_checksums(self, checksums: Dict[str, str]):
        """Sauvegarde les checksums."""
        with open(self.checksums_file, 'w') as f:
            json.dump(checksums, f, indent=2)

    def _save_validation_history(self, report: Dict, level: str, changes: Dict):
        """Sauvegarde l'historique de validation."""
        history_dir = self.state_dir / 'history'
        history_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        history_file = history_dir / f"{timestamp}_{level}.json"

        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'changes': {k: list(v) for k, v in changes.items()},
            'report': report,
        }

        with open(history_file, 'w') as f:
            json.dump(history_entry, f, indent=2)


def incremental_validate(module_name: str, level: str = 'STANDARD') -> Dict:
    """
    Point d'entrée pour la validation incrémentale.

    Args:
        module_name: Nom du module.
        level: QUICK | STANDARD | FULL.

    Returns:
        Rapport de validation.
    """
    validator = IncrementalValidator(module_name)
    return validator.validate(level)
```

### Usage

```bash
# Validation rapide (pendant le dev, en arrière-plan)
python .claude/scripts/validate.py auth --incremental --level QUICK

# Validation standard (avant commit)
python .claude/scripts/validate.py auth --incremental --level STANDARD

# Validation complète (avant push ou PR)
python .claude/scripts/validate.py auth --incremental --level FULL
```

### Quand l'utiliser
- ✅ Gros modules (> 20 fichiers)
- ✅ Dev en continu (validation toutes les 5-10 min)
- ✅ Équipe > 5 personnes
- ✅ Besoin de feedback rapide

---

## Stratégie C : Validation Continue avec File Watcher (Avancé) ⭐⭐

### Principe
Lancer un **daemon** qui surveille les fichiers et valide automatiquement à chaque sauvegarde.

### Avantages
✅ Feedback instantané pendant le dev
✅ Zéro action manuelle
✅ Intégration IDE (via extension)

### Mise en œuvre

```python
# .claude/scripts/watch_validator.py

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from incremental_validator import incremental_validate


class ValidationHandler(FileSystemEventHandler):
    """Handler pour valider à chaque modification de fichier."""

    def __init__(self, module_name: str, debounce_seconds: int = 5):
        self.module_name = module_name
        self.debounce_seconds = debounce_seconds
        self.last_validation = 0

    def on_modified(self, event):
        """Déclenché quand un fichier est modifié."""
        if event.is_directory or not event.src_path.endswith('.py'):
            return

        now = time.time()

        # Debounce : attendre 5 secondes après la dernière modif
        if now - self.last_validation < self.debounce_seconds:
            return

        self.last_validation = now

        print(f"\n🔄 Fichier modifié : {event.src_path}")
        print(f"🚀 Lancement validation incrémentale...")

        try:
            incremental_validate(self.module_name, level='QUICK')
        except Exception as e:
            print(f"❌ Erreur validation : {e}")


def watch_module(module_name: str):
    """
    Lance un watcher qui valide automatiquement le module.

    Usage:
        python .claude/scripts/watch_validator.py auth
    """
    module_path = Path.cwd() / 'backend' / 'modules' / module_name

    if not module_path.exists():
        print(f"❌ Module {module_name} non trouvé")
        return

    print(f"👁️  Surveillance du module {module_name}...")
    print(f"📂 Chemin : {module_path}")
    print(f"⚡ Validation automatique activée (QUICK mode)")
    print(f"Press Ctrl+C to stop\n")

    event_handler = ValidationHandler(module_name, debounce_seconds=5)
    observer = Observer()
    observer.schedule(event_handler, str(module_path), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n👋 Surveillance arrêtée")

    observer.join()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python watch_validator.py <module_name>")
        sys.exit(1)

    watch_module(sys.argv[1])
```

### Installation

```bash
pip install watchdog
```

### Usage

```bash
# Terminal 1 : Lancer le watcher
python .claude/scripts/watch_validator.py auth

# Terminal 2 : Coder normalement
# → Le watcher valide automatiquement à chaque sauvegarde
```

### Quand l'utiliser
- ✅ Dev hardcore (besoin feedback immédiat)
- ✅ Refactoring massif
- ✅ Nouveau dev (apprentissage des conventions)

---

## 📊 Tableau Comparatif

| Critère | Stratégie A (Hooks) | Stratégie B (Incrémental) ⭐ | Stratégie C (Watcher) |
|---------|---------------------|--------------------------|----------------------|
| **Setup** | Simple | Moyen | Complexe |
| **Feedback** | Au commit | À la demande | Temps réel |
| **Performance** | Lent | Rapide | Très rapide |
| **Contexte adaptatif** | ❌ Non | ✅ Oui | ✅ Oui |
| **Automatique** | ✅ Oui | ⚠️ Semi | ✅ Oui |
| **Maintenance** | Faible | Moyenne | Élevée |
| **Équipe > 10** | ⚠️ Limite | ✅ Idéal | ❌ Overkill |

---

## 🎯 Recommandation Finale

**Pour Hub Chantier, je recommande la Stratégie B (Incrémental) ⭐⭐⭐**

### Pourquoi ?

1. **Contexte élargi géré** : S'adapte automatiquement selon les changements
2. **Performance** : Valide uniquement ce qui change
3. **Flexibilité** : 3 niveaux (QUICK/STANDARD/FULL)
4. **Pas de friction** : Le dev choisit quand valider
5. **Maintenance raisonnable** : Code Python simple, pas de daemon

### Plan d'implémentation recommandé

**Phase 1 (Immédiat)** : Hook pre-commit simple (Stratégie A)
- Bloque les commits non conformes
- Validation complète obligatoire

**Phase 2 (Dans 1 mois)** : Ajout validation incrémentale (Stratégie B)
- Utilisable pendant le dev
- Feedback rapide
- Hook pre-commit devient plus rapide

**Phase 3 (Optionnel)** : Watcher pour les power users (Stratégie C)
- Seulement si demande explicite
- Mode opt-in

---

## ❓ Questions pour finaliser la décision

1. **Fréquence** : À quelle fréquence voulez-vous valider automatiquement ?
   - [ ] Uniquement avant commit (Stratégie A suffit)
   - [ ] Pendant le dev, manuellement (Stratégie B)
   - [ ] En continu, automatiquement (Stratégie C)

2. **Tolérance aux faux positifs** :
   - [ ] Zéro tolérance (validation complète toujours)
   - [ ] Acceptable si rapide (validation incrémentale OK)

3. **Taille d'équipe** :
   - [ ] < 5 personnes (Stratégie A OK)
   - [ ] 5-15 personnes (Stratégie B recommandée)
   - [ ] > 15 personnes (Stratégie B + CI/CD obligatoire)

4. **Budget maintenance** :
   - [ ] Minimal (Stratégie A)
   - [ ] Moyen (Stratégie B)
   - [ ] Élevé (Stratégie C)

---

**Quelle stratégie vous correspond le mieux ? Ou voulez-vous un mix ?** 🤔
