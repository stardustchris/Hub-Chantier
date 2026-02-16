"""Tests non-regression pour le module ConfigurationEntreprise.

Module: financier.configuration_entreprise
Couvre:
  - Entite domain (validation, defaults, to_dict)
  - Use cases GET / UPDATE (mock repository, pas de DB)
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from modules.financier.domain.entities import ConfigurationEntreprise
from modules.financier.domain.repositories import ConfigurationEntrepriseRepository
from modules.financier.application.dtos import (
    ConfigurationEntrepriseDTO,
    ConfigurationEntrepriseUpdateDTO,
)
from modules.financier.application.use_cases import (
    GetConfigurationEntrepriseUseCase,
    UpdateConfigurationEntrepriseUseCase,
)


# ============================================================
# Tests unitaires - Entite ConfigurationEntreprise
# ============================================================


class TestConfigurationEntrepriseEntity:
    """Tests pour l'entite domain ConfigurationEntreprise."""

    # --- Defaults ---

    def test_configuration_default_values(self):
        """Test: les valeurs par defaut correspondent aux constantes metier."""
        config = ConfigurationEntreprise()

        assert config.couts_fixes_annuels == Decimal("600000")
        assert config.annee == 2026
        assert config.coeff_frais_generaux == Decimal("19")
        assert config.coeff_charges_patronales == Decimal("1.45")
        assert config.coeff_heures_sup == Decimal("1.25")
        assert config.coeff_heures_sup_2 == Decimal("1.50")
        assert config.coeff_productivite == Decimal("1.0")
        assert config.coeff_charges_ouvrier is None
        assert config.coeff_charges_etam is None
        assert config.coeff_charges_cadre is None
        assert config.seuil_alerte_budget_pct == Decimal("80")
        assert config.seuil_alerte_budget_critique_pct == Decimal("95")
        assert config.id is None
        assert config.notes is None
        assert config.updated_at is None
        assert config.updated_by is None

    # --- Validation annee ---

    def test_configuration_annee_validation_trop_basse(self):
        """Test: annee < 2020 leve ValueError."""
        with pytest.raises(ValueError, match="annee"):
            ConfigurationEntreprise(annee=2019)

    def test_configuration_annee_validation_trop_haute(self):
        """Test: annee > 2099 leve ValueError."""
        with pytest.raises(ValueError, match="annee"):
            ConfigurationEntreprise(annee=2100)

    def test_configuration_annee_validation_ok(self):
        """Test: annee 2026 est acceptee (dans la plage 2020-2099)."""
        config = ConfigurationEntreprise(annee=2026)
        assert config.annee == 2026

    def test_configuration_annee_borne_basse(self):
        """Test: annee 2020 est acceptee (borne incluse)."""
        config = ConfigurationEntreprise(annee=2020)
        assert config.annee == 2020

    def test_configuration_annee_borne_haute(self):
        """Test: annee 2099 est acceptee (borne incluse)."""
        config = ConfigurationEntreprise(annee=2099)
        assert config.annee == 2099

    # --- Validation couts fixes ---

    def test_configuration_couts_fixes_negatifs(self):
        """Test: couts_fixes < 0 leve ValueError."""
        with pytest.raises(ValueError, match="negatif"):
            ConfigurationEntreprise(couts_fixes_annuels=Decimal("-1"))

    def test_configuration_couts_fixes_zero_ok(self):
        """Test: couts_fixes = 0 est accepte (pas negatif)."""
        config = ConfigurationEntreprise(couts_fixes_annuels=Decimal("0"))
        assert config.couts_fixes_annuels == Decimal("0")

    # --- Validation coeff frais generaux ---

    def test_configuration_coeff_fg_negatif(self):
        """Test: coeff_frais_generaux < 0 leve ValueError."""
        with pytest.raises(ValueError, match="frais generaux"):
            ConfigurationEntreprise(coeff_frais_generaux=Decimal("-1"))

    def test_configuration_coeff_fg_superieur_100(self):
        """Test: coeff_frais_generaux > 100 leve ValueError."""
        with pytest.raises(ValueError, match="frais generaux"):
            ConfigurationEntreprise(coeff_frais_generaux=Decimal("101"))

    def test_configuration_coeff_fg_zero_ok(self):
        """Test: coeff_frais_generaux = 0 est accepte (borne incluse)."""
        config = ConfigurationEntreprise(coeff_frais_generaux=Decimal("0"))
        assert config.coeff_frais_generaux == Decimal("0")

    def test_configuration_coeff_fg_100_ok(self):
        """Test: coeff_frais_generaux = 100 est accepte (borne incluse)."""
        config = ConfigurationEntreprise(coeff_frais_generaux=Decimal("100"))
        assert config.coeff_frais_generaux == Decimal("100")

    # --- Validation coeff charges patronales ---

    def test_configuration_coeff_charges_inf_1(self):
        """Test: coeff_charges_patronales < 1 leve ValueError."""
        with pytest.raises(ValueError, match="charges patronales"):
            ConfigurationEntreprise(coeff_charges_patronales=Decimal("0.99"))

    def test_configuration_coeff_charges_egal_1_ok(self):
        """Test: coeff_charges_patronales = 1 est accepte (borne incluse)."""
        config = ConfigurationEntreprise(coeff_charges_patronales=Decimal("1"))
        assert config.coeff_charges_patronales == Decimal("1")

    # --- Validation coeff heures sup ---

    def test_configuration_coeff_heures_sup_inf_1(self):
        """Test: coeff_heures_sup < 1 leve ValueError."""
        with pytest.raises(ValueError, match="heures sup"):
            ConfigurationEntreprise(coeff_heures_sup=Decimal("0.5"))

    def test_configuration_coeff_heures_sup_2_inf_1(self):
        """Test: coeff_heures_sup_2 < 1 leve ValueError."""
        with pytest.raises(ValueError, match="heures sup 2"):
            ConfigurationEntreprise(coeff_heures_sup_2=Decimal("0.8"))

    # --- Validation coeff productivite (Phase 4) ---

    def test_configuration_coeff_productivite_trop_bas(self):
        """Test: coeff_productivite < 0.5 leve ValueError."""
        with pytest.raises(ValueError, match="productivite"):
            ConfigurationEntreprise(coeff_productivite=Decimal("0.49"))

    def test_configuration_coeff_productivite_trop_haut(self):
        """Test: coeff_productivite > 2.0 leve ValueError."""
        with pytest.raises(ValueError, match="productivite"):
            ConfigurationEntreprise(coeff_productivite=Decimal("2.01"))

    def test_configuration_coeff_productivite_bornes_ok(self):
        """Test: coeff_productivite entre 0.5 et 2.0 est accepte."""
        config = ConfigurationEntreprise(coeff_productivite=Decimal("0.5"))
        assert config.coeff_productivite == Decimal("0.5")
        config2 = ConfigurationEntreprise(coeff_productivite=Decimal("2.0"))
        assert config2.coeff_productivite == Decimal("2.0")

    # --- Validation charges par categorie (Phase 4) ---

    def test_configuration_coeff_charges_ouvrier_inf_1(self):
        """Test: coeff_charges_ouvrier < 1 leve ValueError."""
        with pytest.raises(ValueError, match="ouvrier"):
            ConfigurationEntreprise(coeff_charges_ouvrier=Decimal("0.9"))

    def test_configuration_coeff_charges_etam_inf_1(self):
        """Test: coeff_charges_etam < 1 leve ValueError."""
        with pytest.raises(ValueError, match="ETAM"):
            ConfigurationEntreprise(coeff_charges_etam=Decimal("0.5"))

    def test_configuration_coeff_charges_cadre_inf_1(self):
        """Test: coeff_charges_cadre < 1 leve ValueError."""
        with pytest.raises(ValueError, match="cadre"):
            ConfigurationEntreprise(coeff_charges_cadre=Decimal("0.8"))

    def test_configuration_charges_categorie_none_ok(self):
        """Test: charges par categorie None est accepte (fallback global)."""
        config = ConfigurationEntreprise()
        assert config.coeff_charges_ouvrier is None
        assert config.coeff_charges_etam is None
        assert config.coeff_charges_cadre is None

    # --- Validation seuils alertes (Phase 4) ---

    def test_configuration_seuil_alerte_negatif(self):
        """Test: seuil_alerte_budget_pct < 0 leve ValueError."""
        with pytest.raises(ValueError, match="seuil alerte budget"):
            ConfigurationEntreprise(seuil_alerte_budget_pct=Decimal("-1"))

    def test_configuration_seuil_alerte_superieur_100(self):
        """Test: seuil_alerte_budget_pct > 100 leve ValueError."""
        with pytest.raises(ValueError, match="seuil alerte budget"):
            ConfigurationEntreprise(seuil_alerte_budget_pct=Decimal("101"))

    def test_configuration_seuil_critique_inferieur_alerte(self):
        """Test: seuil critique <= seuil alerte leve ValueError."""
        with pytest.raises(ValueError, match="inferieur au seuil critique"):
            ConfigurationEntreprise(
                seuil_alerte_budget_pct=Decimal("90"),
                seuil_alerte_budget_critique_pct=Decimal("80"),
            )

    def test_configuration_seuils_egaux_invalide(self):
        """Test: seuils egaux leve ValueError."""
        with pytest.raises(ValueError, match="inferieur au seuil critique"):
            ConfigurationEntreprise(
                seuil_alerte_budget_pct=Decimal("80"),
                seuil_alerte_budget_critique_pct=Decimal("80"),
            )

    def test_configuration_seuils_valides_ok(self):
        """Test: seuils corrects acceptes."""
        config = ConfigurationEntreprise(
            seuil_alerte_budget_pct=Decimal("70"),
            seuil_alerte_budget_critique_pct=Decimal("90"),
        )
        assert config.seuil_alerte_budget_pct == Decimal("70")
        assert config.seuil_alerte_budget_critique_pct == Decimal("90")

    # --- to_dict ---

    def test_configuration_to_dict(self):
        """Test: to_dict retourne le format attendu avec serialisation correcte."""
        now = datetime(2026, 1, 15, 10, 30, 0)
        config = ConfigurationEntreprise(
            id=42,
            couts_fixes_annuels=Decimal("750000"),
            annee=2026,
            coeff_frais_generaux=Decimal("22"),
            coeff_charges_patronales=Decimal("1.50"),
            coeff_heures_sup=Decimal("1.25"),
            coeff_heures_sup_2=Decimal("1.50"),
            notes="Config annuelle",
            updated_at=now,
            updated_by=7,
        )

        result = config.to_dict()

        assert result == {
            "id": 42,
            "couts_fixes_annuels": "750000",
            "annee": 2026,
            "coeff_frais_generaux": "22",
            "coeff_charges_patronales": "1.50",
            "coeff_heures_sup": "1.25",
            "coeff_heures_sup_2": "1.50",
            "coeff_productivite": "1.0",
            "coeff_charges_ouvrier": None,
            "coeff_charges_etam": None,
            "coeff_charges_cadre": None,
            "seuil_alerte_budget_pct": "80",
            "seuil_alerte_budget_critique_pct": "95",
            "notes": "Config annuelle",
            "updated_at": "2026-01-15T10:30:00",
            "updated_by": 7,
        }

    def test_configuration_to_dict_none_values(self):
        """Test: to_dict gere correctement les champs None."""
        config = ConfigurationEntreprise()
        result = config.to_dict()

        assert result["id"] is None
        assert result["notes"] is None
        assert result["updated_at"] is None
        assert result["updated_by"] is None
        assert result["coeff_charges_ouvrier"] is None
        assert result["coeff_charges_etam"] is None
        assert result["coeff_charges_cadre"] is None
        # Les Decimal sont bien serialises en string
        assert result["couts_fixes_annuels"] == "600000"
        assert result["coeff_productivite"] == "1.0"
        assert result["seuil_alerte_budget_pct"] == "80"
        assert result["seuil_alerte_budget_critique_pct"] == "95"


