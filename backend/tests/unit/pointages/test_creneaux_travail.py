"""Tests du decoupage d'une duree de travail en creneaux horaires.

La paie externe (Costructor) exige une heure de debut et de fin, et compte
l'amplitude sans deduire de pause. Une journee doit donc etre envoyee en
creneaux qui encadrent le repas, pour que le total soit exact.
"""

from datetime import time

import pytest

from modules.pointages.domain.services.creneaux_travail import (
    Creneau,
    HorairesReference,
    decouper_en_creneaux,
)

# Horaires de l'entreprise : 8h00, repas de 12h00 a 13h00, 7h par jour
HORAIRES = HorairesReference(
    debut=time(8, 0), pause_debut=time(12, 0), pause_fin=time(13, 0)
)


def _plages(creneaux):
    return [(c.debut.strftime("%H:%M"), c.fin.strftime("%H:%M")) for c in creneaux]


class TestDecouperEnCreneaux:
    def test_journee_type_de_7h_encadre_le_repas(self):
        """7h -> 8h-12h puis 13h-16h : la journee de reference."""
        assert _plages(decouper_en_creneaux(7 * 60, HORAIRES)) == [
            ("08:00", "12:00"),
            ("13:00", "16:00"),
        ]

    def test_le_total_des_creneaux_egale_la_duree(self):
        for minutes in (30, 60, 239, 240, 241, 420, 450, 600):
            creneaux = decouper_en_creneaux(minutes, HORAIRES)
            assert sum(c.duree_minutes for c in creneaux) == minutes

    def test_journee_longue_prolonge_l_apres_midi(self):
        """10h -> 8h-12h puis 13h-19h."""
        assert _plages(decouper_en_creneaux(10 * 60, HORAIRES)) == [
            ("08:00", "12:00"),
            ("13:00", "19:00"),
        ]

    def test_minutes_conservees(self):
        """7h30 -> l'apres-midi se termine a 16h30."""
        assert _plages(decouper_en_creneaux(7 * 60 + 30, HORAIRES)) == [
            ("08:00", "12:00"),
            ("13:00", "16:30"),
        ]

    def test_demi_journee_tient_dans_la_matinee(self):
        """3h -> un seul creneau, sans franchir le repas."""
        assert _plages(decouper_en_creneaux(3 * 60, HORAIRES)) == [("08:00", "11:00")]

    def test_matinee_complete_sans_apres_midi(self):
        """Exactement 4h -> pas de creneau vide l'apres-midi."""
        assert _plages(decouper_en_creneaux(4 * 60, HORAIRES)) == [("08:00", "12:00")]

    def test_duree_nulle_ne_produit_aucun_creneau(self):
        assert decouper_en_creneaux(0, HORAIRES) == []

    def test_duree_negative_refusee(self):
        with pytest.raises(ValueError):
            decouper_en_creneaux(-30, HORAIRES)

    def test_duree_depassant_la_journee_refusee(self):
        """4h le matin + 11h l'apres-midi atteindrait minuit : impossible a saisir."""
        with pytest.raises(ValueError, match="minuit"):
            decouper_en_creneaux(15 * 60, HORAIRES)

    def test_horaires_incoherents_refuses(self):
        with pytest.raises(ValueError):
            HorairesReference(debut=time(13, 0), pause_debut=time(12, 0), pause_fin=time(13, 0))
        with pytest.raises(ValueError):
            HorairesReference(debut=time(8, 0), pause_debut=time(13, 0), pause_fin=time(12, 0))

    def test_horaires_parametrables(self):
        """Un autre horaire d'entreprise : 7h30, repas 12h-12h45."""
        horaires = HorairesReference(
            debut=time(7, 30), pause_debut=time(12, 0), pause_fin=time(12, 45)
        )
        assert _plages(decouper_en_creneaux(7 * 60, horaires)) == [
            ("07:30", "12:00"),
            ("12:45", "15:15"),
        ]

    def test_horaires_depuis_texte(self):
        horaires = HorairesReference.depuis_texte("08:00", "12:00", "13:00")
        assert horaires == HORAIRES

    def test_creneau_expose_sa_duree(self):
        assert Creneau(time(13, 0), time(16, 0)).duree_minutes == 180
