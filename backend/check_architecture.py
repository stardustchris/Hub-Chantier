#!/usr/bin/env python3
"""
Script de vérification de l'architecture Clean Architecture.
Vérifie que les règles de dépendances sont respectées.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Violation:
    file: str
    line: int
    import_statement: str
    reason: str

# Frameworks interdits dans le domain
FORBIDDEN_DOMAIN_IMPORTS = {
    'fastapi', 'sqlalchemy', 'pydantic.fields', 'pydantic.validator',
    'jose', 'passlib', 'httpx', 'requests', 'redis', 'celery',
    'alembic', 'pytest', 'unittest'
}

# Imports autorisés dans le domain
ALLOWED_DOMAIN_IMPORTS = {
    'pydantic', 'pydantic.BaseModel', 'datetime', 'typing', 'enum',
    'abc', 'uuid', 'dataclasses', 'decimal', 're'
}

def _is_inside_type_checking(node: ast.AST, tree: ast.Module) -> bool:
    """Vérifie si un noeud est à l'intérieur d'un bloc 'if TYPE_CHECKING:'."""
    for top_node in ast.walk(tree):
        if isinstance(top_node, ast.If):
            # Vérifie 'if TYPE_CHECKING:' ou 'if typing.TYPE_CHECKING:'
            test = top_node.test
            is_type_checking = False
            if isinstance(test, ast.Name) and test.id == 'TYPE_CHECKING':
                is_type_checking = True
            elif isinstance(test, ast.Attribute) and test.attr == 'TYPE_CHECKING':
                is_type_checking = True

            if is_type_checking:
                # Vérifie si le noeud import est dans le body de ce if
                for child in ast.walk(top_node):
                    if child is node:
                        return True
    return False


def extract_imports(file_path: str) -> List[Tuple[int, str, str]]:
    """Extrait tous les imports d'un fichier Python (hors TYPE_CHECKING)."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Ignorer les imports dans les blocs TYPE_CHECKING
                if _is_inside_type_checking(node, tree):
                    continue

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((node.lineno, alias.name, f"import {alias.name}"))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_import = f"{module}.{alias.name}" if module else alias.name
                    imports.append((node.lineno, full_import, f"from {module} import {alias.name}"))
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")

    return imports

def check_domain_imports(file_path: str) -> List[Violation]:
    """Vérifie qu'un fichier domain n'importe pas de frameworks."""
    violations = []
    imports = extract_imports(file_path)

    for line_no, import_name, import_stmt in imports:
        # Vérifie les imports interdits
        for forbidden in FORBIDDEN_DOMAIN_IMPORTS:
            if import_name.startswith(forbidden):
                violations.append(Violation(
                    file=file_path,
                    line=line_no,
                    import_statement=import_stmt,
                    reason=f"Import de framework interdit dans domain: {forbidden}"
                ))

        # Vérifie les imports pydantic (sauf BaseModel)
        if import_name.startswith('pydantic'):
            # Autorisé: pydantic, pydantic.BaseModel
            # Interdit: pydantic.Field, pydantic.validator, etc.
            if not any(import_name.startswith(allowed) for allowed in ALLOWED_DOMAIN_IMPORTS):
                if 'Field' in import_name or 'validator' in import_name or 'root_validator' in import_name:
                    violations.append(Violation(
                        file=file_path,
                        line=line_no,
                        import_statement=import_stmt,
                        reason=f"Import Pydantic non autorisé dans domain: {import_name}"
                    ))

    return violations

def check_use_case_dependencies(file_path: str) -> List[Violation]:
    """Vérifie qu'un use case dépend d'interfaces, pas d'implémentations."""
    violations = []
    imports = extract_imports(file_path)

    for line_no, import_name, import_stmt in imports:
        # Vérifie les imports directs d'infrastructure
        if '.infrastructure.' in import_name or '.adapters.persistence.' in import_name:
            violations.append(Violation(
                file=file_path,
                line=line_no,
                import_statement=import_stmt,
                reason="Use case importe directement de l'infrastructure au lieu d'une interface"
            ))

        # Vérifie les imports de SQLAlchemy models
        if 'sqlalchemy' in import_name.lower() or '.models.' in import_name:
            violations.append(Violation(
                file=file_path,
                line=line_no,
                import_statement=import_stmt,
                reason="Use case importe des modèles SQLAlchemy au lieu d'utiliser des entités domain"
            ))

    return violations

