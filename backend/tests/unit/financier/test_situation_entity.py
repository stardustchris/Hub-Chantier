"""Tests unitaires pour les entites SituationTravaux et LigneSituation du module Financier."""

import pytest
from datetime import date, datetime
from decimal import Decimal

from modules.financier.domain.entities import SituationTravaux, LigneSituation


# ============================================================
# Tests SituationTravaux
# ============================================================

class TestSituationTravaux:
    """Tests pour l'entite SituationTravaux."""

    def _make_situation(self, **kwargs):
        """Cree une situation valide avec valeurs par defaut."""
        defaults = {
            "chantier_id": 1,
            "budget_id": 10,
            "numero": "SIT-2026-01",
            "periode_debut": date(2026, 1, 1),
            "periode_fin": date(2026, 1, 31),
            "montant_cumule_ht": Decimal("100000"),
            "retenue_garantie_pct": Decimal("5.00"),
            "taux_tva": Decimal("20.00"),
        }
        defaults.update(kwargs)
        return SituationTravaux(**defaults)

    # -- Creation valide -------------------------------------------------------

    def test_create_situation_valid(self):
        """Test: creation d'une situation valide."""
        situation = self._make_situation(id=1)
        assert situation.id == 1
        assert situation.chantier_id == 1
        assert situation.budget_id == 10
        assert situation.numero == "SIT-2026-01"
        assert situation.statut == "brouillon"
        assert situation.retenue_garantie_pct == Decimal("5.00")
        assert situation.taux_tva == Decimal("20.00")

    def test_create_situation_sans_periodes(self):
        """Test: creation sans periodes est accepte."""
        situation = self._make_situation(
            periode_debut=None,
            periode_fin=None,
        )
        assert situation.periode_debut is None
        assert situation.periode_fin is None

    # -- __post_init__ validation -----------------------------------------------

    def test_create_situation_chantier_id_zero(self):
        """Test: erreur si chantier_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_situation(chantier_id=0)
        assert "chantier" in str(exc_info.value).lower()

    def test_create_situation_chantier_id_negatif(self):
        """Test: erreur si chantier_id est negatif."""
        with pytest.raises(ValueError):
            self._make_situation(chantier_id=-1)

    def test_create_situation_budget_id_zero(self):
        """Test: erreur si budget_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_situation(budget_id=0)
        assert "budget" in str(exc_info.value).lower()

    def test_create_situation_budget_id_negatif(self):
        """Test: erreur si budget_id est negatif."""
        with pytest.raises(ValueError):
            self._make_situation(budget_id=-1)

    def test_create_situation_numero_vide(self):
        """Test: erreur si numero vide."""
        with pytest.raises(ValueError) as exc_info:
            self._make_situation(numero="")
        assert "numero" in str(exc_info.value).lower()

    def test_create_situation_numero_espaces(self):
        """Test: erreur si numero uniquement espaces."""
        with pytest.raises(ValueError):
            self._make_situation(numero="   ")

    def test_create_situation_periode_fin_avant_debut(self):
        """Test: erreur si periode_fin < periode_debut."""
        with pytest.raises(ValueError) as exc_info:
            self._make_situation(
                periode_debut=date(2026, 2, 1),
                periode_fin=date(2026, 1, 15),
            )
        assert "date" in str(exc_info.value).lower() or "periode" in str(exc_info.value).lower()

    def test_create_situation_periode_debut_egal_fin(self):
        """Test: periode_debut == periode_fin est accepte."""
        situation = self._make_situation(
            periode_debut=date(2026, 1, 15),
            periode_fin=date(2026, 1, 15),
        )
        assert situation.periode_debut == situation.periode_fin

    # -- Workflow: soumettre_validation -----------------------------------------------

    def test_soumettre_validation_success(self):
        """Test: soumission d'un brouillon pour validation."""
        situation = self._make_situation()
        situation.soumettre_validation()
        assert situation.statut == "en_validation"
        assert situation.updated_at is not None

    def test_soumettre_validation_depuis_en_validation(self):
        """Test: erreur si deja en_validation."""
        situation = self._make_situation()
        situation.soumettre_validation()
        with pytest.raises(ValueError):
            situation.soumettre_validation()

    def test_soumettre_validation_depuis_emise(self):
        """Test: erreur si situation emise."""
        situation = self._make_situation()
        situation.soumettre_validation()
        situation.valider(validated_by=5)
        with pytest.raises(ValueError):
            situation.soumettre_validation()

    # -- Workflow: valider -------------------------------------------------------

    def test_valider_success(self):
        """Test: validation d'une situation en_validation."""
        situation = self._make_situation()
        situation.soumettre_validation()
        situation.valider(validated_by=5)
        assert situation.statut == "emise"
        assert situation.validated_by == 5
        assert situation.validated_at is not None
        assert situation.emise_at is not None
        assert situation.updated_at is not None

    def test_valider_depuis_brouillon(self):
        """Test: erreur si validation d'un brouillon."""
        situation = self._make_situation()
        with pytest.raises(ValueError):
            situation.valider(validated_by=5)

    def test_valider_depuis_emise(self):
        """Test: erreur si validation d'une situation emise."""
        situation = self._make_situation()
        situation.soumettre_validation()
        situation.valider(validated_by=5)
        with pytest.raises(ValueError):
            situation.valider(validated_by=10)

    # -- Workflow: marquer_validee_client -----------------------------------------------

    def test_marquer_validee_client_success(self):
        """Test: validation client d'une situation emise."""
        situation = self._make_situation()
        situation.soumettre_validation()
        situation.valider(validated_by=5)
        situation.marquer_validee_client()
        assert situation.statut == "validee"
        assert situation.updated_at is not None

    def test_marquer_validee_client_depuis_brouillon(self):
        """Test: erreur si validation client d'un brouillon."""
        situation = self._make_situation()
        with pytest.raises(ValueError):
            situation.marquer_validee_client()

    def test_marquer_validee_client_depuis_en_validation(self):
        """Test: erreur si validation client depuis en_validation."""
        situation = self._make_situation()
        situation.soumettre_validation()
        with pytest.raises(ValueError):
            situation.marquer_validee_client()

    # -- Workflow: marquer_facturee -----------------------------------------------

    def test_marquer_facturee_success(self):
        """Test: facturation d'une situation validee."""
        situation = self._make_situation()
        situation.soumettre_validation()
        situation.valider(validated_by=5)
        situation.marquer_validee_client()
        situation.marquer_facturee()
        assert situation.statut == "facturee"
        assert situation.facturee_at is not None
        assert situation.updated_at is not None

    def test_marquer_facturee_avec_date_specifique(self):
        """Test: facturation avec date specifique."""
        situation = self._make_situation()
        situation.soumettre_validation()
        situation.valider(validated_by=5)
        situation.marquer_validee_client()
        specific_dt = datetime(2026, 2, 15, 10, 30)
        situation.marquer_facturee(facturee_at=specific_dt)
        assert situation.facturee_at == specific_dt

    def test_marquer_facturee_depuis_emise(self):
        """Test: erreur si facturation d'une situation emise (non validee client)."""
        situation = self._make_situation()
        situation.soumettre_validation()
        situation.valider(validated_by=5)
        with pytest.raises(ValueError):
            situation.marquer_facturee()

    def test_marquer_facturee_depuis_brouillon(self):
        """Test: erreur si facturation d'un brouillon."""
        situation = self._make_situation()
        with pytest.raises(ValueError):
            situation.marquer_facturee()

    # -- Workflow complet -------------------------------------------------------

    def test_workflow_complet(self):
        """Test: workflow complet brouillon -> en_validation -> emise -> validee -> facturee."""
        situation = self._make_situation()
        assert situation.statut == "brouillon"

        situation.soumettre_validation()
        assert situation.statut == "en_validation"

        situation.valider(validated_by=5)
        assert situation.statut == "emise"

        situation.marquer_validee_client()
        assert situation.statut == "validee"

        situation.marquer_facturee()
        assert situation.statut == "facturee"

    # -- Properties calculees -------------------------------------------------------

    def test_montant_retenue_garantie(self):
        """Test: montant de la retenue de garantie."""
        situation = self._make_situation(
            montant_cumule_ht=Decimal("100000"),
            retenue_garantie_pct=Decimal("5.00"),
        )
        # 100000 * 5 / 100 = 5000
        assert situation.montant_retenue_garantie == Decimal("5000.00")

    def test_montant_tva(self):
        """Test: montant de la TVA."""
        situation = self._make_situation(
            montant_cumule_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
        )
        # 100000 * 20 / 100 = 20000
        assert situation.montant_tva == Decimal("20000.00")

    def test_montant_ttc(self):
        """Test: montant TTC = HT + TVA."""
        situation = self._make_situation(
            montant_cumule_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
        )
        # 100000 + 20000 = 120000
        assert situation.montant_ttc == Decimal("120000.00")

    def test_montant_net(self):
        """Test: montant net = TTC - retenue garantie."""
        situation = self._make_situation(
            montant_cumule_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
            retenue_garantie_pct=Decimal("5.00"),
        )
        # TTC = 120000, retenue = 5000, net = 115000
        assert situation.montant_net == Decimal("115000.00")

    def test_montant_net_sans_retenue(self):
        """Test: montant net = TTC si retenue de garantie a 0%."""
        situation = self._make_situation(
            montant_cumule_ht=Decimal("100000"),
            taux_tva=Decimal("20.00"),
            retenue_garantie_pct=Decimal("0"),
        )
        assert situation.montant_net == Decimal("120000.00")

    # -- est_supprime -------------------------------------------------------

    def test_est_supprime_false(self):
        """Test: est_supprime est False par defaut."""
        situation = self._make_situation()
        assert situation.est_supprime is False

    def test_est_supprime_true(self):
        """Test: est_supprime est True si deleted_at defini."""
        situation = self._make_situation(
            deleted_at=datetime.utcnow(),
            deleted_by=1,
        )
        assert situation.est_supprime is True

    # -- to_dict -------------------------------------------------------

    def test_to_dict_structure(self):
        """Test: to_dict retourne la structure correcte."""
        now = datetime.utcnow()
        situation = self._make_situation(
            id=1,
            notes="Note de test",
            created_by=5,
            created_at=now,
        )
        d = situation.to_dict()
        assert d["id"] == 1
        assert d["chantier_id"] == 1
        assert d["budget_id"] == 10
        assert d["numero"] == "SIT-2026-01"
        assert d["statut"] == "brouillon"
        assert d["notes"] == "Note de test"
        assert d["created_by"] == 5
        assert d["montant_cumule_ht"] == "100000"
        assert d["retenue_garantie_pct"] == "5.00"
        assert d["taux_tva"] == "20.00"
        assert "montant_retenue_garantie" in d
        assert "montant_tva" in d
        assert "montant_ttc" in d
        assert "montant_net" in d


