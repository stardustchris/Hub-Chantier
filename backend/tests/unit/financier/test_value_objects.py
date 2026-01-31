"""Tests unitaires pour les Value Objects du module Financier."""

import pytest
from decimal import Decimal

from modules.financier.domain.value_objects import (
    TypeFournisseur,
    TypeAchat,
    StatutAchat,
    UniteMesure,
    TauxTVA,
    TAUX_VALIDES,
)


class TestTypeFournisseur:
    """Tests pour TypeFournisseur."""

    def test_all_types_exist(self):
        """Test: tous les types de fournisseur sont definis."""
        assert TypeFournisseur.NEGOCE_MATERIAUX
        assert TypeFournisseur.LOUEUR
        assert TypeFournisseur.SOUS_TRAITANT
        assert TypeFournisseur.SERVICE

    def test_type_values(self):
        """Test: les valeurs des types sont correctes."""
        assert TypeFournisseur.NEGOCE_MATERIAUX.value == "negoce_materiaux"
        assert TypeFournisseur.LOUEUR.value == "loueur"
        assert TypeFournisseur.SOUS_TRAITANT.value == "sous_traitant"
        assert TypeFournisseur.SERVICE.value == "service"

    def test_type_labels(self):
        """Test: chaque type a un label."""
        for t in TypeFournisseur:
            assert t.label is not None
            assert len(t.label) > 0

    def test_specific_labels(self):
        """Test: labels specifiques corrects."""
        assert TypeFournisseur.NEGOCE_MATERIAUX.label == "Négoce matériaux"
        assert TypeFournisseur.LOUEUR.label == "Loueur"
        assert TypeFournisseur.SOUS_TRAITANT.label == "Sous-traitant"
        assert TypeFournisseur.SERVICE.label == "Service"

    def test_is_string_enum(self):
        """Test: TypeFournisseur est un str Enum."""
        assert isinstance(TypeFournisseur.NEGOCE_MATERIAUX, str)


class TestTypeAchat:
    """Tests pour TypeAchat."""

    def test_all_types_exist(self):
        """Test: tous les types d'achat sont definis."""
        assert TypeAchat.MATERIAU
        assert TypeAchat.MATERIEL
        assert TypeAchat.SOUS_TRAITANCE
        assert TypeAchat.SERVICE

    def test_type_values(self):
        """Test: les valeurs des types sont correctes."""
        assert TypeAchat.MATERIAU.value == "materiau"
        assert TypeAchat.MATERIEL.value == "materiel"
        assert TypeAchat.SOUS_TRAITANCE.value == "sous_traitance"
        assert TypeAchat.SERVICE.value == "service"

    def test_type_labels(self):
        """Test: chaque type a un label."""
        for t in TypeAchat:
            assert t.label is not None
            assert len(t.label) > 0

    def test_specific_labels(self):
        """Test: labels specifiques corrects."""
        assert TypeAchat.MATERIAU.label == "Matériau"
        assert TypeAchat.MATERIEL.label == "Matériel"
        assert TypeAchat.SOUS_TRAITANCE.label == "Sous-traitance"
        assert TypeAchat.SERVICE.label == "Service"