# ============================================================
# Tests unitaires - GetConfigurationEntrepriseUseCase
# ============================================================


class TestGetConfigurationEntrepriseUseCase:
    """Tests pour le use case GET configuration entreprise."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ConfigurationEntrepriseRepository)
        self.use_case = GetConfigurationEntrepriseUseCase(self.mock_repo)

    def test_get_config_existante(self):
        """Test: config existante en BDD retourne le DTO correct, is_default=False."""
        now = datetime(2026, 6, 1, 12, 0, 0)
        existing_config = ConfigurationEntreprise(
            id=10,
            couts_fixes_annuels=Decimal("800000"),
            annee=2026,
            coeff_frais_generaux=Decimal("22"),
            coeff_charges_patronales=Decimal("1.50"),
            coeff_heures_sup=Decimal("1.30"),
            coeff_heures_sup_2=Decimal("1.60"),
            notes="Config personnalisee",
            updated_at=now,
            updated_by=5,
        )
        self.mock_repo.find_by_annee.return_value = existing_config

        result, is_default = self.use_case.execute(2026)

        assert is_default is False
        assert result.id == 10
        assert result.couts_fixes_annuels == Decimal("800000")
        assert result.annee == 2026
        assert result.coeff_frais_generaux == Decimal("22")
        assert result.coeff_charges_patronales == Decimal("1.50")
        assert result.coeff_heures_sup == Decimal("1.30")
        assert result.coeff_heures_sup_2 == Decimal("1.60")
        assert result.notes == "Config personnalisee"
        assert result.updated_at == now
        assert result.updated_by == 5
        self.mock_repo.find_by_annee.assert_called_once_with(2026)

    def test_get_config_inexistante_retourne_defaults(self):
        """Test: aucune config en BDD retourne les defaults, is_default=True (EDGE-003)."""
        self.mock_repo.find_by_annee.return_value = None

        result, is_default = self.use_case.execute(2026)

        assert is_default is True
        assert result.id == 0
        assert result.couts_fixes_annuels == Decimal("600000")
        assert result.annee == 2026
        assert result.coeff_frais_generaux == Decimal("19")
        assert result.coeff_charges_patronales == Decimal("1.45")
        assert result.coeff_heures_sup == Decimal("1.25")
        assert result.coeff_heures_sup_2 == Decimal("1.50")
        assert result.coeff_productivite == Decimal("1.0")
        assert result.seuil_alerte_budget_pct == Decimal("80")
        assert result.seuil_alerte_budget_critique_pct == Decimal("95")
        assert result.notes is None
        assert result.updated_at is None
        assert result.updated_by is None
        self.mock_repo.find_by_annee.assert_called_once_with(2026)

    def test_get_config_annee_differente(self):
        """Test: l'annee demandee est transmise au repository."""
        self.mock_repo.find_by_annee.return_value = None

        result, is_default = self.use_case.execute(2025)

        assert result.annee == 2025
        self.mock_repo.find_by_annee.assert_called_once_with(2025)


