"""Tests unitaires pour les Entities du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal

from modules.financier.domain.entities import (
    Fournisseur,
    Budget,
    LotBudgetaire,
    Achat,
    AchatValidationError,
    TransitionStatutAchatInvalideError,
)
from modules.financier.domain.value_objects import (
    TypeFournisseur,
    TypeAchat,
    StatutAchat,
    UniteMesure,
)


# ============================================================
# Tests Fournisseur
# ============================================================

class TestFournisseur:
    """Tests pour l'entite Fournisseur."""

    def test_create_fournisseur_valid(self):
        """Test: creation d'un fournisseur valide."""
        fournisseur = Fournisseur(
            id=1,
            raison_sociale="Materiaux du Sud",
            type=TypeFournisseur.NEGOCE_MATERIAUX,
            siret="12345678901234",
            email="contact@materiaux.fr",
        )
        assert fournisseur.id == 1
        assert fournisseur.raison_sociale == "Materiaux du Sud"
        assert fournisseur.type == TypeFournisseur.NEGOCE_MATERIAUX
        assert fournisseur.siret == "12345678901234"
        assert fournisseur.actif is True

    def test_create_fournisseur_minimal(self):
        """Test: creation d'un fournisseur avec le minimum requis."""
        fournisseur = Fournisseur(raison_sociale="Test SARL")
        assert fournisseur.raison_sociale == "Test SARL"
        assert fournisseur.type == TypeFournisseur.NEGOCE_MATERIAUX  # default
        assert fournisseur.actif is True

    def test_create_fournisseur_sans_raison_sociale(self):
        """Test: erreur si raison sociale vide."""
        with pytest.raises(ValueError) as exc_info:
            Fournisseur(raison_sociale="")
        assert "raison sociale" in str(exc_info.value).lower()

    def test_create_fournisseur_raison_sociale_espaces(self):
        """Test: erreur si raison sociale uniquement espaces."""
        with pytest.raises(ValueError):
            Fournisseur(raison_sociale="   ")

    def test_create_fournisseur_siret_invalide(self):
        """Test: erreur si SIRET invalide (pas 14 chiffres)."""
        with pytest.raises(ValueError) as exc_info:
            Fournisseur(raison_sociale="Test", siret="1234")
        assert "siret" in str(exc_info.value).lower()

    def test_create_fournisseur_siret_avec_lettres(self):
        """Test: erreur si SIRET contient des lettres."""
        with pytest.raises(ValueError):
            Fournisseur(raison_sociale="Test", siret="1234567890123A")

    def test_create_fournisseur_siret_none_ok(self):
        """Test: SIRET None est accepte."""
        fournisseur = Fournisseur(raison_sociale="Test", siret=None)
        assert fournisseur.siret is None

    def test_create_fournisseur_email_invalide(self):
        """Test: erreur si email invalide."""
        with pytest.raises(ValueError) as exc_info:
            Fournisseur(raison_sociale="Test", email="invalide")
        assert "email" in str(exc_info.value).lower()

    def test_create_fournisseur_email_valid(self):
        """Test: email valide accepte."""
        fournisseur = Fournisseur(
            raison_sociale="Test",
            email="test@example.com",
        )
        assert fournisseur.email == "test@example.com"

    def test_activer(self):
        """Test: activation d'un fournisseur."""
        fournisseur = Fournisseur(raison_sociale="Test", actif=False)
        fournisseur.activer()
        assert fournisseur.actif is True
        assert fournisseur.updated_at is not None

    def test_desactiver(self):
        """Test: desactivation d'un fournisseur."""
        fournisseur = Fournisseur(raison_sociale="Test")
        fournisseur.desactiver()
        assert fournisseur.actif is False
        assert fournisseur.updated_at is not None

    def test_modifier_contact(self):
        """Test: modification des informations de contact."""
        fournisseur = Fournisseur(raison_sociale="Test")
        fournisseur.modifier_contact(
            contact_principal="Jean Dupont",
            telephone="0601020304",
            email="jean@test.fr",
        )
        assert fournisseur.contact_principal == "Jean Dupont"
        assert fournisseur.telephone == "0601020304"
        assert fournisseur.email == "jean@test.fr"
        assert fournisseur.updated_at is not None

    def test_modifier_contact_email_invalide(self):
        """Test: erreur si email invalide lors de la modification."""
        fournisseur = Fournisseur(raison_sociale="Test")
        with pytest.raises(ValueError):
            fournisseur.modifier_contact(email="invalide")

    def test_supprimer_soft_delete(self):
        """Test: suppression en soft delete."""
        fournisseur = Fournisseur(raison_sociale="Test")
        assert fournisseur.est_supprime is False
        fournisseur.supprimer(deleted_by=1)
        assert fournisseur.est_supprime is True
        assert fournisseur.deleted_at is not None
        assert fournisseur.deleted_by == 1

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        now = datetime.utcnow()
        fournisseur = Fournisseur(
            id=1,
            raison_sociale="Test",
            type=TypeFournisseur.LOUEUR,
            siret="12345678901234",
            actif=True,
            created_at=now,
        )
        d = fournisseur.to_dict()
        assert d["id"] == 1
        assert d["raison_sociale"] == "Test"
        assert d["type"] == "loueur"
        assert d["siret"] == "12345678901234"
        assert d["actif"] is True
        assert d["created_at"] == now.isoformat()


