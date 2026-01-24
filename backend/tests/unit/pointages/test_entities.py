"""Tests unitaires pour les Entities du module pointages."""

import pytest
from datetime import date, timedelta

from modules.pointages.domain.entities import (
    Pointage,
    VariablePaie,
    FeuilleHeures,
)
from modules.pointages.domain.value_objects import (
    StatutPointage,
    TypeVariablePaie,
    Duree,
)


class TestPointage:
    """Tests pour l'entité Pointage."""

    def test_creation_valid(self):
        """Test création avec valeurs valides."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(8, 0),
        )
        assert p.utilisateur_id == 1
        assert p.chantier_id == 10
        assert p.date_pointage == date(2026, 1, 20)
        assert p.heures_normales.heures == 8
        assert p.statut == StatutPointage.BROUILLON
        assert p.is_editable

    def test_creation_invalid_utilisateur_id(self):
        """Test création avec utilisateur_id invalide."""
        with pytest.raises(ValueError):
            Pointage(
                utilisateur_id=0,
                chantier_id=10,
                date_pointage=date.today(),
            )

    def test_creation_invalid_chantier_id(self):
        """Test création avec chantier_id invalide."""
        with pytest.raises(ValueError):
            Pointage(
                utilisateur_id=1,
                chantier_id=-1,
                date_pointage=date.today(),
            )

    def test_total_heures(self):
        """Test calcul total heures."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            heures_normales=Duree(8, 0),
            heures_supplementaires=Duree(2, 30),
        )
        assert p.total_heures.heures == 10
        assert p.total_heures.minutes == 30
        assert p.total_heures_decimal == 10.5

    def test_set_heures(self):
        """Test modification des heures."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
        )
        p.set_heures(heures_normales=Duree(7, 30))
        assert p.heures_normales.heures == 7
        assert p.heures_normales.minutes == 30

    def test_set_heures_not_editable_raises(self):
        """Test modification quand non modifiable."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            statut=StatutPointage.VALIDE,
        )
        with pytest.raises(ValueError):
            p.set_heures(heures_normales=Duree(7, 0))

    def test_signer(self):
        """Test signature du pointage."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
        )
        p.signer("signature_test")
        assert p.is_signed
        assert p.signature_utilisateur == "signature_test"
        assert p.signature_date is not None

    def test_signer_already_signed_raises(self):
        """Test signature quand déjà signé."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            signature_utilisateur="already_signed",
        )
        with pytest.raises(ValueError):
            p.signer("new_signature")

    def test_soumettre(self):
        """Test soumission pour validation."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
        )
        p.soumettre()
        assert p.statut == StatutPointage.SOUMIS
        assert not p.is_editable

    def test_soumettre_invalid_state_raises(self):
        """Test soumission depuis état invalide."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            statut=StatutPointage.VALIDE,
        )
        with pytest.raises(ValueError):
            p.soumettre()

    def test_valider(self):
        """Test validation."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            statut=StatutPointage.SOUMIS,
        )
        p.valider(validateur_id=5)
        assert p.statut == StatutPointage.VALIDE
        assert p.validateur_id == 5
        assert p.validation_date is not None
        assert p.is_validated

    def test_rejeter(self):
        """Test rejet."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            statut=StatutPointage.SOUMIS,
        )
        p.rejeter(validateur_id=5, motif="Heures incorrectes")
        assert p.statut == StatutPointage.REJETE
        assert p.validateur_id == 5
        assert p.motif_rejet == "Heures incorrectes"
        assert p.is_editable

    def test_rejeter_without_motif_raises(self):
        """Test rejet sans motif."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            statut=StatutPointage.SOUMIS,
        )
        with pytest.raises(ValueError):
            p.rejeter(validateur_id=5, motif="")

    def test_corriger(self):
        """Test correction après rejet."""
        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date.today(),
            statut=StatutPointage.REJETE,
            signature_utilisateur="old_signature",
        )
        p.corriger()
        assert p.statut == StatutPointage.BROUILLON
        assert p.signature_utilisateur is None  # Reset signature
        assert p.is_editable


class TestVariablePaie:
    """Tests pour l'entité VariablePaie."""

    def test_creation_valid(self):
        """Test création avec valeurs valides."""
        from decimal import Decimal

        v = VariablePaie(
            type_variable=TypeVariablePaie.PANIER_REPAS,
            valeur=Decimal("15.50"),
            date_application=date.today(),
            pointage_id=1,
        )
        assert v.type_variable == TypeVariablePaie.PANIER_REPAS
        assert v.valeur == Decimal("15.50")
        assert v.is_amount
        assert not v.is_hours

    def test_creation_negative_value_raises(self):
        """Test création avec valeur négative."""
        from decimal import Decimal

        with pytest.raises(ValueError):
            VariablePaie(
                type_variable=TypeVariablePaie.PANIER_REPAS,
                valeur=Decimal("-5.00"),
                date_application=date.today(),
            )

    def test_libelle(self):
        """Test propriété libelle."""
        from decimal import Decimal

        v = VariablePaie(
            type_variable=TypeVariablePaie.HEURES_SUPPLEMENTAIRES,
            valeur=Decimal("2.5"),
            date_application=date.today(),
        )
        assert v.libelle == "Heures supplémentaires"

    def test_update_valeur(self):
        """Test mise à jour de la valeur."""
        from decimal import Decimal

        v = VariablePaie(
            type_variable=TypeVariablePaie.PANIER_REPAS,
            valeur=Decimal("10.00"),
            date_application=date.today(),
        )
        v.update_valeur(Decimal("15.00"))
        assert v.valeur == Decimal("15.00")