class TestStatutAchat:
    """Tests pour StatutAchat avec state machine."""

    def test_all_statuts_exist(self):
        """Test: tous les statuts sont definis."""
        assert StatutAchat.DEMANDE
        assert StatutAchat.VALIDE
        assert StatutAchat.REFUSE
        assert StatutAchat.COMMANDE
        assert StatutAchat.LIVRE
        assert StatutAchat.FACTURE

    def test_statut_values(self):
        """Test: les valeurs des statuts sont correctes."""
        assert StatutAchat.DEMANDE.value == "demande"
        assert StatutAchat.VALIDE.value == "valide"
        assert StatutAchat.REFUSE.value == "refuse"
        assert StatutAchat.COMMANDE.value == "commande"
        assert StatutAchat.LIVRE.value == "livre"
        assert StatutAchat.FACTURE.value == "facture"

    def test_statut_labels(self):
        """Test: chaque statut a un label."""
        for statut in StatutAchat:
            assert statut.label is not None
            assert len(statut.label) > 0

    def test_statut_couleurs(self):
        """Test: chaque statut a une couleur CSS valide."""
        for statut in StatutAchat:
            assert statut.couleur is not None
            assert statut.couleur.startswith("#")

    def test_statut_emoji(self):
        """Test: chaque statut a un emoji."""
        for statut in StatutAchat:
            assert statut.emoji is not None

    def test_est_final_refuse(self):
        """Test: REFUSE est un etat final."""
        assert StatutAchat.REFUSE.est_final is True

    def test_est_final_facture(self):
        """Test: FACTURE est un etat final."""
        assert StatutAchat.FACTURE.est_final is True

    def test_est_final_demande(self):
        """Test: DEMANDE n'est pas un etat final."""
        assert StatutAchat.DEMANDE.est_final is False

    def test_est_final_valide(self):
        """Test: VALIDE n'est pas un etat final."""
        assert StatutAchat.VALIDE.est_final is False

    def test_est_final_commande(self):
        """Test: COMMANDE n'est pas un etat final."""
        assert StatutAchat.COMMANDE.est_final is False

    def test_est_final_livre(self):
        """Test: LIVRE n'est pas un etat final."""
        assert StatutAchat.LIVRE.est_final is False

    def test_est_actif_demande(self):
        """Test: DEMANDE est actif."""
        assert StatutAchat.DEMANDE.est_actif is True

    def test_est_actif_refuse(self):
        """Test: REFUSE n'est pas actif."""
        assert StatutAchat.REFUSE.est_actif is False

    def test_est_actif_valide(self):
        """Test: VALIDE est actif."""
        assert StatutAchat.VALIDE.est_actif is True

    def test_est_actif_facture(self):
        """Test: FACTURE est actif."""
        assert StatutAchat.FACTURE.est_actif is True

    # State machine transitions
    def test_transition_demande_vers_valide(self):
        """Test: transition DEMANDE -> VALIDE autorisee."""
        assert StatutAchat.DEMANDE.peut_transitionner_vers(StatutAchat.VALIDE)

    def test_transition_demande_vers_refuse(self):
        """Test: transition DEMANDE -> REFUSE autorisee."""
        assert StatutAchat.DEMANDE.peut_transitionner_vers(StatutAchat.REFUSE)

    def test_transition_demande_vers_commande_interdite(self):
        """Test: transition DEMANDE -> COMMANDE interdite."""
        assert not StatutAchat.DEMANDE.peut_transitionner_vers(StatutAchat.COMMANDE)

    def test_transition_valide_vers_commande(self):
        """Test: transition VALIDE -> COMMANDE autorisee."""
        assert StatutAchat.VALIDE.peut_transitionner_vers(StatutAchat.COMMANDE)

    def test_transition_valide_vers_refuse(self):
        """Test: transition VALIDE -> REFUSE autorisee (annulation)."""
        assert StatutAchat.VALIDE.peut_transitionner_vers(StatutAchat.REFUSE)

    def test_transition_refuse_terminal(self):
        """Test: REFUSE ne peut transitionner vers aucun statut."""
        assert len(StatutAchat.REFUSE.transitions_possibles()) == 0

    def test_transition_commande_vers_livre(self):
        """Test: transition COMMANDE -> LIVRE autorisee."""
        assert StatutAchat.COMMANDE.peut_transitionner_vers(StatutAchat.LIVRE)

    def test_transition_commande_vers_facture_interdite(self):
        """Test: transition COMMANDE -> FACTURE interdite."""
        assert not StatutAchat.COMMANDE.peut_transitionner_vers(StatutAchat.FACTURE)

    def test_transition_livre_vers_facture(self):
        """Test: transition LIVRE -> FACTURE autorisee."""
        assert StatutAchat.LIVRE.peut_transitionner_vers(StatutAchat.FACTURE)

    def test_transition_facture_terminal(self):
        """Test: FACTURE ne peut transitionner vers aucun statut."""
        assert len(StatutAchat.FACTURE.transitions_possibles()) == 0

    def test_transitions_possibles_demande(self):
        """Test: transitions possibles depuis DEMANDE."""
        transitions = StatutAchat.DEMANDE.transitions_possibles()
        assert transitions == {StatutAchat.VALIDE, StatutAchat.REFUSE}

    def test_transitions_possibles_valide(self):
        """Test: transitions possibles depuis VALIDE."""
        transitions = StatutAchat.VALIDE.transitions_possibles()
        assert transitions == {StatutAchat.COMMANDE, StatutAchat.REFUSE}

    def test_initial(self):
        """Test: statut initial est DEMANDE."""
        assert StatutAchat.initial() == StatutAchat.DEMANDE


class TestUniteMesure:
    """Tests pour UniteMesure."""

    def test_all_unites_exist(self):
        """Test: toutes les unites de mesure sont definies."""
        assert UniteMesure.M2
        assert UniteMesure.M3
        assert UniteMesure.FORFAIT
        assert UniteMesure.KG
        assert UniteMesure.HEURE
        assert UniteMesure.ML
        assert UniteMesure.U

    def test_unite_values(self):
        """Test: les valeurs des unites sont correctes."""
        assert UniteMesure.M2.value == "m2"
        assert UniteMesure.M3.value == "m3"
        assert UniteMesure.FORFAIT.value == "forfait"
        assert UniteMesure.KG.value == "kg"
        assert UniteMesure.HEURE.value == "heure"
        assert UniteMesure.ML.value == "ml"
        assert UniteMesure.U.value == "u"

    def test_unite_labels(self):
        """Test: chaque unite a un label."""
        for u in UniteMesure:
            assert u.label is not None
            assert len(u.label) > 0

    def test_unite_symboles(self):
        """Test: chaque unite a un symbole."""
        for u in UniteMesure:
            assert u.symbole is not None
            assert len(u.symbole) > 0

    def test_specific_symboles(self):
        """Test: symboles specifiques corrects."""
        assert UniteMesure.M2.symbole == "m\u00b2"
        assert UniteMesure.M3.symbole == "m\u00b3"
        assert UniteMesure.FORFAIT.symbole == "fft"
        assert UniteMesure.KG.symbole == "kg"
        assert UniteMesure.HEURE.symbole == "h"


