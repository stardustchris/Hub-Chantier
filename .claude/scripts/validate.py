#!/usr/bin/env python3
"""
Script CLI pour valider un module avec les agents.

Usage:
    python .claude/scripts/validate.py auth
    python .claude/scripts/validate.py auth --agents architect-reviewer code-reviewer
    python .claude/scripts/validate.py auth --no-fail-fast
"""

import sys
import argparse
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator import validate_module


def main():
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        description="Validation d'un module Hub Chantier avec les 7 agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Valider le module auth (tous les agents, fail-fast)
  python .claude/scripts/validate.py auth

  # Valider uniquement avec architect-reviewer et code-reviewer
  python .claude/scripts/validate.py auth --agents architect-reviewer code-reviewer

  # Valider en mode continue-all (ne pas arrêter au premier échec)
  python .claude/scripts/validate.py auth --no-fail-fast

Agents disponibles:
  - sql-pro            : Validation migrations et schéma DB
  - python-pro         : Validation patterns Python et Clean Architecture
  - typescript-pro     : Validation types TypeScript et React
  - architect-reviewer : Validation Clean Architecture (4 layers)
  - test-automator     : Validation couverture tests
  - code-reviewer      : Validation qualité code
  - security-auditor   : Validation sécurité et RGPD
        """
    )

    parser.add_argument(
        'module',
        help="Nom du module à valider (ex: auth, employes, chantiers)"
    )

    parser.add_argument(
        '--agents',
        nargs='+',
        help="Liste des agents à exécuter (défaut: tous)",
        choices=[
            'sql-pro',
            'python-pro',
            'typescript-pro',
            'architect-reviewer',
            'test-automator',
            'code-reviewer',
            'security-auditor'
        ]
    )

    parser.add_argument(
        '--no-fail-fast',
        action='store_true',
        help="Continue l'exécution même si un agent échoue"
    )

    args = parser.parse_args()

    try:
        # Exécuter la validation
        report = validate_module(
            module_name=args.module,
            agents=args.agents,
            fail_fast=not args.no_fail_fast
        )

        # Code de sortie basé sur le statut global
        if report['global_status'] == 'FAIL':
            sys.exit(1)
        elif report['global_status'] == 'WARN':
            sys.exit(2)
        else:
            sys.exit(0)

    except ValueError as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