# ============================================================
# Tests unitaires - UpdateConfigurationEntrepriseUseCase
# ============================================================


class TestUpdateConfigurationEntrepriseUseCase:
    """Tests pour le use case UPDATE configuration entreprise."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_repo = Mock(spec=ConfigurationEntrepriseRepository)
        self.use_case = UpdateConfigurationEntrepriseUseCase(self.mock_repo)

    def _save_side_effect(self, config: ConfigurationEntreprise) -> ConfigurationEntreprise:
        """Helper: simule la persistence en attribuant un ID."""
        if config.id is None:
            config.id = 99
        return config

    def test_update_config_existante(self):
        """Test: mise a jour d'une config existante, created=False."""
        existing_config = ConfigurationEntreprise(
            id=10,
            couts_fixes_annuels=Decimal("600000"),
            annee=2026,
        )
        self.mock_repo.find_by_annee.return_value = existing_config
        self.mock_repo.save.side_effect = self._save_side_effect

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("750000"),
            coeff_frais_generaux=Decimal("22"),
        )

        result, created, warnings = self.use_case.execute(2026, dto, updated_by=5)

        assert created is False
        assert result.id == 10
        assert result.couts_fixes_annuels == Decimal("750000")
        assert result.coeff_frais_generaux == Decimal("22")
        assert result.updated_by == 5
        assert result.updated_at is not None
        self.mock_repo.find_by_annee.assert_called_once_with(2026)
        self.mock_repo.save.assert_called_once()

    def test_update_config_inexistante_cree(self):
        """Test: aucune config en BDD en cree une nouvelle, created=True (EDGE-001)."""
        self.mock_repo.find_by_annee.return_value = None
        self.mock_repo.save.side_effect = self._save_side_effect

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("500000"),
        )

        result, created, warnings = self.use_case.execute(2026, dto, updated_by=3)

        assert created is True
        assert result.id == 99  # Attribue par _save_side_effect
        assert result.couts_fixes_annuels == Decimal("500000")
        assert result.annee == 2026
        assert result.updated_by == 3
        self.mock_repo.save.assert_called_once()

    def test_update_config_warnings_couts_zero(self):
        """Test: couts_fixes=0 genere un warning (VAL-002, EDGE-002)."""
        self.mock_repo.find_by_annee.return_value = None
        self.mock_repo.save.side_effect = self._save_side_effect

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("0"),
        )

        result, created, warnings = self.use_case.execute(2026, dto, updated_by=1)

        assert len(warnings) > 0
        assert any("0 EUR" in w for w in warnings)

    def test_update_config_warnings_coeff_fg_zero(self):
        """Test: coeff_frais_generaux=0 genere un warning (VAL-002, EDGE-002)."""
        self.mock_repo.find_by_annee.return_value = None
        self.mock_repo.save.side_effect = self._save_side_effect

        dto = ConfigurationEntrepriseUpdateDTO(
            coeff_frais_generaux=Decimal("0"),
        )

        result, created, warnings = self.use_case.execute(2026, dto, updated_by=1)

        assert len(warnings) > 0
        assert any("0%" in w for w in warnings)

    def test_update_config_warnings_both_zero(self):
        """Test: les deux a zero genere deux warnings."""
        self.mock_repo.find_by_annee.return_value = None
        self.mock_repo.save.side_effect = self._save_side_effect

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("0"),
            coeff_frais_generaux=Decimal("0"),
        )

        result, created, warnings = self.use_case.execute(2026, dto, updated_by=1)

        assert len(warnings) == 2

    def test_update_config_no_warnings_normal_values(self):
        """Test: valeurs normales ne generent pas de warnings."""
        self.mock_repo.find_by_annee.return_value = None
        self.mock_repo.save.side_effect = self._save_side_effect

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("600000"),
            coeff_frais_generaux=Decimal("19"),
        )

        result, created, warnings = self.use_case.execute(2026, dto, updated_by=1)

        assert len(warnings) == 0

    def test_update_config_validation_error_annee_invalide(self):
        """Test: annee invalide dans la re-validation leve ValueError."""
        # On simule un scenario ou la config existante a une annee valide
        # mais la re-validation __post_init__ echoue apres mutation.
        # En pratique, c'est l'entite qui valide via __post_init__.
        # Ici on teste le passage d'une annee invalide au constructeur
        # qui est appele quand created=True.
        self.mock_repo.find_by_annee.return_value = None

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("600000"),
        )

        # L'annee invalide cause un ValueError lors de la creation de l'entite
        with pytest.raises(ValueError, match="annee"):
            self.use_case.execute(2019, dto, updated_by=1)

    def test_update_config_validation_error_couts_negatifs(self):
        """Test: couts fixes negatifs dans le DTO leve ValueError a la re-validation."""
        existing_config = ConfigurationEntreprise(id=10, annee=2026)
        self.mock_repo.find_by_annee.return_value = existing_config

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("-100"),
        )

        with pytest.raises(ValueError, match="negatif"):
            self.use_case.execute(2026, dto, updated_by=1)

    def test_update_config_partial_update(self):
        """Test: seuls les champs fournis (non-None) sont modifies."""
        existing_config = ConfigurationEntreprise(
            id=10,
            couts_fixes_annuels=Decimal("600000"),
            annee=2026,
            coeff_frais_generaux=Decimal("19"),
            coeff_charges_patronales=Decimal("1.45"),
            coeff_heures_sup=Decimal("1.25"),
            coeff_heures_sup_2=Decimal("1.50"),
            notes="Note initiale",
        )
        self.mock_repo.find_by_annee.return_value = existing_config
        self.mock_repo.save.side_effect = self._save_side_effect

        # On ne modifie que les notes
        dto = ConfigurationEntrepriseUpdateDTO(notes="Nouvelle note")

        result, created, warnings = self.use_case.execute(2026, dto, updated_by=5)

        assert created is False
        assert result.notes == "Nouvelle note"
        # Les autres champs restent inchanges
        assert result.couts_fixes_annuels == Decimal("600000")
        assert result.coeff_frais_generaux == Decimal("19")
        assert result.coeff_charges_patronales == Decimal("1.45")
        assert result.coeff_heures_sup == Decimal("1.25")
        assert result.coeff_heures_sup_2 == Decimal("1.50")

    def test_update_config_sets_updated_at(self):
        """Test: updated_at est positionne automatiquement."""
        self.mock_repo.find_by_annee.return_value = None
        self.mock_repo.save.side_effect = self._save_side_effect

        dto = ConfigurationEntrepriseUpdateDTO(
            couts_fixes_annuels=Decimal("700000"),
        )

        before = datetime.utcnow()
        result, created, warnings = self.use_case.execute(2026, dto, updated_by=1)
        after = datetime.utcnow()

        assert result.updated_at is not None
        assert before <= result.updated_at <= after