# ============================================================
# Tests Budget
# ============================================================

class TestBudget:
    """Tests pour l'entite Budget."""

    def test_create_budget_valid(self):
        """Test: creation d'un budget valide."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            retenue_garantie_pct=Decimal("5"),
            seuil_alerte_pct=Decimal("80"),
            seuil_validation_achat=Decimal("1000"),
        )
        assert budget.chantier_id == 100
        assert budget.montant_initial_ht == Decimal("500000")

    def test_create_budget_chantier_id_zero(self):
        """Test: erreur si chantier_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            Budget(chantier_id=0)
        assert "chantier" in str(exc_info.value).lower()

    def test_create_budget_chantier_id_negatif(self):
        """Test: erreur si chantier_id est negatif."""
        with pytest.raises(ValueError):
            Budget(chantier_id=-1)

    def test_create_budget_montant_negatif(self):
        """Test: erreur si montant initial negatif."""
        with pytest.raises(ValueError) as exc_info:
            Budget(chantier_id=1, montant_initial_ht=Decimal("-100"))
        assert "montant" in str(exc_info.value).lower()

    def test_create_budget_retenue_hors_limites(self):
        """Test: erreur si retenue de garantie hors limites."""
        with pytest.raises(ValueError):
            Budget(chantier_id=1, retenue_garantie_pct=Decimal("101"))
        with pytest.raises(ValueError):
            Budget(chantier_id=1, retenue_garantie_pct=Decimal("-1"))

    def test_create_budget_seuil_alerte_hors_limites(self):
        """Test: erreur si seuil d'alerte hors limites (max 200%)."""
        with pytest.raises(ValueError):
            Budget(chantier_id=1, seuil_alerte_pct=Decimal("250"))
        with pytest.raises(ValueError):
            Budget(chantier_id=1, seuil_alerte_pct=Decimal("-5"))

    def test_create_budget_seuil_validation_negatif(self):
        """Test: erreur si seuil de validation negatif."""
        with pytest.raises(ValueError):
            Budget(chantier_id=1, seuil_validation_achat=Decimal("-100"))

    def test_montant_revise_ht(self):
        """Test: propriete calculee montant_revise_ht."""
        budget = Budget(
            chantier_id=1,
            montant_initial_ht=Decimal("500000"),
            montant_avenants_ht=Decimal("50000"),
        )
        assert budget.montant_revise_ht == Decimal("550000")

    def test_montant_revise_ht_sans_avenant(self):
        """Test: montant revise = montant initial si pas d'avenant."""
        budget = Budget(
            chantier_id=1,
            montant_initial_ht=Decimal("500000"),
        )
        assert budget.montant_revise_ht == Decimal("500000")

    def test_ajouter_avenant(self):
        """Test: ajout d'un avenant au budget."""
        budget = Budget(chantier_id=1, montant_initial_ht=Decimal("500000"))
        budget.ajouter_avenant(Decimal("25000"), "Travaux supplementaires")
        assert budget.montant_avenants_ht == Decimal("25000")
        assert budget.montant_revise_ht == Decimal("525000")
        assert budget.updated_at is not None

    def test_ajouter_avenant_negatif(self):
        """Test: ajout d'un avenant negatif (reduction)."""
        budget = Budget(
            chantier_id=1,
            montant_initial_ht=Decimal("500000"),
            montant_avenants_ht=Decimal("50000"),
        )
        budget.ajouter_avenant(Decimal("-10000"), "Reduction perimetre")
        assert budget.montant_avenants_ht == Decimal("40000")

    def test_ajouter_avenant_sans_motif(self):
        """Test: erreur si motif d'avenant vide."""
        budget = Budget(chantier_id=1, montant_initial_ht=Decimal("500000"))
        with pytest.raises(ValueError) as exc_info:
            budget.ajouter_avenant(Decimal("10000"), "")
        assert "motif" in str(exc_info.value).lower()

    def test_modifier_retenue_garantie(self):
        """Test: modification de la retenue de garantie."""
        budget = Budget(chantier_id=1)
        budget.modifier_retenue_garantie(Decimal("5"))
        assert budget.retenue_garantie_pct == Decimal("5")
        assert budget.updated_at is not None

    def test_modifier_retenue_garantie_invalide(self):
        """Test: erreur si retenue hors limites."""
        budget = Budget(chantier_id=1)
        with pytest.raises(ValueError):
            budget.modifier_retenue_garantie(Decimal("101"))
        with pytest.raises(ValueError):
            budget.modifier_retenue_garantie(Decimal("-1"))

    def test_necessite_validation_achat_au_dessus_seuil(self):
        """Test: achat au-dessus du seuil necessite validation."""
        budget = Budget(chantier_id=1, seuil_validation_achat=Decimal("1000"))
        assert budget.necessite_validation_achat(Decimal("1500")) is True

    def test_necessite_validation_achat_egal_seuil(self):
        """Test: achat egal au seuil necessite validation."""
        budget = Budget(chantier_id=1, seuil_validation_achat=Decimal("1000"))
        assert budget.necessite_validation_achat(Decimal("1000")) is True

    def test_necessite_validation_achat_sous_seuil(self):
        """Test: achat sous le seuil ne necessite pas validation."""
        budget = Budget(chantier_id=1, seuil_validation_achat=Decimal("1000"))
        assert budget.necessite_validation_achat(Decimal("999")) is False

    def test_supprimer_soft_delete(self):
        """Test: suppression en soft delete."""
        budget = Budget(chantier_id=1)
        assert budget.est_supprime is False
        budget.supprimer(deleted_by=1)
        assert budget.est_supprime is True
        assert budget.deleted_at is not None
        assert budget.deleted_by == 1

    def test_create_budget_with_devis_id(self):
        """Test GAP #6: creation d'un budget avec devis_id."""
        budget = Budget(
            chantier_id=1,
            montant_initial_ht=Decimal("100000"),
            devis_id=42,
        )
        assert budget.devis_id == 42

    def test_create_budget_without_devis_id(self):
        """Test GAP #6: budget sans devis_id a None par defaut."""
        budget = Budget(chantier_id=1)
        assert budget.devis_id is None

    def test_to_dict_includes_devis_id(self):
        """Test GAP #6: to_dict contient devis_id."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            devis_id=7,
        )
        d = budget.to_dict()
        assert d["devis_id"] == 7

    def test_to_dict_devis_id_none(self):
        """Test GAP #6: to_dict avec devis_id None."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
        )
        d = budget.to_dict()
        assert d["devis_id"] is None

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            montant_avenants_ht=Decimal("50000"),
        )
        d = budget.to_dict()
        assert d["id"] == 1
        assert d["chantier_id"] == 100
        assert d["montant_initial_ht"] == "500000"
        assert d["montant_avenants_ht"] == "50000"
        assert d["montant_revise_ht"] == "550000"


