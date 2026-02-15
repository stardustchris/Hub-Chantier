"""Tests unitaires pour les macros de paie (FDH-18).

Tests de l'entité MacroPaie et des use cases CRUD + calcul.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import MagicMock

from modules.pointages.domain.entities.macro_paie import MacroPaie, TypeMacroPaie
from modules.pointages.application.use_cases.macro_paie_use_cases import (
    CreateMacroPaieUseCase,
    GetMacroPaieUseCase,
    ListMacrosPaieUseCase,
    UpdateMacroPaieUseCase,
    DeleteMacroPaieUseCase,
    CalculerMacrosPeriodeUseCase,
    MacroNotFoundError,
    MacroPaieCreateDTO,
    MacroPaieUpdateDTO,
)


# ============ ENTITE TESTS ============


class TestMacroPaieEntity:
    """Tests pour l'entité MacroPaie."""

    def test_create_basic(self):
        """Test: création d'une macro basique."""
        macro = MacroPaie(
            nom="Panier repas",
            type_macro=TypeMacroPaie.PANIER_REPAS,
            formule="jours_travailles * montant_unitaire",
            parametres={"montant_unitaire": 10.10},
        )
        assert macro.nom == "Panier repas"
        assert macro.type_macro == TypeMacroPaie.PANIER_REPAS
        assert macro.active is True
        assert macro.id is None

    def test_create_strips_whitespace(self):
        """Test: nettoyage des espaces."""
        macro = MacroPaie(
            nom="  Test  ",
            type_macro=TypeMacroPaie.PERSONNALISE,
            formule="  1 + 1  ",
            description="  Desc  ",
        )
        assert macro.nom == "Test"
        assert macro.formule == "1 + 1"
        assert macro.description == "Desc"

    def test_create_empty_nom_error(self):
        """Test: erreur si nom vide."""
        with pytest.raises(ValueError, match="nom"):
            MacroPaie(
                nom="",
                type_macro=TypeMacroPaie.PANIER_REPAS,
                formule="1",
            )

    def test_create_empty_formule_error(self):
        """Test: erreur si formule vide."""
        with pytest.raises(ValueError, match="formule"):
            MacroPaie(
                nom="Test",
                type_macro=TypeMacroPaie.PANIER_REPAS,
                formule="",
            )

    def test_calculer_simple(self):
        """Test: calcul simple."""
        macro = MacroPaie(
            nom="Test",
            type_macro=TypeMacroPaie.PANIER_REPAS,
            formule="jours_travailles * montant_unitaire",
            parametres={"montant_unitaire": 10.10},
        )
        result = macro.calculer({"jours_travailles": 22})
        assert result == Decimal("222.20")

    def test_calculer_with_min_max(self):
        """Test: calcul avec min/max."""
        macro = MacroPaie(
            nom="Transport",
            type_macro=TypeMacroPaie.INDEMNITE_TRAJET,
            formule="min(distance_chantier * tarif_km * jours_travailles, plafond_journalier * jours_travailles)",
            parametres={
                "tarif_km": 0.45,
                "plafond_journalier": 50.0,
            },
        )
        # distance * tarif * jours = 30 * 0.45 * 22 = 297.0
        # plafond * jours = 50 * 22 = 1100
        # min(297, 1100) = 297
        result = macro.calculer({
            "distance_chantier": 30.0,
            "jours_travailles": 22,
        })
        assert result == Decimal("297.00")

    def test_calculer_plafond_atteint(self):
        """Test: calcul avec plafond atteint."""
        macro = MacroPaie(
            nom="Transport plafonné",
            type_macro=TypeMacroPaie.INDEMNITE_TRAJET,
            formule="min(distance_chantier * tarif_km * jours_travailles, plafond_journalier * jours_travailles)",
            parametres={
                "tarif_km": 0.45,
                "plafond_journalier": 5.0,
            },
        )
        # distance * tarif * jours = 100 * 0.45 * 22 = 990.0
        # plafond * jours = 5 * 22 = 110
        # min(990, 110) = 110
        result = macro.calculer({
            "distance_chantier": 100.0,
            "jours_travailles": 22,
        })
        assert result == Decimal("110.00")

    def test_calculer_invalid_formule(self):
        """Test: erreur si formule invalide."""
        macro = MacroPaie(
            nom="Test",
            type_macro=TypeMacroPaie.PERSONNALISE,
            formule="variable_inexistante * 2",
        )
        with pytest.raises(ValueError, match="Erreur calcul"):
            macro.calculer({})

    def test_calculer_no_system_access(self):
        """Test: pas d'accès système dans les formules."""
        macro = MacroPaie(
            nom="Malicious",
            type_macro=TypeMacroPaie.PERSONNALISE,
            formule="__import__('os').system('rm -rf /')",
        )
        with pytest.raises(ValueError):
            macro.calculer({})

    def test_factory_panier_repas(self):
        """Test: factory panier repas."""
        macro = MacroPaie.creer_macro_panier_repas(montant_unitaire=10.50, created_by=1)
        assert macro.type_macro == TypeMacroPaie.PANIER_REPAS
        assert macro.parametres["montant_unitaire"] == 10.50
        assert macro.created_by == 1

        result = macro.calculer({"jours_travailles": 20})
        assert result == Decimal("210.00")

    def test_factory_indemnite_trajet(self):
        """Test: factory indemnité trajet."""
        macro = MacroPaie.creer_macro_indemnite_trajet()
        assert macro.type_macro == TypeMacroPaie.INDEMNITE_TRAJET
        assert "tarif_km" in macro.parametres

    def test_factory_prime_intemperies(self):
        """Test: factory prime intempéries."""
        macro = MacroPaie.creer_macro_prime_intemperies(montant_journalier=20.0)
        assert macro.type_macro == TypeMacroPaie.PRIME_INTEMPERIES
        result = macro.calculer({"jours_intemperies": 3})
        assert result == Decimal("60.00")

    def test_activer_desactiver(self):
        """Test: activation/désactivation."""
        macro = MacroPaie(
            nom="Test",
            type_macro=TypeMacroPaie.PERSONNALISE,
            formule="1",
        )
        assert macro.active is True

        macro.desactiver()
        assert macro.active is False

        macro.activer()
        assert macro.active is True

    def test_modifier_parametres(self):
        """Test: modification des paramètres."""
        macro = MacroPaie(
            nom="Test",
            type_macro=TypeMacroPaie.PANIER_REPAS,
            formule="montant_unitaire",
            parametres={"montant_unitaire": 10.0},
        )
        macro.modifier_parametres({"montant_unitaire": 12.0})
        assert macro.parametres["montant_unitaire"] == 12.0

    def test_modifier_formule(self):
        """Test: modification de la formule."""
        macro = MacroPaie(
            nom="Test",
            type_macro=TypeMacroPaie.PERSONNALISE,
            formule="1",
        )
        macro.modifier_formule("jours_travailles * 2")
        assert macro.formule == "jours_travailles * 2"

    def test_modifier_formule_vide_error(self):
        """Test: erreur si formule vide."""
        macro = MacroPaie(
            nom="Test",
            type_macro=TypeMacroPaie.PERSONNALISE,
            formule="1",
        )
        with pytest.raises(ValueError, match="formule"):
            macro.modifier_formule("")

    def test_type_macro_from_string(self):
        """Test: conversion string -> TypeMacroPaie."""
        assert TypeMacroPaie.from_string("panier_repas") == TypeMacroPaie.PANIER_REPAS
        assert TypeMacroPaie.from_string("INDEMNITE_TRAJET") == TypeMacroPaie.INDEMNITE_TRAJET

    def test_type_macro_from_string_invalid(self):
        """Test: erreur pour type invalide."""
        with pytest.raises(ValueError, match="Type macro invalide"):
            TypeMacroPaie.from_string("invalid_type")


