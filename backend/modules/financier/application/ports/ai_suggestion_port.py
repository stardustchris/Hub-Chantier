"""Interface AISuggestionPort - Port pour les suggestions IA.

FIN-21: Abstraction pour les providers de suggestions IA (Gemini, etc.).
Le use case depend uniquement de cette interface, pas de l'implementation concrete.
"""

from abc import ABC, abstractmethod
from typing import List

from ..dtos.suggestions_dtos import SuggestionDTO


class AISuggestionPort(ABC):
    """Interface abstraite pour les providers de suggestions IA.

    Clean Architecture : ce port est dans la couche Application.
    L'implementation concrete (GeminiSuggestionProvider) est dans Infrastructure.

    Note:
        L'Application ne connait pas l'implementation.
    """

    @abstractmethod
    def generate_suggestions(self, kpi_data: dict) -> List[SuggestionDTO]:
        """Genere des suggestions financieres via IA a partir des KPI.

        Args:
            kpi_data: Dictionnaire contenant les KPI du chantier :
                - montant_revise (str): Montant revise HT.
                - total_engage (str): Total engage.
                - total_realise (str): Total realise.
                - pct_engage (str): Pourcentage engage.
                - pct_realise (str): Pourcentage realise.
                - marge_pct (str): Marge estimee en pourcentage.
                - reste_a_depenser (str): Reste a depenser.
                - burn_rate (str): Burn rate mensuel.

        Returns:
            Liste de SuggestionDTO generees par l'IA.
            Liste vide en cas d'erreur (fallback silencieux).
        """
        pass
