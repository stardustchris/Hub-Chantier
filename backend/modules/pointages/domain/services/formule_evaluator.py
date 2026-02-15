"""Service d'evaluation securisee de formules arithmetiques (FDH-18).

Extrait du domain entity MacroPaie pour garder le layer entites pur
(pas de dependance stdlib ast dans les entites).

L'evaluateur parse les expressions via l'AST Python et n'autorise
qu'un sous-ensemble strict d'operations arithmetiques et de fonctions.
"""

import ast
from typing import Dict, Any


def evaluer_formule_safe(formule: str, variables: Dict[str, Any]) -> float:
    """
    Evalue une formule de maniere securisee via AST.

    Parse l'expression en arbre syntaxique et n'autorise que :
    - Operations arithmetiques (+, -, *, /, //, %, **)
    - Operateurs unaires (+, -)
    - Fonctions whitelist (min, max, round, abs, int, float)
    - Variables nommees et constantes numeriques

    Aucun eval(), exec(), import, acces attribut ou indexation.

    Args:
        formule: Expression a evaluer.
        variables: Variables disponibles.

    Returns:
        Resultat numerique.

    Raises:
        ValueError: Si la formule contient des noeuds non autorises.
    """
    safe_functions: Dict[str, Any] = {
        "min": min,
        "max": max,
        "round": round,
        "abs": abs,
        "int": int,
        "float": float,
    }

    # Convertir toutes les valeurs en float
    safe_vars: Dict[str, float] = {}
    for key, value in variables.items():
        try:
            safe_vars[key] = float(value) if value is not None else 0.0
        except (TypeError, ValueError):
            safe_vars[key] = 0.0

    def _eval_node(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)

        if isinstance(node, ast.Name):
            if node.id in safe_vars:
                return safe_vars[node.id]
            raise ValueError(f"Variable inconnue: {node.id}")

        if isinstance(node, ast.BinOp):
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            ops = {
                ast.Add: lambda a, b: a + b,
                ast.Sub: lambda a, b: a - b,
                ast.Mult: lambda a, b: a * b,
                ast.Div: lambda a, b: a / b,
                ast.FloorDiv: lambda a, b: a // b,
                ast.Mod: lambda a, b: a % b,
                ast.Pow: lambda a, b: a ** b,
            }
            op_type = type(node.op)
            if op_type not in ops:
                raise ValueError(f"Opérateur non autorisé: {op_type.__name__}")
            return ops[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = _eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError(f"Opérateur unaire non autorisé: {type(node.op).__name__}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Seuls les appels de fonctions nommées sont autorisés")
            func_name = node.func.id
            if func_name not in safe_functions:
                raise ValueError(f"Fonction non autorisée: {func_name}")
            args = [_eval_node(arg) for arg in node.args]
            return float(safe_functions[func_name](*args))

        raise ValueError(f"Expression non autorisée: {type(node).__name__}")

    tree = ast.parse(formule, mode="eval")
    return _eval_node(tree)
