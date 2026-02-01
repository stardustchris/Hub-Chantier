"""Tests unitaires pour les fonctionnalités Devis de LotBudgetaire."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from modules.financier.domain.entities import LotBudgetaire
from modules.financier.domain.value_objects import UniteMesure


class TestLotBudgetairePhaseDevis:
    """Tests pour la phase devis des lots budgétaires."""

    def test_create_lot_with_devis_id(self):
        """Test: création d'un lot en phase devis."""
        devis_id = uuid4()
        lot = LotBudgetaire(
            devis_id=devis_id,
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite=UniteMesure.M2,
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
            debourse_main_oeuvre=Decimal("2000"),
            debourse_materiaux=Decimal("1500"),
            marge_pct=Decimal("20"),
        )

        assert lot.devis_id == devis_id
        assert lot.budget_id is None
        assert lot.est_en_phase_devis is True
        assert lot.debourse_main_oeuvre == Decimal("2000")
        assert lot.debourse_materiaux == Decimal("1500")

    def test_create_lot_with_budget_id(self):
        """Test: création d'un lot en phase chantier."""
        lot = LotBudgetaire(
            budget_id=10,
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite=UniteMesure.M2,
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )

        assert lot.budget_id == 10
        assert lot.devis_id is None
        assert lot.est_en_phase_devis is False

    def test_validation_xor_both_set_fails(self):
        """Test: erreur si devis_id ET budget_id sont renseignés."""
        with pytest.raises(ValueError, match="ne peut être lié à la fois"):
            LotBudgetaire(
                devis_id=uuid4(),
                budget_id=10,
                code_lot="GO-01",
                libelle="Test",
            )

    def test_validation_xor_both_none_fails(self):
        """Test: erreur si ni devis_id ni budget_id ne sont renseignés."""
        with pytest.raises(ValueError, match="doit être lié soit"):
            LotBudgetaire(
                code_lot="GO-01",
                libelle="Test",
            )

    def test_debourse_sec_total_calculation(self):
        """Test: calcul automatique du déboursé sec total."""
        lot = LotBudgetaire(
            devis_id=uuid4(),
            code_lot="GO-01",
            libelle="Test",
            debourse_main_oeuvre=Decimal("1000"),
            debourse_materiaux=Decimal("500"),
            debourse_sous_traitance=Decimal("300"),
            debourse_materiel=Decimal("200"),
            debourse_divers=Decimal("50"),
        )

        expected = Decimal("1000") + Decimal("500") + Decimal("300") + Decimal("200") + Decimal("50")
        assert lot.debourse_sec_total == expected

    def test_debourse_sec_total_with_partial_values(self):
        """Test: calcul du déboursé sec total avec valeurs partielles."""
        lot = LotBudgetaire(
            devis_id=uuid4(),
            code_lot="GO-01",
            libelle="Test",
            debourse_main_oeuvre=Decimal("1000"),
            debourse_materiaux=Decimal("500"),
            # Autres champs non renseignés (None)
        )

        assert lot.debourse_sec_total == Decimal("1500")

    def test_debourse_sec_total_all_none(self):
        """Test: déboursé sec total = 0 si aucun champ renseigné."""
        lot = LotBudgetaire(
            budget_id=10,
            code_lot="GO-01",
            libelle="Test",
        )

        assert lot.debourse_sec_total == Decimal("0")

    def test_prix_vente_calcule_ht(self):
        """Test: calcul automatique du prix de vente HT avec marge."""
        lot = LotBudgetaire(
            devis_id=uuid4(),
            code_lot="GO-01",
            libelle="Test",
            debourse_main_oeuvre=Decimal("1000"),
            debourse_materiaux=Decimal("500"),
            marge_pct=Decimal("20"),  # 20% de marge
        )

        # Déboursé total = 1500
        # Prix vente = 1500 * (1 + 20/100) = 1500 * 1.20 = 1800
        expected = Decimal("1800")
        assert lot.prix_vente_calcule_ht == expected

    def test_prix_vente_calcule_ht_no_marge(self):
        """Test: prix de vente calculé = None si pas de marge."""
        lot = LotBudgetaire(
            devis_id=uuid4(),
            code_lot="GO-01",
            libelle="Test",
            debourse_main_oeuvre=Decimal("1000"),
            # marge_pct non renseigné
        )

        assert lot.prix_vente_calcule_ht is None

    def test_prix_vente_calcule_ht_zero_debourse(self):
        """Test: prix de vente calculé = None si déboursé = 0."""
        lot = LotBudgetaire(
            devis_id=uuid4(),
            code_lot="GO-01",
            libelle="Test",
            marge_pct=Decimal("20"),
            # Aucun déboursé renseigné
        )

        assert lot.debourse_sec_total == Decimal("0")
        assert lot.prix_vente_calcule_ht is None

    def test_validation_debourse_negative_fails(self):
        """Test: erreur si un déboursé est négatif."""
        with pytest.raises(ValueError, match="ne peut pas être négatif"):
            LotBudgetaire(
                devis_id=uuid4(),
                code_lot="GO-01",
                libelle="Test",
                debourse_main_oeuvre=Decimal("-100"),
            )

    def test_validation_marge_negative_fails(self):
        """Test: erreur si la marge est négative."""
        with pytest.raises(ValueError, match="ne peut pas être négatif"):
            LotBudgetaire(
                devis_id=uuid4(),
                code_lot="GO-01",
                libelle="Test",
                marge_pct=Decimal("-10"),
            )

    def test_validation_prix_vente_negative_fails(self):
        """Test: erreur si le prix de vente est négatif."""
        with pytest.raises(ValueError, match="ne peut pas être négatif"):
            LotBudgetaire(
                devis_id=uuid4(),
                code_lot="GO-01",
                libelle="Test",
                prix_vente_ht=Decimal("-1000"),
            )

    def test_to_dict_phase_devis_includes_extra_fields(self):
        """Test: to_dict inclut les champs devis en phase devis."""
        lot = LotBudgetaire(
            id=1,
            devis_id=uuid4(),
            code_lot="GO-01",
            libelle="Test",
            debourse_main_oeuvre=Decimal("1000"),
            debourse_materiaux=Decimal("500"),
            marge_pct=Decimal("20"),
        )

        result = lot.to_dict()

        assert "devis_id" in result
        assert result["devis_id"] is not None
        assert "debourse_main_oeuvre" in result
        assert result["debourse_main_oeuvre"] == "1000"
        assert "debourse_materiaux" in result
        assert result["debourse_materiaux"] == "500"
        assert "debourse_sec_total" in result
        assert result["debourse_sec_total"] == "1500"
        assert "marge_pct" in result
        assert result["marge_pct"] == "20"
        assert "prix_vente_calcule_ht" in result

    def test_to_dict_phase_chantier_excludes_devis_fields(self):
        """Test: to_dict n'inclut pas les champs devis en phase chantier."""
        lot = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="GO-01",
            libelle="Test",
        )

        result = lot.to_dict()

        assert result["budget_id"] == 10
        assert result["devis_id"] is None
        # Les champs devis ne doivent pas être dans le dict en phase chantier
        assert "debourse_main_oeuvre" not in result
        assert "debourse_sec_total" not in result
