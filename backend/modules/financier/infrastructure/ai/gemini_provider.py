"""Provider Gemini pour les suggestions financieres IA.

FIN-21: Implementation concrete du port AISuggestionPort
utilisant Google Gemini 3 Flash (gemini-3-flash-preview) pour generer des
suggestions financieres contextuelles pour les chantiers BTP.

Layer: Infrastructure (depend du port Application via AISuggestionPort).
"""

import json
import logging
import os
import time
from typing import List, Dict, Any

from ...application.ports.ai_suggestion_port import AISuggestionPort
from ...application.dtos.suggestions_dtos import SuggestionDTO

logger = logging.getLogger(__name__)

# Constantes de configuration
GEMINI_MODEL = "gemini-3-flash-preview"  # Gemini 3 Flash - dernier modèle rapide (février 2026)
GEMINI_TEMPERATURE = 0.3
GEMINI_MAX_OUTPUT_TOKENS = 800
GEMINI_TIMEOUT_SECONDS = 30  # Timeout augmenté pour les analyses complexes
GEMINI_MAX_RETRIES = 2
GEMINI_BACKOFF_SECONDS = [1, 2]

SYSTEM_PROMPT = """<role>
Tu es un expert financier senior specialise dans le BTP (Batiment et Travaux Publics) en France.
Tu as 15 ans d'experience dans la gestion financiere de chantiers pour des PME de construction.
</role>

<context>
- Client type : PME construction (20 employes, CA ~4M EUR)
- Secteur : BTP France (reglementation, TVA, sous-traitance)
- Objectif : Optimiser la rentabilite et anticiper les risques financiers
</context>

<rules>
- Reponds UNIQUEMENT en JSON valide, sans commentaires ni texte supplementaire
- Suggestions pragmatiques et actionnables
- Langage professionnel mais accessible
- Chiffres et pourcentages precis
</rules>"""

USER_PROMPT_TEMPLATE = """<task>
Analyse les KPI financiers de ce chantier BTP et genere des suggestions d'optimisation.
</task>

<data>
- Montant revise HT : {montant_revise} EUR
- Total engage : {total_engage} EUR
- Total realise : {total_realise} EUR
- Pourcentage engage : {pct_engage}%
- Pourcentage realise : {pct_realise}%
- Marge estimee : {marge_pct}%
- Reste a depenser : {reste_a_depenser} EUR
- Burn rate mensuel : {burn_rate} EUR/mois
</data>

<output_format>
Genere entre 1 et 3 suggestions au format JSON :
[{{
  "type": "CREATE_AVENANT|REDUCE_COSTS|OPTIMIZE_LOTS|ALERT_BURN_RATE|CREATE_SITUATION|RENEGOCIATE_SUPPLIERS|REVIEW_PLANNING",
  "severity": "CRITICAL|WARNING|INFO",
  "titre": "Titre court en francais",
  "description": "Description detaillee en francais (2-3 phrases)",
  "impact_estime_eur": "0.00"
}}]
</output_format>"""

# Prompt pour l'analyse consolidée multi-chantiers
CONSOLIDATED_SYSTEM_PROMPT = """<role>
Tu es un directeur financier (DAF) specialise dans le BTP en France.
Tu conseilles les dirigeants de PME de construction sur leur strategie financiere.
Tu as une vision globale du portefeuille de chantiers et identifies les tendances.
</role>

<context>
- Client : PME construction (20 employes, CA ~4M EUR)
- Mission : Analyse strategique consolidee multi-chantiers
- Frequence : Tableau de bord mensuel pour la direction
</context>

<rules>
- Reponds UNIQUEMENT en JSON valide
- Synthese executive claire et actionnable
- Alertes priorisees par impact financier
- Recommandations concretes avec horizon temporel
- Score de sante base sur les indicateurs objectifs
</rules>"""

CONSOLIDATED_PROMPT_TEMPLATE = """<task>
Analyse le portefeuille de {nb_chantiers} chantiers BTP et fournis une synthese strategique pour la direction.
</task>

<data>
<kpi_globaux>
- Budget total revise : {total_budget} EUR
- Total engage : {total_engage} EUR ({pct_engage}%)
- Total realise : {total_realise} EUR ({pct_realise}%)
- Reste a depenser : {reste_a_depenser} EUR
- Marge moyenne : {marge_moyenne}%
</kpi_globaux>

<repartition_sante>
- Chantiers sains (marge > 5%) : {nb_ok}
- Chantiers a surveiller (marge 0-5%) : {nb_attention}
- Chantiers en depassement (marge < 0%) : {nb_depassement}
</repartition_sante>

<top_3_rentables>
{top_rentables}
</top_3_rentables>

<top_3_derives>
{top_derives}
</top_3_derives>
</data>

<output_format>
{{
  "synthese": "Resume executif 2-3 phrases : situation globale, point fort, point de vigilance",
  "alertes": ["Alerte 1 (la plus critique)", "Alerte 2", "Alerte 3"],
  "recommandations": ["Action 1 prioritaire", "Action 2", "Action 3"],
  "tendance": "hausse|stable|baisse",
  "score_sante": 0-100
}}
</output_format>

<scoring_guide>
- 90-100 : Excellent (toutes marges > 10%, aucun depassement)
- 70-89 : Bon (marges moyennes 5-10%, surveillance legere)
- 50-69 : Moyen (marges tendues, 1-2 chantiers a risque)
- 30-49 : Fragile (plusieurs depassements, tresorerie tendue)
- 0-29 : Critique (pertes generalisees, risque de defaillance)
</scoring_guide>"""


