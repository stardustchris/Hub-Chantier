"""Agent Code Reviewer - Validation qualité code."""

import re
from pathlib import Path
from typing import List, Set
from .base import BaseAgent, AgentReport, AgentStatus


class CodeReviewerAgent(BaseAgent):
    """
    Agent de revue de code.

    Vérifie :
    - Docstrings Google style
    - Type hints obligatoires
    - Conventions de nommage
    - Gestion des erreurs
    - Complexité cyclomatique
    """

    def validate(self) -> AgentReport:
        """Exécute la validation qualité code."""
        print(f"  📝 Revue de code...")

        module_path = Path(self.module_path)

        if not module_path.exists():
            return self._create_report(
                AgentStatus.SKIP,
                "Module non trouvé"
            )

        # Vérification 1 : Docstrings
        self._check_docstrings(module_path)

        # Vérification 2 : Type hints
        self._check_type_hints(module_path)

        # Vérification 3 : Nommage
        self._check_naming_conventions(module_path)

        # Vérification 4 : Gestion des erreurs
        self._check_error_handling(module_path)

        # Vérification 5 : Complexité
        self._check_complexity(module_path)

        # Déterminer le statut
        status = self._determine_status()

        # Calculer les scores
        score = self._calculate_scores()

        summary = self._generate_summary(status)

        return self._create_report(status, summary, score)

    def _check_docstrings(self, module_path: Path):
        """Vérifie la présence de docstrings Google style."""
        for py_file in module_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Trouver toutes les définitions de fonctions/méthodes
            func_pattern = r'^\s*def\s+(\w+)\s*\([^)]*\)\s*(?:->.*?)?:'
            functions = re.finditer(func_pattern, content, re.MULTILINE)

            for func_match in functions:
                func_name = func_match.group(1)

                # Ignorer les méthodes privées et __init__
                if func_name.startswith('_') and func_name != '__init__':
                    continue

                # Vérifier si docstring présente après la définition
                func_end = func_match.end()
                after_def = content[func_end:func_end+200]

                if not re.search(r'^\s*"""', after_def, re.MULTILINE):
                    self.add_finding(
                        severity='MEDIUM',
                        message=f"Fonction '{func_name}' sans docstring Google style",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Ajouter une docstring avec Args, Returns, Raises",
                        category='quality'
                    )

    def _check_type_hints(self, module_path: Path):
        """Vérifie la présence de type hints."""
        for py_file in module_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Trouver les fonctions sans type hints sur les paramètres ou retour
            # Pattern: def func(param) ou def func(...) -> None: sans : Type
            pattern = r'def\s+(\w+)\s*\(([^)]*)\)\s*(?!->)'
            matches = re.finditer(pattern, content)

            for match in matches:
                func_name = match.group(1)
                params = match.group(2)

                # Ignorer __init__ et méthodes privées
                if func_name.startswith('_'):
                    continue

                # Vérifier si les paramètres ont des type hints
                if params and 'self' not in params and 'cls' not in params:
                    if ':' not in params:
                        self.add_finding(
                            severity='HIGH',
                            message=f"Fonction '{func_name}' sans type hints sur les paramètres",
                            file=str(py_file.relative_to(Path.cwd())),
                            suggestion="Ajouter les type hints : def func(param: Type) -> ReturnType:",
                            category='quality'
                        )

            # Vérifier les fonctions sans annotation de retour
            pattern_no_return = r'def\s+(\w+)\s*\([^)]*\)\s*:'
            matches_no_return = re.finditer(pattern_no_return, content)

            for match in matches_no_return:
                func_name = match.group(1)
                if not func_name.startswith('_'):
                    self.add_finding(
                        severity='MEDIUM',
                        message=f"Fonction '{func_name}' sans annotation de retour",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Ajouter -> ReturnType ou -> None",
                        category='quality'
                    )

    def _check_naming_conventions(self, module_path: Path):
        """Vérifie les conventions de nommage."""
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les classes (PascalCase)
            class_pattern = r'class\s+([a-z_]\w*)'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                self.add_finding(
                    severity='LOW',
                    message=f"Classe '{class_name}' ne suit pas PascalCase",
                    file=str(py_file.relative_to(Path.cwd())),
                    suggestion=f"Renommer en {self._to_pascal_case(class_name)}",
                    category='quality'
                )

            # Vérifier les constantes (UPPER_CASE)
            # Pattern: variable = au niveau module (pas indenté)
            const_pattern = r'^([a-z]\w*)\s*=\s*["\']|^([a-z]\w*)\s*=\s*\d'
            for match in re.finditer(const_pattern, content, re.MULTILINE):
                const_name = match.group(1) or match.group(2)
                if const_name and const_name.isupper() is False:
                    # Vérifier si c'est vraiment une constante (valeur simple)
                    line = content[match.start():match.end()]
                    if '=' in line and not line.strip().startswith('def'):
                        self.add_finding(
                            severity='LOW',
                            message=f"Constante '{const_name}' devrait être en UPPER_CASE",
                            file=str(py_file.relative_to(Path.cwd())),
                            suggestion=f"Renommer en {const_name.upper()}",
                            category='quality'
                        )

    def _check_error_handling(self, module_path: Path):
        """Vérifie la gestion des erreurs."""
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les exceptions génériques
            if re.search(r'raise Exception\(', content):
                self.add_finding(
                    severity='HIGH',
                    message="Utilisation d'Exception générique au lieu d'exceptions custom",
                    file=str(py_file.relative_to(Path.cwd())),
                    suggestion="Créer une exception custom héritant de Exception",
                    category='quality'
                )

            # Vérifier les except: sans type
            if re.search(r'except\s*:', content):
                self.add_finding(
                    severity='MEDIUM',
                    message="Clause except sans type d'exception spécifique",
                    file=str(py_file.relative_to(Path.cwd())),
                    suggestion="Spécifier le type : except ValueError:",
                    category='quality'
                )

            # Vérifier les pass silencieux dans except
            if re.search(r'except.*:\s*pass', content):
                self.add_finding(
                    severity='HIGH',
                    message="Exception capturée et ignorée silencieusement",
                    file=str(py_file.relative_to(Path.cwd())),
                    suggestion="Logger l'erreur ou la re-lever",
                    category='quality'
                )

    def _check_complexity(self, module_path: Path):
        """Vérifie la complexité cyclomatique approximative."""
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Trouver toutes les fonctions
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            functions = re.finditer(func_pattern, content)

            for func_match in functions:
                func_name = func_match.group(1)
                func_start = func_match.start()

                # Trouver la fin de la fonction (prochaine def ou fin de fichier)
                next_func = re.search(r'\ndef\s+\w+', content[func_start+1:])
                func_end = func_start + next_func.start() if next_func else len(content)

                func_body = content[func_start:func_end]

                # Compter les branches (if, elif, for, while, except, and, or)
                complexity = 1  # Base complexity
                complexity += len(re.findall(r'\bif\b', func_body))
                complexity += len(re.findall(r'\belif\b', func_body))
                complexity += len(re.findall(r'\bfor\b', func_body))
                complexity += len(re.findall(r'\bwhile\b', func_body))
                complexity += len(re.findall(r'\bexcept\b', func_body))
                complexity += len(re.findall(r'\band\b', func_body))
                complexity += len(re.findall(r'\bor\b', func_body))

                if complexity > 10:
                    self.add_finding(
                        severity='MEDIUM',
                        message=f"Fonction '{func_name}' a une complexité cyclomatique élevée ({complexity})",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Refactorer en fonctions plus petites (complexité cible < 10)",
                        category='quality'
                    )

    def _calculate_scores(self) -> dict:
        """Calcule les scores de qualité."""
        total_files = len(list(Path(self.module_path).rglob("*.py")))
        files_with_issues = len(set(f.file for f in self.findings))

        critical_high = len([f for f in self.findings if f.severity in ['CRITICAL', 'HIGH']])

        quality_score = max(0, 10 - critical_high)
        maintainability_score = max(0, 10 - files_with_issues)

        return {
            "quality": f"{quality_score}/10",
            "maintainability": f"{maintainability_score}/10",
            "files_reviewed": total_files,
            "issues_found": len(self.findings),
        }

    def _generate_summary(self, status: AgentStatus) -> str:
        """Génère un résumé basé sur le statut."""
        critical = len([f for f in self.findings if f.severity == 'CRITICAL'])
        high = len([f for f in self.findings if f.severity == 'HIGH'])
        medium = len([f for f in self.findings if f.severity == 'MEDIUM'])

        if status == AgentStatus.FAIL:
            return f"❌ ÉCHEC : {critical} problème(s) critique(s) de qualité"
        elif status == AgentStatus.WARN:
            return f"⚠️  WARNING : {high} problème(s) haute(s) priorité, {medium} moyen(s)"
        else:
            return "✅ Code de qualité acceptable"

    @staticmethod
    def _to_pascal_case(snake_str: str) -> str:
        """Convertit snake_case en PascalCase."""
        return ''.join(word.capitalize() for word in snake_str.split('_'))
