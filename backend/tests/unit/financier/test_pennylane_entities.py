"""Tests unitaires pour les entites Pennylane du module Financier.

CONN-10: Tests pour les champs Pennylane de l'entite Achat.
CONN-11: Tests pour les champs Pennylane de l'entite FactureClient.
CONN-12: Tests pour la validation IBAN/BIC de l'entite Fournisseur.
CONN-14: Tests pour l'entite PennylaneMappingAnalytique.
CONN-15: Tests pour l'entite PennylanePendingReconciliation.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal

from modules.financier.domain.entities import (
    Achat,
    AchatValidationError,
    Fournisseur,
    FactureClient,
    PennylaneSyncLog,
    PennylaneMappingAnalytique,
    PennylanePendingReconciliation,
)
from modules.financier.domain.value_objects import StatutAchat


class TestAchatPennylaneFields:
    """Tests pour les champs Pennylane de l'entite Achat (CONN-10)."""

    def _make_achat(self, **kwargs):
        """Cree un achat avec des valeurs par defaut."""
        defaults = {
            "chantier_id": 100,
            "libelle": "Ciment CEM II 25kg",
            "quantite": Decimal("10"),
            "prix_unitaire_ht": Decimal("8.50"),
            "taux_tva": Decimal("20"),
        }
        defaults.update(kwargs)
        return Achat(**defaults)

    def test_ecart_budget_reel_avec_montant_reel(self):
        """Test: ecart_budget_reel calcule quand montant_ht_reel est present."""
        achat = self._make_achat(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),  # total_ht = 1000
            montant_ht_reel=Decimal("1100"),  # Depassement de 100
        )

        assert achat.ecart_budget_reel == Decimal("100")

    def test_ecart_budget_reel_economie(self):
        """Test: ecart_budget_reel negatif quand economie."""
        achat = self._make_achat(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),  # total_ht = 1000
            montant_ht_reel=Decimal("900"),  # Economie de 100
        )

        assert achat.ecart_budget_reel == Decimal("-100")

    def test_ecart_budget_reel_sans_montant_reel(self):
        """Test: ecart_budget_reel None quand montant_ht_reel absent."""
        achat = self._make_achat()

        assert achat.ecart_budget_reel is None

    def test_montant_pour_budget_avec_montant_reel(self):
        """Test: montant_pour_budget utilise montant_ht_reel si present."""
        achat = self._make_achat(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            montant_ht_reel=Decimal("1100"),
        )

        assert achat.montant_pour_budget == Decimal("1100")

    def test_montant_pour_budget_sans_montant_reel(self):
        """Test: montant_pour_budget utilise total_ht si montant_ht_reel absent."""
        achat = self._make_achat(
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
        )

        assert achat.montant_pour_budget == Decimal("1000")

    def test_a_montant_reel_true(self):
        """Test: a_montant_reel True si montant_ht_reel present."""
        achat = self._make_achat(montant_ht_reel=Decimal("500"))

        assert achat.a_montant_reel is True

    def test_a_montant_reel_false(self):
        """Test: a_montant_reel False si montant_ht_reel absent."""
        achat = self._make_achat()

        assert achat.a_montant_reel is False

    def test_source_donnee_defaut_hub(self):
        """Test: source_donnee par defaut est HUB."""
        achat = self._make_achat()

        assert achat.source_donnee == "HUB"

    def test_source_donnee_pennylane(self):
        """Test: source_donnee peut etre PENNYLANE."""
        achat = self._make_achat(source_donnee="PENNYLANE")

        assert achat.source_donnee == "PENNYLANE"

    def test_pennylane_invoice_id_initial_none(self):
        """Test: pennylane_invoice_id initialement None."""
        achat = self._make_achat()

        assert achat.pennylane_invoice_id is None

    def test_pennylane_invoice_id_set(self):
        """Test: pennylane_invoice_id peut etre defini."""
        achat = self._make_achat(pennylane_invoice_id="pl-inv-123")

        assert achat.pennylane_invoice_id == "pl-inv-123"

    def test_to_dict_inclut_champs_pennylane(self):
        """Test: to_dict inclut les champs Pennylane."""
        achat = self._make_achat(
            montant_ht_reel=Decimal("1100"),
            date_facture_reelle=date(2026, 2, 1),
            pennylane_invoice_id="pl-inv-123",
            source_donnee="PENNYLANE",
        )
        achat.id = 1

        result = achat.to_dict()

        assert result["montant_ht_reel"] == "1100"
        assert result["date_facture_reelle"] == "2026-02-01"
        assert result["pennylane_invoice_id"] == "pl-inv-123"
        assert result["source_donnee"] == "PENNYLANE"
        assert result["ecart_budget_reel"] is not None
        assert result["montant_pour_budget"] is not None