# ============ USE CASE TESTS ============


class TestCreateMacroPaieUseCase:
    """Tests pour le use case de création."""

    def test_create_success(self):
        """Test: création réussie."""
        repo = MagicMock()

        def mock_save(macro):
            macro.id = 1
            return macro

        repo.save.side_effect = mock_save

        use_case = CreateMacroPaieUseCase(repo)

        dto = MacroPaieCreateDTO(
            nom="Panier repas",
            type_macro="panier_repas",
            formule="jours_travailles * montant_unitaire",
            parametres={"montant_unitaire": 10.10},
            created_by=1,
        )

        result = use_case.execute(dto)
        assert result.nom == "Panier repas"
        assert result.type_macro == "panier_repas"
        repo.save.assert_called_once()

    def test_create_invalid_type(self):
        """Test: erreur si type invalide."""
        repo = MagicMock()
        use_case = CreateMacroPaieUseCase(repo)

        dto = MacroPaieCreateDTO(
            nom="Test",
            type_macro="invalid",
            formule="1",
        )

        with pytest.raises(ValueError):
            use_case.execute(dto)

    def test_create_invalid_formule(self):
        """Test: erreur si formule invalide à l'exécution."""
        repo = MagicMock()
        use_case = CreateMacroPaieUseCase(repo)

        dto = MacroPaieCreateDTO(
            nom="Test",
            type_macro="personnalise",
            formule="invalid syntax %%%",
        )

        with pytest.raises(ValueError, match="Formule invalide"):
            use_case.execute(dto)


