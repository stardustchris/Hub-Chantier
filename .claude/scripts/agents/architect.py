"""Agent Architect Reviewer - Validation Clean Architecture."""

import re
from pathlib import Path
from typing import List
from .base import BaseAgent, AgentReport, AgentStatus


class ArchitectReviewerAgent(BaseAgent):
    """
    Agent de validation Clean Architecture.

    Vérifie :
    - Domain n'importe d'aucun framework
    - Use cases dépendent d'interfaces (pas d'implémentations)
    - Pas d'imports directs entre modules
    - Communication via Events uniquement
    """

    FORBIDDEN_IMPORTS_IN_DOMAIN = [
        'fastapi', 'sqlalchemy', 'pydantic', 'flask', 'django',
        'requests', 'httpx', 'aiohttp'
    ]

    ALLOWED_IMPORTS_IN_DOMAIN = [
        'dataclasses', 'datetime', 'typing', 'abc', 'enum',
        'collections', 'functools', 'itertools'
    ]

    def validate(self) -> AgentReport:
        """Exécute la validation architecture."""
        print(f"  🏛️  Vérification Clean Architecture...")

        domain_path = Path(self.module_path) / "domain"

        if not domain_path.exists():
            return self._create_report(
                AgentStatus.SKIP,
                "Pas de couche Domain trouvée"
            )

        # Vérification 1 : Domain layer purity
        self._check_domain_imports(domain_path)

        # Vérification 2 : Use cases dépendent d'interfaces
        self._check_use_case_dependencies()

        # Vérification 3 : Pas d'imports directs entre modules
        self._check_cross_module_imports()

        # Déterminer le statut
        status = self._determine_status()

        # Calculer les scores
        score = self._calculate_scores()

        summary = self._generate_summary(status)

        return self._create_report(status, summary, score)

    def _check_domain_imports(self, domain_path: Path):
        """Vérifie que Domain n'importe pas de frameworks."""
        for py_file in domain_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les imports interdits
            for forbidden in self.FORBIDDEN_IMPORTS_IN_DOMAIN:
                pattern = rf'(?:from {forbidden}|import {forbidden})'
                if re.search(pattern, content):
                    self.add_finding(
                        severity='CRITICAL',
                        message=f"Domain ne doit pas importer '{forbidden}' (violation Clean Architecture)",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion=f"Déplacer cette dépendance dans Infrastructure ou Application",
                        category='architecture'
                    )

    def _check_use_case_dependencies(self):
        """Vérifie que les Use Cases dépendent d'interfaces."""
        use_cases_path = Path(self.module_path) / "application" / "use_cases"

        if not use_cases_path.exists():
            return

        for py_file in use_cases_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier imports directs d'implémentations
            # Pattern: from ...infrastructure.persistence import SQLAlchemy*Repository
            pattern = r'from \.\.\.infrastructure\.persistence import \w+'
            if re.search(pattern, content):
                self.add_finding(
                    severity='HIGH',
                    message="Use Case importe une implémentation directement (violation Dependency Inversion)",
                    file=str(py_file.relative_to(Path.cwd())),
                    suggestion="Injecter le Repository via __init__ avec le type de l'interface",
                    category='architecture'
                )

    def _check_cross_module_imports(self):
        """Vérifie qu'il n'y a pas d'imports directs entre modules."""
        module_files = Path(self.module_path).rglob("*.py")

        for py_file in module_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Pattern: from modules.autre_module.
            pattern = r'from modules\.(?!' + self.module_name + r')(\w+)\.'
            matches = re.findall(pattern, content)

            if matches:
                for other_module in matches:
                    self.add_finding(
                        severity='HIGH',
                        message=f"Import direct du module '{other_module}' (violation isolation des modules)",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Utiliser EventBus pour la communication inter-modules",
                        category='architecture'
                    )

    def _calculate_scores(self) -> dict:
        """Calcule les scores d'architecture."""
        total_files = len(list(Path(self.module_path).rglob("*.py")))
        files_with_issues = len(set(f.file for f in self.findings))

        clean_architecture_score = max(0, 10 - len([f for f in self.findings if f.severity in ['CRITICAL', 'HIGH']]))
        modularity_score = max(0, 10 - files_with_issues)

        return {
            "clean_architecture": f"{clean_architecture_score}/10",
            "modularity": f"{modularity_score}/10",
            "files_analyzed": total_files,
        }

    def _generate_summary(self, status: AgentStatus) -> str:
        """Génère un résumé basé sur le statut."""
        critical = len([f for f in self.findings if f.severity == 'CRITICAL'])
        high = len([f for f in self.findings if f.severity == 'HIGH'])

        if status == AgentStatus.FAIL:
            return f"❌ ÉCHEC : {critical} violation(s) critique(s) Clean Architecture"
        elif status == AgentStatus.WARN:
            return f"⚠️  WARNING : {high} violation(s) haute(s) architecture"
        else:
            return "✅ Architecture Clean respectée"