class GeminiSuggestionProvider(AISuggestionPort):
    """Provider Gemini pour les suggestions financieres IA.

    Utilise le modele Gemini 3 Flash (gemini-3-flash-preview) de Google
    pour generer des suggestions contextuelles basees sur les KPI d'un chantier.

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

    def generate_consolidated_analysis(self, consolidated_data: dict) -> Dict[str, Any]:
        """Genere une analyse IA consolidee multi-chantiers via Gemini 3 Flash.

        Args:
            consolidated_data: Dictionnaire des KPI consolides avec :
                - kpi_globaux: KPIGlobauxDTO en dict
                - top_rentables: Liste des top 3 chantiers rentables
                - top_derives: Liste des top 3 chantiers en dérive

        Returns:
            Dictionnaire avec synthese, alertes, recommandations, tendance, score_sante.
            Dictionnaire vide en cas d'erreur.
        """
        try:
            import google.generativeai as genai

            # Creer un modele avec le prompt systeme consolide
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=CONSOLIDATED_SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=1500,  # Augmenté pour prompts XML plus riches
                    response_mime_type="application/json",
                ),
            )

            # Construire le prompt
            kpi = consolidated_data.get("kpi_globaux", {})
            top_rentables = consolidated_data.get("top_rentables", [])
            top_derives = consolidated_data.get("top_derives", [])

            # Formater les top rentables
            top_rentables_str = "\n".join([
                f"  - {c.get('nom_chantier', 'N/A')}: marge {c.get('marge_estimee_pct', '0')}%, "
                f"budget {c.get('montant_revise_ht', '0')} EUR"
                for c in top_rentables
            ]) or "  Aucun"

            # Formater les top dérivés
            top_derives_str = "\n".join([
                f"  - {c.get('nom_chantier', 'N/A')}: engage {c.get('pct_engage', '0')}%, "
                f"depassement {float(c.get('pct_engage', '0')) - 100:.1f}%"
                for c in top_derives if float(c.get('pct_engage', '0')) > 100
            ]) or "  Aucun"

            prompt = CONSOLIDATED_PROMPT_TEMPLATE.format(
                nb_chantiers=kpi.get("nb_chantiers", 0),
                total_budget=kpi.get("total_budget_revise", "0"),
                total_engage=kpi.get("total_engage", "0"),
                pct_engage=self._calc_pct(kpi.get("total_engage", "0"), kpi.get("total_budget_revise", "0")),
                total_realise=kpi.get("total_realise", "0"),
                pct_realise=self._calc_pct(kpi.get("total_realise", "0"), kpi.get("total_budget_revise", "0")),
                reste_a_depenser=kpi.get("total_reste_a_depenser", "0"),
                marge_moyenne=kpi.get("marge_moyenne_pct", "0"),
                nb_ok=kpi.get("nb_chantiers_ok", 0),
                nb_attention=kpi.get("nb_chantiers_attention", 0),
                nb_depassement=kpi.get("nb_chantiers_depassement", 0),
                top_rentables=top_rentables_str,
                top_derives=top_derives_str,
            )

            # Appel Gemini 3 Flash
            response = model.generate_content(
                prompt,
                request_options={"timeout": GEMINI_TIMEOUT_SECONDS},
            )

            if not response or not response.text:
                logger.warning("Reponse Gemini vide pour analyse consolidee")
                return {}

            response_text = response.text
            logger.debug("Reponse brute Gemini: %s", response_text[:500])

            # Tenter de parser le JSON (avec nettoyage si nécessaire)
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                # Essayer de nettoyer la réponse (enlever markdown, etc.)
                cleaned = response_text.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                try:
                    data = json.loads(cleaned)
                except json.JSONDecodeError as e2:
                    logger.warning("JSON invalide de Gemini apres nettoyage: %s", str(e2))
                    return {}

            logger.info("Gemini 3 Flash a genere une analyse consolidee avec succes")

            # Valider et normaliser la reponse
            return {
                "synthese": str(data.get("synthese", "Analyse non disponible")),
                "alertes": [str(a) for a in data.get("alertes", [])][:3],
                "recommandations": [str(r) for r in data.get("recommandations", [])][:3],
                "tendance": str(data.get("tendance", "stable")),
                "score_sante": min(100, max(0, int(data.get("score_sante", 50)))),
                "source": "gemini-3-flash",
                "ai_available": True,
            }

        except Exception as e:
            logger.warning("Erreur analyse consolidee Gemini 3 Flash: %s", str(e))
            return {}

    def _calc_pct(self, value: str, total: str) -> str:
        """Calcule un pourcentage."""
        try:
            v = float(value)
            t = float(total)
            if t > 0:
                return f"{(v / t) * 100:.1f}"
            return "0.0"
        except (ValueError, TypeError):
            return "0.0"