class TestGetMacroPaieUseCase:
    """Tests pour le use case de récupération."""

    def test_get_found(self):
        """Test: macro trouvée."""
        repo = MagicMock()
        macro = MacroPaie(
            id=1,
            nom="Test",
            type_macro=TypeMacroPaie.PANIER_REPAS,
            formule="1",
        )
        repo.find_by_id.return_value = macro

        use_case = GetMacroPaieUseCase(repo)
        result = use_case.execute(1)
        assert result.id == 1

    def test_get_not_found(self):
        """Test: macro non trouvée."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        use_case = GetMacroPaieUseCase(repo)
        with pytest.raises(MacroNotFoundError):
            use_case.execute(999)


class TestListMacrosPaieUseCase:
    """Tests pour le use case de listing."""

    def test_list_all(self):
        """Test: listing de toutes les macros."""
        repo = MagicMock()
        macros = [
            MacroPaie(id=1, nom="A", type_macro=TypeMacroPaie.PANIER_REPAS, formule="1"),
            MacroPaie(id=2, nom="B", type_macro=TypeMacroPaie.INDEMNITE_TRAJET, formule="2"),
        ]
        repo.find_all.return_value = macros

        use_case = ListMacrosPaieUseCase(repo)
        result = use_case.execute()
        assert len(result) == 2

    def test_list_by_type(self):
        """Test: listing par type."""
        repo = MagicMock()
        repo.find_by_type.return_value = [
            MacroPaie(id=1, nom="A", type_macro=TypeMacroPaie.PANIER_REPAS, formule="1"),
        ]

        use_case = ListMacrosPaieUseCase(repo)
        result = use_case.execute(type_macro="panier_repas")
        assert len(result) == 1
        repo.find_by_type.assert_called_once()


class TestUpdateMacroPaieUseCase:
    """Tests pour le use case de mise à jour."""

    def test_update_success(self):
        """Test: mise à jour réussie."""
        repo = MagicMock()
        macro = MacroPaie(
            id=1,
            nom="Ancien nom",
            type_macro=TypeMacroPaie.PANIER_REPAS,
            formule="jours_travailles * 10",
        )
        repo.find_by_id.return_value = macro
        repo.save.return_value = macro

        use_case = UpdateMacroPaieUseCase(repo)

        dto = MacroPaieUpdateDTO(nom="Nouveau nom")
        result = use_case.execute(1, dto)
        assert result.nom == "Nouveau nom"

    def test_update_not_found(self):
        """Test: erreur si macro non trouvée."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        use_case = UpdateMacroPaieUseCase(repo)
        with pytest.raises(MacroNotFoundError):
            use_case.execute(999, MacroPaieUpdateDTO())