class TestFournisseurValidationIBANBIC:
    """Tests pour la validation IBAN/BIC de l'entite Fournisseur (CONN-12)."""

    def _make_fournisseur(self, **kwargs):
        """Cree un fournisseur avec des valeurs par defaut."""
        defaults = {
            "raison_sociale": "Materiaux du Sud",
        }
        defaults.update(kwargs)
        return Fournisseur(**defaults)

    def test_iban_valide_france(self):
        """Test: IBAN francais valide accepte."""
        fournisseur = self._make_fournisseur(iban="FR7630001007941234567890185")

        assert fournisseur.iban == "FR7630001007941234567890185"

    def test_iban_valide_avec_espaces(self):
        """Test: IBAN avec espaces accepte (normalisee)."""
        fournisseur = self._make_fournisseur(iban="FR76 3000 1007 9412 3456 7890 185")

        assert fournisseur.iban == "FR76 3000 1007 9412 3456 7890 185"

    def test_iban_trop_court(self):
        """Test: erreur si IBAN trop court."""
        with pytest.raises(ValueError) as exc_info:
            self._make_fournisseur(iban="FR76123")
        assert "IBAN" in str(exc_info.value)

    def test_iban_trop_long(self):
        """Test: erreur si IBAN trop long (> 34 caracteres)."""
        with pytest.raises(ValueError) as exc_info:
            self._make_fournisseur(iban="FR76" + "1" * 35)
        assert "IBAN" in str(exc_info.value)

    def test_iban_format_invalide(self):
        """Test: erreur si IBAN format invalide."""
        with pytest.raises(ValueError) as exc_info:
            self._make_fournisseur(iban="1234567890123456789")
        assert "IBAN" in str(exc_info.value)

    def test_iban_none_accepte(self):
        """Test: IBAN None accepte."""
        fournisseur = self._make_fournisseur(iban=None)

        assert fournisseur.iban is None

    def test_iban_vide_accepte(self):
        """Test: IBAN vide accepte (sera ignore)."""
        fournisseur = self._make_fournisseur(iban="")

        assert fournisseur.iban == ""

    def test_bic_valide_8_caracteres(self):
        """Test: BIC 8 caracteres valide accepte."""
        fournisseur = self._make_fournisseur(bic="BNPAFRPP")

        assert fournisseur.bic == "BNPAFRPP"

    def test_bic_valide_11_caracteres(self):
        """Test: BIC 11 caracteres valide accepte."""
        fournisseur = self._make_fournisseur(bic="BNPAFRPPXXX")

        assert fournisseur.bic == "BNPAFRPPXXX"

    def test_bic_invalide_longueur(self):
        """Test: erreur si BIC longueur incorrecte."""
        with pytest.raises(ValueError) as exc_info:
            self._make_fournisseur(bic="BNPA")
        assert "BIC" in str(exc_info.value)

    def test_bic_invalide_format(self):
        """Test: erreur si BIC format incorrect."""
        with pytest.raises(ValueError) as exc_info:
            self._make_fournisseur(bic="12345678")
        assert "BIC" in str(exc_info.value)

    def test_bic_none_accepte(self):
        """Test: BIC None accepte."""
        fournisseur = self._make_fournisseur(bic=None)

        assert fournisseur.bic is None

    def test_pennylane_supplier_id(self):
        """Test: pennylane_supplier_id peut etre defini."""
        fournisseur = self._make_fournisseur(pennylane_supplier_id="pl-sup-123")

        assert fournisseur.pennylane_supplier_id == "pl-sup-123"

    def test_source_donnee_defaut_hub(self):
        """Test: source_donnee par defaut est HUB."""
        fournisseur = self._make_fournisseur()

        assert fournisseur.source_donnee == "HUB"

    def test_source_donnee_pennylane(self):
        """Test: source_donnee peut etre PENNYLANE."""
        fournisseur = self._make_fournisseur(source_donnee="PENNYLANE")

        assert fournisseur.source_donnee == "PENNYLANE"

    def test_est_importe_pennylane_true(self):
        """Test: est_importe_pennylane True si source PENNYLANE."""
        fournisseur = self._make_fournisseur(source_donnee="PENNYLANE")

        assert fournisseur.est_importe_pennylane is True

    def test_est_importe_pennylane_false(self):
        """Test: est_importe_pennylane False si source HUB."""
        fournisseur = self._make_fournisseur()

        assert fournisseur.est_importe_pennylane is False

    def test_marquer_sync_pennylane(self):
        """Test: marquer_sync_pennylane met a jour la date de sync."""
        fournisseur = self._make_fournisseur()
        assert fournisseur.derniere_sync_pennylane is None

        fournisseur.marquer_sync_pennylane()

        assert fournisseur.derniere_sync_pennylane is not None
        assert isinstance(fournisseur.derniere_sync_pennylane, datetime)

    def test_delai_paiement_jours_defaut(self):
        """Test: delai_paiement_jours par defaut est 30."""
        fournisseur = self._make_fournisseur()

        assert fournisseur.delai_paiement_jours == 30

    def test_delai_paiement_jours_personnalise(self):
        """Test: delai_paiement_jours peut etre personnalise."""
        fournisseur = self._make_fournisseur(delai_paiement_jours=45)

        assert fournisseur.delai_paiement_jours == 45

    def test_to_dict_inclut_champs_pennylane(self):
        """Test: to_dict inclut les champs Pennylane."""
        fournisseur = self._make_fournisseur(
            pennylane_supplier_id="pl-sup-123",
            delai_paiement_jours=45,
            iban="FR7630001007941234567890185",
            bic="BNPAFRPP",
            source_donnee="PENNYLANE",
        )
        fournisseur.marquer_sync_pennylane()

        result = fournisseur.to_dict()

        assert result["pennylane_supplier_id"] == "pl-sup-123"
        assert result["delai_paiement_jours"] == 45
        assert result["iban"] == "FR7630001007941234567890185"
        assert result["bic"] == "BNPAFRPP"
        assert result["source_donnee"] == "PENNYLANE"
        assert result["derniere_sync_pennylane"] is not None


