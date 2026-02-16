"""Tests unitaires pour l'entite Devis.

DEV-03: Creation devis structure
DEV-06: Gestion marges et coefficients
DEV-15: Workflow statut devis
DEV-22: Retenue de garantie
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from modules.devis.domain.entities.devis import (
    Devis,
    DevisValidationError,
    TransitionStatutDevisInvalideError,
)
from modules.devis.domain.value_objects.statut_devis import StatutDevis


class TestDevisCreation:
    """Tests pour la creation d'un devis."""

    def test_create_devis_valid(self):
        """Test: creation d'un devis valide avec valeurs par defaut."""
        devis = Devis(numero="DEV-2026-001", client_nom="Greg Construction")
        assert devis.numero == "DEV-2026-001"
        assert devis.client_nom == "Greg Construction"
        assert devis.statut == StatutDevis.BROUILLON
        assert devis.montant_total_ht == Decimal("0")
        assert devis.montant_total_ttc == Decimal("0")
        assert devis.taux_marge_global == Decimal("15")
        assert devis.coefficient_frais_generaux == Decimal("19")
        assert devis.taux_tva_defaut == Decimal("20")
        assert devis.retenue_garantie_pct == Decimal("0")

    def test_create_devis_complet(self):
        """Test: creation d'un devis avec tous les champs."""
        devis = Devis(
            id=1,
            numero="DEV-2026-002",
            client_nom="Client SARL",
            client_adresse="123 Rue de la Paix, 75001 Paris",
            client_telephone="0601020304",
            client_email="contact@client.fr",
            chantier_ref="CHANTIER-001",
            objet="Renovation bureau",
            date_creation=date(2026, 1, 15),
            date_validite=date(2026, 3, 15),
            taux_marge_global=Decimal("20"),
            coefficient_frais_generaux=Decimal("10"),
            taux_tva_defaut=Decimal("20"),
            retenue_garantie_pct=Decimal("5"),
            taux_marge_moe=Decimal("25"),
            taux_marge_materiaux=Decimal("18"),
            commercial_id=5,
            created_by=1,
        )
        assert devis.id == 1
        assert devis.client_adresse == "123 Rue de la Paix, 75001 Paris"
        assert devis.objet == "Renovation bureau"
        assert devis.taux_marge_global == Decimal("20")
        assert devis.taux_marge_moe == Decimal("25")
        assert devis.retenue_garantie_pct == Decimal("5")

    def test_create_devis_numero_vide(self):
        """Test: erreur si numero vide."""
        with pytest.raises(DevisValidationError) as exc_info:
            Devis(numero="", client_nom="Client")
        assert "numero" in str(exc_info.value).lower()

    def test_create_devis_numero_espaces(self):
        """Test: erreur si numero uniquement espaces."""
        with pytest.raises(DevisValidationError):
            Devis(numero="   ", client_nom="Client")

    def test_create_devis_client_nom_vide(self):
        """Test: erreur si nom client vide."""
        with pytest.raises(DevisValidationError) as exc_info:
            Devis(numero="DEV-001", client_nom="")
        assert "client" in str(exc_info.value).lower()

    def test_create_devis_client_nom_espaces(self):
        """Test: erreur si nom client uniquement espaces."""
        with pytest.raises(DevisValidationError):
            Devis(numero="DEV-001", client_nom="   ")

    def test_create_devis_taux_marge_negatif(self):
        """Test: erreur si taux de marge global negatif."""
        with pytest.raises(DevisValidationError) as exc_info:
            Devis(
                numero="DEV-001",
                client_nom="Client",
                taux_marge_global=Decimal("-1"),
            )
        assert "marge" in str(exc_info.value).lower()

    def test_create_devis_coefficient_frais_negatif(self):
        """Test: erreur si coefficient frais generaux negatif."""
        with pytest.raises(DevisValidationError) as exc_info:
            Devis(
                numero="DEV-001",
                client_nom="Client",
                coefficient_frais_generaux=Decimal("-1"),
            )
        assert "frais" in str(exc_info.value).lower()

    def test_create_devis_tva_negative(self):
        """Test: erreur si TVA negative."""
        with pytest.raises(DevisValidationError):
            Devis(
                numero="DEV-001",
                client_nom="Client",
                taux_tva_defaut=Decimal("-1"),
            )

    def test_create_devis_tva_superieure_100(self):
        """Test: erreur si TVA superieure a 100%."""
        with pytest.raises(DevisValidationError):
            Devis(
                numero="DEV-001",
                client_nom="Client",
                taux_tva_defaut=Decimal("101"),
            )

    def test_create_devis_retenue_garantie_negative(self):
        """Test: erreur si retenue de garantie negative."""
        with pytest.raises(DevisValidationError):
            Devis(
                numero="DEV-001",
                client_nom="Client",
                retenue_garantie_pct=Decimal("-1"),
            )

    def test_create_devis_retenue_garantie_superieure_100(self):
        """Test: erreur si retenue de garantie superieure a 100%."""
        with pytest.raises(DevisValidationError):
            Devis(
                numero="DEV-001",
                client_nom="Client",
                retenue_garantie_pct=Decimal("101"),
            )

    def test_create_devis_date_validite_anterieure(self):
        """Test: erreur si date de validite anterieure a date de creation."""
        with pytest.raises(DevisValidationError) as exc_info:
            Devis(
                numero="DEV-001",
                client_nom="Client",
                date_creation=date(2026, 3, 1),
                date_validite=date(2026, 1, 1),
            )
        assert "validite" in str(exc_info.value).lower()

    def test_create_devis_date_validite_egale_creation(self):
        """Test: date validite egale a creation est acceptee."""
        devis = Devis(
            numero="DEV-001",
            client_nom="Client",
            date_creation=date(2026, 3, 1),
            date_validite=date(2026, 3, 1),
        )
        assert devis.date_validite == devis.date_creation

    def test_create_devis_taux_marge_zero(self):
        """Test: taux de marge a zero est accepte."""
        devis = Devis(
            numero="DEV-001",
            client_nom="Client",
            taux_marge_global=Decimal("0"),
        )
        assert devis.taux_marge_global == Decimal("0")