class TestDeleteMacroPaieUseCase:
    """Tests pour le use case de suppression."""

    def test_delete_success(self):
        """Test: suppression réussie."""
        repo = MagicMock()
        macro = MacroPaie(
            id=1,
            nom="Test",
            type_macro=TypeMacroPaie.PANIER_REPAS,
            formule="1",
        )
        repo.find_by_id.return_value = macro
        repo.delete.return_value = True

        use_case = DeleteMacroPaieUseCase(repo)
        assert use_case.execute(1) is True

    def test_delete_not_found(self):
        """Test: erreur si macro non trouvée."""
        repo = MagicMock()
        repo.find_by_id.return_value = None

        use_case = DeleteMacroPaieUseCase(repo)
        with pytest.raises(MacroNotFoundError):
            use_case.execute(999)


class TestCalculerMacrosPeriodeUseCase:
    """Tests pour le use case de calcul sur période."""

    def _make_pointage_mock(self, heures_n=8.0, heures_sup=0.0):
        """Crée un mock de pointage."""
        from modules.pointages.domain.value_objects.duree import Duree

        p = MagicMock()
        p.heures_normales = Duree.from_decimal(heures_n)
        p.heures_supplementaires = Duree.from_decimal(heures_sup)
        return p

    def test_calcul_aucune_macro(self):
        """Test: pas de macros actives."""
        macro_repo = MagicMock()
        pointage_repo = MagicMock()
        macro_repo.find_all.return_value = []

        use_case = CalculerMacrosPeriodeUseCase(macro_repo, pointage_repo)
        result = use_case.execute(
            utilisateur_id=1,
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert result.total == 0.0
        assert result.resultats == []

    def test_calcul_panier_repas(self):
        """Test: calcul panier repas sur période."""
        macro_repo = MagicMock()
        pointage_repo = MagicMock()

        macro = MacroPaie.creer_macro_panier_repas(montant_unitaire=10.0)
        macro.id = 1
        macro_repo.find_all.return_value = [macro]

        # 22 jours de pointages
        pointages = [self._make_pointage_mock() for _ in range(22)]
        pointage_repo.search.return_value = (pointages, 22)

        use_case = CalculerMacrosPeriodeUseCase(macro_repo, pointage_repo)
        result = use_case.execute(
            utilisateur_id=1,
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
        )

        assert len(result.resultats) == 1
        assert result.resultats[0].resultat == 220.0
        assert result.total == 220.0

    def test_calcul_avec_contexte_supplementaire(self):
        """Test: calcul avec contexte supplémentaire (distance, intempéries)."""
        macro_repo = MagicMock()
        pointage_repo = MagicMock()

        macro = MacroPaie.creer_macro_prime_intemperies(montant_journalier=15.0)
        macro.id = 1
        macro_repo.find_all.return_value = [macro]

        pointages = [self._make_pointage_mock() for _ in range(5)]
        pointage_repo.search.return_value = (pointages, 5)

        use_case = CalculerMacrosPeriodeUseCase(macro_repo, pointage_repo)
        result = use_case.execute(
            utilisateur_id=1,
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
            contexte_supplementaire={"jours_intemperies": 3},
        )

        assert len(result.resultats) == 1
        assert result.resultats[0].resultat == 45.0  # 3 * 15

    def test_calcul_multiple_macros(self):
        """Test: calcul de plusieurs macros."""
        macro_repo = MagicMock()
        pointage_repo = MagicMock()

        macro1 = MacroPaie.creer_macro_panier_repas(montant_unitaire=10.0)
        macro1.id = 1
        macro2 = MacroPaie.creer_macro_prime_intemperies(montant_journalier=15.0)
        macro2.id = 2
        macro_repo.find_all.return_value = [macro1, macro2]

        pointages = [self._make_pointage_mock() for _ in range(20)]
        pointage_repo.search.return_value = (pointages, 20)

        use_case = CalculerMacrosPeriodeUseCase(macro_repo, pointage_repo)
        result = use_case.execute(
            utilisateur_id=1,
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 1, 31),
            contexte_supplementaire={"jours_intemperies": 5},
        )

        assert len(result.resultats) == 2
        # Panier: 20 * 10 = 200
        # Intempéries: 5 * 15 = 75
        assert result.total == 275.0