class TestFactureClientPennylaneFields:
    """Tests pour les champs Pennylane de l'entite FactureClient (CONN-11)."""

    def _make_facture(self, **kwargs):
        """Cree une facture client avec des valeurs par defaut."""
        defaults = {
            "chantier_id": 100,
            "numero_facture": "FAC-2026-001",
            "montant_ht": Decimal("10000"),
            "montant_tva": Decimal("2000"),
            "montant_ttc": Decimal("12000"),
            "montant_net": Decimal("12000"),
        }
        defaults.update(kwargs)
        return FactureClient(**defaults)

    def test_est_encaissee_false_par_defaut(self):
        """Test: est_encaissee False par defaut."""
        facture = self._make_facture()

        assert facture.est_encaissee is False

    def test_est_encaissee_true_quand_montant_egal(self):
        """Test: est_encaissee True quand montant_encaisse >= montant_net."""
        facture = self._make_facture(
            montant_net=Decimal("12000"),
            montant_encaisse=Decimal("12000"),
        )

        assert facture.est_encaissee is True

    def test_est_encaissee_true_quand_montant_superieur(self):
        """Test: est_encaissee True quand montant_encaisse > montant_net."""
        facture = self._make_facture(
            montant_net=Decimal("12000"),
            montant_encaisse=Decimal("12500"),
        )

        assert facture.est_encaissee is True

    def test_est_encaissee_false_quand_partiel(self):
        """Test: est_encaissee False quand encaissement partiel."""
        facture = self._make_facture(
            montant_net=Decimal("12000"),
            montant_encaisse=Decimal("6000"),
        )

        assert facture.est_encaissee is False

    def test_reste_a_encaisser_complet(self):
        """Test: reste_a_encaisser retourne montant_net si rien encaisse."""
        facture = self._make_facture(
            montant_net=Decimal("12000"),
        )

        assert facture.reste_a_encaisser == Decimal("12000")

    def test_reste_a_encaisser_partiel(self):
        """Test: reste_a_encaisser calcule correctement."""
        facture = self._make_facture(
            montant_net=Decimal("12000"),
            montant_encaisse=Decimal("5000"),
        )

        assert facture.reste_a_encaisser == Decimal("7000")

    def test_reste_a_encaisser_zero(self):
        """Test: reste_a_encaisser zero quand entierement encaissee."""
        facture = self._make_facture(
            montant_net=Decimal("12000"),
            montant_encaisse=Decimal("12000"),
        )

        assert facture.reste_a_encaisser == Decimal("0")

    def test_reste_a_encaisser_jamais_negatif(self):
        """Test: reste_a_encaisser ne peut pas etre negatif."""
        facture = self._make_facture(
            montant_net=Decimal("12000"),
            montant_encaisse=Decimal("15000"),
        )

        assert facture.reste_a_encaisser == Decimal("0")

    def test_enregistrer_encaissement_success(self):
        """Test: enregistrer_encaissement met a jour les champs."""
        facture = self._make_facture(statut="envoyee")
        date_paiement = date(2026, 2, 1)

        facture.enregistrer_encaissement(
            montant=Decimal("12000"),
            date_paiement=date_paiement,
        )

        assert facture.montant_encaisse == Decimal("12000")
        assert facture.date_paiement_reel == date_paiement
        assert facture.statut == "payee"  # Auto-passage en payee

    def test_enregistrer_encaissement_partiel(self):
        """Test: encaissement partiel ne passe pas en payee."""
        facture = self._make_facture(statut="envoyee")

        facture.enregistrer_encaissement(
            montant=Decimal("6000"),
            date_paiement=date(2026, 2, 1),
        )

        assert facture.montant_encaisse == Decimal("6000")
        assert facture.statut == "envoyee"  # Reste en envoyee

    def test_enregistrer_encaissement_montant_negatif_erreur(self):
        """Test: erreur si montant negatif."""
        facture = self._make_facture(statut="envoyee")

        with pytest.raises(ValueError) as exc_info:
            facture.enregistrer_encaissement(
                montant=Decimal("-100"),
                date_paiement=date(2026, 2, 1),
            )
        assert "negatif" in str(exc_info.value)

    def test_enregistrer_encaissement_facture_annulee_erreur(self):
        """Test: erreur si facture annulee."""
        facture = self._make_facture(statut="annulee")

        with pytest.raises(ValueError) as exc_info:
            facture.enregistrer_encaissement(
                montant=Decimal("12000"),
                date_paiement=date(2026, 2, 1),
            )
        assert "annulee" in str(exc_info.value)

    def test_pennylane_invoice_id_initial_none(self):
        """Test: pennylane_invoice_id initialement None."""
        facture = self._make_facture()

        assert facture.pennylane_invoice_id is None

    def test_pennylane_invoice_id_set(self):
        """Test: pennylane_invoice_id peut etre defini."""
        facture = self._make_facture(pennylane_invoice_id="pl-cust-inv-123")

        assert facture.pennylane_invoice_id == "pl-cust-inv-123"

    def test_to_dict_inclut_champs_pennylane(self):
        """Test: to_dict inclut les champs Pennylane."""
        facture = self._make_facture(
            montant_encaisse=Decimal("6000"),
            date_paiement_reel=date(2026, 2, 1),
            pennylane_invoice_id="pl-cust-inv-123",
        )

        result = facture.to_dict()

        assert result["date_paiement_reel"] == "2026-02-01"
        assert result["montant_encaisse"] == "6000"
        assert result["pennylane_invoice_id"] == "pl-cust-inv-123"
        assert result["est_encaissee"] is False
        assert result["reste_a_encaisser"] == "6000"


