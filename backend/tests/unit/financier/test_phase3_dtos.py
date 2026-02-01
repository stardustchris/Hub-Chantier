"""Tests unitaires pour les DTOs Phase 3 du module Financier (affectation + export)."""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.financier.domain.entities import AffectationTacheLot
from modules.financier.application.dtos.affectation_dtos import (
    AffectationCreateDTO,
    AffectationDTO,
    SuiviAffectationDTO,
)
from modules.financier.application.dtos.export_dtos import (
    ExportLigneComptableDTO,
    ExportComptableDTO,
)


# ==============================================================================
# Tests AffectationCreateDTO
# ==============================================================================


class TestAffectationCreateDTO:
    """Tests pour le DTO de creation d'affectation."""

    def test_create_dto_valid(self):
        """Test: creation d'un DTO valide avec tous les champs."""
        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("75"),
        )
        assert dto.chantier_id == 5
        assert dto.tache_id == 10
        assert dto.lot_budgetaire_id == 20
        assert dto.pourcentage_affectation == Decimal("75")

    def test_create_dto_default_pourcentage(self):
        """Test: le pourcentage par defaut est 100."""
        dto = AffectationCreateDTO(
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )
        assert dto.pourcentage_affectation == Decimal("100")


# ==============================================================================
# Tests AffectationDTO
# ==============================================================================


class TestAffectationDTO:
    """Tests pour le DTO de sortie d'affectation."""

    def test_from_entity(self):
        """Test: creation d'un DTO depuis une entite AffectationTacheLot."""
        now = datetime(2026, 1, 15, 10, 30, 0)
        entity = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation=Decimal("75"),
            created_at=now,
            created_by=3,
        )

        dto = AffectationDTO.from_entity(entity)

        assert dto.id == 1
        assert dto.chantier_id == 5
        assert dto.tache_id == 10
        assert dto.lot_budgetaire_id == 20
        assert dto.pourcentage_affectation == "75"
        assert dto.created_at == now
        assert dto.created_by == 3

    def test_from_entity_none_optionals(self):
        """Test: creation d'un DTO avec des champs optionnels None."""
        entity = AffectationTacheLot(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
        )

        dto = AffectationDTO.from_entity(entity)

        assert dto.created_at is None
        assert dto.created_by is None

    def test_to_dict(self):
        """Test: conversion du DTO en dictionnaire."""
        now = datetime(2026, 1, 15, 10, 30, 0)
        dto = AffectationDTO(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation="75",
            created_at=now,
            created_by=3,
        )

        d = dto.to_dict()

        assert d["id"] == 1
        assert d["chantier_id"] == 5
        assert d["tache_id"] == 10
        assert d["lot_budgetaire_id"] == 20
        assert d["pourcentage_affectation"] == "75"
        assert d["created_at"] == now.isoformat()
        assert d["created_by"] == 3

    def test_to_dict_none_created_at(self):
        """Test: to_dict gere created_at None."""
        dto = AffectationDTO(
            id=1,
            chantier_id=5,
            tache_id=10,
            lot_budgetaire_id=20,
            pourcentage_affectation="100",
            created_at=None,
            created_by=None,
        )

        d = dto.to_dict()

        assert d["created_at"] is None
        assert d["created_by"] is None


# ==============================================================================
# Tests SuiviAffectationDTO
# ==============================================================================


class TestSuiviAffectationDTO:
    """Tests pour le DTO de suivi croise avancement/financier."""

    def test_create_suivi_dto(self):
        """Test: creation d'un DTO de suivi valide."""
        dto = SuiviAffectationDTO(
            affectation_id=1,
            tache_id=10,
            tache_titre="Terrassement zone A",
            tache_statut="en_cours",
            tache_progression_pct="60",
            lot_budgetaire_id=20,
            lot_code="LOT-001",
            lot_libelle="Terrassement",
            lot_montant_prevu_ht="5000.00",
            pourcentage_affectation="100",
            montant_affecte_ht="5000.00",
        )
        assert dto.affectation_id == 1
        assert dto.tache_titre == "Terrassement zone A"
        assert dto.lot_montant_prevu_ht == "5000.00"
        assert dto.montant_affecte_ht == "5000.00"

    def test_to_dict(self):
        """Test: conversion du DTO de suivi en dictionnaire."""
        dto = SuiviAffectationDTO(
            affectation_id=1,
            tache_id=10,
            tache_titre="Terrassement zone A",
            tache_statut="en_cours",
            tache_progression_pct="60",
            lot_budgetaire_id=20,
            lot_code="LOT-001",
            lot_libelle="Terrassement",
            lot_montant_prevu_ht="5000.00",
            pourcentage_affectation="100",
            montant_affecte_ht="5000.00",
        )

        d = dto.to_dict()

        assert d["affectation_id"] == 1
        assert d["tache_id"] == 10
        assert d["tache_titre"] == "Terrassement zone A"
        assert d["tache_statut"] == "en_cours"
        assert d["tache_progression_pct"] == "60"
        assert d["lot_budgetaire_id"] == 20
        assert d["lot_code"] == "LOT-001"
        assert d["lot_libelle"] == "Terrassement"
        assert d["lot_montant_prevu_ht"] == "5000.00"
        assert d["pourcentage_affectation"] == "100"
        assert d["montant_affecte_ht"] == "5000.00"


