"""Tests unitaires pour StatutChantier Value Object."""

import pytest

from modules.chantiers.domain.value_objects import StatutChantier, StatutChantierEnum


class TestStatutChantier:
    """Tests pour le Value Object StatutChantier (CHT-03)."""

    # ==========================================================================
    # Tests de création
    # ==========================================================================

    def test_create_ouvert(self):
        """Test: création du statut Ouvert."""
        statut = StatutChantier.ouvert()
        assert statut.value == StatutChantierEnum.OUVERT
        assert str(statut) == "ouvert"

    def test_create_en_cours(self):
        """Test: création du statut En cours."""
        statut = StatutChantier.en_cours()
        assert statut.value == StatutChantierEnum.EN_COURS
        assert str(statut) == "en_cours"

    def test_create_receptionne(self):
        """Test: création du statut Réceptionné."""
        statut = StatutChantier.receptionne()
        assert statut.value == StatutChantierEnum.RECEPTIONNE
        assert str(statut) == "receptionne"

    def test_create_ferme(self):
        """Test: création du statut Fermé."""
        statut = StatutChantier.ferme()
        assert statut.value == StatutChantierEnum.FERME
        assert str(statut) == "ferme"

    # ==========================================================================
    # Tests from_string
    # ==========================================================================

    def test_from_string_ouvert(self):
        """Test: création depuis chaîne 'ouvert'."""
        statut = StatutChantier.from_string("ouvert")
        assert statut.value == StatutChantierEnum.OUVERT

    def test_from_string_en_cours(self):
        """Test: création depuis chaîne 'en_cours'."""
        statut = StatutChantier.from_string("en_cours")
        assert statut.value == StatutChantierEnum.EN_COURS

    def test_from_string_uppercase_normalized(self):
        """Test: les majuscules sont normalisées."""
        statut = StatutChantier.from_string("OUVERT")
        assert statut.value == StatutChantierEnum.OUVERT

    def test_from_string_with_spaces_trimmed(self):
        """Test: les espaces sont supprimés."""
        statut = StatutChantier.from_string("  en_cours  ")
        assert statut.value == StatutChantierEnum.EN_COURS

    def test_from_string_invalid_raises_error(self):
        """Test: statut invalide lève une erreur."""
        with pytest.raises(ValueError) as exc_info:
            StatutChantier.from_string("invalid_status")
        assert "Statut invalide" in str(exc_info.value)

    # ==========================================================================
    # Tests des transitions autorisées
    # ==========================================================================

    def test_transition_ouvert_to_en_cours_allowed(self):
        """Test: Ouvert → En cours est autorisé."""
        statut = StatutChantier.ouvert()
        assert statut.can_transition_to(StatutChantier.en_cours()) is True

    def test_transition_ouvert_to_ferme_allowed(self):
        """Test: Ouvert → Fermé est autorisé."""
        statut = StatutChantier.ouvert()
        assert statut.can_transition_to(StatutChantier.ferme()) is True

    def test_transition_ouvert_to_receptionne_not_allowed(self):
        """Test: Ouvert → Réceptionné n'est pas autorisé."""
        statut = StatutChantier.ouvert()
        assert statut.can_transition_to(StatutChantier.receptionne()) is False

    def test_transition_en_cours_to_receptionne_allowed(self):
        """Test: En cours → Réceptionné est autorisé."""
        statut = StatutChantier.en_cours()
        assert statut.can_transition_to(StatutChantier.receptionne()) is True

    def test_transition_en_cours_to_ferme_allowed(self):
        """Test: En cours → Fermé est autorisé."""
        statut = StatutChantier.en_cours()
        assert statut.can_transition_to(StatutChantier.ferme()) is True

    def test_transition_en_cours_to_ouvert_not_allowed(self):
        """Test: En cours → Ouvert n'est pas autorisé."""
        statut = StatutChantier.en_cours()
        assert statut.can_transition_to(StatutChantier.ouvert()) is False

    def test_transition_receptionne_to_en_cours_allowed(self):
        """Test: Réceptionné → En cours est autorisé (réouverture)."""
        statut = StatutChantier.receptionne()
        assert statut.can_transition_to(StatutChantier.en_cours()) is True

    def test_transition_receptionne_to_ferme_allowed(self):
        """Test: Réceptionné → Fermé est autorisé."""
        statut = StatutChantier.receptionne()
        assert statut.can_transition_to(StatutChantier.ferme()) is True

    def test_transition_ferme_to_any_not_allowed(self):
        """Test: Fermé ne peut pas transitionner."""
        statut = StatutChantier.ferme()
        assert statut.can_transition_to(StatutChantier.ouvert()) is False
        assert statut.can_transition_to(StatutChantier.en_cours()) is False
        assert statut.can_transition_to(StatutChantier.receptionne()) is False

    # ==========================================================================
    # Tests des propriétés métier
    # ==========================================================================

    def test_is_active_ouvert(self):
        """Test: Ouvert est actif."""
        assert StatutChantier.ouvert().is_active() is True

    def test_is_active_en_cours(self):
        """Test: En cours est actif."""
        assert StatutChantier.en_cours().is_active() is True

    def test_is_active_receptionne(self):
        """Test: Réceptionné est actif."""
        assert StatutChantier.receptionne().is_active() is True

    def test_is_active_ferme(self):
        """Test: Fermé n'est pas actif."""
        assert StatutChantier.ferme().is_active() is False

    def test_allows_modifications_ouvert(self):
        """Test: Ouvert permet les modifications."""
        assert StatutChantier.ouvert().allows_modifications() is True

    def test_allows_modifications_en_cours(self):
        """Test: En cours permet les modifications."""
        assert StatutChantier.en_cours().allows_modifications() is True

    def test_allows_modifications_receptionne(self):
        """Test: Réceptionné ne permet pas les modifications."""
        assert StatutChantier.receptionne().allows_modifications() is False

    def test_allows_modifications_ferme(self):
        """Test: Fermé ne permet pas les modifications."""
        assert StatutChantier.ferme().allows_modifications() is False

    def test_allows_planning_ouvert(self):
        """Test: Ouvert permet la planification."""
        assert StatutChantier.ouvert().allows_planning() is True

    def test_allows_planning_en_cours(self):
        """Test: En cours permet la planification."""
        assert StatutChantier.en_cours().allows_planning() is True

    def test_allows_planning_receptionne(self):
        """Test: Réceptionné ne permet pas la planification."""
        assert StatutChantier.receptionne().allows_planning() is False

    # ==========================================================================
    # Tests des propriétés d'affichage
    # ==========================================================================

    def test_display_name_ouvert(self):
        """Test: nom d'affichage Ouvert."""
        assert StatutChantier.ouvert().display_name == "Ouvert"

    def test_display_name_en_cours(self):
        """Test: nom d'affichage En cours."""
        assert StatutChantier.en_cours().display_name == "En cours"

    def test_display_name_receptionne(self):
        """Test: nom d'affichage Réceptionné."""
        assert StatutChantier.receptionne().display_name == "Réceptionné"

    def test_display_name_ferme(self):
        """Test: nom d'affichage Fermé."""
        assert StatutChantier.ferme().display_name == "Fermé"

    def test_icon_exists_for_all_statuts(self):
        """Test: chaque statut a une icône."""
        for statut_enum in StatutChantierEnum:
            statut = StatutChantier(statut_enum)
            assert statut.icon is not None
            assert len(statut.icon) > 0

    # ==========================================================================
    # Tests all_statuts
    # ==========================================================================

    def test_all_statuts_returns_list(self):
        """Test: all_statuts retourne une liste."""
        statuts = StatutChantier.all_statuts()
        assert isinstance(statuts, list)
        assert len(statuts) == 4

    def test_all_statuts_contains_all_values(self):
        """Test: all_statuts contient tous les statuts."""
        statuts = StatutChantier.all_statuts()
        assert "ouvert" in statuts
        assert "en_cours" in statuts
        assert "receptionne" in statuts
        assert "ferme" in statuts