class TestPennylaneSyncLog:
    """Tests pour l'entite PennylaneSyncLog."""

    def _make_sync_log(self, **kwargs):
        """Cree un sync log avec des valeurs par defaut."""
        defaults = {
            "sync_type": "supplier_invoices",
            "started_at": datetime(2026, 2, 1, 10, 0, 0),
        }
        defaults.update(kwargs)
        return PennylaneSyncLog(**defaults)

    def test_creation_valide(self):
        """Test: creation avec valeurs valides."""
        log = self._make_sync_log()

        assert log.sync_type == "supplier_invoices"
        assert log.status == "running"
        assert log.records_processed == 0

    def test_sync_type_supplier_invoices(self):
        """Test: sync_type supplier_invoices accepte."""
        log = self._make_sync_log(sync_type="supplier_invoices")
        assert log.sync_type == "supplier_invoices"

    def test_sync_type_customer_invoices(self):
        """Test: sync_type customer_invoices accepte."""
        log = self._make_sync_log(sync_type="customer_invoices")
        assert log.sync_type == "customer_invoices"

    def test_sync_type_suppliers(self):
        """Test: sync_type suppliers accepte."""
        log = self._make_sync_log(sync_type="suppliers")
        assert log.sync_type == "suppliers"

    def test_sync_type_invalide(self):
        """Test: erreur si sync_type invalide."""
        with pytest.raises(ValueError) as exc_info:
            self._make_sync_log(sync_type="invalid_type")
        assert "invalide" in str(exc_info.value)

    def test_marquer_complete_sans_pending(self):
        """Test: marquer_complete passe en completed si pas de pending."""
        log = self._make_sync_log()

        log.marquer_complete(
            records_processed=100,
            records_created=20,
            records_updated=70,
            records_pending=0,
        )

        assert log.status == "completed"
        assert log.records_processed == 100
        assert log.records_created == 20
        assert log.records_updated == 70
        assert log.records_pending == 0
        assert log.completed_at is not None

    def test_marquer_complete_avec_pending(self):
        """Test: marquer_complete passe en partial si pending > 0."""
        log = self._make_sync_log()

        log.marquer_complete(
            records_processed=100,
            records_created=20,
            records_updated=70,
            records_pending=10,
        )

        assert log.status == "partial"
        assert log.records_pending == 10

    def test_marquer_echec(self):
        """Test: marquer_echec passe en failed avec message."""
        log = self._make_sync_log()

        log.marquer_echec("Erreur API: Connection refused")

        assert log.status == "failed"
        assert log.error_message == "Erreur API: Connection refused"
        assert log.completed_at is not None

    def test_duree_secondes_calcul(self):
        """Test: duree_secondes calcule correctement."""
        log = self._make_sync_log(
            started_at=datetime(2026, 2, 1, 10, 0, 0)
        )
        log.completed_at = datetime(2026, 2, 1, 10, 1, 30)

        assert log.duree_secondes == 90.0

    def test_duree_secondes_none_si_en_cours(self):
        """Test: duree_secondes None si pas termine."""
        log = self._make_sync_log()

        assert log.duree_secondes is None

    def test_est_en_cours(self):
        """Test: est_en_cours True si status running."""
        log = self._make_sync_log()

        assert log.est_en_cours is True

        log.marquer_complete(records_processed=10)

        assert log.est_en_cours is False

    def test_a_echoue(self):
        """Test: a_echoue True si status failed."""
        log = self._make_sync_log()

        assert log.a_echoue is False

        log.marquer_echec("Erreur")

        assert log.a_echoue is True

    def test_to_dict(self):
        """Test: to_dict retourne les champs corrects."""
        log = self._make_sync_log()
        log.id = 1
        log.marquer_complete(
            records_processed=100,
            records_created=20,
            records_updated=70,
            records_pending=10,
        )

        result = log.to_dict()

        assert result["id"] == 1
        assert result["sync_type"] == "supplier_invoices"
        assert result["status"] == "partial"
        assert result["records_processed"] == 100
        assert result["duree_secondes"] is not None


