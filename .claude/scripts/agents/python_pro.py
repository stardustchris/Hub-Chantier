"""Agent Python Pro - Validation patterns Python et Clean Architecture."""

import re
from pathlib import Path
from typing import List, Dict
from .base import BaseAgent, AgentReport, AgentStatus


class PythonProAgent(BaseAgent):
    """
    Agent expert Python.

    Vérifie :
    - Patterns pythoniques
    - Type hints complets
    - Dataclasses pour entités
    - Respect Clean Architecture (4 layers)
    - Gestion d'erreurs avec exceptions custom
    """

    def validate(self) -> AgentReport:
        """Exécute la validation Python."""
        print(f"  🐍 Validation Python...")

        module_path = Path(self.module_path)

        if not module_path.exists():
            return self._create_report(
                AgentStatus.SKIP,
                "Module non trouvé"
            )

        # Vérification 1 : Entités Domain (dataclasses)
        self._check_domain_entities(module_path)

        # Vérification 2 : Use cases structure
        self._check_use_cases(module_path)

        # Vérification 3 : Repository interfaces
        self._check_repositories(module_path)

        # Vérification 4 : FastAPI routes
        self._check_routes(module_path)

        # Déterminer le statut
        status = self._determine_status()

        # Calculer les scores
        score = self._calculate_scores()

        summary = self._generate_summary(status)

        return self._create_report(status, summary, score)

    def _check_domain_entities(self, module_path: Path):
        """Vérifie les entités Domain."""
        entities_path = module_path / 'domain' / 'entities'

        if not entities_path.exists():
            return

        entity_files = list(entities_path.glob("*.py"))
        entity_files = [f for f in entity_files if f.name != '__init__.py']

        for entity_file in entity_files:
            with open(entity_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier utilisation de dataclass
            if '@dataclass' not in content and 'class ' in content:
                self.add_finding(
                    severity='HIGH',
                    message=f"Entité sans @dataclass",
                    file=str(entity_file.relative_to(Path.cwd())),
                    suggestion="Utiliser @dataclass pour les entités Domain",
                    category='python'
                )

            # Vérifier présence de type hints
            class_matches = re.finditer(r'class\s+(\w+)', content)
            for class_match in class_matches:
                class_name = class_match.group(1)

                # Chercher les attributs de classe
                class_start = class_match.start()
                next_class = re.search(r'\nclass\s+\w+', content[class_start+1:])
                class_end = class_start + next_class.start() if next_class else len(content)
                class_body = content[class_start:class_end]

                # Vérifier les attributs sans type hints
                attr_pattern = r'^\s+(\w+)\s*='
                for attr_match in re.finditer(attr_pattern, class_body, re.MULTILINE):
                    attr_name = attr_match.group(1)
                    attr_line = class_body[attr_match.start():attr_match.end()+50]

                    if ':' not in attr_line and attr_name not in ['self', 'cls']:
                        self.add_finding(
                            severity='MEDIUM',
                            message=f"Attribut '{attr_name}' dans '{class_name}' sans type hint",
                            file=str(entity_file.relative_to(Path.cwd())),
                            suggestion=f"{attr_name}: Type = ...",
                            category='python'
                        )

            # Vérifier __eq__ et __hash__ pour entités
            if 'class ' in content:
                if '__eq__' not in content:
                    self.add_finding(
                        severity='LOW',
                        message="Entité sans __eq__ défini",
                        file=str(entity_file.relative_to(Path.cwd())),
                        suggestion="Implémenter __eq__ basé sur l'ID",
                        category='python'
                    )

    def _check_use_cases(self, module_path: Path):
        """Vérifie les use cases."""
        use_cases_path = module_path / 'application' / 'use_cases'

        if not use_cases_path.exists():
            return

        use_case_files = list(use_cases_path.glob("*.py"))
        use_case_files = [f for f in use_case_files if f.name != '__init__.py']

        for use_case_file in use_case_files:
            with open(use_case_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier présence de méthode execute
            if 'def execute(' not in content:
                self.add_finding(
                    severity='HIGH',
                    message="Use case sans méthode execute()",
                    file=str(use_case_file.relative_to(Path.cwd())),
                    suggestion="Ajouter def execute(self, dto: InputDTO) -> OutputDTO:",
                    category='python'
                )

            # Vérifier injection de dépendances
            if '__init__' in content:
                init_match = re.search(r'def __init__\(self([^)]*)\)', content)
                if init_match:
                    params = init_match.group(1)
                    # Vérifier que les dépendances sont injectées
                    if 'repo' not in params.lower() and 'repository' not in params.lower():
                        self.add_finding(
                            severity='MEDIUM',
                            message="Use case sans injection de repository",
                            file=str(use_case_file.relative_to(Path.cwd())),
                            suggestion="Injecter le repository via __init__(self, repo: RepoInterface)",
                            category='python'
                        )

            # Vérifier exceptions custom
            if 'raise Exception(' in content:
                self.add_finding(
                    severity='HIGH',
                    message="Use case utilise Exception générique",
                    file=str(use_case_file.relative_to(Path.cwd())),
                    suggestion="Créer une exception custom (class XxxError(Exception))",
                    category='python'
                )

    def _check_repositories(self, module_path: Path):
        """Vérifie les repository interfaces."""
        repo_path = module_path / 'domain' / 'repositories'

        if not repo_path.exists():
            return

        repo_files = list(repo_path.glob("*.py"))
        repo_files = [f for f in repo_files if f.name != '__init__.py']

        for repo_file in repo_files:
            with open(repo_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier que c'est une interface (ABC)
            if 'ABC' not in content and 'class ' in content:
                self.add_finding(
                    severity='CRITICAL',
                    message="Repository n'hérite pas de ABC",
                    file=str(repo_file.relative_to(Path.cwd())),
                    suggestion="Utiliser from abc import ABC, abstractmethod et hériter de ABC",
                    category='python'
                )

            # Vérifier @abstractmethod
            if 'def ' in content and '@abstractmethod' not in content:
                self.add_finding(
                    severity='HIGH',
                    message="Repository sans @abstractmethod",
                    file=str(repo_file.relative_to(Path.cwd())),
                    suggestion="Décorer toutes les méthodes avec @abstractmethod",
                    category='python'
                )

            # Vérifier méthodes standard
            required_methods = ['find_by_id', 'save', 'delete']
            for method in required_methods:
                if f'def {method}' not in content:
                    self.add_finding(
                        severity='MEDIUM',
                        message=f"Repository sans méthode {method}()",
                        file=str(repo_file.relative_to(Path.cwd())),
                        suggestion=f"Ajouter @abstractmethod def {method}(...)",
                        category='python'
                    )

    def _check_routes(self, module_path: Path):
        """Vérifie les routes FastAPI."""
        web_path = module_path / 'infrastructure' / 'web'

        if not web_path.exists():
            return

        route_files = list(web_path.glob("*_routes.py"))

        for route_file in route_files:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier utilisation de router
            if 'APIRouter' not in content:
                self.add_finding(
                    severity='HIGH',
                    message="Routes sans APIRouter",
                    file=str(route_file.relative_to(Path.cwd())),
                    suggestion="Créer router = APIRouter(prefix='/xxx', tags=['xxx'])",
                    category='python'
                )

            # Vérifier gestion des erreurs
            route_defs = re.findall(r'@router\.(get|post|put|delete)', content)
            if route_defs and 'try:' not in content:
                self.add_finding(
                    severity='MEDIUM',
                    message="Routes sans gestion d'erreurs",
                    file=str(route_file.relative_to(Path.cwd())),
                    suggestion="Entourer les appels use case avec try/except et lever HTTPException",
                    category='python'
                )

            # Vérifier response_model
            if '@router.' in content:
                routes_without_response = re.findall(
                    r'@router\.(get|post|put|delete)\([^)]*\)\s*\n\s*def',
                    content
                )
                if routes_without_response:
                    for match in routes_without_response:
                        if 'response_model=' not in content:
                            self.add_finding(
                                severity='LOW',
                                message="Route sans response_model",
                                file=str(route_file.relative_to(Path.cwd())),
                                suggestion="Ajouter response_model=ResponseModel dans le décorateur",
                                category='python'
                            )
                            break

    def _calculate_scores(self) -> dict:
        """Calcule les scores Python."""
        critical_high = len([f for f in self.findings if f.severity in ['CRITICAL', 'HIGH']])

        python_quality_score = max(0, 10 - critical_high * 2)

        return {
            "python_quality": f"{python_quality_score}/10",
            "total_findings": len(self.findings),
        }

    def _generate_summary(self, status: AgentStatus) -> str:
        """Génère un résumé basé sur le statut."""
        critical = len([f for f in self.findings if f.severity == 'CRITICAL'])
        high = len([f for f in self.findings if f.severity == 'HIGH'])

        if status == AgentStatus.FAIL:
            return f"❌ ÉCHEC : {critical} problème(s) critique(s) Python"
        elif status == AgentStatus.WARN:
            return f"⚠️  WARNING : {high} problème(s) haute(s) priorité Python"
        else:
            return "✅ Code Python conforme aux standards"