class TestFeuilleHeures:
    """Tests pour l'entité FeuilleHeures."""

    def test_creation_valid(self):
        """Test création avec valeurs valides."""
        monday = date(2026, 1, 19)  # Un lundi
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )
        assert f.utilisateur_id == 1
        assert f.semaine_debut == monday
        assert f.annee == 2026
        assert f.numero_semaine == 4
        assert f.statut_global == StatutPointage.BROUILLON

    def test_creation_not_monday_raises(self):
        """Test création avec date qui n'est pas un lundi."""
        tuesday = date(2026, 1, 20)  # Un mardi
        with pytest.raises(ValueError):
            FeuilleHeures(
                utilisateur_id=1,
                semaine_debut=tuesday,
                annee=2026,
                numero_semaine=4,
            )

    def test_for_week_factory(self):
        """Test factory for_week."""
        any_date = date(2026, 1, 22)  # Un jeudi
        f = FeuilleHeures.for_week(utilisateur_id=1, date_in_week=any_date)

        assert f.semaine_debut.weekday() == 0  # Lundi
        assert f.semaine_debut == date(2026, 1, 19)

    def test_semaine_fin(self):
        """Test propriété semaine_fin."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )
        assert f.semaine_fin == date(2026, 1, 25)  # Dimanche

    def test_jours_semaine(self):
        """Test propriété jours_semaine."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )
        jours = f.jours_semaine
        assert len(jours) == 7
        assert jours[0] == monday
        assert jours[6] == date(2026, 1, 25)

    def test_jours_travailles(self):
        """Test propriété jours_travailles (lundi-vendredi)."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )
        jours = f.jours_travailles
        assert len(jours) == 5
        assert jours[0] == monday
        assert jours[4] == date(2026, 1, 23)  # Vendredi

    def test_label_semaine(self):
        """Test label de la semaine."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )
        assert f.label_semaine == "Semaine 4 - 2026"

    def test_ajouter_pointage(self):
        """Test ajout d'un pointage."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )

        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),  # Mardi
            heures_normales=Duree(8, 0),
        )
        f.ajouter_pointage(p)

        assert len(f.pointages) == 1
        assert f.total_heures.heures == 8

    def test_ajouter_pointage_wrong_user_raises(self):
        """Test ajout d'un pointage d'un autre utilisateur."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )

        p = Pointage(
            utilisateur_id=2,  # Autre utilisateur
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
        )
        with pytest.raises(ValueError):
            f.ajouter_pointage(p)

    def test_ajouter_pointage_wrong_week_raises(self):
        """Test ajout d'un pointage hors de la semaine."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )

        p = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 26),  # Semaine suivante
        )
        with pytest.raises(ValueError):
            f.ajouter_pointage(p)

    def test_total_heures_par_chantier(self):
        """Test total heures par chantier."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )

        p1 = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 19),
            heures_normales=Duree(8, 0),
        )
        p2 = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=date(2026, 1, 20),
            heures_normales=Duree(7, 30),
        )
        p3 = Pointage(
            utilisateur_id=1,
            chantier_id=20,
            date_pointage=date(2026, 1, 21),
            heures_normales=Duree(4, 0),
        )

        f.ajouter_pointage(p1)
        f.ajouter_pointage(p2)
        f.ajouter_pointage(p3)

        totaux = f.total_heures_par_chantier()
        assert totaux[10].heures == 15
        assert totaux[10].minutes == 30
        assert totaux[20].heures == 4

    def test_is_complete(self):
        """Test is_complete (tous les jours ouvrés ont un pointage)."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )

        # Pas de pointage = incomplet
        assert not f.is_complete

        # Ajoute un pointage pour chaque jour ouvré
        for i in range(5):
            p = Pointage(
                utilisateur_id=1,
                chantier_id=10,
                date_pointage=monday + timedelta(days=i),
                heures_normales=Duree(8, 0),
            )
            f.ajouter_pointage(p)

        assert f.is_complete

    def test_calculer_statut_global(self):
        """Test calcul du statut global."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )

        # Pas de pointage = brouillon
        assert f.calculer_statut_global() == StatutPointage.BROUILLON

        # Tous validés = validé
        for i in range(3):
            p = Pointage(
                utilisateur_id=1,
                chantier_id=10,
                date_pointage=monday + timedelta(days=i),
                heures_normales=Duree(8, 0),
                statut=StatutPointage.VALIDE,
            )
            f.ajouter_pointage(p)

        assert f.calculer_statut_global() == StatutPointage.VALIDE

    def test_get_chantiers_ids(self):
        """Test récupération des IDs de chantiers (FDH-06 multi-chantiers)."""
        monday = date(2026, 1, 19)
        f = FeuilleHeures(
            utilisateur_id=1,
            semaine_debut=monday,
            annee=2026,
            numero_semaine=4,
        )

        p1 = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=monday,
        )
        p2 = Pointage(
            utilisateur_id=1,
            chantier_id=20,
            date_pointage=monday + timedelta(days=1),
        )
        p3 = Pointage(
            utilisateur_id=1,
            chantier_id=10,
            date_pointage=monday + timedelta(days=2),
        )

        f.ajouter_pointage(p1)
        f.ajouter_pointage(p2)
        f.ajouter_pointage(p3)

        chantiers = f.get_chantiers_ids()
        assert set(chantiers) == {10, 20}