# ============================================================
# Tests LigneSituation
# ============================================================

class TestLigneSituation:
    """Tests pour l'entite LigneSituation."""

    def _make_ligne(self, **kwargs):
        """Cree une ligne de situation valide avec valeurs par defaut."""
        defaults = {
            "situation_id": 1,
            "lot_budgetaire_id": 10,
            "pourcentage_avancement": Decimal("50"),
            "montant_marche_ht": Decimal("100000"),
            "montant_cumule_precedent_ht": Decimal("0"),
        }
        defaults.update(kwargs)
        return LigneSituation(**defaults)

    # -- Creation valide -------------------------------------------------------

    def test_create_ligne_valid(self):
        """Test: creation d'une ligne valide."""
        ligne = self._make_ligne(id=1)
        assert ligne.id == 1
        assert ligne.situation_id == 1
        assert ligne.lot_budgetaire_id == 10
        assert ligne.pourcentage_avancement == Decimal("50")
        assert ligne.montant_marche_ht == Decimal("100000")

    def test_create_ligne_avancement_zero(self):
        """Test: avancement a 0% est valide."""
        ligne = self._make_ligne(pourcentage_avancement=Decimal("0"))
        assert ligne.pourcentage_avancement == Decimal("0")

    def test_create_ligne_avancement_cent(self):
        """Test: avancement a 100% est valide."""
        ligne = self._make_ligne(pourcentage_avancement=Decimal("100"))
        assert ligne.pourcentage_avancement == Decimal("100")

    # -- __post_init__ validation -----------------------------------------------

    def test_create_ligne_situation_id_zero(self):
        """Test: erreur si situation_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_ligne(situation_id=0)
        assert "situation" in str(exc_info.value).lower()

    def test_create_ligne_situation_id_negatif(self):
        """Test: erreur si situation_id est negatif."""
        with pytest.raises(ValueError):
            self._make_ligne(situation_id=-1)

    def test_create_ligne_lot_id_zero(self):
        """Test: erreur si lot_budgetaire_id est 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_ligne(lot_budgetaire_id=0)
        assert "lot" in str(exc_info.value).lower()

    def test_create_ligne_lot_id_negatif(self):
        """Test: erreur si lot_budgetaire_id est negatif."""
        with pytest.raises(ValueError):
            self._make_ligne(lot_budgetaire_id=-1)

    def test_create_ligne_avancement_negatif(self):
        """Test: erreur si pourcentage_avancement < 0."""
        with pytest.raises(ValueError) as exc_info:
            self._make_ligne(pourcentage_avancement=Decimal("-1"))
        assert "avancement" in str(exc_info.value).lower()

    def test_create_ligne_avancement_superieur_100(self):
        """Test: erreur si pourcentage_avancement > 100."""
        with pytest.raises(ValueError) as exc_info:
            self._make_ligne(pourcentage_avancement=Decimal("101"))
        assert "avancement" in str(exc_info.value).lower()

    # -- calculer_montants -------------------------------------------------------

    def test_calculer_montants(self):
        """Test: calcul des montants a partir du pourcentage."""
        ligne = self._make_ligne(
            pourcentage_avancement=Decimal("60"),
            montant_marche_ht=Decimal("100000"),
            montant_cumule_precedent_ht=Decimal("30000"),
        )
        ligne.calculer_montants()
        # cumule = 100000 * 60 / 100 = 60000
        assert ligne.montant_cumule_ht == Decimal("60000")
        # periode = 60000 - 30000 = 30000
        assert ligne.montant_periode_ht == Decimal("30000")

    def test_calculer_montants_sans_precedent(self):
        """Test: calcul sans montant cumule precedent."""
        ligne = self._make_ligne(
            pourcentage_avancement=Decimal("40"),
            montant_marche_ht=Decimal("50000"),
            montant_cumule_precedent_ht=Decimal("0"),
        )
        ligne.calculer_montants()
        assert ligne.montant_cumule_ht == Decimal("20000")
        assert ligne.montant_periode_ht == Decimal("20000")

    def test_calculer_montants_avancement_100(self):
        """Test: calcul a 100% d'avancement."""
        ligne = self._make_ligne(
            pourcentage_avancement=Decimal("100"),
            montant_marche_ht=Decimal("75000"),
            montant_cumule_precedent_ht=Decimal("50000"),
        )
        ligne.calculer_montants()
        assert ligne.montant_cumule_ht == Decimal("75000")
        assert ligne.montant_periode_ht == Decimal("25000")

    def test_calculer_montants_avancement_zero(self):
        """Test: calcul a 0% d'avancement."""
        ligne = self._make_ligne(
            pourcentage_avancement=Decimal("0"),
            montant_marche_ht=Decimal("50000"),
            montant_cumule_precedent_ht=Decimal("0"),
        )
        ligne.calculer_montants()
        assert ligne.montant_cumule_ht == Decimal("0")
        assert ligne.montant_periode_ht == Decimal("0")

    # -- to_dict -------------------------------------------------------

    def test_to_dict_structure(self):
        """Test: to_dict retourne la structure correcte."""
        ligne = self._make_ligne(id=1)
        ligne.calculer_montants()
        d = ligne.to_dict()
        assert d["id"] == 1
        assert d["situation_id"] == 1
        assert d["lot_budgetaire_id"] == 10
        assert d["pourcentage_avancement"] == "50"
        assert d["montant_marche_ht"] == "100000"
        assert "montant_cumule_precedent_ht" in d
        assert "montant_periode_ht" in d
        assert "montant_cumule_ht" in d
