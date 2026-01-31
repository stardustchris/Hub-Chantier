#!/usr/bin/env python3
"""Analyse la type coverage du module chantiers."""

import ast
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class TypeHintAnalyzer(ast.NodeVisitor):
    """Analyse AST pour identifier les manques de type hints."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues: List[Dict[str, Any]] = []
        self.total_functions = 0
        self.typed_functions = 0
        self.total_params = 0
        self.typed_params = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visite chaque fonction/méthode."""
        self.total_functions += 1

        # Ignorer les méthodes spéciales sauf __init__
        if node.name.startswith("__") and node.name != "__init__":
            self.generic_visit(node)
            return

        # Vérifier le type de retour
        has_return_type = node.returns is not None
        if has_return_type:
            self.typed_functions += 1
        else:
            # Cas spécial: __init__ doit avoir -> None
            if node.name == "__init__":
                self.issues.append({
                    "line": node.lineno,
                    "function": node.name,
                    "issue": "Missing -> None on __init__",
                    "severity": "HIGH"
                })
            else:
                self.issues.append({
                    "line": node.lineno,
                    "function": node.name,
                    "issue": "Missing return type annotation",
                    "severity": "MEDIUM"
                })

        # Vérifier les paramètres
        for arg in node.args.args:
            self.total_params += 1
            # Ignorer 'self' et 'cls'
            if arg.arg in ("self", "cls"):
                continue

            if arg.annotation is None:
                self.issues.append({
                    "line": node.lineno,
                    "function": node.name,
                    "issue": f"Parameter '{arg.arg}' missing type hint",
                    "severity": "HIGH"
                })
            else:
                self.typed_params += 1

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visite chaque fonction async."""
        # Même traitement que FunctionDef
        self.visit_FunctionDef(node)  # type: ignore

    def analyze(self) -> Dict[str, Any]:
        """Analyse le fichier et retourne les résultats."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=self.filepath)
            self.visit(tree)

            # Calculer le taux de couverture
            func_coverage = (self.typed_functions / self.total_functions * 100) if self.total_functions > 0 else 100
            param_coverage = (self.typed_params / self.total_params * 100) if self.total_params > 0 else 100

            return {
                "file": str(self.filepath),
                "total_functions": self.total_functions,
                "typed_functions": self.typed_functions,
                "function_coverage": round(func_coverage, 1),
                "total_params": self.total_params,
                "typed_params": self.typed_params,
                "param_coverage": round(param_coverage, 1),
                "issues": self.issues,
                "needs_fixes": len(self.issues) > 0
            }
        except Exception as e:
            return {
                "file": str(self.filepath),
                "error": str(e),
                "needs_fixes": False
            }


def analyze_module(module_path: Path) -> Dict[str, Any]:
    """Analyse tous les fichiers Python d'un module."""
    python_files = list(module_path.rglob("*.py"))

    results = []
    total_issues = 0
    files_needing_fixes = []

    for filepath in python_files:
        # Ignorer les fichiers de test et migrations
        if "test" in str(filepath) or "migration" in str(filepath):
            continue

        analyzer = TypeHintAnalyzer(str(filepath))
        result = analyzer.analyze()

        if result.get("needs_fixes"):
            files_needing_fixes.append(result)
            total_issues += len(result.get("issues", []))

        results.append(result)

    # Calculer les statistiques globales
    total_funcs = sum(r.get("total_functions", 0) for r in results if "error" not in r)
    typed_funcs = sum(r.get("typed_functions", 0) for r in results if "error" not in r)
    total_params = sum(r.get("total_params", 0) for r in results if "error" not in r)
    typed_params = sum(r.get("typed_params", 0) for r in results if "error" not in r)

    func_coverage = (typed_funcs / total_funcs * 100) if total_funcs > 0 else 100
    param_coverage = (typed_params / total_params * 100) if total_params > 0 else 100
    overall_coverage = (func_coverage + param_coverage) / 2

    # Trier par priorité (HIGH d'abord, puis nombre d'issues)
    files_needing_fixes.sort(key=lambda x: (
        -sum(1 for i in x.get("issues", []) if i.get("severity") == "HIGH"),
        -len(x.get("issues", []))
    ))

    return {
        "module": str(module_path),
        "files_analyzed": len(results),
        "files_needing_fixes": len(files_needing_fixes),
        "total_issues": total_issues,
        "statistics": {
            "total_functions": total_funcs,
            "typed_functions": typed_funcs,
            "function_coverage": round(func_coverage, 1),
            "total_parameters": total_params,
            "typed_parameters": typed_params,
            "parameter_coverage": round(param_coverage, 1),
            "overall_coverage": round(overall_coverage, 1)
        },
        "files_with_issues": files_needing_fixes,
        "recommendations": generate_recommendations(files_needing_fixes)
    }


