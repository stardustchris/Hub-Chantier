"""Provider Gemini pour les suggestions financieres IA.

FIN-21: Implementation concrete du port AISuggestionPort
utilisant Google Gemini (gemini-1.5-flash) pour generer des
suggestions financieres contextuelles pour les chantiers BTP.

Layer: Infrastructure (depend du port Application via AISuggestionPort).
"""

import json
import logging
import os
import time
from typing import List

from ...application.ports.ai_suggestion_port import AISuggestionPort
from ...application.dtos.suggestions_dtos import SuggestionDTO

logger = logging.getLogger(__name__)

# Constantes de configuration
GEMINI_MODEL = "gemini-3-flash"  # Gemini 3 Flash - latest fast model
GEMINI_TEMPERATURE = 0.3
GEMINI_MAX_OUTPUT_TOKENS = 800
GEMINI_TIMEOUT_SECONDS = 10
GEMINI_MAX_RETRIES = 2
GEMINI_BACKOFF_SECONDS = [1, 2]

SYSTEM_PROMPT = (
    "Tu es un expert financier specialise dans le BTP (Batiment et Travaux Publics) en France. "
    "Tu analyses les indicateurs financiers d'un chantier et tu generes des suggestions "
    "actionnables pour ameliorer la gestion financiere. "
    "Tes suggestions doivent etre pragmatiques, specifiques au secteur BTP, "
    "et adaptees aux PME de construction (20 employes, CA ~4M EUR). "
    "Reponds UNIQUEMENT en JSON valide, sans commentaires ni texte supplementaire."
)

USER_PROMPT_TEMPLATE = (
    "Analyse les KPI financiers suivants pour un chantier BTP et genere des suggestions :\n\n"
    "- Montant revise HT : {montant_revise} EUR\n"
    "- Total engage : {total_engage} EUR\n"
    "- Total realise : {total_realise} EUR\n"
    "- Pourcentage engage : {pct_engage}%\n"
    "- Pourcentage realise : {pct_realise}%\n"
    "- Marge estimee : {marge_pct}%\n"
    "- Reste a depenser : {reste_a_depenser} EUR\n"
    "- Burn rate mensuel : {burn_rate} EUR/mois\n\n"
    "Genere entre 1 et 3 suggestions au format JSON suivant :\n"
    '[{{"type": "CREATE_AVENANT|REDUCE_COSTS|OPTIMIZE_LOTS|ALERT_BURN_RATE|CREATE_SITUATION|RENEGOCIATE_SUPPLIERS|REVIEW_PLANNING",'
    ' "severity": "CRITICAL|WARNING|INFO",'
    ' "titre": "Titre court en francais",'
    ' "description": "Description detaillee en francais (2-3 phrases)",'
    ' "impact_estime_eur": "0.00"}}]'
)


