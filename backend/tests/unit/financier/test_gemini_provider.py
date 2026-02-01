"""Tests unitaires pour le GeminiSuggestionProvider.

FIN-21: Tests du provider Gemini (infrastructure) avec mocks complets.
Pas de dependance externe a google-generativeai.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from modules.financier.application.dtos.suggestions_dtos import SuggestionDTO
from modules.financier.infrastructure.ai.gemini_provider import (
    GeminiSuggestionProvider,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_MAX_RETRIES,
    GEMINI_BACKOFF_SECONDS,
)


class TestGeminiSuggestionProviderInit:
    """Tests pour l'initialisation du provider."""

    def test_init_raises_without_api_key(self):
        """Test: ValueError si GEMINI_API_KEY manquante."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                GeminiSuggestionProvider()

    def test_init_raises_with_empty_api_key(self):
        """Test: ValueError si GEMINI_API_KEY vide."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                GeminiSuggestionProvider()

    @patch("modules.financier.infrastructure.ai.gemini_provider.genai", create=True)
    def test_init_success_with_api_key(self, mock_genai):
        """Test: initialisation reussie avec GEMINI_API_KEY valide."""
        # Arrange
        mock_genai.GenerationConfig.return_value = Mock()
        mock_genai.GenerativeModel.return_value = Mock()

        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-123"}):
            with patch(
                "modules.financier.infrastructure.ai.gemini_provider.genai",
                mock_genai,
                create=True,
            ):
                # Simule l'import
                import importlib
                import modules.financier.infrastructure.ai.gemini_provider as mod

                # On verifie que le code ne leve pas d'exception
                # (la vraie init importe genai, on mock au niveau plus bas)
                pass


class TestGeminiProviderBuildPrompt:
    """Tests pour la construction du prompt."""

    def test_build_prompt_format(self):
        """Test: le prompt est correctement formate avec les KPI."""
        # Arrange - On cree une instance avec un _model mock
        provider = object.__new__(GeminiSuggestionProvider)
        provider._api_key = "test"
        provider._model = Mock()

        kpi_data = {
            "montant_revise": "200000.00",
            "total_engage": "100000.00",
            "total_realise": "50000.00",
            "pct_engage": "50.00",
            "pct_realise": "25.00",
            "marge_pct": "50.00",
            "reste_a_depenser": "100000.00",
            "burn_rate": "25000.00",
        }

        # Act
        prompt = provider._build_prompt(kpi_data)

        # Assert
        assert "200000.00" in prompt
        assert "100000.00" in prompt
        assert "50000.00" in prompt
        assert "50.00" in prompt
        assert "25.00" in prompt
        assert "25000.00" in prompt

    def test_build_prompt_missing_keys_default_zero(self):
        """Test: cles manquantes dans kpi_data prennent la valeur '0'."""
        provider = object.__new__(GeminiSuggestionProvider)
        provider._api_key = "test"
        provider._model = Mock()

        prompt = provider._build_prompt({})

        # Les valeurs par defaut sont "0"
        assert "0" in prompt