def generate_recommendations(files_with_issues: List[Dict[str, Any]]) -> List[str]:
    """Génère des recommandations basées sur les issues trouvées."""
    recommendations = []

    # Compter les types d'issues
    missing_init_return = sum(
        1 for f in files_with_issues
        for i in f.get("issues", [])
        if "__init__" in i.get("issue", "")
    )

    missing_return_types = sum(
        1 for f in files_with_issues
        for i in f.get("issues", [])
        if "return type" in i.get("issue", "") and "__init__" not in i.get("issue", "")
    )

    missing_param_types = sum(
        1 for f in files_with_issues
        for i in f.get("issues", [])
        if "Parameter" in i.get("issue", "")
    )

    if missing_init_return > 0:
        recommendations.append(f"Add -> None to {missing_init_return} __init__ methods")

    if missing_return_types > 0:
        recommendations.append(f"Add return type annotations to {missing_return_types} functions/methods")

    if missing_param_types > 0:
        recommendations.append(f"Add type hints to {missing_param_types} parameters")

    # Fichiers prioritaires
    high_priority_files = [
        f for f in files_with_issues
        if any(i.get("severity") == "HIGH" for i in f.get("issues", []))
    ]

    if high_priority_files:
        recommendations.append(f"Focus on {len(high_priority_files)} files with HIGH severity issues first")

    return recommendations


if __name__ == "__main__":
    module_path = Path(__file__).parent.parent / "backend" / "modules" / "chantiers"

    print("🔍 Analyzing type coverage for module 'chantiers'...")
    print()

    result = analyze_module(module_path)

    # Affichage console
    print(f"📊 Analysis Results:")
    print(f"  Files analyzed: {result['files_analyzed']}")
    print(f"  Files needing fixes: {result['files_needing_fixes']}")
    print(f"  Total issues found: {result['total_issues']}")
    print()

    stats = result['statistics']
    print(f"📈 Type Coverage:")
    print(f"  Function coverage: {stats['function_coverage']}% ({stats['typed_functions']}/{stats['total_functions']})")
    print(f"  Parameter coverage: {stats['parameter_coverage']}% ({stats['typed_parameters']}/{stats['total_parameters']})")
    print(f"  Overall coverage: {stats['overall_coverage']}%")
    print()

    if result['recommendations']:
        print(f"💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
        print()

    # Sauvegarder le rapport JSON
    output_path = Path(__file__).parent / "type_coverage_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Full report saved to: {output_path}")
    print()

    # Afficher les 10 fichiers prioritaires
    if result['files_with_issues']:
        print(f"🔥 Top 10 files needing attention:")
        for i, file_info in enumerate(result['files_with_issues'][:10], 1):
            file_path = Path(file_info['file'])
            rel_path = file_path.relative_to(module_path)
            issue_count = len(file_info.get('issues', []))
            high_count = sum(1 for iss in file_info.get('issues', []) if iss.get('severity') == 'HIGH')
            print(f"  {i}. {rel_path}")
            print(f"     Issues: {issue_count} (HIGH: {high_count})")
