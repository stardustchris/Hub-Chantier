"""Tests unitaires pour l'entite Fournisseur du module Financier.

Item 9: Tests de la propriete est_sous_traitant.
CGI art. 283-2 nonies : seuls les fournisseurs de type SOUS_TRAITANT
doivent etre identifies comme sous-traitants (autoliquidation TVA).
"""

import pytest

from modules.financier.domain.entities import Fournisseur
from modules.financier.domain.value_objects import TypeFournisseur


class TestFournisseurEstSousTraitant:
    """Tests pour la propriete Fournisseur.est_sous_traitant."""

    def test_fournisseur_sous_traitant(self):
        """Test: fournisseur de type SOUS_TRAITANT -> est_sous_traitant == True.

        Un sous-traitant BTP facture HT (CGI art. 283-2 nonies).
        """
        fournisseur = Fournisseur(
            id=1,
            raison_sociale="BTP Sous-Traitance SARL",
            type=TypeFournisseur.SOUS_TRAITANT,
            actif=True,
        )

        assert fournisseur.est_sous_traitant is True

    def test_fournisseur_negoce_pas_sous_traitant(self):
        """Test: fournisseur de type NEGOCE_MATERIAUX -> est_sous_traitant == False.

        Un negoce materiaux facture normalement avec TVA.
        """
        fournisseur = Fournisseur(
            id=2,
            raison_sociale="Materiaux du Sud",
            type=TypeFournisseur.NEGOCE_MATERIAUX,
            actif=True,
        )

        assert fournisseur.est_sous_traitant is False

    def test_fournisseur_loueur_pas_sous_traitant(self):
        """Test: fournisseur de type LOUEUR -> est_sous_traitant == False.

        Un loueur de materiel facture normalement avec TVA.
        """
        fournisseur = Fournisseur(
            id=3,
            raison_sociale="Location Engins Pro",
            type=TypeFournisseur.LOUEUR,
            actif=True,
        )

        assert fournisseur.est_sous_traitant is False

    def test_fournisseur_prestataire_pas_sous_traitant(self):
        """Test: fournisseur de type SERVICE -> est_sous_traitant == False.

        Un prestataire de services facture normalement avec TVA.
        """
        fournisseur = Fournisseur(
            id=4,
            raison_sociale="Bureau Etudes ABC",
            type=TypeFournisseur.SERVICE,
            actif=True,
        )

        assert fournisseur.est_sous_traitant is False
