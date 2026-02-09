"""Tests unitaires pour l'entite FactureClient du module Financier."""

import pytest
from datetime import date, datetime
from decimal import Decimal

from modules.financier.domain.entities import FactureClient


class TestFactureClient:
    """Tests pour l'entite FactureClient."""

    def _make_facture(self, **kwargs):
        """Cree une facture valide avec valeurs par defaut."""
        defaults = {
            "chantier_id": 1,
            "numero_facture": "FAC-2026-01",
            "type_facture": "situation",
            "montant_ht": Decimal("100000"),
            "taux_tva": Decimal("20.00"),
            "montant_tva": Decimal("20000"),
            "montant_ttc": Decimal("120000"),
            "retenue_garantie_montant": Decimal("6000"),
            "montant_net": Decimal("114000"),
        }
        defaults.update(kwargs)
        return FactureClient(**defaults)

    # -- Creation valide -------------------------------------------------------

    def test_create_facture_valid(self):
        """Test: creation d'une facture valide."""
        facture = self._make_facture(id=1, situation_id=5)
        assert facture.id == 1
        assert facture.chantier_id == 1
        assert facture.situation_id == 5
        assert facture.numero_facture == "FAC-2026-01"
        assert facture.type_facture == "situation"
        assert facture.montant_ht == Decimal("100000")
        assert facture.statut == "brouillon"

    def test_create_facture_acompte(self):
        """Test: creation d'une facture d'acompte."""
        facture = self._make_facture(
            type_facture="acompte",
            situation_id=None,
        )
        assert facture.type_facture == "acompte"
        assert facture.situation_id is None

    # -- __post_init__ validation -----------------------------------------------

    def test_create_facture_chantier_id_zero(self):
        """Test: erreur si chantier_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_facture(chantier_id=0)
        assert "chantier" in str(exc_info.value).lower()

    def test_create_facture_chantier_id_negatif(self):
        """Test: erreur si chantier_id est negatif."""
        with pytest.raises(ValueError):
            self._make_facture(chantier_id=-1)

    def test_create_facture_montant_ht_negatif(self):
        """Test: erreur si montant_ht est negatif."""
        with pytest.raises(ValueError) as exc_info:
            self._make_facture(montant_ht=Decimal("-1"))
        assert "montant" in str(exc_info.value).lower()

    def test_create_facture_montant_ht_zero(self):
        """Test: montant HT a zero est accepte."""
        facture = self._make_facture(montant_ht=Decimal("0"))
        assert facture.montant_ht == Decimal("0")

    # -- Workflow: emettre -------------------------------------------------------

    def test_emettre_success(self):
        """Test: emission d'une facture brouillon."""
        facture = self._make_facture()
        facture.emettre()
        assert facture.statut == "emise"
        assert facture.date_emission == date.today()
        assert facture.updated_at is not None

    def test_emettre_depuis_emise(self):
        """Test: erreur si emission d'une facture deja emise."""
        facture = self._make_facture()
        facture.emettre()
        with pytest.raises(ValueError):
            facture.emettre()

    def test_emettre_depuis_envoyee(self):
        """Test: erreur si emission d'une facture envoyee."""
        facture = self._make_facture()
        facture.emettre()
        facture.envoyer()
        with pytest.raises(ValueError):
            facture.emettre()

    # -- Workflow: envoyer -------------------------------------------------------

    def test_envoyer_success(self):
        """Test: envoi d'une facture emise."""
        facture = self._make_facture()
        facture.emettre()
        facture.envoyer()
        assert facture.statut == "envoyee"
        assert facture.updated_at is not None

    def test_envoyer_depuis_brouillon(self):
        """Test: erreur si envoi d'un brouillon."""
        facture = self._make_facture()
        with pytest.raises(ValueError):
            facture.envoyer()

    def test_envoyer_depuis_envoyee(self):
        """Test: erreur si envoi d'une facture deja envoyee."""
        facture = self._make_facture()
        facture.emettre()
        facture.envoyer()
        with pytest.raises(ValueError):
            facture.envoyer()

    # -- Workflow: marquer_payee -------------------------------------------------------

    def test_marquer_payee_success(self):
        """Test: paiement d'une facture envoyee."""
        facture = self._make_facture()
        facture.emettre()
        facture.envoyer()
        facture.marquer_payee()
        assert facture.statut == "payee"
        assert facture.updated_at is not None

    def test_marquer_payee_depuis_brouillon(self):
        """Test: erreur si paiement d'un brouillon."""
        facture = self._make_facture()
        with pytest.raises(ValueError):
            facture.marquer_payee()

    def test_marquer_payee_depuis_emise(self):
        """Test: erreur si paiement d'une facture emise (non envoyee)."""
        facture = self._make_facture()
        facture.emettre()
        with pytest.raises(ValueError):
            facture.marquer_payee()

    # -- Workflow: annuler -------------------------------------------------------

    def test_annuler_depuis_brouillon(self):
        """Test: annulation d'un brouillon."""
        facture = self._make_facture()
        facture.annuler()
        assert facture.statut == "annulee"
        assert facture.updated_at is not None

    def test_annuler_depuis_emise(self):
        """Test: annulation d'une facture emise."""
        facture = self._make_facture()
        facture.emettre()
        facture.annuler()
        assert facture.statut == "annulee"

    def test_annuler_depuis_envoyee(self):
        """Test: erreur si annulation d'une facture envoyee."""
        facture = self._make_facture()
        facture.emettre()
        facture.envoyer()
        with pytest.raises(ValueError):
            facture.annuler()

    def test_annuler_depuis_payee(self):
        """Test: erreur si annulation d'une facture payee."""
        facture = self._make_facture()
        facture.emettre()
        facture.envoyer()
        facture.marquer_payee()
        with pytest.raises(ValueError):
            facture.annuler()

    # -- Workflow complet -------------------------------------------------------

    def test_workflow_complet(self):
        """Test: workflow complet brouillon -> emise -> envoyee -> payee."""
        facture = self._make_facture()
        assert facture.statut == "brouillon"

        facture.emettre()
        assert facture.statut == "emise"

        facture.envoyer()
        assert facture.statut == "envoyee"

        facture.marquer_payee()
        assert facture.statut == "payee"

    # -- calculer_montants (static) -------------------------------------------------------

    def test_calculer_montants_static(self):
        """Test: calcul statique des montants (loi 71-584: retenue sur HT)."""
        montant_tva, montant_ttc, retenue, montant_net = FactureClient.calculer_montants(
            montant_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
            retenue_garantie_pct=Decimal("5.00"),
        )
        assert montant_tva == Decimal("20000.00")
        assert montant_ttc == Decimal("120000.00")
        # Loi 71-584: retenue sur HT = 100000 * 5 / 100 = 5000
        assert retenue == Decimal("5000.00")
        # net = 120000 - 5000 = 115000
        assert montant_net == Decimal("115000.00")

    def test_calculer_montants_static_sans_retenue(self):
        """Test: calcul statique sans retenue de garantie."""
        montant_tva, montant_ttc, retenue, montant_net = FactureClient.calculer_montants(
            montant_ht=Decimal("50000"),
            taux_tva=Decimal("20.00"),
            retenue_garantie_pct=Decimal("0"),
        )
        assert montant_tva == Decimal("10000.00")
        assert montant_ttc == Decimal("60000.00")
        assert retenue == Decimal("0")
        assert montant_net == Decimal("60000.00")

    def test_calculer_montants_static_tva_zero(self):
        """Test: calcul statique avec TVA a 0%."""
        montant_tva, montant_ttc, retenue, montant_net = FactureClient.calculer_montants(
            montant_ht=Decimal("50000"),
            taux_tva=Decimal("0"),
            retenue_garantie_pct=Decimal("5.00"),
        )
        assert montant_tva == Decimal("0")
        assert montant_ttc == Decimal("50000")
        assert retenue == Decimal("2500.00")
        assert montant_net == Decimal("47500.00")

    # -- Properties -------------------------------------------------------

    def test_est_supprime_false(self):
        """Test: est_supprime est False par defaut."""
        facture = self._make_facture()
        assert facture.est_supprime is False

    def test_est_supprime_true(self):
        """Test: est_supprime est True si deleted_at defini."""
        facture = self._make_facture(
            deleted_at=datetime.utcnow(),
            deleted_by=1,
        )
        assert facture.est_supprime is True

    # -- to_dict -------------------------------------------------------

    def test_to_dict_structure(self):
        """Test: to_dict retourne la structure correcte."""
        now = datetime.utcnow()
        facture = self._make_facture(
            id=1,
            notes="Note de test",
            created_by=5,
            created_at=now,
        )
        d = facture.to_dict()
        assert d["id"] == 1
        assert d["chantier_id"] == 1
        assert d["numero_facture"] == "FAC-2026-01"
        assert d["type_facture"] == "situation"
        assert d["montant_ht"] == "100000"
        assert d["statut"] == "brouillon"
        assert d["notes"] == "Note de test"
        assert d["created_by"] == 5