def check_cross_module_imports(file_path: str) -> List[Violation]:
    """Vérifie qu'il n'y a pas d'imports cross-modules directs (sauf events)."""
    violations = []

    # Déterminer le module courant
    parts = Path(file_path).parts
    try:
        modules_idx = parts.index('modules')
        current_module = parts[modules_idx + 1]
    except (ValueError, IndexError):
        return violations

    imports = extract_imports(file_path)

    for line_no, import_name, import_stmt in imports:
        # Vérifie les imports depuis d'autres modules
        if '.modules.' in import_name or import_name.startswith('modules.'):
            # Extrait le module cible
            if '.modules.' in import_name:
                target_module = import_name.split('.modules.')[1].split('.')[0]
            else:
                target_module = import_name.split('.')[1] if len(import_name.split('.')) > 1 else ''

            # Autorisé si c'est le même module ou si c'est un event
            if target_module != current_module and '.events' not in import_name:
                violations.append(Violation(
                    file=file_path,
                    line=line_no,
                    import_statement=import_stmt,
                    reason=f"Import cross-module direct de '{target_module}' depuis '{current_module}' (utilisez events)"
                ))

    return violations

def scan_directory(base_path: str, pattern: str, check_func) -> List[Violation]:
    """Scanne un répertoire et applique une fonction de vérification."""
    violations = []
    base = Path(base_path)

    for file_path in base.rglob(pattern):
        if file_path.is_file() and file_path.suffix == '.py':
            violations.extend(check_func(str(file_path)))

    return violations

def main():
    backend_path = Path(__file__).parent

    print("=" * 80)
    print("VERIFICATION ARCHITECTURE CLEAN ARCHITECTURE")
    print("=" * 80)
    print()

    all_violations = []

    # 1. Vérification des imports domain
    print("1. Vérification des imports dans domain/...")
    domain_violations = scan_directory(
        str(backend_path / 'modules'),
        '*/domain/**/*.py',
        check_domain_imports
    )
    all_violations.extend(domain_violations)
    print(f"   → {len(domain_violations)} violation(s) trouvée(s)")
    print()

    # 2. Vérification des dépendances use cases
    print("2. Vérification des dépendances dans application/use_cases/...")
    use_case_violations = scan_directory(
        str(backend_path / 'modules'),
        '*/application/use_cases/**/*.py',
        check_use_case_dependencies
    )
    all_violations.extend(use_case_violations)
    print(f"   → {len(use_case_violations)} violation(s) trouvée(s)")
    print()

    # 3. Vérification des imports cross-modules
    print("3. Vérification des imports cross-modules...")
    cross_module_violations = []
    for pattern in ['*/domain/**/*.py', '*/application/**/*.py']:
        cross_module_violations.extend(scan_directory(
            str(backend_path / 'modules'),
            pattern,
            check_cross_module_imports
        ))
    all_violations.extend(cross_module_violations)
    print(f"   → {len(cross_module_violations)} violation(s) trouvée(s)")
    print()

    # Affichage des violations
    print("=" * 80)
    print(f"TOTAL: {len(all_violations)} VIOLATION(S)")
    print("=" * 80)
    print()

    if all_violations:
        # Grouper par fichier
        violations_by_file: Dict[str, List[Violation]] = {}
        for v in all_violations:
            if v.file not in violations_by_file:
                violations_by_file[v.file] = []
            violations_by_file[v.file].append(v)

        # Afficher par fichier
        for file_path, violations in sorted(violations_by_file.items()):
            rel_path = str(Path(file_path).relative_to(backend_path))
            print(f"\n📄 {rel_path}")
            print("-" * 80)
            for v in sorted(violations, key=lambda x: x.line):
                print(f"   Ligne {v.line}: {v.import_statement}")
                print(f"   ❌ {v.reason}")
                print()

        print("=" * 80)
        print("STATUS: ❌ FAIL")
        print("=" * 80)
        return 1
    else:
        print("✅ Aucune violation détectée")
        print()
        print("=" * 80)
        print("STATUS: ✅ PASS")
        print("=" * 80)
        return 0

if __name__ == '__main__':
    exit(main())