class TestDevisProprietes:
    """Tests pour les proprietes calculees du devis."""

    def _make_devis(self, **kwargs):
        """Cree un devis valide avec valeurs par defaut."""
        defaults = {
            "numero": "DEV-2026-001",
            "client_nom": "Greg Construction",
        }
        defaults.update(kwargs)
        return Devis(**defaults)

    def test_est_modifiable_brouillon(self):
        """Test: un devis en brouillon est modifiable."""
        devis = self._make_devis()
        assert devis.est_modifiable is True

    def test_est_modifiable_en_validation(self):
        """Test: un devis en validation n'est pas modifiable."""
        devis = self._make_devis(statut=StatutDevis.EN_VALIDATION)
        assert devis.est_modifiable is False

    def test_est_modifiable_envoye(self):
        """Test: un devis envoye n'est pas modifiable."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        assert devis.est_modifiable is False

    def test_est_supprime_non(self):
        """Test: un devis non supprime."""
        devis = self._make_devis()
        assert devis.est_supprime is False

    def test_est_supprime_oui(self):
        """Test: un devis supprime (soft delete)."""
        devis = self._make_devis(deleted_at=datetime.utcnow())
        assert devis.est_supprime is True

    def test_est_expire_sans_date(self):
        """Test: un devis sans date de validite n'est pas expire."""
        devis = self._make_devis(date_validite=None)
        assert devis.est_expire is False

    def test_est_expire_date_future(self):
        """Test: un devis avec date future n'est pas expire."""
        devis = self._make_devis(date_validite=date(2099, 12, 31))
        assert devis.est_expire is False

    def test_est_expire_date_passee(self):
        """Test: un devis avec date passee est expire."""
        devis = self._make_devis(date_validite=date(2020, 1, 1))
        assert devis.est_expire is True


