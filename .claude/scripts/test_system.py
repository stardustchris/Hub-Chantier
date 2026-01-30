#!/usr/bin/env python3
"""Script de test rapide du système de validation."""

import sys
from pathlib import Path

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import validate_module

if __name__ == '__main__':
    print("🧪 Test du système de validation\n")

    try:
        # Test sur le module auth avec un seul agent
        print("Test 1 : Validation module 'auth' avec architect-reviewer uniquement\n")

        report = validate_module(
            module_name='auth',
            agents=['architect-reviewer'],
            fail_fast=True
        )

        print(f"\n✅ Test réussi !")
        print(f"   Status global : {report['global_status']}")
        print(f"   Agents exécutés : {report['agents_executed']}")
        print(f"   Durée : {report['duration_seconds']:.2f}s")

    except Exception as e:
        print(f"\n❌ Test échoué : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