class GeminiSuggestionProvider(AISuggestionPort):
    """Provider Gemini pour les suggestions financieres IA.

    Utilise le modele gemini-1.5-flash de Google pour generer
    des suggestions contextuelles basees sur les KPI d'un chantier.

    Configuration via variable d'environnement GEMINI_API_KEY.

    Attributes:
        _api_key: Cle API Google Generative AI.
        _model: Instance du modele Gemini configure.
    """

    def __init__(self) -> None:
        """Initialise le provider Gemini.

        Configure l'API key et le modele avec les parametres optimaux
        pour la generation de suggestions financieres BTP.

        Raises:
            ValueError: Si GEMINI_API_KEY n'est pas definie.
        """
        self._api_key: str = os.environ.get("GEMINI_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY non configuree. "
                "Definir la variable d'environnement GEMINI_API_KEY."
            )

        try:
            import google.generativeai as genai

            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                    response_mime_type="application/json",
                ),
            )
            logger.info("GeminiSuggestionProvider initialise avec succes (model=%s)", GEMINI_MODEL)
        except ImportError:
            logger.error("google-generativeai non installe. pip install google-generativeai>=0.4.0")
            raise
        except Exception as e:
            logger.error("Erreur initialisation Gemini: %s", str(e))
            raise

    def generate_suggestions(self, kpi_data: dict) -> List[SuggestionDTO]:
        """Genere des suggestions financieres via Gemini.

        Construit le prompt utilisateur a partir des KPI, appelle Gemini
        avec retry et backoff, puis parse la reponse JSON en SuggestionDTO.

        Args:
            kpi_data: Dictionnaire des KPI du chantier.

        Returns:
            Liste de SuggestionDTO generees par Gemini.
            Liste vide en cas d'erreur (fallback silencieux).
        """
        try:
            prompt = self._build_prompt(kpi_data)
            response_text = self._call_gemini_with_retry(prompt)
            suggestions = self._parse_response(response_text)
            logger.info(
                "Gemini a genere %d suggestion(s) pour le chantier",
                len(suggestions),
            )
            return suggestions
        except Exception as e:
            logger.warning(
                "Erreur generation suggestions Gemini (fallback algo): %s",
                str(e),
            )
            return []

    def _build_prompt(self, kpi_data: dict) -> str:
        """Construit le prompt utilisateur a partir des KPI.

        Args:
            kpi_data: Dictionnaire des KPI du chantier.

        Returns:
            Prompt formate pour Gemini.
        """
        return USER_PROMPT_TEMPLATE.format(
            montant_revise=kpi_data.get("montant_revise", "0"),
            total_engage=kpi_data.get("total_engage", "0"),
            total_realise=kpi_data.get("total_realise", "0"),
            pct_engage=kpi_data.get("pct_engage", "0"),
            pct_realise=kpi_data.get("pct_realise", "0"),
            marge_pct=kpi_data.get("marge_pct", "0"),
            reste_a_depenser=kpi_data.get("reste_a_depenser", "0"),
            burn_rate=kpi_data.get("burn_rate", "0"),
        )

    def _call_gemini_with_retry(self, prompt: str) -> str:
        """Appelle Gemini avec retry et backoff exponentiel.

        Args:
            prompt: Le prompt utilisateur a envoyer.

        Returns:
            Texte de la reponse Gemini.

        Raises:
            Exception: Si toutes les tentatives echouent.
        """
        last_error: Exception | None = None

        for attempt in range(GEMINI_MAX_RETRIES + 1):
            try:
                response = self._model.generate_content(
                    prompt,
                    request_options={"timeout": GEMINI_TIMEOUT_SECONDS},
                )
                if response and response.text:
                    return response.text
                raise ValueError("Reponse Gemini vide ou invalide")
            except Exception as e:
                last_error = e
                if attempt < GEMINI_MAX_RETRIES:
                    backoff = GEMINI_BACKOFF_SECONDS[attempt]
                    logger.warning(
                        "Tentative %d/%d echouee pour Gemini: %s. "
                        "Retry dans %ds...",
                        attempt + 1,
                        GEMINI_MAX_RETRIES + 1,
                        str(e),
                        backoff,
                    )
                    time.sleep(backoff)
                else:
                    logger.error(
                        "Toutes les tentatives Gemini echouees (%d/%d): %s",
                        attempt + 1,
                        GEMINI_MAX_RETRIES + 1,
                        str(e),
                    )

        raise last_error  # type: ignore[misc]

    def _parse_response(self, response_text: str) -> List[SuggestionDTO]:
        """Parse la reponse JSON de Gemini en liste de SuggestionDTO.

        Args:
            response_text: Texte JSON retourne par Gemini.

        Returns:
            Liste de SuggestionDTO validees.

        Raises:
            ValueError: Si le JSON est invalide ou mal structure.
        """
        data = json.loads(response_text)

        # Gemini peut retourner un objet avec une cle "suggestions" ou directement une liste
        if isinstance(data, dict):
            if "suggestions" in data:
                items = data["suggestions"]
            else:
                # Essayer de trouver la premiere cle contenant une liste
                items = None
                for value in data.values():
                    if isinstance(value, list):
                        items = value
                        break
                if items is None:
                    items = [data]
        elif isinstance(data, list):
            items = data
        else:
            raise ValueError(f"Format de reponse Gemini inattendu: {type(data)}")

        suggestions: List[SuggestionDTO] = []
        valid_types = {
            "CREATE_AVENANT", "REDUCE_COSTS", "OPTIMIZE_LOTS",
            "ALERT_BURN_RATE", "CREATE_SITUATION",
            "RENEGOCIATE_SUPPLIERS", "REVIEW_PLANNING",
        }
        valid_severities = {"CRITICAL", "WARNING", "INFO"}

        for item in items:
            if not isinstance(item, dict):
                continue

            suggestion_type = item.get("type", "")
            severity = item.get("severity", "INFO")
            titre = item.get("titre", "")
            description = item.get("description", "")
            impact = item.get("impact_estime_eur", "0.00")

            # Validation des champs
            if suggestion_type not in valid_types:
                logger.warning("Type de suggestion IA ignore: %s", suggestion_type)
                continue
            if severity not in valid_severities:
                severity = "INFO"
            if not titre or not description:
                continue

            suggestions.append(
                SuggestionDTO(
                    type=suggestion_type,
                    severity=severity,
                    titre=titre,
                    description=description,
                    impact_estime_eur=str(impact),
                )
            )

        return suggestions