class TestDevisWorkflow:
    """Tests pour les transitions de statut du devis."""

    def _make_devis(self, **kwargs):
        """Cree un devis valide avec valeurs par defaut."""
        defaults = {
            "numero": "DEV-2026-001",
            "client_nom": "Greg Construction",
        }
        defaults.update(kwargs)
        return Devis(**defaults)

    def test_soumettre_validation_depuis_brouillon(self):
        """Test: soumettre un brouillon en validation."""
        devis = self._make_devis()
        devis.soumettre_validation()
        assert devis.statut == StatutDevis.EN_VALIDATION
        assert devis.updated_at is not None

    def test_soumettre_validation_depuis_envoye_interdit(self):
        """Test: soumettre un devis envoye est interdit."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        with pytest.raises(TransitionStatutDevisInvalideError):
            devis.soumettre_validation()

    def test_retourner_brouillon_depuis_en_validation(self):
        """Test: retourner un devis en brouillon depuis en_validation."""
        devis = self._make_devis(statut=StatutDevis.EN_VALIDATION)
        devis.retourner_brouillon()
        assert devis.statut == StatutDevis.BROUILLON

    def test_retourner_brouillon_depuis_envoye_interdit(self):
        """Test: retourner en brouillon depuis envoye est interdit."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        with pytest.raises(TransitionStatutDevisInvalideError):
            devis.retourner_brouillon()

    def test_envoyer_depuis_en_validation(self):
        """Test: envoyer un devis depuis en_validation."""
        devis = self._make_devis(statut=StatutDevis.EN_VALIDATION)
        devis.envoyer()
        assert devis.statut == StatutDevis.ENVOYE

    def test_envoyer_depuis_brouillon_interdit(self):
        """Test: envoyer un devis depuis brouillon est interdit."""
        devis = self._make_devis()
        with pytest.raises(TransitionStatutDevisInvalideError):
            devis.envoyer()

    def test_marquer_vu_depuis_envoye(self):
        """Test: marquer comme vu depuis envoye."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        devis.marquer_vu()
        assert devis.statut == StatutDevis.VU

    def test_marquer_vu_depuis_brouillon_interdit(self):
        """Test: marquer comme vu depuis brouillon est interdit."""
        devis = self._make_devis()
        with pytest.raises(TransitionStatutDevisInvalideError):
            devis.marquer_vu()

    def test_passer_en_negociation_depuis_envoye(self):
        """Test: passer en negociation depuis envoye."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        devis.passer_en_negociation()
        assert devis.statut == StatutDevis.EN_NEGOCIATION

    def test_passer_en_negociation_depuis_vu(self):
        """Test: passer en negociation depuis vu."""
        devis = self._make_devis(statut=StatutDevis.VU)
        devis.passer_en_negociation()
        assert devis.statut == StatutDevis.EN_NEGOCIATION

    def test_passer_en_negociation_depuis_expire(self):
        """Test: passer en negociation depuis expire."""
        devis = self._make_devis(statut=StatutDevis.EXPIRE)
        devis.passer_en_negociation()
        assert devis.statut == StatutDevis.EN_NEGOCIATION

    def test_accepter_depuis_envoye(self):
        """Test: accepter un devis depuis envoye."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        devis.accepter()
        assert devis.statut == StatutDevis.ACCEPTE

    def test_accepter_depuis_vu(self):
        """Test: accepter un devis depuis vu."""
        devis = self._make_devis(statut=StatutDevis.VU)
        devis.accepter()
        assert devis.statut == StatutDevis.ACCEPTE

    def test_accepter_depuis_en_negociation(self):
        """Test: accepter un devis depuis en_negociation."""
        devis = self._make_devis(statut=StatutDevis.EN_NEGOCIATION)
        devis.accepter()
        assert devis.statut == StatutDevis.ACCEPTE

    def test_accepter_depuis_brouillon_interdit(self):
        """Test: accepter un devis depuis brouillon est interdit."""
        devis = self._make_devis()
        with pytest.raises(TransitionStatutDevisInvalideError):
            devis.accepter()

    def test_refuser_depuis_envoye(self):
        """Test: refuser un devis depuis envoye."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        devis.refuser()
        assert devis.statut == StatutDevis.REFUSE

    def test_refuser_depuis_en_negociation(self):
        """Test: refuser un devis depuis en_negociation."""
        devis = self._make_devis(statut=StatutDevis.EN_NEGOCIATION)
        devis.refuser()
        assert devis.statut == StatutDevis.REFUSE

    def test_refuser_depuis_brouillon_interdit(self):
        """Test: refuser un devis depuis brouillon est interdit."""
        devis = self._make_devis()
        with pytest.raises(TransitionStatutDevisInvalideError):
            devis.refuser()

    def test_marquer_perdu_depuis_en_negociation(self):
        """Test: marquer perdu depuis en_negociation."""
        devis = self._make_devis(statut=StatutDevis.EN_NEGOCIATION)
        devis.marquer_perdu()
        assert devis.statut == StatutDevis.PERDU

    def test_marquer_perdu_depuis_envoye_interdit(self):
        """Test: marquer perdu depuis envoye est interdit."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        with pytest.raises(TransitionStatutDevisInvalideError):
            devis.marquer_perdu()

    def test_marquer_expire_depuis_envoye(self):
        """Test: marquer expire depuis envoye."""
        devis = self._make_devis(statut=StatutDevis.ENVOYE)
        devis.marquer_expire()
        assert devis.statut == StatutDevis.EXPIRE

    def test_marquer_expire_depuis_vu(self):
        """Test: marquer expire depuis vu."""
        devis = self._make_devis(statut=StatutDevis.VU)
        devis.marquer_expire()
        assert devis.statut == StatutDevis.EXPIRE

    def test_workflow_complet_brouillon_a_accepte(self):
        """Test: workflow complet brouillon -> en_validation -> envoye -> vu -> accepte."""
        devis = self._make_devis()
        assert devis.statut == StatutDevis.BROUILLON

        devis.soumettre_validation()
        assert devis.statut == StatutDevis.EN_VALIDATION

        devis.envoyer()
        assert devis.statut == StatutDevis.ENVOYE

        devis.marquer_vu()
        assert devis.statut == StatutDevis.VU

        devis.accepter()
        assert devis.statut == StatutDevis.ACCEPTE

    def test_workflow_avec_negociation(self):
        """Test: workflow avec negociation avant acceptation."""
        devis = self._make_devis()
        devis.soumettre_validation()
        devis.envoyer()
        devis.passer_en_negociation()
        assert devis.statut == StatutDevis.EN_NEGOCIATION

        devis.accepter()
        assert devis.statut == StatutDevis.ACCEPTE

    def test_transition_invalide_contient_statuts(self):
        """Test: l'erreur de transition contient les statuts."""
        devis = self._make_devis()
        with pytest.raises(TransitionStatutDevisInvalideError) as exc_info:
            devis.accepter()
        assert exc_info.value.statut_actuel == StatutDevis.BROUILLON
        assert exc_info.value.statut_cible == StatutDevis.ACCEPTE


