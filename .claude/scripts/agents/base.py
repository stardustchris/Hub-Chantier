"""Classe de base pour tous les agents de validation."""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import time


class AgentStatus(Enum):
    """Statuts possibles d'un agent."""
    PASS = "PASS"           # ✅ Validation réussie
    WARN = "WARN"           # ⚠️ Avertissements non-bloquants
    FAIL = "FAIL"           # ❌ Échec bloquant
    SKIP = "SKIP"           # ⏭️ Agent non applicable


@dataclass
class Finding:
    """Résultat d'une vérification."""
    severity: str           # CRITICAL, HIGH, MEDIUM, LOW, INFO
    message: str           # Description du problème
    file: str             # Fichier concerné
    line: Optional[int] = None
    suggestion: Optional[str] = None  # Comment corriger
    category: Optional[str] = None    # security, performance, quality, design


@dataclass
class AgentReport:
    """Rapport de validation d'un agent."""
    agent_name: str
    status: AgentStatus
    findings: List[Finding]
    execution_time: float
    summary: str
    score: Optional[dict] = None  # Scores optionnels (ex: {"clean_architecture": "8/10"})


class BaseAgent(ABC):
    """
    Classe abstraite pour tous les agents.

    Tous les agents héritent de cette classe et implémentent la méthode validate().
    """

    def __init__(self, module_path: str, module_name: str):
        """
        Initialise l'agent.

        Args:
            module_path: Chemin vers le module (ex: "backend/modules/auth")
            module_name: Nom du module (ex: "auth")
        """
        self.module_path = module_path
        self.module_name = module_name
        self.findings: List[Finding] = []

    @abstractmethod
    def validate(self) -> AgentReport:
        """
        Exécute la validation et retourne un rapport.

        Returns:
            AgentReport avec le statut et les findings.
        """
        pass

    def add_finding(
        self,
        severity: str,
        message: str,
        file: str,
        line: Optional[int] = None,
        suggestion: Optional[str] = None,
        category: Optional[str] = None,
    ):
        """
        Ajoute un finding au rapport.

        Args:
            severity: CRITICAL, HIGH, MEDIUM, LOW, INFO
            message: Description du problème
            file: Fichier concerné
            line: Numéro de ligne (optionnel)
            suggestion: Comment corriger (optionnel)
            category: Catégorie (optionnel)
        """
        self.findings.append(
            Finding(
                severity=severity,
                message=message,
                file=file,
                line=line,
                suggestion=suggestion,
                category=category,
            )
        )

    def _determine_status(self) -> AgentStatus:
        """
        Détermine le statut final basé sur les findings.

        Returns:
            AgentStatus (FAIL si CRITICAL, WARN si HIGH, PASS sinon)
        """
        if not self.findings:
            return AgentStatus.PASS

        critical_count = sum(1 for f in self.findings if f.severity == 'CRITICAL')
        high_count = sum(1 for f in self.findings if f.severity == 'HIGH')

        if critical_count > 0:
            return AgentStatus.FAIL
        elif high_count > 0:
            return AgentStatus.WARN
        else:
            return AgentStatus.PASS

    def _create_report(self, status: AgentStatus, summary: str, score: Optional[dict] = None) -> AgentReport:
        """
        Crée un rapport final.

        Args:
            status: Statut de validation
            summary: Résumé en une ligne
            score: Scores optionnels

        Returns:
            AgentReport complet
        """
        return AgentReport(
            agent_name=self.__class__.__name__.replace('Agent', '').lower(),
            status=status,
            findings=self.findings,
            execution_time=0,  # Sera mis à jour par le wrapper
            summary=summary,
            score=score,
        )