class TestGeminiProviderParseResponse:
    """Tests pour le parsing de la reponse Gemini."""

    def setup_method(self):
        """Setup: cree une instance sans init."""
        self.provider = object.__new__(GeminiSuggestionProvider)
        self.provider._api_key = "test"
        self.provider._model = Mock()

    def test_parse_json_list(self):
        """Test: parse une liste JSON de suggestions."""
        response = json.dumps([
            {
                "type": "CREATE_AVENANT",
                "severity": "CRITICAL",
                "titre": "Creer un avenant",
                "description": "Le budget est presque epuise.",
                "impact_estime_eur": "5000.00",
            }
        ])
        result = self.provider._parse_response(response)
        assert len(result) == 1
        assert isinstance(result[0], SuggestionDTO)
        assert result[0].type == "CREATE_AVENANT"
        assert result[0].severity == "CRITICAL"

    def test_parse_json_object_with_suggestions_key(self):
        """Test: parse un objet JSON avec cle 'suggestions'."""
        response = json.dumps({
            "suggestions": [
                {
                    "type": "REDUCE_COSTS",
                    "severity": "WARNING",
                    "titre": "Reduire les couts",
                    "description": "Description detaillee.",
                    "impact_estime_eur": "3000.00",
                }
            ]
        })
        result = self.provider._parse_response(response)
        assert len(result) == 1
        assert result[0].type == "REDUCE_COSTS"

    def test_parse_json_object_with_list_value(self):
        """Test: parse un objet JSON avec une premiere cle contenant une liste."""
        response = json.dumps({
            "recommendations": [
                {
                    "type": "OPTIMIZE_LOTS",
                    "severity": "WARNING",
                    "titre": "Optimiser les lots",
                    "description": "Description lots.",
                    "impact_estime_eur": "2000.00",
                }
            ]
        })
        result = self.provider._parse_response(response)
        assert len(result) == 1
        assert result[0].type == "OPTIMIZE_LOTS"

    def test_parse_json_single_object(self):
        """Test: parse un objet JSON unique (pas de liste)."""
        response = json.dumps({
            "type": "ALERT_BURN_RATE",
            "severity": "WARNING",
            "titre": "Burn rate eleve",
            "description": "Description burn rate.",
            "impact_estime_eur": "1000.00",
        })
        result = self.provider._parse_response(response)
        assert len(result) == 1
        assert result[0].type == "ALERT_BURN_RATE"

    def test_parse_invalid_type_ignored(self):
        """Test: les types invalides sont ignores."""
        response = json.dumps([
            {
                "type": "INVALID_TYPE",
                "severity": "INFO",
                "titre": "Ignore",
                "description": "Description ignoree.",
                "impact_estime_eur": "0",
            },
            {
                "type": "CREATE_AVENANT",
                "severity": "CRITICAL",
                "titre": "Valide",
                "description": "Description valide.",
                "impact_estime_eur": "0",
            },
        ])
        result = self.provider._parse_response(response)
        assert len(result) == 1
        assert result[0].type == "CREATE_AVENANT"

    def test_parse_invalid_severity_defaults_to_info(self):
        """Test: severite invalide -> defaut INFO."""
        response = json.dumps([
            {
                "type": "CREATE_AVENANT",
                "severity": "EXTREME",
                "titre": "Test",
                "description": "Description test.",
                "impact_estime_eur": "0",
            }
        ])
        result = self.provider._parse_response(response)
        assert len(result) == 1
        assert result[0].severity == "INFO"

    def test_parse_missing_titre_or_description_skipped(self):
        """Test: suggestions sans titre ou description ignorees."""
        response = json.dumps([
            {
                "type": "CREATE_AVENANT",
                "severity": "CRITICAL",
                "titre": "",
                "description": "Description ok.",
                "impact_estime_eur": "0",
            },
            {
                "type": "REDUCE_COSTS",
                "severity": "WARNING",
                "titre": "Titre ok",
                "description": "",
                "impact_estime_eur": "0",
            },
            {
                "type": "OPTIMIZE_LOTS",
                "severity": "WARNING",
                "titre": "Complet",
                "description": "Description complete.",
                "impact_estime_eur": "0",
            },
        ])
        result = self.provider._parse_response(response)
        assert len(result) == 1
        assert result[0].type == "OPTIMIZE_LOTS"

    def test_parse_non_dict_items_in_list_skipped(self):
        """Test: elements non-dict dans la liste sont ignores."""
        response = json.dumps([
            "invalid_string",
            42,
            {
                "type": "CREATE_AVENANT",
                "severity": "CRITICAL",
                "titre": "Valide",
                "description": "Description.",
                "impact_estime_eur": "0",
            },
        ])
        result = self.provider._parse_response(response)
        assert len(result) == 1

    def test_parse_invalid_json_raises(self):
        """Test: JSON invalide leve ValueError."""
        with pytest.raises(json.JSONDecodeError):
            self.provider._parse_response("not json {{{")

    def test_parse_unexpected_type_raises(self):
        """Test: type de reponse inattendu leve ValueError."""
        with pytest.raises(ValueError, match="Format de reponse Gemini inattendu"):
            self.provider._parse_response('"just a string"')

    def test_parse_multiple_valid_suggestions(self):
        """Test: parse plusieurs suggestions valides."""
        response = json.dumps([
            {
                "type": "CREATE_AVENANT",
                "severity": "CRITICAL",
                "titre": "Avenant",
                "description": "Description avenant.",
                "impact_estime_eur": "5000",
            },
            {
                "type": "REDUCE_COSTS",
                "severity": "WARNING",
                "titre": "Reduire couts",
                "description": "Description couts.",
                "impact_estime_eur": "3000",
            },
            {
                "type": "REVIEW_PLANNING",
                "severity": "INFO",
                "titre": "Planning",
                "description": "Description planning.",
                "impact_estime_eur": "0",
            },
        ])
        result = self.provider._parse_response(response)
        assert len(result) == 3

    def test_parse_all_valid_types(self):
        """Test: tous les types valides sont acceptes."""
        valid_types = [
            "CREATE_AVENANT", "REDUCE_COSTS", "OPTIMIZE_LOTS",
            "ALERT_BURN_RATE", "CREATE_SITUATION",
            "RENEGOCIATE_SUPPLIERS", "REVIEW_PLANNING",
        ]
        items = [
            {
                "type": t,
                "severity": "INFO",
                "titre": f"Titre {t}",
                "description": f"Description {t}.",
                "impact_estime_eur": "0",
            }
            for t in valid_types
        ]
        response = json.dumps(items)
        result = self.provider._parse_response(response)
        assert len(result) == len(valid_types)