class TestPennylaneMappingAnalytique:
    """Tests pour l'entite PennylaneMappingAnalytique (CONN-14)."""

    def test_creation_valide(self):
        """Test: creation avec valeurs valides."""
        mapping = PennylaneMappingAnalytique(
            code_analytique="MONTMELIAN",
            chantier_id=100,
        )

        assert mapping.code_analytique == "MONTMELIAN"
        assert mapping.chantier_id == 100

    def test_code_analytique_normalise_majuscules(self):
        """Test: code analytique normalise en majuscules."""
        mapping = PennylaneMappingAnalytique(
            code_analytique="montmelian",
            chantier_id=100,
        )

        assert mapping.code_analytique == "MONTMELIAN"

    def test_code_analytique_normalise_espaces(self):
        """Test: code analytique sans espaces de debut/fin."""
        mapping = PennylaneMappingAnalytique(
            code_analytique="  MONTMELIAN  ",
            chantier_id=100,
        )

        assert mapping.code_analytique == "MONTMELIAN"

    def test_code_analytique_vide_erreur(self):
        """Test: erreur si code analytique vide."""
        with pytest.raises(ValueError) as exc_info:
            PennylaneMappingAnalytique(
                code_analytique="",
                chantier_id=100,
            )
        assert "obligatoire" in str(exc_info.value)

    def test_code_analytique_espaces_seuls_erreur(self):
        """Test: erreur si code analytique uniquement espaces."""
        with pytest.raises(ValueError) as exc_info:
            PennylaneMappingAnalytique(
                code_analytique="   ",
                chantier_id=100,
            )
        assert "obligatoire" in str(exc_info.value)

    def test_chantier_id_zero_erreur(self):
        """Test: erreur si chantier_id <= 0."""
        with pytest.raises(ValueError) as exc_info:
            PennylaneMappingAnalytique(
                code_analytique="TEST",
                chantier_id=0,
            )
        assert "positif" in str(exc_info.value)

    def test_chantier_id_negatif_erreur(self):
        """Test: erreur si chantier_id negatif."""
        with pytest.raises(ValueError) as exc_info:
            PennylaneMappingAnalytique(
                code_analytique="TEST",
                chantier_id=-1,
            )
        assert "positif" in str(exc_info.value)

    def test_to_dict(self):
        """Test: to_dict retourne les champs corrects."""
        mapping = PennylaneMappingAnalytique(
            code_analytique="MONTMELIAN",
            chantier_id=100,
            created_at=datetime(2026, 2, 1, 10, 0, 0),
            created_by=5,
        )
        mapping.id = 1

        result = mapping.to_dict()

        assert result["id"] == 1
        assert result["code_analytique"] == "MONTMELIAN"
        assert result["chantier_id"] == 100
        assert result["created_at"] == "2026-02-01T10:00:00"
        assert result["created_by"] == 5


