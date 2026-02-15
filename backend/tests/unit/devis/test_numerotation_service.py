"""Tests unitaires pour le service de numerotation automatique.

DEV-03: Creation devis structure - Numerotation hierarchique.
"""

import pytest

from modules.devis.domain.services.numerotation_service import NumerotationService


class TestGenererCodeLot:
    """Tests pour la generation de codes de lots."""

    def test_lot_racine_premier(self):
        """Test: premier lot racine = '1'."""
        assert NumerotationService.generer_code_lot(0) == "1"

    def test_lot_racine_deuxieme(self):
        """Test: deuxieme lot racine = '2'."""
        assert NumerotationService.generer_code_lot(1) == "2"

    def test_lot_racine_dixieme(self):
        """Test: dixieme lot racine = '10'."""
        assert NumerotationService.generer_code_lot(9) == "10"

    def test_sous_chapitre_premier(self):
        """Test: premier sous-chapitre du lot 1 = '1.1'."""
        assert NumerotationService.generer_code_lot(0, parent_code="1") == "1.1"

    def test_sous_chapitre_troisieme(self):
        """Test: troisieme sous-chapitre du lot 2 = '2.3'."""
        assert NumerotationService.generer_code_lot(2, parent_code="2") == "2.3"

    def test_sous_sous_chapitre(self):
        """Test: sous-sous-chapitre = '1.2.1'."""
        assert NumerotationService.generer_code_lot(0, parent_code="1.2") == "1.2.1"

    def test_profondeur_trois(self):
        """Test: profondeur 4 niveaux = '1.2.3.1'."""
        assert NumerotationService.generer_code_lot(0, parent_code="1.2.3") == "1.2.3.1"


class TestGenererCodeLigne:
    """Tests pour la generation de codes de lignes."""

    def test_premiere_ligne_lot_1(self):
        """Test: premiere ligne du lot 1 = '1.01'."""
        assert NumerotationService.generer_code_ligne(0, "1") == "1.01"

    def test_cinquieme_ligne_lot_2_1(self):
        """Test: cinquieme ligne du sous-lot 2.1 = '2.1.05'."""
        assert NumerotationService.generer_code_ligne(4, "2.1") == "2.1.05"

    def test_ligne_ordre_99(self):
        """Test: ligne 100 (ordre 99) = '1.100' (3 chiffres si > 99)."""
        # Note: le format %02d produit "100" pour 100 (pas de troncature)
        assert NumerotationService.generer_code_ligne(99, "1") == "1.100"

    def test_ligne_avec_sous_chapitre_profond(self):
        """Test: ligne dans sous-sous-chapitre = '1.2.3.01'."""
        assert NumerotationService.generer_code_ligne(0, "1.2.3") == "1.2.3.01"


class TestRenumeroterLots:
    """Tests pour le renumerotage en batch."""

    def test_renumeroter_lots_racine(self):
        """Test: renumerotation de 3 lots racine."""
        parents = [None, None, None]
        ordres = [0, 1, 2]
        result = NumerotationService.renumeroter_lots(parents, ordres)
        assert result == ["1", "2", "3"]

    def test_renumeroter_sous_chapitres(self):
        """Test: renumerotation de sous-chapitres."""
        parents = ["1", "1", "2"]
        ordres = [0, 1, 0]
        result = NumerotationService.renumeroter_lots(parents, ordres)
        assert result == ["1.1", "1.2", "2.1"]

    def test_renumeroter_listes_tailles_differentes(self):
        """Test: erreur si listes de tailles differentes."""
        with pytest.raises(ValueError) as exc_info:
            NumerotationService.renumeroter_lots([None, None], [0])
        assert "meme longueur" in str(exc_info.value).lower()

    def test_renumeroter_listes_vides(self):
        """Test: listes vides retourne liste vide."""
        result = NumerotationService.renumeroter_lots([], [])
        assert result == []


class TestRenumeroterLignes:
    """Tests pour le renumerotage des lignes d'un lot."""

    def test_renumeroter_lignes_lot_1(self):
        """Test: 3 lignes dans le lot 1."""
        result = NumerotationService.renumeroter_lignes("1", 3)
        assert result == ["1.01", "1.02", "1.03"]

    def test_renumeroter_lignes_sous_chapitre(self):
        """Test: 2 lignes dans le sous-chapitre 2.1."""
        result = NumerotationService.renumeroter_lignes("2.1", 2)
        assert result == ["2.1.01", "2.1.02"]

    def test_renumeroter_zero_lignes(self):
        """Test: 0 lignes retourne liste vide."""
        result = NumerotationService.renumeroter_lignes("1", 0)
        assert result == []
