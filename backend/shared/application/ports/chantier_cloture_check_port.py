"""Port pour verifier les pre-requis de cloture d'un chantier.

Permet au module chantiers de verifier l'etat financier
sans dependance directe sur le module financier.

Conforme Clean Architecture:
- Interface definie dans Application layer (shared)
- Implementation dans Infrastructure layer (shared)
- Aucun import de modules specifiques
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class ClotureCheckResult:
    """Resultat de la verification des pre-requis de cloture.

    Attributes:
        peut_fermer: True si tous les pre-requis sont remplis.
        blocages: Liste des raisons bloquant la fermeture.
        avertissements: Liste des avertissements non bloquants.
    """

    peut_fermer: bool = True
    blocages: List[str] = field(default_factory=list)
    avertissements: List[str] = field(default_factory=list)


class ChantierClotureCheckPort(ABC):
    """Port pour verifier les pre-requis financiers de cloture.

    Permet au module chantiers de s'assurer que les conditions
    financieres sont remplies avant de fermer un chantier :
    - Achats au statut terminal (facture ou refuse)
    - Situations de travaux validees ou facturees
    - Pas d'avenants en brouillon
    """

    @abstractmethod
    def verifier_prerequis_cloture(self, chantier_id: int) -> ClotureCheckResult:
        """Verifie si un chantier peut etre ferme.

        Controle que :
        - Tous les achats sont au statut FACTURE ou REFUSE
        - Toutes les situations sont validees ou facturees
        - Pas d'avenants en brouillon (avertissement)

        Args:
            chantier_id: ID du chantier.

        Returns:
            ClotureCheckResult avec les blocages eventuels.
        """
        ...
