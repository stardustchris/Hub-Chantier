"""Module de sécurité pour les connecteurs externes.

Fournit des fonctions de validation, sanitization et audit trail
pour protéger contre XSS, injection et violations RGPD.
"""

import re
import hashlib
import logging
from typing import Optional, Union
from decimal import Decimal

try:
    import bleach
except ImportError:
    bleach = None

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Exception levée pour les violations de sécurité."""

    def __init__(self, message: str, field: Optional[str] = None):
        """
        Initialise l'exception de sécurité.

        Args:
            message: Description de l'erreur.
            field: Nom du champ concerné (optionnel).
        """
        self.message = message
        self.field = field
        super().__init__(self.message)


def sanitize_text(
    text: str,
    max_length: int = 500,
    allow_tags: bool = False
) -> str:
    """
    Sanitize du texte pour prévenir les attaques XSS.

    Supprime ou échappe tous les caractères dangereux (HTML, scripts, etc.).
    Utilise bleach si disponible, sinon fallback sur strip HTML basique.

    Args:
        text: Texte à sanitizer.
        max_length: Longueur maximale autorisée.
        allow_tags: Si True, autorise certaines balises HTML sûres (b, i, em, strong).

    Returns:
        Texte sanitizé et safe pour affichage/stockage.

    Raises:
        SecurityError: Si le texte dépasse max_length après sanitization.

    Example:
        >>> sanitize_text("Achat matériaux <script>alert('xss')</script>")
        "Achat matériaux"
        >>> sanitize_text("Montant: <b>1500€</b>", allow_tags=True)
        "Montant: <b>1500€</b>"
    """
    if not text:
        return ""

    if bleach is not None:
        # Mode sécurisé avec bleach
        allowed_tags = ['b', 'i', 'em', 'strong'] if allow_tags else []
        sanitized = bleach.clean(
            text,
            tags=allowed_tags,
            strip=True,
            strip_comments=True
        )
    else:
        # Fallback: suppression basique des balises HTML
        sanitized = re.sub(r'<[^>]*>', '', text)
        # Échappement des caractères dangereux
        sanitized = (
            sanitized
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;')
        )

    # Trim et validation longueur
    sanitized = sanitized.strip()
    if len(sanitized) > max_length:
        raise SecurityError(
            f"Texte trop long après sanitization: {len(sanitized)} > {max_length}",
            field="text"
        )

    return sanitized


def validate_code(
    code: str,
    pattern: str = r'^[A-Z0-9_-]{1,50}$',
    field_name: str = "code"
) -> str:
    """
    Valide le format d'un code (facture, employé, chantier).

    Prévient les injections en validant que le code respecte un format strict.

    Args:
        code: Code à valider.
        pattern: Regex pattern attendu (défaut: alphanumérique + underscore/tiret).
        field_name: Nom du champ pour les messages d'erreur.

    Returns:
        Code validé et uppercasé.

    Raises:
        SecurityError: Si le code ne respecte pas le pattern.

    Example:
        >>> validate_code("EMP001")
        "EMP001"
        >>> validate_code("CHT-2026-01")
        "CHT-2026-01"
        >>> validate_code("'; DROP TABLE users; --")
        SecurityError: Format de code invalide
    """
    if not code or not isinstance(code, str):
        raise SecurityError(
            f"{field_name} vide ou invalide",
            field=field_name
        )

    # Normalisation
    code_normalized = code.strip().upper()

    # Validation pattern
    if not re.match(pattern, code_normalized):
        raise SecurityError(
            f"Format de {field_name} invalide: '{code}'. "
            f"Attendu: {pattern}",
            field=field_name
        )

    return code_normalized


def validate_amount(
    amount: Union[float, Decimal, int],
    min_value: float = 0.0,
    max_value: Optional[float] = None,
    field_name: str = "montant"
) -> float:
    """
    Valide un montant financier.

    Prévient les montants négatifs, NaN, infinis ou hors limites.

    Args:
        amount: Montant à valider.
        min_value: Valeur minimale autorisée (défaut: 0.0).
        max_value: Valeur maximale autorisée (optionnel).
        field_name: Nom du champ pour les messages d'erreur.

    Returns:
        Montant validé en float.

    Raises:
        SecurityError: Si le montant est invalide ou hors limites.

    Example:
        >>> validate_amount(1500.00)
        1500.0
        >>> validate_amount(-100.00)
        SecurityError: Montant négatif détecté
        >>> validate_amount(float('inf'))
        SecurityError: Montant invalide (infini ou NaN)
    """
    try:
        amount_float = float(amount)
    except (ValueError, TypeError):
        raise SecurityError(
            f"{field_name} invalide: impossible de convertir en nombre",
            field=field_name
        )

    # Validation NaN / infini
    if not (amount_float == amount_float):  # NaN check
        raise SecurityError(
            f"{field_name} invalide: NaN détecté",
            field=field_name
        )

    if amount_float in [float('inf'), float('-inf')]:
        raise SecurityError(
            f"{field_name} invalide: infini détecté",
            field=field_name
        )

    # Validation limites
    if amount_float < min_value:
        raise SecurityError(
            f"{field_name} négatif ou en dessous du minimum: {amount_float} < {min_value}",
            field=field_name
        )

    if max_value is not None and amount_float > max_value:
        raise SecurityError(
            f"{field_name} au-dessus du maximum: {amount_float} > {max_value}",
            field=field_name
        )

    return amount_float


def mask_employee_code(employee_code: str) -> str:
    """
    Masque un code employé pour les logs (RGPD).

    Garde les 2 premiers et 2 derniers caractères, masque le reste.

    Args:
        employee_code: Code employé à masquer.

    Returns:
        Code masqué (ex: "EMP001" → "EM***01").

    Example:
        >>> mask_employee_code("EMP001")
        "EM***01"
        >>> mask_employee_code("EMPLOYE12345")
        "EM*******45"
        >>> mask_employee_code("E1")
        "**"
    """
    if not employee_code or len(employee_code) < 4:
        return "***"

    first_part = employee_code[:2]
    last_part = employee_code[-2:]
    masked_middle = "*" * (len(employee_code) - 4)

    return f"{first_part}{masked_middle}{last_part}"


def hash_employee_code(employee_code: str, salt: str = "hub-chantier-v1") -> str:
    """
    Hash un code employé pour l'audit trail.

    Utilise SHA-256 avec un salt pour permettre la traçabilité
    sans stocker le code en clair.

    Args:
        employee_code: Code employé à hasher.
        salt: Salt pour le hash (défaut: "hub-chantier-v1").

    Returns:
        Hash hexadécimal (64 caractères).

    Example:
        >>> hash_employee_code("EMP001")
        "a7b2c3d4e5f6..." (64 chars)
    """
    if not employee_code:
        raise SecurityError("Code employé vide pour hashing", field="employee_code")

    # Concatenation salt + code
    salted = f"{salt}:{employee_code}"

    # SHA-256 hash
    hash_object = hashlib.sha256(salted.encode('utf-8'))
    return hash_object.hexdigest()


def audit_log_employee_data(
    action: str,
    employee_code: str,
    period: Optional[str] = None,
    hours_count: Optional[int] = None,
    connector_name: str = "unknown"
) -> None:
    """
    Log un événement d'audit pour les données employé (RGPD).

    Stocke uniquement le hash de l'employé, pas le code en clair.

    Args:
        action: Action effectuée (ex: "send_hours", "update_payroll").
        employee_code: Code employé (sera hashé).
        period: Période concernée (optionnel).
        hours_count: Nombre d'heures traitées (optionnel).
        connector_name: Nom du connecteur externe.

    Example:
        >>> audit_log_employee_data(
        ...     action="send_hours",
        ...     employee_code="EMP001",
        ...     period="2026-01",
        ...     hours_count=5,
        ...     connector_name="silae"
        ... )
        # Log: [AUDIT] silae: send_hours | employee_hash=a7b2c3... | period=2026-01 | hours=5
    """
    employee_hash = hash_employee_code(employee_code)
    masked_code = mask_employee_code(employee_code)

    audit_parts = [
        f"action={action}",
        f"employee_hash={employee_hash[:12]}...",  # Premiers 12 chars du hash
        f"employee_masked={masked_code}",
        f"connector={connector_name}"
    ]

    if period:
        audit_parts.append(f"period={period}")
    if hours_count is not None:
        audit_parts.append(f"hours_count={hours_count}")

    # Log structuré pour audit trail
    logger.info(f"[AUDIT] {' | '.join(audit_parts)}")
