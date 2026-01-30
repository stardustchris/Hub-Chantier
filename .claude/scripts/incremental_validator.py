#!/usr/bin/env python3
"""
Validation Incrémentale Intelligente (Stratégie B).

Valide uniquement les fichiers modifiés depuis la dernière validation,
avec adaptation automatique du contexte (QUICK/STANDARD/FULL).
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional
import sys

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import validate_module


class IncrementalValidator:
    """
    Valide uniquement les fichiers modifiés depuis la dernière validation.

    Niveaux de validation :
    - QUICK   : Fichiers modifiés uniquement (architect + code)
    - STANDARD: Fichiers modifiés + dépendances (+ test + security)
    - FULL    : Tout le module (tous les agents)
    """

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module_path = Path.cwd() / 'backend' / 'modules' / module_name
        self.state_dir = Path.cwd() / '.claude' / 'validation_state' / module_name
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.checksums_file = self.state_dir / 'file_checksums.json'
        self.last_validation_file = self.state_dir / 'last_validation.json'

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
            'adapters': set(),
            'tests': set(),
        }

        # Charger les checksums précédents
        old_checksums = self._load_checksums()

        # Calculer les checksums actuels
        new_checksums = {}

        if not self.module_path.exists():
            print(f"❌ Module {self.module_name} non trouvé à {self.module_path}")
            return changes

        for py_file in self.module_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue

            rel_path = str(py_file.relative_to(self.module_path))
            checksum = self._file_checksum(py_file)
            new_checksums[rel_path] = checksum

            # Comparer avec l'ancien
            if rel_path not in old_checksums or old_checksums[rel_path] != checksum:
                # Fichier modifié ou nouveau
                file_name = py_file.name

                if '/domain/' in rel_path:
                    changes['domain'].add(file_name)
                elif '/application/' in rel_path:
                    changes['application'].add(file_name)
                elif '/infrastructure/' in rel_path:
                    changes['infrastructure'].add(file_name)
                elif '/adapters/' in rel_path:
                    changes['adapters'].add(file_name)
                elif 'test' in rel_path.lower():
                    changes['tests'].add(file_name)

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

        if changes['infrastructure'] or changes['adapters']:
            agents.add('sql-pro')  # Peut impacter DB
            if level == 'STANDARD':
                agents.add('security-auditor')

        if changes['tests']:
            agents.add('test-automator')

        if level == 'QUICK':
            # Mode rapide : enlever test-automator et security
            agents.discard('test-automator')
            agents.discard('security-auditor')
            agents.discard('sql-pro')

        return list(agents)

    def validate(self, level: str = 'STANDARD') -> Dict:
        """
        Valide le module de manière incrémentale.

        Args:
            level: Niveau de validation (QUICK | STANDARD | FULL).

        Returns:
            Rapport de validation.
        """
        print(f"\n🔍 Détection des changements dans '{self.module_name}'...")
        changes = self.detect_changes()

        total_changes = sum(len(files) for files in changes.values())

        if total_changes == 0:
            print(f"✅ Aucun changement détecté, skip validation\n")
            return {
                'status': 'SKIP',
                'message': 'No changes detected',
                'module': self.module_name,
                'timestamp': datetime.now().isoformat()
            }

        print(f"\n📝 {total_changes} fichier(s) modifié(s) :")
        for category, files in changes.items():
            if files:
                print(f"   • {category:15} : {len(files)} fichier(s)")
                for file in sorted(list(files)[:3]):  # Max 3 par catégorie
                    print(f"      - {file}")
                if len(files) > 3:
                    print(f"      ... et {len(files) - 3} autres")

        # Sélectionner les agents
        agents = self.select_agents(changes, level)

        print(f"\n🤖 Agents sélectionnés (mode {level}) :")
        print(f"   {', '.join(agents)}\n")

        # Exécuter la validation
        report = validate_module(
            module_name=self.module_name,
            agents=agents,
            fail_fast=True
        )

        # Sauvegarder l'historique
        self._save_validation_history(report, level, changes)

        # Mettre à jour la dernière validation
        self._save_last_validation(report, level)

        return report

    def _file_checksum(self, file_path: Path) -> str:
        """Calcule le checksum MD5 d'un fichier."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _load_checksums(self) -> Dict[str, str]:
        """Charge les checksums sauvegardés."""
        if not self.checksums_file.exists():
            return {}
        try:
            with open(self.checksums_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

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
            'report_summary': {
                'status': report['global_status'],
                'agents': report['agents_executed'],
                'duration': report['duration_seconds'],
                'findings': report['total_findings'],
            }
        }

        with open(history_file, 'w') as f:
            json.dump(history_entry, f, indent=2, ensure_ascii=False)

    def _save_last_validation(self, report: Dict, level: str):
        """Sauvegarde la dernière validation."""
        last_validation = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'status': report['global_status'],
            'agents_executed': report['agents_executed'],
        }

        with open(self.last_validation_file, 'w') as f:
            json.dump(last_validation, f, indent=2)

    def get_last_validation(self) -> Optional[Dict]:
        """Récupère la dernière validation."""
        if not self.last_validation_file.exists():
            return None
        try:
            with open(self.last_validation_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None


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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Validation incrémentale intelligente (Stratégie B)"
    )
    parser.add_argument('module', help="Nom du module")
    parser.add_argument(
        '--level',
        choices=['QUICK', 'STANDARD', 'FULL'],
        default='STANDARD',
        help="Niveau de validation (défaut: STANDARD)"
    )

    args = parser.parse_args()

    try:
        report = incremental_validate(args.module, args.level)

        # Code de sortie
        if report.get('status') == 'SKIP':
            sys.exit(0)
        elif report.get('global_status') == 'FAIL':
            sys.exit(1)
        elif report.get('global_status') == 'WARN':
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
