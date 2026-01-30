"""Agent TypeScript Pro - Validation types et React."""

import re
from pathlib import Path
from typing import List, Dict
from .base import BaseAgent, AgentReport, AgentStatus


class TypeScriptProAgent(BaseAgent):
    """
    Agent expert TypeScript/React.

    Vérifie :
    - Mode strict TypeScript
    - Types complets pour APIs
    - Composants React typés
    - Hooks avec types
    - Pas de 'any' explicite
    """

    def validate(self) -> AgentReport:
        """Exécute la validation TypeScript."""
        print(f"  ⚛️  Validation TypeScript/React...")

        module_path = Path(self.module_path)

        if not module_path.exists():
            return self._create_report(
                AgentStatus.SKIP,
                "Module non trouvé"
            )

        # Vérification 1 : Configuration TypeScript
        self._check_tsconfig()

        # Vérification 2 : Types API
        self._check_api_types(module_path)

        # Vérification 3 : Composants React
        self._check_react_components(module_path)

        # Vérification 4 : Hooks
        self._check_hooks(module_path)

        # Déterminer le statut
        status = self._determine_status()

        # Calculer les scores
        score = self._calculate_scores()

        summary = self._generate_summary(status)

        return self._create_report(status, summary, score)

    def _check_tsconfig(self):
        """Vérifie la configuration TypeScript."""
        tsconfig_path = Path.cwd() / 'frontend' / 'tsconfig.json'

        if not tsconfig_path.exists():
            self.add_finding(
                severity='CRITICAL',
                message="Fichier tsconfig.json manquant",
                file=str(tsconfig_path.relative_to(Path.cwd())),
                suggestion="Créer tsconfig.json avec strict: true",
                category='typescript'
            )
            return

        with open(tsconfig_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Vérifier mode strict
        if '"strict": true' not in content and "'strict': true" not in content:
            self.add_finding(
                severity='HIGH',
                message="Mode strict TypeScript désactivé",
                file=str(tsconfig_path.relative_to(Path.cwd())),
                suggestion='Activer "strict": true dans compilerOptions',
                category='typescript'
            )

        # Vérifier autres flags importants
        recommended_flags = {
            'noUnusedLocals': 'Détecte les variables non utilisées',
            'noUnusedParameters': 'Détecte les paramètres non utilisés',
            'noFallthroughCasesInSwitch': 'Détecte les switch sans break',
        }

        for flag, description in recommended_flags.items():
            if f'"{flag}"' not in content and f"'{flag}'" not in content:
                self.add_finding(
                    severity='LOW',
                    message=f"Flag TypeScript '{flag}' manquant",
                    file=str(tsconfig_path.relative_to(Path.cwd())),
                    suggestion=f'Ajouter "{flag}": true ({description})',
                    category='typescript'
                )

    def _check_api_types(self, module_path: Path):
        """Vérifie les types pour l'API."""
        # Chercher src/types/api.ts dans le frontend
        frontend_path = Path.cwd() / 'frontend' / 'src'

        if not frontend_path.exists():
            return

        types_path = frontend_path / 'types' / 'api.ts'

        if not types_path.exists():
            self.add_finding(
                severity='MEDIUM',
                message="Fichier src/types/api.ts manquant",
                file=str(types_path.relative_to(Path.cwd())),
                suggestion="Créer types/api.ts avec les interfaces pour l'API",
                category='typescript'
            )
            return

        with open(types_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Vérifier présence de types essentiels
        required_types = ['User', 'AuthResponse', 'LoginRequest']
        for type_name in required_types:
            if f'interface {type_name}' not in content and f'type {type_name}' not in content:
                self.add_finding(
                    severity='MEDIUM',
                    message=f"Type '{type_name}' manquant dans api.ts",
                    file=str(types_path.relative_to(Path.cwd())),
                    suggestion=f"Ajouter export interface {type_name} {{ ... }}",
                    category='typescript'
                )

    def _check_react_components(self, module_path: Path):
        """Vérifie les composants React."""
        frontend_path = Path.cwd() / 'frontend' / 'src'

        if not frontend_path.exists():
            return

        tsx_files = list(frontend_path.rglob("*.tsx"))

        for tsx_file in tsx_files:
            with open(tsx_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier les composants sans props typées
            # Pattern: export function Component({...}) ou export default function Component({...})
            comp_pattern = r'export\s+(?:default\s+)?function\s+(\w+)\s*\(\s*\{([^}]*)\}'
            matches = re.finditer(comp_pattern, content)

            for match in matches:
                comp_name = match.group(1)
                props_destructure = match.group(2)

                # Chercher si une interface Props est définie
                if f'{comp_name}Props' not in content and props_destructure.strip():
                    self.add_finding(
                        severity='MEDIUM',
                        message=f"Composant '{comp_name}' sans interface Props",
                        file=str(tsx_file.relative_to(Path.cwd())),
                        suggestion=f"Créer interface {comp_name}Props {{ ... }}",
                        category='typescript'
                    )

            # Vérifier utilisation de 'any'
            if ': any' in content or '<any>' in content:
                self.add_finding(
                    severity='HIGH',
                    message="Utilisation de 'any' explicite",
                    file=str(tsx_file.relative_to(Path.cwd())),
                    suggestion="Remplacer 'any' par un type spécifique ou 'unknown'",
                    category='typescript'
                )

            # Vérifier les useState sans type
            usestate_pattern = r'useState\(([^)]+)\)'
            usestate_matches = re.finditer(usestate_pattern, content)

            for usestate_match in usestate_matches:
                initial_value = usestate_match.group(1).strip()
                # Vérifier si type générique fourni
                before_useState = content[:usestate_match.start()]
                if '<' not in before_useState[-20:] and initial_value in ['null', 'undefined', '{}', '[]']:
                    self.add_finding(
                        severity='MEDIUM',
                        message="useState sans type explicite (valeur initiale ambiguë)",
                        file=str(tsx_file.relative_to(Path.cwd())),
                        suggestion="Utiliser useState<Type>(initialValue)",
                        category='typescript'
                    )

    def _check_hooks(self, module_path: Path):
        """Vérifie les hooks custom."""
        frontend_path = Path.cwd() / 'frontend' / 'src'

        if not frontend_path.exists():
            return

        hooks_path = frontend_path / 'hooks'

        if not hooks_path.exists():
            return

        hook_files = list(hooks_path.glob("use*.ts")) + list(hooks_path.glob("use*.tsx"))

        for hook_file in hook_files:
            with open(hook_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier que le hook retourne un type explicite
            hook_pattern = r'export\s+function\s+(use\w+)\s*\([^)]*\)\s*(?::\s*([^{]+))?\s*\{'
            matches = re.finditer(hook_pattern, content)

            for match in matches:
                hook_name = match.group(1)
                return_type = match.group(2)

                if not return_type or return_type.strip() == '':
                    self.add_finding(
                        severity='MEDIUM',
                        message=f"Hook '{hook_name}' sans type de retour explicite",
                        file=str(hook_file.relative_to(Path.cwd())),
                        suggestion=f"Ajouter : ReturnType après les paramètres",
                        category='typescript'
                    )

    def _calculate_scores(self) -> dict:
        """Calcule les scores TypeScript."""
        critical_high = len([f for f in self.findings if f.severity in ['CRITICAL', 'HIGH']])

        typescript_quality_score = max(0, 10 - critical_high * 2)

        return {
            "typescript_quality": f"{typescript_quality_score}/10",
            "total_findings": len(self.findings),
        }

    def _generate_summary(self, status: AgentStatus) -> str:
        """Génère un résumé basé sur le statut."""
        critical = len([f for f in self.findings if f.severity == 'CRITICAL'])
        high = len([f for f in self.findings if f.severity == 'HIGH'])

        if status == AgentStatus.FAIL:
            return f"❌ ÉCHEC : {critical} problème(s) critique(s) TypeScript"
        elif status == AgentStatus.WARN:
            return f"⚠️  WARNING : {high} problème(s) haute(s) priorité TypeScript"
        else:
            return "✅ Code TypeScript conforme aux standards"
