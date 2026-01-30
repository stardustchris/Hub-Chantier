"""Agent Security Auditor - Validation sécurité RGPD/OWASP."""

import re
from pathlib import Path
from typing import List, Dict
from .base import BaseAgent, AgentReport, AgentStatus


class SecurityAuditorAgent(BaseAgent):
    """
    Agent d'audit de sécurité.

    Vérifie :
    - Validation des entrées (injection SQL, XSS, CSRF)
    - Authentification et sessions
    - Chiffrement des données sensibles
    - Gestion des secrets
    - Logging et audit trail
    - Conformité RGPD
    """

    SENSITIVE_DATA_PATTERNS = {
        # Cherche uniquement les VALEURS hardcodées, pas les noms de paramètres
        'password': r'password\s*=\s*["\'][^"\']{8,}["\']',  # password = "actualvalue"
        'api_key': r'api_key\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']',  # api_key = "sk_..."
        'secret': r'SECRET\s*=\s*["\'][^"\']{16,}["\']',  # SECRET = "value"
        'token': r'token\s*=\s*["\'][a-zA-Z0-9_-]{32,}["\']',  # token = "longvalue"
        'credit_card': r'["\']?\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}["\']?',
    }

    SQL_INJECTION_PATTERNS = [
        r'execute\([^)]*%[^)]*\)',  # execute("SELECT * FROM users WHERE id=%s" % id)
        r'execute\([^)]*\+[^)]*\)',  # execute("SELECT * FROM users WHERE id=" + id)
        r'f"SELECT.*\{.*\}"',  # f"SELECT * FROM users WHERE id={user_id}"
        r"f'SELECT.*\{.*\}'",
    ]

    XSS_PATTERNS = [
        r'innerHTML\s*=',
        r'dangerouslySetInnerHTML',
        r'\.html\(',
    ]

    WEAK_CRYPTO = [
        r'hashlib\.md5',
        r'hashlib\.sha1',
        r'random\.random\(',
    ]

    def validate(self) -> AgentReport:
        """Exécute l'audit de sécurité."""
        print(f"  🔒 Audit de sécurité...")

        module_path = Path(self.module_path)

        if not module_path.exists():
            return self._create_report(
                AgentStatus.SKIP,
                "Module non trouvé"
            )

        # Vérification 1 : Secrets en dur
        self._check_hardcoded_secrets(module_path)

        # Vérification 2 : Injection SQL
        self._check_sql_injection(module_path)

        # Vérification 3 : XSS
        self._check_xss_vulnerabilities(module_path)

        # Vérification 4 : Cryptographie faible
        self._check_weak_crypto(module_path)

        # Vérification 5 : Authentification
        self._check_authentication_security(module_path)

        # Vérification 6 : RGPD
        self._check_gdpr_compliance(module_path)

        # Déterminer le statut
        status = self._determine_status()

        # Calculer les scores
        score = self._calculate_scores()

        summary = self._generate_summary(status)

        return self._create_report(status, summary, score)

    def _check_hardcoded_secrets(self, module_path: Path):
        """Vérifie la présence de secrets en dur."""
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for secret_type, pattern in self.SENSITIVE_DATA_PATTERNS.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Ignorer si dans un commentaire
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line = content[line_start:match.end()]
                    if line.strip().startswith('#'):
                        continue

                    # Ignorer si valeur depuis env ou config
                    context = content[match.start():match.end()+100]
                    if 'os.getenv' in context or 'os.environ' in context or 'config' in context.lower():
                        continue

                    self.add_finding(
                        severity='CRITICAL',
                        message=f"Secret potentiel en dur : {secret_type}",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Utiliser des variables d'environnement (os.getenv)",
                        category='security'
                    )

    def _check_sql_injection(self, module_path: Path):
        """Vérifie les vulnérabilités d'injection SQL."""
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern in self.SQL_INJECTION_PATTERNS:
                matches = re.finditer(pattern, content)
                for match in matches:
                    self.add_finding(
                        severity='CRITICAL',
                        message="Vulnérabilité potentielle d'injection SQL",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Utiliser des requêtes paramétrées (SQLAlchemy ORM ou prepared statements)",
                        category='security'
                    )

            # Vérifier les raw SQL queries
            if re.search(r'\.execute\(.*text\(', content):
                self.add_finding(
                    severity='HIGH',
                    message="Utilisation de requêtes SQL brutes avec text()",
                    file=str(py_file.relative_to(Path.cwd())),
                    suggestion="Préférer l'ORM SQLAlchemy ou utiliser des paramètres bindés",
                    category='security'
                )

    def _check_xss_vulnerabilities(self, module_path: Path):
        """Vérifie les vulnérabilités XSS."""
        # Vérifier les fichiers TypeScript/React
        for tsx_file in module_path.rglob("*.tsx"):
            with open(tsx_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern in self.XSS_PATTERNS:
                matches = re.finditer(pattern, content)
                for match in matches:
                    self.add_finding(
                        severity='HIGH',
                        message="Vulnérabilité potentielle XSS",
                        file=str(tsx_file.relative_to(Path.cwd())),
                        suggestion="Sanitizer le contenu HTML avec DOMPurify ou éviter innerHTML",
                        category='security'
                    )

        # Vérifier Python (templates)
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier si validation Pydantic manquante sur endpoints
            if '@router.post' in content or '@router.put' in content:
                # Vérifier si les paramètres utilisent Pydantic
                if 'BaseModel' not in content and 'constr' not in content:
                    self.add_finding(
                        severity='MEDIUM',
                        message="Endpoint sans validation Pydantic stricte",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Utiliser des modèles Pydantic avec validators",
                        category='security'
                    )

    def _check_weak_crypto(self, module_path: Path):
        """Vérifie l'utilisation de cryptographie faible."""
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern in self.WEAK_CRYPTO:
                matches = re.finditer(pattern, content)
                for match in matches:
                    self.add_finding(
                        severity='CRITICAL',
                        message="Utilisation d'algorithme cryptographique faible",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Utiliser bcrypt (passwords) ou SHA-256+ (hashing)",
                        category='security'
                    )

            # Vérifier bcrypt cost factor
            bcrypt_match = re.search(r'bcrypt\.using\(rounds=(\d+)\)', content)
            if bcrypt_match:
                rounds = int(bcrypt_match.group(1))
                if rounds < 12:
                    self.add_finding(
                        severity='HIGH',
                        message=f"Facteur de coût bcrypt trop faible (rounds={rounds})",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Utiliser au minimum rounds=12 pour bcrypt",
                        category='security'
                    )

    def _check_authentication_security(self, module_path: Path):
        """Vérifie la sécurité de l'authentification."""
        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les sessions sans expiration
            if 'create_access_token' in content:
                if 'expires_delta' not in content and 'timedelta' not in content:
                    self.add_finding(
                        severity='HIGH',
                        message="Token JWT sans expiration définie",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Définir une expiration avec timedelta",
                        category='security'
                    )

            # Vérifier absence de rate limiting sur login
            if '/login' in content or '@router.post' in content:
                if 'login' in content.lower() and 'limiter' not in content.lower():
                    self.add_finding(
                        severity='HIGH',
                        message="Endpoint de login sans rate limiting",
                        file=str(py_file.relative_to(Path.cwd())),
                        suggestion="Implémenter rate limiting (slowapi ou similar)",
                        category='security'
                    )

    def _check_gdpr_compliance(self, module_path: Path):
        """Vérifie la conformité RGPD."""
        gdpr_features = {
            'export': False,
            'delete': False,
            'consent': False,
        }

        for py_file in module_path.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier présence d'export de données
            if 'export' in content.lower() or 'download.*data' in content.lower():
                gdpr_features['export'] = True

            # Vérifier droit à l'oubli
            if 'delete.*user' in content.lower() or 'remove.*account' in content.lower():
                gdpr_features['delete'] = True

            # Vérifier gestion du consentement
            if 'consent' in content.lower() or 'gdpr' in content.lower():
                gdpr_features['consent'] = True

        # Avertir si fonctionnalités RGPD manquantes
        if not gdpr_features['export']:
            self.add_finding(
                severity='MEDIUM',
                message="RGPD : Droit d'accès aux données non implémenté",
                file=str(module_path.relative_to(Path.cwd())),
                suggestion="Implémenter l'export des données utilisateur",
                category='security'
            )

        if not gdpr_features['delete']:
            self.add_finding(
                severity='MEDIUM',
                message="RGPD : Droit à l'oubli non implémenté",
                file=str(module_path.relative_to(Path.cwd())),
                suggestion="Implémenter la suppression complète des données",
                category='security'
            )

    def _calculate_scores(self) -> dict:
        """Calcule les scores de sécurité."""
        critical = len([f for f in self.findings if f.severity == 'CRITICAL'])
        high = len([f for f in self.findings if f.severity == 'HIGH'])

        security_score = max(0, 10 - critical * 3 - high)

        return {
            "security": f"{security_score}/10",
            "critical_issues": critical,
            "high_issues": high,
            "total_findings": len(self.findings),
        }

    def _generate_summary(self, status: AgentStatus) -> str:
        """Génère un résumé basé sur le statut."""
        critical = len([f for f in self.findings if f.severity == 'CRITICAL'])
        high = len([f for f in self.findings if f.severity == 'HIGH'])

        if status == AgentStatus.FAIL:
            return f"❌ ÉCHEC : {critical} vulnérabilité(s) critique(s)"
        elif status == AgentStatus.WARN:
            return f"⚠️  WARNING : {high} vulnérabilité(s) haute(s)"
        else:
            return "✅ Aucune vulnérabilité critique détectée"