class TestTauxTVA:
    """Tests pour TauxTVA."""

    def test_taux_valides_list(self):
        """Test: la liste des taux valides contient les 4 taux francais."""
        assert Decimal("0") in TAUX_VALIDES
        assert Decimal("5.5") in TAUX_VALIDES
        assert Decimal("10") in TAUX_VALIDES
        assert Decimal("20") in TAUX_VALIDES
        assert len(TAUX_VALIDES) == 4

    def test_creation_taux_normal(self):
        """Test: creation du taux normal 20%."""
        taux = TauxTVA(taux=Decimal("20"))
        assert taux.taux == Decimal("20")

    def test_creation_taux_intermediaire(self):
        """Test: creation du taux intermediaire 10%."""
        taux = TauxTVA(taux=Decimal("10"))
        assert taux.taux == Decimal("10")

    def test_creation_taux_reduit(self):
        """Test: creation du taux reduit 5.5%."""
        taux = TauxTVA(taux=Decimal("5.5"))
        assert taux.taux == Decimal("5.5")

    def test_creation_taux_zero(self):
        """Test: creation du taux zero 0%."""
        taux = TauxTVA(taux=Decimal("0"))
        assert taux.taux == Decimal("0")

    def test_creation_taux_invalide(self):
        """Test: erreur si taux invalide."""
        with pytest.raises(ValueError) as exc_info:
            TauxTVA(taux=Decimal("7"))
        assert "invalide" in str(exc_info.value).lower()

    def test_creation_taux_negatif_invalide(self):
        """Test: erreur si taux negatif."""
        with pytest.raises(ValueError):
            TauxTVA(taux=Decimal("-5"))

    def test_calculer_tva_20_pct(self):
        """Test: calcul TVA a 20% sur 1000 EUR HT."""
        taux = TauxTVA.taux_normal()
        montant_ht = Decimal("1000")
        tva = taux.calculer_tva(montant_ht)
        assert tva == Decimal("200")

    def test_calculer_tva_10_pct(self):
        """Test: calcul TVA a 10% sur 500 EUR HT."""
        taux = TauxTVA.taux_intermediaire()
        montant_ht = Decimal("500")
        tva = taux.calculer_tva(montant_ht)
        assert tva == Decimal("50")

    def test_calculer_tva_5_5_pct(self):
        """Test: calcul TVA a 5.5% sur 200 EUR HT."""
        taux = TauxTVA.taux_reduit()
        montant_ht = Decimal("200")
        tva = taux.calculer_tva(montant_ht)
        assert tva == Decimal("11.0")

    def test_calculer_tva_zero(self):
        """Test: calcul TVA a 0% donne 0."""
        taux = TauxTVA.taux_zero()
        montant_ht = Decimal("1000")
        tva = taux.calculer_tva(montant_ht)
        assert tva == Decimal("0")

    def test_calculer_ttc_20_pct(self):
        """Test: calcul TTC a 20% sur 1000 EUR HT."""
        taux = TauxTVA.taux_normal()
        montant_ht = Decimal("1000")
        ttc = taux.calculer_ttc(montant_ht)
        assert ttc == Decimal("1200")

    def test_calculer_ttc_zero(self):
        """Test: calcul TTC a 0% donne le montant HT."""
        taux = TauxTVA.taux_zero()
        montant_ht = Decimal("1000")
        ttc = taux.calculer_ttc(montant_ht)
        assert ttc == montant_ht

    def test_factory_taux_normal(self):
        """Test: factory taux_normal retourne 20%."""
        taux = TauxTVA.taux_normal()
        assert taux.taux == Decimal("20")

    def test_factory_taux_intermediaire(self):
        """Test: factory taux_intermediaire retourne 10%."""
        taux = TauxTVA.taux_intermediaire()
        assert taux.taux == Decimal("10")

    def test_factory_taux_reduit(self):
        """Test: factory taux_reduit retourne 5.5%."""
        taux = TauxTVA.taux_reduit()
        assert taux.taux == Decimal("5.5")

    def test_factory_taux_zero(self):
        """Test: factory taux_zero retourne 0%."""
        taux = TauxTVA.taux_zero()
        assert taux.taux == Decimal("0")

    def test_immutabilite(self):
        """Test: TauxTVA est immutable (frozen dataclass)."""
        taux = TauxTVA.taux_normal()
        with pytest.raises(Exception):
            taux.taux = Decimal("10")

    def test_egalite(self):
        """Test: egalite entre TauxTVA."""
        taux1 = TauxTVA(taux=Decimal("20"))
        taux2 = TauxTVA(taux=Decimal("20"))
        taux3 = TauxTVA(taux=Decimal("10"))
        assert taux1 == taux2
        assert taux1 != taux3
