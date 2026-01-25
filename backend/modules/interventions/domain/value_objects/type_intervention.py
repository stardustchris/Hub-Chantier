"""Value Object TypeIntervention.

Types d'interventions selon le CDC Section 12.
"""

from enum import Enum


class TypeIntervention(str, Enum):
    """Types d'interventions possibles.

    Selon le CDC, les interventions sont distinctes des chantiers:
    - SAV: Service apres-vente
    - MAINTENANCE: Maintenance preventive ou curative
    - DEPANNAGE: Intervention d'urgence
    - LEVEE_RESERVES: Levee des reserves apres reception
    - AUTRE: Type personnalise
    """

    SAV = "sav"
    MAINTENANCE = "maintenance"
    DEPANNAGE = "depannage"
    LEVEE_RESERVES = "levee_reserves"
    AUTRE = "autre"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du type."""
        labels = {
            TypeIntervention.SAV: "SAV",
            TypeIntervention.MAINTENANCE: "Maintenance",
            TypeIntervention.DEPANNAGE: "Depannage",
            TypeIntervention.LEVEE_RESERVES: "Levee de reserves",
            TypeIntervention.AUTRE: "Autre",
        }
        return labels[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur associee au type."""
        couleurs = {
            TypeIntervention.SAV: "#8B5CF6",  # Violet
            TypeIntervention.MAINTENANCE: "#3B82F6",  # Bleu
            TypeIntervention.DEPANNAGE: "#EF4444",  # Rouge
            TypeIntervention.LEVEE_RESERVES: "#F59E0B",  # Orange
            TypeIntervention.AUTRE: "#6B7280",  # Gris
        }
        return couleurs[self]

    @property
    def icone(self) -> str:
        """Retourne l'icone associee au type."""
        icones = {
            TypeIntervention.SAV: "🔧",
            TypeIntervention.MAINTENANCE: "🛠️",
            TypeIntervention.DEPANNAGE: "🚨",
            TypeIntervention.LEVEE_RESERVES: "📋",
            TypeIntervention.AUTRE: "📝",
        }
        return icones[self]

    @property
    def description(self) -> str:
        """Retourne la description du type d'intervention."""
        descriptions = {
            TypeIntervention.SAV: "Intervention de service apres-vente",
            TypeIntervention.MAINTENANCE: "Maintenance preventive ou curative",
            TypeIntervention.DEPANNAGE: "Intervention d'urgence pour reparation",
            TypeIntervention.LEVEE_RESERVES: "Levee des reserves apres reception",
            TypeIntervention.AUTRE: "Autre type d'intervention",
        }
        return descriptions[self]