# ============================================================
# Tests LotBudgetaire
# ============================================================

class TestLotBudgetaire:
    """Tests pour l'entite LotBudgetaire."""

    def test_create_lot_valid(self):
        """Test: creation d'un lot budgetaire valide."""
        lot = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="LOT001",
            libelle="Gros oeuvre",
            unite=UniteMesure.M2,
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        assert lot.code_lot == "LOT001"
        assert lot.libelle == "Gros oeuvre"
        assert lot.unite == UniteMesure.M2

    def test_create_lot_sans_code(self):
        """Test: erreur si code du lot vide."""
        with pytest.raises(ValueError) as exc_info:
            LotBudgetaire(budget_id=1, code_lot="", libelle="Test")
        assert "code" in str(exc_info.value).lower()

    def test_create_lot_sans_libelle(self):
        """Test: erreur si libelle du lot vide."""
        with pytest.raises(ValueError) as exc_info:
            LotBudgetaire(budget_id=1, code_lot="LOT001", libelle="")
        assert "libellé" in str(exc_info.value).lower() or "libelle" in str(exc_info.value).lower()

    def test_create_lot_quantite_negative(self):
        """Test: erreur si quantite negative."""
        with pytest.raises(ValueError):
            LotBudgetaire(
                budget_id=1,
                code_lot="LOT001",
                libelle="Test",
                quantite_prevue=Decimal("-1"),
            )

    def test_create_lot_prix_unitaire_negatif(self):
        """Test: erreur si prix unitaire negatif."""
        with pytest.raises(ValueError):
            LotBudgetaire(
                budget_id=1,
                code_lot="LOT001",
                libelle="Test",
                prix_unitaire_ht=Decimal("-10"),
            )

    def test_total_prevu_ht(self):
        """Test: propriete calculee total_prevu_ht."""
        lot = LotBudgetaire(
            budget_id=1,
            code_lot="LOT001",
            libelle="Test",
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        assert lot.total_prevu_ht == Decimal("5000")

    def test_total_prevu_ht_zero(self):
        """Test: total prevu HT a zero si quantite ou prix a zero."""
        lot = LotBudgetaire(
            budget_id=1,
            code_lot="LOT001",
            libelle="Test",
            quantite_prevue=Decimal("0"),
            prix_unitaire_ht=Decimal("50"),
        )
        assert lot.total_prevu_ht == Decimal("0")

    def test_supprimer_soft_delete(self):
        """Test: suppression en soft delete."""
        lot = LotBudgetaire(budget_id=1, code_lot="LOT001", libelle="Test")
        assert lot.est_supprime is False
        lot.supprimer(deleted_by=1)
        assert lot.est_supprime is True
        assert lot.deleted_at is not None

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        lot = LotBudgetaire(
            id=1,
            budget_id=10,
            code_lot="LOT001",
            libelle="Gros oeuvre",
            unite=UniteMesure.M2,
            quantite_prevue=Decimal("100"),
            prix_unitaire_ht=Decimal("50"),
        )
        d = lot.to_dict()
        assert d["id"] == 1
        assert d["code_lot"] == "LOT001"
        assert d["libelle"] == "Gros oeuvre"
        assert d["unite"] == "m2"
        assert d["total_prevu_ht"] == "5000.00"


# ============================================================
# Tests Achat
# ============================================================

class TestAchat:
    """Tests pour l'entite Achat."""

    def _make_achat(self, **kwargs):
        """Cree un achat valide avec valeurs par defaut."""
        defaults = {
            "chantier_id": 1,
            "libelle": "Ciment CEM II 25kg",
            "quantite": Decimal("10"),
            "prix_unitaire_ht": Decimal("8.50"),
            "taux_tva": Decimal("20"),
        }
        defaults.update(kwargs)
        return Achat(**defaults)

    def test_create_achat_valid(self):
        """Test: creation d'un achat valide."""
        achat = self._make_achat(id=1, chantier_id=100, fournisseur_id=5)
        assert achat.id == 1
        assert achat.chantier_id == 100
        assert achat.statut == StatutAchat.DEMANDE
        assert achat.libelle == "Ciment CEM II 25kg"

    def test_create_achat_sans_libelle(self):
        """Test: erreur si libelle vide."""
        with pytest.raises(AchatValidationError) as exc_info:
            self._make_achat(libelle="")
        assert "libellé" in str(exc_info.value).lower() or "libelle" in str(exc_info.value).lower()

    def test_create_achat_quantite_zero(self):
        """Test: erreur si quantite a zero."""
        with pytest.raises(AchatValidationError):
            self._make_achat(quantite=Decimal("0"))

    def test_create_achat_quantite_negative(self):
        """Test: erreur si quantite negative."""
        with pytest.raises(AchatValidationError):
            self._make_achat(quantite=Decimal("-1"))

    def test_create_achat_prix_negatif(self):
        """Test: erreur si prix unitaire negatif."""
        with pytest.raises(AchatValidationError):
            self._make_achat(prix_unitaire_ht=Decimal("-5"))

    def test_create_achat_taux_tva_invalide(self):
        """Test: erreur si taux TVA invalide."""
        with pytest.raises(AchatValidationError):
            self._make_achat(taux_tva=Decimal("7"))

    def test_total_ht(self):
        """Test: propriete calculee total_ht."""
        achat = self._make_achat(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("8.50"),
        )
        assert achat.total_ht == Decimal("85.00")

    def test_montant_tva(self):
        """Test: propriete calculee montant_tva."""
        achat = self._make_achat(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
        )
        # total_ht = 1000, tva = 200
        assert achat.montant_tva == Decimal("200")

    def test_total_ttc(self):
        """Test: propriete calculee total_ttc."""
        achat = self._make_achat(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
        )
        # total_ht = 1000, tva = 200, ttc = 1200
        assert achat.total_ttc == Decimal("1200")

    def test_total_ttc_taux_zero(self):
        """Test: total_ttc = total_ht si TVA a 0%."""
        achat = self._make_achat(
            quantite=Decimal("5"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("0"),
        )
        assert achat.total_ttc == Decimal("500")
        assert achat.montant_tva == Decimal("0")

    # Workflow transitions
    def test_valider_achat(self):
        """Test: validation d'un achat (demande -> valide)."""
        achat = self._make_achat()
        achat.valider(valideur_id=5)
        assert achat.statut == StatutAchat.VALIDE
        assert achat.valideur_id == 5
        assert achat.validated_at is not None

    def test_valider_achat_deja_valide(self):
        """Test: erreur si on valide un achat deja valide."""
        achat = self._make_achat()
        achat.valider(5)
        with pytest.raises(TransitionStatutAchatInvalideError):
            achat.valider(5)

    def test_refuser_achat(self):
        """Test: refus d'un achat (demande -> refuse)."""
        achat = self._make_achat()
        achat.refuser(valideur_id=5, motif="Trop cher")
        assert achat.statut == StatutAchat.REFUSE
        assert achat.valideur_id == 5
        assert achat.motif_refus == "Trop cher"
        assert achat.validated_at is not None

    def test_refuser_achat_sans_motif(self):
        """Test: erreur si motif de refus vide."""
        achat = self._make_achat()
        with pytest.raises(AchatValidationError):
            achat.refuser(5, "")

    def test_refuser_achat_motif_espaces(self):
        """Test: erreur si motif de refus uniquement espaces."""
        achat = self._make_achat()
        with pytest.raises(AchatValidationError):
            achat.refuser(5, "   ")

    def test_refuser_achat_deja_commande(self):
        """Test: erreur si on refuse un achat commande."""
        achat = self._make_achat()
        achat.valider(5)
        achat.passer_commande()
        with pytest.raises(TransitionStatutAchatInvalideError):
            achat.refuser(5, "Motif")

    def test_passer_commande(self):
        """Test: passage en commande (valide -> commande)."""
        achat = self._make_achat()
        achat.valider(5)
        achat.passer_commande()
        assert achat.statut == StatutAchat.COMMANDE
        assert achat.date_commande is not None

    def test_passer_commande_depuis_demande(self):
        """Test: erreur si commande depuis statut demande."""
        achat = self._make_achat()
        with pytest.raises(TransitionStatutAchatInvalideError):
            achat.passer_commande()

    def test_marquer_livre(self):
        """Test: marquer comme livre (commande -> livre)."""
        achat = self._make_achat()
        achat.valider(5)
        achat.passer_commande()
        achat.marquer_livre()
        assert achat.statut == StatutAchat.LIVRE

    def test_marquer_livre_depuis_valide(self):
        """Test: erreur si livre depuis statut valide."""
        achat = self._make_achat()
        achat.valider(5)
        with pytest.raises(TransitionStatutAchatInvalideError):
            achat.marquer_livre()

    def test_marquer_facture(self):
        """Test: marquer comme facture (livre -> facture)."""
        achat = self._make_achat()
        achat.valider(5)
        achat.passer_commande()
        achat.marquer_livre()
        achat.marquer_facture("FAC-2026-001")
        assert achat.statut == StatutAchat.FACTURE
        assert achat.numero_facture == "FAC-2026-001"

    def test_marquer_facture_sans_numero(self):
        """Test: erreur si numero de facture vide."""
        achat = self._make_achat()
        achat.valider(5)
        achat.passer_commande()
        achat.marquer_livre()
        with pytest.raises(AchatValidationError):
            achat.marquer_facture("")

    def test_marquer_facture_depuis_commande(self):
        """Test: erreur si facture depuis statut commande."""
        achat = self._make_achat()
        achat.valider(5)
        achat.passer_commande()
        with pytest.raises(TransitionStatutAchatInvalideError):
            achat.marquer_facture("FAC-001")

    def test_workflow_complet(self):
        """Test: workflow complet demande -> valide -> commande -> livre -> facture."""
        achat = self._make_achat()
        assert achat.statut == StatutAchat.DEMANDE

        achat.valider(5)
        assert achat.statut == StatutAchat.VALIDE

        achat.passer_commande()
        assert achat.statut == StatutAchat.COMMANDE

        achat.marquer_livre()
        assert achat.statut == StatutAchat.LIVRE

        achat.marquer_facture("FAC-2026-001")
        assert achat.statut == StatutAchat.FACTURE

    def test_supprimer_soft_delete(self):
        """Test: suppression en soft delete."""
        achat = self._make_achat()
        assert achat.est_supprime is False
        achat.supprimer(deleted_by=1)
        assert achat.est_supprime is True
        assert achat.deleted_at is not None
        assert achat.deleted_by == 1

    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        achat = self._make_achat(
            id=1,
            chantier_id=100,
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
        )
        d = achat.to_dict()
        assert d["id"] == 1
        assert d["chantier_id"] == 100
        assert d["total_ht"] == "1000.00"
        assert d["montant_tva"] == "200.00"
        assert d["total_ttc"] == "1200.00"
        assert d["statut"] == "demande"

    def test_to_dict_statut_label(self):
        """Test: to_dict contient le type_achat et unite."""
        achat = self._make_achat(
            type_achat=TypeAchat.MATERIAU,
            unite=UniteMesure.KG,
        )
        d = achat.to_dict()
        assert d["type_achat"] == "materiau"
        assert d["unite"] == "kg"


# ============================================================
# Tests Fournisseur.est_sous_traitant
# ============================================================

class TestFournisseurEstSousTraitant:
    """Tests pour la propriete est_sous_traitant du Fournisseur.

    CGI art. 283-2 nonies : seuls les sous-traitants declenchent
    l'autoliquidation TVA. La propriete doit retourner True uniquement
    pour TypeFournisseur.SOUS_TRAITANT.
    """

    def test_sous_traitant_retourne_true(self):
        """Test: type=SOUS_TRAITANT -> est_sous_traitant == True."""
        fournisseur = Fournisseur(
            raison_sociale="BTP Sous-Traitance SARL",
            type=TypeFournisseur.SOUS_TRAITANT,
        )
        assert fournisseur.est_sous_traitant is True

    def test_negoce_retourne_false(self):
        """Test: type=NEGOCE_MATERIAUX -> est_sous_traitant == False."""
        fournisseur = Fournisseur(
            raison_sociale="Materiaux du Sud",
            type=TypeFournisseur.NEGOCE_MATERIAUX,
        )
        assert fournisseur.est_sous_traitant is False

    def test_loueur_retourne_false(self):
        """Test: type=LOUEUR -> est_sous_traitant == False."""
        fournisseur = Fournisseur(
            raison_sociale="Location Engins Pro",
            type=TypeFournisseur.LOUEUR,
        )
        assert fournisseur.est_sous_traitant is False

    def test_service_retourne_false(self):
        """Test: type=SERVICE -> est_sous_traitant == False."""
        fournisseur = Fournisseur(
            raison_sociale="Bureau Etudes ABC",
            type=TypeFournisseur.SERVICE,
        )
        assert fournisseur.est_sous_traitant is False
