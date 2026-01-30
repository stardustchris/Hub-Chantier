"""Orchestrateur des agents de validation."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from agents.base import AgentStatus, AgentReport
from agents.architect import ArchitectReviewerAgent
from agents.code_reviewer import CodeReviewerAgent
from agents.security import SecurityAuditorAgent
from agents.test_automator import TestAutomatorAgent
from agents.sql_pro import SqlProAgent
from agents.python_pro import PythonProAgent
from agents.typescript_pro import TypeScriptProAgent


class ValidationOrchestrator:
    """
    Orchestrateur des 7 agents de validation.

    Exécute les agents dans l'ordre :
    1. sql-pro (si modifs DB)
    2. python-pro / typescript-pro (selon le contexte)
    3. architect-reviewer
    4. test-automator
    5. code-reviewer
    6. security-auditor

    Stratégie Fail-Fast : arrêt dès le premier FAIL.
    """

    def __init__(self, module_path: str, module_name: str, fail_fast: bool = True):
        """
        Initialise l'orchestrateur.

        Args:
            module_path: Chemin vers le module à valider.
            module_name: Nom du module (ex: 'auth').
            fail_fast: Si True, arrêt au premier FAIL.
        """
        self.module_path = module_path
        self.module_name = module_name
        self.fail_fast = fail_fast
        self.reports: List[AgentReport] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def run(self, agents: Optional[List[str]] = None) -> Dict:
        """
        Exécute la validation complète.

        Args:
            agents: Liste des agents à exécuter (None = tous).

        Returns:
            Rapport consolidé avec statut global et rapports des agents.
        """
        self.start_time = datetime.now()
        print(f"\n{'='*70}")
        print(f"🚀 VALIDATION DU MODULE : {self.module_name}")
        print(f"{'='*70}\n")

        # Définir l'ordre d'exécution
        all_agents = [
            ('sql-pro', SqlProAgent),
            ('python-pro', PythonProAgent),
            ('typescript-pro', TypeScriptProAgent),
            ('architect-reviewer', ArchitectReviewerAgent),
            ('test-automator', TestAutomatorAgent),
            ('code-reviewer', CodeReviewerAgent),
            ('security-auditor', SecurityAuditorAgent),
        ]

        # Filtrer si liste fournie
        if agents:
            all_agents = [(name, cls) for name, cls in all_agents if name in agents]

        # Exécuter chaque agent
        for agent_name, agent_class in all_agents:
            print(f"\n{'─'*70}")
            print(f"🤖 Agent : {agent_name}")
            print(f"{'─'*70}")

            try:
                agent = agent_class(
                    module_path=self.module_path,
                    module_name=self.module_name
                )
                report = agent.validate()
                self.reports.append(report)

                # Afficher le résumé
                self._print_report_summary(report)

                # Fail-Fast : arrêt si FAIL
                if self.fail_fast and report.status == AgentStatus.FAIL:
                    print(f"\n⛔ ARRÊT : Fail-Fast activé, agent '{agent_name}' a échoué")
                    break

            except Exception as e:
                print(f"❌ Erreur lors de l'exécution de {agent_name} : {e}")
                # Créer un rapport d'erreur
                error_report = AgentReport(
                    agent_name=agent_name,
                    status=AgentStatus.FAIL,
                    summary=f"Erreur d'exécution : {str(e)}",
                    findings=[],
                    score={},
                    module_name=self.module_name,
                    timestamp=datetime.now()
                )
                self.reports.append(error_report)

                if self.fail_fast:
                    break

        self.end_time = datetime.now()

        # Générer le rapport consolidé
        consolidated_report = self._consolidate_reports()

        # Sauvegarder le rapport JSON
        self._save_json_report(consolidated_report)

        # Afficher le résumé final
        self._print_final_summary(consolidated_report)

        return consolidated_report

    def _print_report_summary(self, report: AgentReport):
        """Affiche le résumé d'un rapport agent."""
        status_emoji = {
            AgentStatus.PASS: '✅',
            AgentStatus.WARN: '⚠️',
            AgentStatus.FAIL: '❌',
            AgentStatus.SKIP: '⏭️',
        }

        emoji = status_emoji.get(report.status, '❓')
        print(f"\n{emoji} Statut : {report.status.value}")
        print(f"📝 {report.summary}")

        if report.score:
            print(f"\n📊 Scores :")
            for key, value in report.score.items():
                print(f"   • {key}: {value}")

        if report.findings:
            print(f"\n🔍 Findings ({len(report.findings)}) :")
            # Grouper par sévérité
            by_severity = {}
            for finding in report.findings:
                by_severity.setdefault(finding.severity, []).append(finding)

            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity in by_severity:
                    findings = by_severity[severity]
                    severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}
                    print(f"\n   {severity_emoji.get(severity, '⚪')} {severity} ({len(findings)}) :")
                    for finding in findings[:3]:  # Limiter à 3 par sévérité
                        print(f"      - {finding.message}")
                        if finding.file:
                            print(f"        📄 {finding.file}")
                    if len(findings) > 3:
                        print(f"      ... et {len(findings) - 3} autres")

    def _consolidate_reports(self) -> Dict:
        """Consolide tous les rapports en un rapport global."""
        # Déterminer le statut global
        global_status = AgentStatus.PASS

        for report in self.reports:
            if report.status == AgentStatus.FAIL:
                global_status = AgentStatus.FAIL
                break
            elif report.status == AgentStatus.WARN and global_status != AgentStatus.FAIL:
                global_status = AgentStatus.WARN

        # Compter les findings par sévérité
        total_findings = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
        }

        for report in self.reports:
            for finding in report.findings:
                total_findings[finding.severity] += 1

        # Calculer la durée
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0

        return {
            'module': self.module_name,
            'global_status': global_status.value,
            'timestamp': self.end_time.isoformat() if self.end_time else datetime.now().isoformat(),
            'duration_seconds': duration,
            'agents_executed': len(self.reports),
            'total_findings': total_findings,
            'reports': [
                {
                    'agent': report.agent_name,
                    'status': report.status.value,
                    'summary': report.summary,
                    'score': report.score,
                    'findings_count': len(report.findings),
                    'findings': [
                        {
                            'severity': f.severity,
                            'message': f.message,
                            'file': f.file,
                            'suggestion': f.suggestion,
                            'category': f.category,
                        }
                        for f in report.findings
                    ]
                }
                for report in self.reports
            ]
        }

    def _save_json_report(self, consolidated_report: Dict):
        """Sauvegarde le rapport JSON."""
        reports_dir = Path.cwd() / '.claude' / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f"{self.module_name}_validation_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Rapport sauvegardé : {report_file.relative_to(Path.cwd())}")

    def _print_final_summary(self, consolidated_report: Dict):
        """Affiche le résumé final de la validation."""
        print(f"\n{'='*70}")
        print(f"📋 RÉSUMÉ FINAL - Module {self.module_name}")
        print(f"{'='*70}")

        status = consolidated_report['global_status']
        status_emoji = {
            'PASS': '✅',
            'WARN': '⚠️',
            'FAIL': '❌',
            'SKIP': '⏭️',
        }

        print(f"\n{status_emoji.get(status, '❓')} Statut global : {status}")
        print(f"⏱️  Durée : {consolidated_report['duration_seconds']:.2f}s")
        print(f"🤖 Agents exécutés : {consolidated_report['agents_executed']}")

        total = consolidated_report['total_findings']
        print(f"\n📊 Findings totaux :")
        print(f"   🔴 CRITICAL : {total['CRITICAL']}")
        print(f"   🟠 HIGH     : {total['HIGH']}")
        print(f"   🟡 MEDIUM   : {total['MEDIUM']}")
        print(f"   🔵 LOW      : {total['LOW']}")

        # Résumé par agent
        print(f"\n🎯 Résultats par agent :")
        for report_data in consolidated_report['reports']:
            agent_status = report_data['status']
            emoji = status_emoji.get(agent_status, '❓')
            print(f"   {emoji} {report_data['agent']:20} : {report_data['findings_count']} finding(s)")

        print(f"\n{'='*70}\n")

        # Décision finale
        if status == 'PASS':
            print("✅ VALIDATION RÉUSSIE - Module prêt à être commité")
        elif status == 'WARN':
            print("⚠️  WARNINGS PRÉSENTS - Corriger les problèmes avant commit")
        else:
            print("❌ VALIDATION ÉCHOUÉE - Corrections obligatoires")


def validate_module(module_name: str, agents: Optional[List[str]] = None, fail_fast: bool = True) -> Dict:
    """
    Point d'entrée principal pour valider un module.

    Args:
        module_name: Nom du module (ex: 'auth').
        agents: Liste des agents à exécuter (None = tous).
        fail_fast: Si True, arrêt au premier FAIL.

    Returns:
        Rapport consolidé.
    """
    # Déterminer le chemin du module
    module_path = Path.cwd() / 'backend' / 'modules' / module_name

    if not module_path.exists():
        raise ValueError(f"Module '{module_name}' non trouvé à {module_path}")

    orchestrator = ValidationOrchestrator(
        module_path=str(module_path),
        module_name=module_name,
        fail_fast=fail_fast
    )

    return orchestrator.run(agents=agents)