class TestPennylanePendingReconciliation:
    """Tests pour l'entite PennylanePendingReconciliation (CONN-15)."""

    def _make_pending(self, **kwargs):
        """Cree une pending reconciliation avec des valeurs par defaut."""
        defaults = {
            "pennylane_invoice_id": "pl-inv-123",
        }
        defaults.update(kwargs)
        return PennylanePendingReconciliation(**defaults)

    def test_creation_valide(self):
        """Test: creation avec valeurs valides."""
        pending = self._make_pending(
            supplier_name="Materiaux du Sud",
            amount_ht=Decimal("1500"),
            code_analytique="MONTMELIAN",
        )

        assert pending.pennylane_invoice_id == "pl-inv-123"
        assert pending.supplier_name == "Materiaux du Sud"
        assert pending.amount_ht == Decimal("1500")
        assert pending.status == "pending"

    def test_pennylane_invoice_id_vide_erreur(self):
        """Test: erreur si pennylane_invoice_id vide."""
        with pytest.raises(ValueError) as exc_info:
            self._make_pending(pennylane_invoice_id="")
        assert "obligatoire" in str(exc_info.value)

    def test_valider_match_success(self):
        """Test: valider_match met a jour le statut et l'achat."""
        pending = self._make_pending()

        pending.valider_match(resolved_by=5, achat_id=100)

        assert pending.status == "matched"
        assert pending.suggested_achat_id == 100
        assert pending.resolved_by == 5
        assert pending.resolved_at is not None

    def test_valider_match_deja_resolue_erreur(self):
        """Test: erreur si deja resolue."""
        pending = self._make_pending()
        pending.valider_match(resolved_by=5, achat_id=100)

        with pytest.raises(ValueError) as exc_info:
            pending.valider_match(resolved_by=6, achat_id=200)
        assert "matched" in str(exc_info.value)

    def test_rejeter_success(self):
        """Test: rejeter met a jour le statut."""
        pending = self._make_pending()

        pending.rejeter(resolved_by=5)

        assert pending.status == "rejected"
        assert pending.resolved_by == 5
        assert pending.resolved_at is not None

    def test_rejeter_deja_resolue_erreur(self):
        """Test: erreur si deja resolue."""
        pending = self._make_pending()
        pending.rejeter(resolved_by=5)

        with pytest.raises(ValueError) as exc_info:
            pending.rejeter(resolved_by=6)
        assert "rejected" in str(exc_info.value)

    def test_creer_achat_manuel_success(self):
        """Test: creer_achat_manuel met a jour le statut."""
        pending = self._make_pending()

        pending.creer_achat_manuel(resolved_by=5)

        assert pending.status == "manual"
        assert pending.resolved_by == 5
        assert pending.resolved_at is not None

    def test_creer_achat_manuel_deja_resolue_erreur(self):
        """Test: erreur si deja resolue."""
        pending = self._make_pending()
        pending.creer_achat_manuel(resolved_by=5)

        with pytest.raises(ValueError) as exc_info:
            pending.creer_achat_manuel(resolved_by=6)
        assert "manual" in str(exc_info.value)

    def test_est_resolue_false_pending(self):
        """Test: est_resolue False si status pending."""
        pending = self._make_pending()

        assert pending.est_resolue is False

    def test_est_resolue_true_matched(self):
        """Test: est_resolue True si status matched."""
        pending = self._make_pending()
        pending.valider_match(resolved_by=5, achat_id=100)

        assert pending.est_resolue is True

    def test_est_resolue_true_rejected(self):
        """Test: est_resolue True si status rejected."""
        pending = self._make_pending()
        pending.rejeter(resolved_by=5)

        assert pending.est_resolue is True

    def test_est_resolue_true_manual(self):
        """Test: est_resolue True si status manual."""
        pending = self._make_pending()
        pending.creer_achat_manuel(resolved_by=5)

        assert pending.est_resolue is True

    def test_ecart_match_pct_retourne_none(self):
        """Test: ecart_match_pct retourne None (calcul fait dans service)."""
        pending = self._make_pending()

        assert pending.ecart_match_pct is None

    def test_to_dict(self):
        """Test: to_dict retourne les champs corrects."""
        pending = self._make_pending(
            supplier_name="Materiaux du Sud",
            supplier_siret="12345678901234",
            amount_ht=Decimal("1500.50"),
            code_analytique="MONTMELIAN",
            invoice_date=date(2026, 2, 1),
            created_at=datetime(2026, 2, 1, 10, 0, 0),
        )
        pending.id = 1

        result = pending.to_dict()

        assert result["id"] == 1
        assert result["pennylane_invoice_id"] == "pl-inv-123"
        assert result["supplier_name"] == "Materiaux du Sud"
        assert result["supplier_siret"] == "12345678901234"
        assert result["amount_ht"] == "1500.50"
        assert result["code_analytique"] == "MONTMELIAN"
        assert result["invoice_date"] == "2026-02-01"
        assert result["status"] == "pending"
        assert result["created_at"] == "2026-02-01T10:00:00"
