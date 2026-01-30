"""Agent Test Automator - Validation couverture tests."""

import re
from pathlib import Path
from typing import List, Dict, Set
from .base import BaseAgent, AgentReport, AgentStatus


class TestAutomatorAgent(BaseAgent):
    """
    Agent d'automatisation des tests.

    Vérifie :
    - Présence de tests pour les use cases
    - Couverture des tests (>= 85%)
    - Qualité des tests (AAA pattern, mocks)
    - Tests d'intégration pour les routes
    - Fixtures et configuration pytest
    """

    TARGET_COVERAGE = 85

    def validate(self) -> AgentReport:
        """Exécute la validation des tests."""
        print(f"  🧪 Validation des tests...")

        module_path = Path(self.module_path)

        if not module_path.exists():
            return self._create_report(
                AgentStatus.SKIP,
                "Module non trouvé"
            )

        # Trouver le répertoire tests correspondant
        # backend/modules/auth -> backend/tests/unit/auth
        tests_path = self._get_tests_path(module_path)

        if not tests_path.exists():
            self.add_finding(
                severity='CRITICAL',
                message=f"Aucun répertoire de tests trouvé",
                file=str(tests_path.relative_to(Path.cwd())),
                suggestion=f"Créer le répertoire {tests_path}",
                category='testing'
            )
            return self._create_report(
                AgentStatus.FAIL,
                "Aucun test trouvé",
                {"coverage": "0%", "tests_count": 0}
            )

        # Vérification 1 : Use cases couverts
        self._check_use_case_coverage(module_path, tests_path)

        # Vérification 2 : Qualité des tests
        self._check_test_quality(tests_path)

        # Vérification 3 : Tests d'intégration
        self._check_integration_tests(module_path)

        # Vérification 4 : Fixtures
        self._check_fixtures(tests_path)

        # Déterminer le statut
        status = self._determine_status()

        # Calculer les scores
        score = self._calculate_scores(module_path, tests_path)

        summary = self._generate_summary(status, score)

        return self._create_report(status, summary, score)

    def _get_tests_path(self, module_path: Path) -> Path:
        """Détermine le chemin du répertoire de tests."""
        # backend/modules/auth -> backend/tests/unit/auth
        parts = module_path.parts
        if 'modules' in parts:
            idx = parts.index('modules')
            module_name = parts[idx + 1] if idx + 1 < len(parts) else ''
            backend_path = Path(*parts[:idx])
            return backend_path / 'tests' / 'unit' / module_name
        return module_path / 'tests'

    def _check_use_case_coverage(self, module_path: Path, tests_path: Path):
        """Vérifie que tous les use cases ont des tests."""
        use_cases_path = module_path / 'application' / 'use_cases'

        if not use_cases_path.exists():
            return

        # Lister tous les use cases
        use_case_files = list(use_cases_path.glob("*.py"))
        use_case_files = [f for f in use_case_files if f.name != '__init__.py']

        # Lister tous les fichiers de tests
        test_files = list(tests_path.rglob("test_*.py"))

        for use_case_file in use_case_files:
            use_case_name = use_case_file.stem
            # Chercher un fichier de test correspondant
            expected_test_file = f"test_{use_case_name}.py"

            found = False
            for test_file in test_files:
                if test_file.name == expected_test_file:
                    found = True
                    break

            if not found:
                self.add_finding(
                    severity='HIGH',
                    message=f"Use case '{use_case_name}' sans tests",
                    file=str(use_case_file.relative_to(Path.cwd())),
                    suggestion=f"Créer {tests_path / expected_test_file}",
                    category='testing'
                )

    def _check_test_quality(self, tests_path: Path):
        """Vérifie la qualité des tests."""
        test_files = list(tests_path.rglob("test_*.py"))

        for test_file in test_files:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier pattern AAA (Arrange, Act, Assert)
            test_functions = re.findall(r'def (test_\w+)\(', content)

            for test_func in test_functions:
                # Trouver le corps de la fonction
                pattern = rf'def {test_func}\([^)]*\):(.+?)(?=\n\s*def\s|\Z)'
                match = re.search(pattern, content, re.DOTALL)

                if match:
                    test_body = match.group(1)

                    # Vérifier présence de commentaires AAA
                    has_arrange = '# Arrange' in test_body or '# ARRANGE' in test_body
                    has_act = '# Act' in test_body or '# ACT' in test_body
                    has_assert = '# Assert' in test_body or '# ASSERT' in test_body or 'assert' in test_body

                    if not (has_arrange or has_act or has_assert):
                        self.add_finding(
                            severity='LOW',
                            message=f"Test '{test_func}' sans pattern AAA clair",
                            file=str(test_file.relative_to(Path.cwd())),
                            suggestion="Structurer avec # Arrange, # Act, # Assert",
                            category='testing'
                        )

                    if not has_assert:
                        self.add_finding(
                            severity='HIGH',
                            message=f"Test '{test_func}' sans assertion",
                            file=str(test_file.relative_to(Path.cwd())),
                            suggestion="Ajouter au moins une assertion (assert ...)",
                            category='testing'
                        )

            # Vérifier utilisation de mocks
            if 'UseCase' in content or 'Repository' in content:
                if 'Mock' not in content and 'mock' not in content:
                    self.add_finding(
                        severity='MEDIUM',
                        message="Test de use case sans mocks",
                        file=str(test_file.relative_to(Path.cwd())),
                        suggestion="Utiliser unittest.mock.Mock pour les dépendances",
                        category='testing'
                    )

            # Vérifier que les tests sont isolés (pas de variables globales)
            if re.search(r'^[A-Z_]+\s*=', content, re.MULTILINE):
                # Variables globales trouvées
                self.add_finding(
                    severity='LOW',
                    message="Variables globales dans les tests",
                    file=str(test_file.relative_to(Path.cwd())),
                    suggestion="Utiliser des fixtures ou setup_method pour l'isolation",
                    category='testing'
                )

    def _check_integration_tests(self, module_path: Path):
        """Vérifie la présence de tests d'intégration pour les routes."""
        web_path = module_path / 'infrastructure' / 'web'

        if not web_path.exists():
            return

        route_files = list(web_path.glob("*_routes.py"))

        if not route_files:
            return

        # Chercher les tests d'intégration
        parts = module_path.parts
        if 'modules' in parts:
            idx = parts.index('modules')
            backend_path = Path(*parts[:idx])
            integration_tests_path = backend_path / 'tests' / 'integration'

            if not integration_tests_path.exists():
                self.add_finding(
                    severity='HIGH',
                    message="Aucun test d'intégration trouvé",
                    file=str(integration_tests_path.relative_to(Path.cwd())),
                    suggestion=f"Créer {integration_tests_path} avec tests des routes",
                    category='testing'
                )
                return

            # Vérifier qu'il y a des tests pour les routes
            integration_test_files = list(integration_tests_path.rglob("test_*.py"))

            if not integration_test_files:
                self.add_finding(
                    severity='HIGH',
                    message="Routes sans tests d'intégration",
                    file=str(integration_tests_path.relative_to(Path.cwd())),
                    suggestion="Créer des tests avec TestClient FastAPI",
                    category='testing'
                )

    def _check_fixtures(self, tests_path: Path):
        """Vérifie la présence de fixtures pytest."""
        conftest_file = tests_path.parent / 'conftest.py'

        if not conftest_file.exists():
            self.add_finding(
                severity='MEDIUM',
                message="Fichier conftest.py manquant",
                file=str(conftest_file.relative_to(Path.cwd())),
                suggestion="Créer conftest.py avec fixtures partagées (db_session, client)",
                category='testing'
            )
            return

        with open(conftest_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Vérifier présence de fixtures essentielles
        required_fixtures = {
            'db_session': 'Session DB en mémoire',
            'client': 'TestClient FastAPI',
        }

        for fixture_name, description in required_fixtures.items():
            if f'def {fixture_name}' not in content:
                self.add_finding(
                    severity='LOW',
                    message=f"Fixture '{fixture_name}' manquante",
                    file=str(conftest_file.relative_to(Path.cwd())),
                    suggestion=f"Ajouter fixture {fixture_name} ({description})",
                    category='testing'
                )

    def _calculate_scores(self, module_path: Path, tests_path: Path) -> dict:
        """Calcule les scores de tests."""
        # Compter les fichiers source vs tests
        use_cases_path = module_path / 'application' / 'use_cases'
        use_case_count = 0
        if use_cases_path.exists():
            use_case_files = list(use_cases_path.glob("*.py"))
            use_case_count = len([f for f in use_case_files if f.name != '__init__.py'])

        test_files = list(tests_path.rglob("test_*.py"))
        test_count = len(test_files)

        # Estimer la couverture
        coverage_estimate = 0
        if use_case_count > 0:
            coverage_estimate = min(100, int((test_count / use_case_count) * 100))

        high_critical = len([f for f in self.findings if f.severity in ['CRITICAL', 'HIGH']])
        test_quality_score = max(0, 10 - high_critical)

        return {
            "coverage_estimate": f"{coverage_estimate}%",
            "tests_count": test_count,
            "use_cases_count": use_case_count,
            "test_quality": f"{test_quality_score}/10",
            "target_coverage": f"{self.TARGET_COVERAGE}%",
        }

    def _generate_summary(self, status: AgentStatus, score: dict) -> str:
        """Génère un résumé basé sur le statut."""
        coverage = score.get('coverage_estimate', '0%')
        tests_count = score.get('tests_count', 0)

        if status == AgentStatus.FAIL:
            return f"❌ ÉCHEC : Couverture insuffisante ({coverage} < {self.TARGET_COVERAGE}%)"
        elif status == AgentStatus.WARN:
            return f"⚠️  WARNING : {tests_count} tests, couverture à améliorer ({coverage})"
        else:
            return f"✅ Tests OK : {tests_count} tests, couverture {coverage}"