# ==============================================================================
# Tests ExportLigneComptableDTO
# ==============================================================================


class TestExportLigneComptableDTO:
    """Tests pour le DTO d'une ligne d'ecriture comptable."""

    def test_create_ligne_dto(self):
        """Test: creation d'un DTO de ligne comptable valide."""
        dto = ExportLigneComptableDTO(
            date="2026-01-15",
            code_journal="HA",
            numero_piece="FA-001",
            code_analytique="5",
            libelle="Ciment Portland",
            compte_general="601000",
            debit="10000.00",
            credit="0.00",
            tva_code="20",
        )
        assert dto.date == "2026-01-15"
        assert dto.code_journal == "HA"
        assert dto.numero_piece == "FA-001"
        assert dto.compte_general == "601000"
        assert dto.debit == "10000.00"
        assert dto.credit == "0.00"
        assert dto.tva_code == "20"

    def test_to_dict(self):
        """Test: conversion du DTO de ligne comptable en dictionnaire."""
        dto = ExportLigneComptableDTO(
            date="2026-01-15",
            code_journal="HA",
            numero_piece="FA-001",
            code_analytique="5",
            libelle="Ciment Portland",
            compte_general="601000",
            debit="10000.00",
            credit="0.00",
            tva_code="20",
        )

        d = dto.to_dict()

        assert d["date"] == "2026-01-15"
        assert d["code_journal"] == "HA"
        assert d["numero_piece"] == "FA-001"
        assert d["code_analytique"] == "5"
        assert d["libelle"] == "Ciment Portland"
        assert d["compte_general"] == "601000"
        assert d["debit"] == "10000.00"
        assert d["credit"] == "0.00"
        assert d["tva_code"] == "20"

    def test_to_dict_journal_vente(self):
        """Test: to_dict pour une ligne de journal de vente."""
        dto = ExportLigneComptableDTO(
            date="2026-01-25",
            code_journal="VE",
            numero_piece="FC-001",
            code_analytique="5",
            libelle="Facture FC-001",
            compte_general="411000",
            debit="24000.00",
            credit="0.00",
            tva_code="20",
        )

        d = dto.to_dict()

        assert d["code_journal"] == "VE"
        assert d["compte_general"] == "411000"


# ==============================================================================
# Tests ExportComptableDTO
# ==============================================================================


class TestExportComptableDTO:
    """Tests pour le DTO d'export comptable complet."""

    def test_create_export_dto_empty(self):
        """Test: creation d'un DTO d'export vide avec valeurs par defaut."""
        dto = ExportComptableDTO(
            chantier_id=None,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
        )
        assert dto.chantier_id is None
        assert dto.date_debut == "2026-01-01"
        assert dto.date_fin == "2026-01-31"
        assert dto.lignes == []
        assert dto.total_debit == "0.00"
        assert dto.total_credit == "0.00"
        assert dto.nombre_lignes == 0

    def test_create_export_dto_with_lignes(self):
        """Test: creation d'un DTO d'export avec des lignes."""
        lignes = [
            ExportLigneComptableDTO(
                date="2026-01-15",
                code_journal="HA",
                numero_piece="FA-001",
                code_analytique="5",
                libelle="Test",
                compte_general="601000",
                debit="10000.00",
                credit="0.00",
                tva_code="20",
            ),
        ]
        dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=lignes,
            total_debit="10000.00",
            total_credit="0.00",
            nombre_lignes=1,
        )
        assert dto.chantier_id == 5
        assert len(dto.lignes) == 1
        assert dto.total_debit == "10000.00"
        assert dto.nombre_lignes == 1

    def test_to_dict(self):
        """Test: conversion du DTO d'export en dictionnaire."""
        lignes = [
            ExportLigneComptableDTO(
                date="2026-01-15",
                code_journal="HA",
                numero_piece="FA-001",
                code_analytique="5",
                libelle="Test",
                compte_general="601000",
                debit="10000.00",
                credit="0.00",
                tva_code="20",
            ),
        ]
        dto = ExportComptableDTO(
            chantier_id=5,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
            lignes=lignes,
            total_debit="10000.00",
            total_credit="0.00",
            nombre_lignes=1,
        )

        d = dto.to_dict()

        assert d["chantier_id"] == 5
        assert d["date_debut"] == "2026-01-01"
        assert d["date_fin"] == "2026-01-31"
        assert len(d["lignes"]) == 1
        assert d["lignes"][0]["compte_general"] == "601000"
        assert d["total_debit"] == "10000.00"
        assert d["total_credit"] == "0.00"
        assert d["nombre_lignes"] == 1

    def test_to_dict_empty(self):
        """Test: to_dict sur un export vide."""
        dto = ExportComptableDTO(
            chantier_id=None,
            date_debut="2026-01-01",
            date_fin="2026-01-31",
        )

        d = dto.to_dict()

        assert d["chantier_id"] is None
        assert d["lignes"] == []
        assert d["nombre_lignes"] == 0
