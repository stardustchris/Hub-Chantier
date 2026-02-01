"""DTOs pour les suggestions financieres et indicateurs predictifs.

FIN-21/22 Phase 3: Suggestions algorithmiques deterministes + indicateurs predictifs.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class SuggestionDTO:
    """DTO pour une suggestion financiere individuelle.

    Attributes:
        type: Type de suggestion (CREATE_AVENANT, REDUCE_COSTS,
              CREATE_SITUATION, OPTIMIZE_LOTS, ALERT_BURN_RATE).
        severity: Severite (CRITICAL, WARNING, INFO).
        titre: Titre court de la suggestion.
        description: Description detaillee de la suggestion.
        impact_estime_eur: Impact estime en EUR (Decimal->str, peut etre "0").
    """

    type: str
    severity: str
    titre: str
    description: str
    impact_estime_eur: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "type": self.type,
            "severity": self.severity,
            "titre": self.titre,
            "description": self.description,
            "impact_estime_eur": self.impact_estime_eur,
        }


@dataclass
class IndicateursPredictifDTO:
    """DTO pour les indicateurs predictifs d'un chantier.

    Calculs purs, pas d'IA - regles deterministes.

    Attributes:
        burn_rate_mensuel: Depense mensuelle moyenne en EUR (Decimal->str).
        budget_moyen_mensuel: Budget mensuel prevu en EUR (Decimal->str).
        ecart_burn_rate_pct: Ecart burn rate vs prevu en % (Decimal->str).
        mois_restants_budget: Estimation mois restants (Decimal->str).
        date_epuisement_estimee: Date ISO estimee d'epuisement ou "N/A".
        avancement_financier_pct: Avancement financier en % (Decimal->str).
    """

    burn_rate_mensuel: str
    budget_moyen_mensuel: str
    ecart_burn_rate_pct: str
    mois_restants_budget: str
    date_epuisement_estimee: str
    avancement_financier_pct: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "burn_rate_mensuel": self.burn_rate_mensuel,
            "budget_moyen_mensuel": self.budget_moyen_mensuel,
            "ecart_burn_rate_pct": self.ecart_burn_rate_pct,
            "mois_restants_budget": self.mois_restants_budget,
            "date_epuisement_estimee": self.date_epuisement_estimee,
            "avancement_financier_pct": self.avancement_financier_pct,
        }


@dataclass
class SuggestionsFinancieresDTO:
    """DTO principal des suggestions financieres d'un chantier.

    FIN-21/22: Suggestions algorithmiques et/ou IA + indicateurs predictifs.

    Attributes:
        chantier_id: Identifiant du chantier.
        suggestions: Liste des suggestions (max 5).
        indicateurs: Indicateurs predictifs calcules.
        ai_available: True si le provider IA etait disponible et a repondu.
        source: Source des suggestions ("gemini" si IA, "algorithmic" sinon).
    """

    chantier_id: int
    suggestions: List[SuggestionDTO]
    indicateurs: IndicateursPredictifDTO
    ai_available: bool = False
    source: str = "algorithmic"

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "chantier_id": self.chantier_id,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "indicateurs": self.indicateurs.to_dict(),
            "ai_available": self.ai_available,
            "source": self.source,
        }