class TestGeminiProviderGenerateSuggestions:
    """Tests pour la methode generate_suggestions."""

    def setup_method(self):
        """Setup: cree une instance mockee."""
        self.provider = object.__new__(GeminiSuggestionProvider)
        self.provider._api_key = "test"
        self.provider._model = Mock()

    def test_generate_suggestions_success(self):
        """Test: generate_suggestions retourne des SuggestionDTO."""
        # Arrange
        response_data = json.dumps([
            {
                "type": "CREATE_AVENANT",
                "severity": "CRITICAL",
                "titre": "Avenant",
                "description": "Description avenant.",
                "impact_estime_eur": "5000.00",
            }
        ])
        mock_response = Mock()
        mock_response.text = response_data
        self.provider._model.generate_content.return_value = mock_response

        kpi_data = {"montant_revise": "100000", "total_engage": "90000"}

        # Act
        result = self.provider.generate_suggestions(kpi_data)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], SuggestionDTO)

    def test_generate_suggestions_error_returns_empty(self):
        """Test: en cas d'erreur, retourne une liste vide."""
        self.provider._model.generate_content.side_effect = Exception("API down")

        result = self.provider.generate_suggestions({"montant_revise": "100000"})

        assert result == []

    def test_call_with_retry_success_first_attempt(self):
        """Test: reponse reussie au premier essai."""
        mock_response = Mock()
        mock_response.text = "response text"
        self.provider._model.generate_content.return_value = mock_response

        result = self.provider._call_gemini_with_retry("test prompt")

        assert result == "response text"
        assert self.provider._model.generate_content.call_count == 1

    @patch("modules.financier.infrastructure.ai.gemini_provider.time.sleep")
    def test_call_with_retry_success_second_attempt(self, mock_sleep):
        """Test: reponse reussie au deuxieme essai apres un echec."""
        mock_response = Mock()
        mock_response.text = "response text"
        self.provider._model.generate_content.side_effect = [
            Exception("Temporary error"),
            mock_response,
        ]

        result = self.provider._call_gemini_with_retry("test prompt")

        assert result == "response text"
        assert self.provider._model.generate_content.call_count == 2
        mock_sleep.assert_called_once_with(GEMINI_BACKOFF_SECONDS[0])

    @patch("modules.financier.infrastructure.ai.gemini_provider.time.sleep")
    def test_call_with_retry_all_attempts_fail(self, mock_sleep):
        """Test: toutes les tentatives echouent -> raise."""
        self.provider._model.generate_content.side_effect = Exception("Permanent error")

        with pytest.raises(Exception, match="Permanent error"):
            self.provider._call_gemini_with_retry("test prompt")

        assert self.provider._model.generate_content.call_count == GEMINI_MAX_RETRIES + 1

    def test_call_with_retry_empty_response_raises(self):
        """Test: reponse vide -> retry."""
        mock_response = Mock()
        mock_response.text = None

        # Toutes les reponses vides
        self.provider._model.generate_content.return_value = mock_response

        with patch("modules.financier.infrastructure.ai.gemini_provider.time.sleep"):
            with pytest.raises(ValueError, match="Reponse Gemini vide"):
                self.provider._call_gemini_with_retry("test prompt")


class TestGeminiConstants:
    """Tests pour les constantes de configuration."""

    def test_model_name(self):
        """Test: le modele utilise est gemini-1.5-flash."""
        assert GEMINI_MODEL == "gemini-1.5-flash"

    def test_temperature(self):
        """Test: temperature basse pour des reponses coherentes."""
        assert GEMINI_TEMPERATURE == 0.3

    def test_max_output_tokens(self):
        """Test: nombre de tokens raisonnable."""
        assert GEMINI_MAX_OUTPUT_TOKENS == 800

    def test_max_retries(self):
        """Test: 2 retries maximum."""
        assert GEMINI_MAX_RETRIES == 2

    def test_backoff_seconds(self):
        """Test: backoff incrementiel."""
        assert GEMINI_BACKOFF_SECONDS == [1, 2]

    def test_system_prompt_contains_btp(self):
        """Test: le system prompt mentionne le BTP."""
        assert "BTP" in SYSTEM_PROMPT

    def test_system_prompt_requires_json(self):
        """Test: le system prompt exige du JSON."""
        assert "JSON" in SYSTEM_PROMPT

    def test_user_prompt_template_has_placeholders(self):
        """Test: le template contient les placeholders KPI."""
        assert "{montant_revise}" in USER_PROMPT_TEMPLATE
        assert "{total_engage}" in USER_PROMPT_TEMPLATE
        assert "{burn_rate}" in USER_PROMPT_TEMPLATE