class TestDevisSoftDelete:
    """Tests pour le soft delete."""

    def test_supprimer(self):
        """Test: suppression en soft delete."""
        devis = Devis(numero="DEV-001", client_nom="Client")
        assert devis.est_supprime is False
        devis.supprimer(deleted_by=1)
        assert devis.est_supprime is True
        assert devis.deleted_at is not None
        assert devis.deleted_by == 1


class TestDevisToDict:
    """Tests pour la conversion en dictionnaire."""

    def test_to_dict_basic(self):
        """Test: conversion en dictionnaire."""
        devis = Devis(
            id=1,
            numero="DEV-2026-001",
            client_nom="Greg Construction",
            objet="Renovation",
        )
        d = devis.to_dict()
        assert d["id"] == 1
        assert d["numero"] == "DEV-2026-001"
        assert d["client_nom"] == "Greg Construction"
        assert d["statut"] == "brouillon"
        assert d["montant_total_ht"] == "0"
        assert d["montant_total_ttc"] == "0"
        assert d["taux_marge_global"] == "15"

    def test_to_dict_optional_fields(self):
        """Test: champs optionnels dans to_dict."""
        devis = Devis(
            id=1,
            numero="DEV-001",
            client_nom="Client",
            taux_marge_moe=Decimal("25"),
        )
        d = devis.to_dict()
        assert d["taux_marge_moe"] == "25"
        assert d["taux_marge_materiaux"] is None
