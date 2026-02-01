"""Tests unitaires pour les DTOs LotBudgetaire."""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from modules.financier.domain.entities import LotBudgetaire
from modules.financier.domain.value_objects import UniteMesure
from modules.financier.application.dtos import (
    LotBudgetaireDTO,
    LotBudgetaireCreateDTO,
    LotBudgetaireUpdateDTO,
    LotBudgetaireListDTO,
)


class TestLotBudgetaireDTO:
    """Tests pour le DTO de sortie LotBudgetaireDTO."""

    def test_from_entity_phase_chantier(self):
        """Test: from_entity pour un lot en phase chantier."""
        # Arrange
        lot = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite=UniteMesure.M2,
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
            created_at=datetime(2026, 1, 1, 10, 0, 0),
            updated_at=datetime(2026, 1, 2, 10, 0, 0),
            created_by=5,
        )
        engage = Decimal("3000")
        realise = Decimal("2000")

        # Act
        dto = LotBudgetaireDTO.from_entity(lot, engage=engage, realise=realise)

        # Assert
        assert dto.id == 1
        assert dto.budget_id == 10
        assert dto.devis_id is None
        assert dto.code_lot == "GO-01"
        assert dto.libelle == "Gros oeuvre"
        assert dto.unite == "m2"
        assert dto.unite_label == "Mètre carré"
        assert dto.quantite_prevue == "100"
        assert dto.prix_unitaire_ht == "50"
        assert dto.total_prevu_ht == "5000"
        assert dto.engage == "3000"
        assert dto.realise == "2000"
        assert dto.ecart == "2000"  # 5000 - 3000
        assert dto.est_en_phase_devis is False
        assert dto.created_at == lot.created_at
        assert dto.created_by == 5

        # Champs phase devis doivent être None
        assert dto.debourse_main_oeuvre is None
        assert dto.debourse_sec_total is None
        assert dto.marge_pct is None

    def test_from_entity_phase_devis(self):
        """Test: from_entity pour un lot en phase devis."""
        # Arrange
        devis_id = uuid4()
        lot = LotBudgetaire(
            id=2,
            devis_id=devis_id,
            code_lot="GO-02",
            libelle="Fondations",
            unite=UniteMesure.M3,
            quantite_prevue=Decimal("50"),
            prix_unitaire_ht=Decimal("80"),
            debourse_main_oeuvre=Decimal("1500"),
            debourse_materiaux=Decimal("1000"),
            debourse_sous_traitance=Decimal("500"),
            marge_pct=Decimal("25"),
            prix_vente_ht=Decimal("3750"),
            created_at=datetime(2026, 1, 1, 10, 0, 0),
            created_by=5,
        )

        # Act
        dto = LotBudgetaireDTO.from_entity(lot)

        # Assert
        assert dto.id == 2
        assert dto.budget_id is None
        assert dto.devis_id == str(devis_id)
        assert dto.code_lot == "GO-02"
        assert dto.unite == "m3"
        assert dto.unite_label == "Mètre cube"
        assert dto.est_en_phase_devis is True

        # Champs phase devis doivent être présents
        assert dto.debourse_main_oeuvre == "1500"
        assert dto.debourse_materiaux == "1000"
        assert dto.debourse_sous_traitance == "500"
        assert dto.debourse_sec_total == "3000"  # 1500 + 1000 + 500
        assert dto.marge_pct == "25"
        assert dto.prix_vente_ht == "3750"
        # prix_vente_calcule_ht = 3000 * (1 + 25/100) = 3750
        assert dto.prix_vente_calcule_ht == "3750.00"

    def test_from_entity_with_partial_debourses(self):
        """Test: from_entity avec déboursés partiels."""
        # Arrange
        lot = LotBudgetaire(
            id=3,
            devis_id=uuid4(),
            code_lot="GO-03",
            libelle="Test",
            debourse_main_oeuvre=Decimal("1000"),
            debourse_materiaux=Decimal("500"),
            # Autres déboursés non renseignés (None)
            marge_pct=Decimal("20"),
        )

        # Act
        dto = LotBudgetaireDTO.from_entity(lot)

        # Assert
        assert dto.debourse_main_oeuvre == "1000"
        assert dto.debourse_materiaux == "500"
        assert dto.debourse_sous_traitance is None
        assert dto.debourse_materiel is None
        assert dto.debourse_divers is None
        assert dto.debourse_sec_total == "1500"  # 1000 + 500
        # prix_vente_calcule_ht = 1500 * 1.20 = 1800
        assert dto.prix_vente_calcule_ht == "1800.0"

    def test_from_entity_zero_engage_and_realise_by_default(self):
        """Test: from_entity avec engage et realise à zéro par défaut."""
        # Arrange
        lot = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="TEST",
            libelle="Test",
        )

        # Act
        dto = LotBudgetaireDTO.from_entity(lot)

        # Assert
        assert dto.engage == "0"
        assert dto.realise == "0"
        assert dto.ecart == str(lot.total_prevu_ht)

    def test_to_dict_phase_chantier(self):
        """Test: to_dict pour un lot en phase chantier."""
        # Arrange
        dto = LotBudgetaireDTO(
            id=1,
            budget_id=10,
            devis_id=None,
            code_lot="GO-01",
            libelle="Gros oeuvre",
            unite="m2",
            unite_label="Mètre carré",
            quantite_prevue="100",
            prix_unitaire_ht="50",
            total_prevu_ht="5000",
            engage="3000",
            realise="2000",
            ecart="2000",
            parent_lot_id=None,
            ordre=1,
            created_at=datetime(2026, 1, 1),
            updated_at=None,
            created_by=5,
            est_en_phase_devis=False,
        )

        # Act
        result = dto.to_dict()

        # Assert
        assert result["id"] == 1
        assert result["budget_id"] == 10
        assert result["devis_id"] is None
        assert result["code_lot"] == "GO-01"
        assert result["libelle"] == "Gros oeuvre"
        assert result["unite"] == "m2"
        assert result["unite_label"] == "Mètre carré"
        assert result["quantite_prevue"] == "100"
        assert result["prix_unitaire_ht"] == "50"
        assert result["total_prevu_ht"] == "5000"
        assert result["engage"] == "3000"
        assert result["realise"] == "2000"
        assert result["ecart"] == "2000"
        assert result["est_en_phase_devis"] is False
        assert result["created_at"] == "2026-01-01T00:00:00"
        assert result["created_by"] == 5

        # Champs phase devis ne doivent PAS être dans le dict
        assert "debourse_main_oeuvre" not in result
        assert "debourse_sec_total" not in result
        assert "marge_pct" not in result

    def test_to_dict_phase_devis(self):
        """Test: to_dict pour un lot en phase devis."""
        # Arrange
        dto = LotBudgetaireDTO(
            id=2,
            budget_id=None,
            devis_id="550e8400-e29b-41d4-a716-446655440000",
            code_lot="GO-02",
            libelle="Fondations",
            unite="m3",
            unite_label="Mètre cube",
            quantite_prevue="50",
            prix_unitaire_ht="80",
            total_prevu_ht="4000",
            engage="0",
            realise="0",
            ecart="4000",
            parent_lot_id=None,
            ordre=1,
            created_at=datetime(2026, 1, 1),
            updated_at=None,
            created_by=5,
            debourse_main_oeuvre="1500",
            debourse_materiaux="1000",
            debourse_sous_traitance="500",
            debourse_materiel=None,
            debourse_divers=None,
            debourse_sec_total="3000",
            marge_pct="25",
            prix_vente_ht="3750",
            prix_vente_calcule_ht="3750",
            est_en_phase_devis=True,
        )

        # Act
        result = dto.to_dict()

        # Assert
        assert result["id"] == 2
        assert result["budget_id"] is None
        assert result["devis_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["est_en_phase_devis"] is True

        # Champs phase devis DOIVENT être dans le dict
        assert result["debourse_main_oeuvre"] == "1500"
        assert result["debourse_materiaux"] == "1000"
        assert result["debourse_sous_traitance"] == "500"
        assert result["debourse_materiel"] is None
        assert result["debourse_divers"] is None
        assert result["debourse_sec_total"] == "3000"
        assert result["marge_pct"] == "25"
        assert result["prix_vente_ht"] == "3750"
        assert result["prix_vente_calcule_ht"] == "3750"


class TestLotBudgetaireListDTO:
    """Tests pour le DTO de liste paginée."""

    def test_has_more_property_true(self):
        """Test: has_more retourne True si plus de résultats."""
        # Arrange - 100 résultats au total, offset=0, limit=20, 20 items retournés
        items = [
            LotBudgetaireDTO(
                id=i,
                budget_id=10,
                devis_id=None,
                code_lot=f"LOT-{i}",
                libelle=f"Lot {i}",
                unite="u",
                unite_label="Unité",
                quantite_prevue="1",
                prix_unitaire_ht="100",
                total_prevu_ht="100",
                engage="0",
                realise="0",
                ecart="100",
                parent_lot_id=None,
                ordre=i,
                created_at=None,
                updated_at=None,
                created_by=None,
            )
            for i in range(1, 21)
        ]
        dto_list = LotBudgetaireListDTO(
            items=items,
            total=100,
            limit=20,
            offset=0,
        )

        # Act & Assert
        assert dto_list.has_more is True
        # offset (0) + items (20) = 20 < total (100)

    def test_has_more_property_false(self):
        """Test: has_more retourne False si pas plus de résultats."""
        # Arrange - 20 résultats au total, offset=0, limit=20, 20 items retournés
        items = [
            LotBudgetaireDTO(
                id=i,
                budget_id=10,
                devis_id=None,
                code_lot=f"LOT-{i}",
                libelle=f"Lot {i}",
                unite="u",
                unite_label="Unité",
                quantite_prevue="1",
                prix_unitaire_ht="100",
                total_prevu_ht="100",
                engage="0",
                realise="0",
                ecart="100",
                parent_lot_id=None,
                ordre=i,
                created_at=None,
                updated_at=None,
                created_by=None,
            )
            for i in range(1, 21)
        ]
        dto_list = LotBudgetaireListDTO(
            items=items,
            total=20,
            limit=20,
            offset=0,
        )

        # Act & Assert
        assert dto_list.has_more is False
        # offset (0) + items (20) = 20 >= total (20)

    def test_has_more_property_last_page(self):
        """Test: has_more retourne False pour la dernière page."""
        # Arrange - 100 résultats au total, offset=80, limit=20, 20 items retournés
        items = [
            LotBudgetaireDTO(
                id=i,
                budget_id=10,
                devis_id=None,
                code_lot=f"LOT-{i}",
                libelle=f"Lot {i}",
                unite="u",
                unite_label="Unité",
                quantite_prevue="1",
                prix_unitaire_ht="100",
                total_prevu_ht="100",
                engage="0",
                realise="0",
                ecart="100",
                parent_lot_id=None,
                ordre=i,
                created_at=None,
                updated_at=None,
                created_by=None,
            )
            for i in range(81, 101)
        ]
        dto_list = LotBudgetaireListDTO(
            items=items,
            total=100,
            limit=20,
            offset=80,
        )

        # Act & Assert
        assert dto_list.has_more is False
        # offset (80) + items (20) = 100 >= total (100)
