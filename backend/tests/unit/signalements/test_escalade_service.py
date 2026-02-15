"""Tests unitaires pour EscaladeService."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from modules.signalements.domain.services.escalade_service import (
    EscaladeService,
    EscaladeInfo,
)


class TestEscaladeService:
    """Tests pour EscaladeService."""

    @pytest.fixture
    def service(self):
        """Instance du service."""
        return EscaladeService()

    @pytest.fixture
    def mock_signalement_actif(self):
        """Signalement actif (non resolu)."""
        sig = Mock()
        sig.id = 1
        sig.titre = "Probleme securite"
        sig.statut = Mock(est_resolu=False)
        sig.priorite = Mock(label="Haute")
        sig.nb_escalades = 0
        sig.localisation = "Zone A"
        sig.temps_restant_formatte = "2h 30min"
        sig.created_at = datetime.now() - timedelta(hours=2)
        return sig

    @pytest.fixture
    def mock_signalement_resolu(self):
        """Signalement resolu."""
        sig = Mock()
        sig.id = 2
        sig.statut = Mock(est_resolu=True)
        sig.nb_escalades = 0
        return sig


class TestDeterminerEscalades:
    """Tests pour determiner_escalades."""

    @pytest.fixture
    def service(self):
        return EscaladeService()

    def test_liste_vide_retourne_vide(self, service):
        """Liste vide retourne liste vide."""
        result = service.determiner_escalades([])
        assert result == []

    def test_signalement_resolu_ignore(self, service):
        """Signalement resolu est ignore."""
        sig = Mock()
        sig.statut = Mock(est_resolu=True)

        result = service.determiner_escalades([sig])
        assert result == []

    def test_signalement_sous_50_pct_pas_escalade(self, service):
        """Signalement sous 50% pas d'escalade."""
        sig = Mock()
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 30.0
        sig.nb_escalades = 0

        result = service.determiner_escalades([sig])
        assert result == []

    def test_signalement_a_50_pct_escalade_chef_chantier(self, service):
        """Signalement a 50% -> escalade createur + chef chantier (CDC 10.5)."""
        sig = Mock()
        sig.id = 1
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 55.0
        sig.nb_escalades = 0

        result = service.determiner_escalades([sig])

        assert len(result) == 1
        assert result[0].niveau == "chef_chantier"
        assert result[0].destinataires_roles == ["createur", "chef_chantier"]

    def test_signalement_a_100_pct_escalade_conducteur(self, service):
        """Signalement a 100% -> escalade conducteur."""
        sig = Mock()
        sig.id = 1
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 110.0
        sig.nb_escalades = 1  # Deja escalade niveau 0

        result = service.determiner_escalades([sig])

        assert len(result) == 1
        assert result[0].niveau == "conducteur"
        assert result[0].destinataires_roles == ["conducteur"]

    def test_signalement_a_200_pct_escalade_admin(self, service):
        """Signalement a 200% -> escalade admin."""
        sig = Mock()
        sig.id = 1
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 210.0
        sig.nb_escalades = 2  # Deja escalade niveau 0 et 1

        result = service.determiner_escalades([sig])

        assert len(result) == 1
        assert result[0].niveau == "admin"
        assert result[0].destinataires_roles == ["admin"]

    def test_signalement_deja_escalade_pas_reescalade(self, service):
        """Signalement deja escalade n'est pas re-escalade."""
        sig = Mock()
        sig.id = 1
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 55.0
        sig.nb_escalades = 1  # Deja escalade au niveau chef_chantier

        result = service.determiner_escalades([sig])
        assert result == []

    def test_plusieurs_signalements(self, service):
        """Gere plusieurs signalements."""
        sig1 = Mock()
        sig1.id = 1
        sig1.statut = Mock(est_resolu=False)
        sig1.pourcentage_temps_ecoule = 60.0
        sig1.nb_escalades = 0

        sig2 = Mock()
        sig2.id = 2
        sig2.statut = Mock(est_resolu=True)  # Ignore

        sig3 = Mock()
        sig3.id = 3
        sig3.statut = Mock(est_resolu=False)
        sig3.pourcentage_temps_ecoule = 30.0  # Pas escalade
        sig3.nb_escalades = 0

        result = service.determiner_escalades([sig1, sig2, sig3])

        assert len(result) == 1
        assert result[0].signalement == sig1


class TestCalculerProchaineEscalade:
    """Tests pour calculer_prochaine_escalade."""

    @pytest.fixture
    def service(self):
        return EscaladeService()

    def test_signalement_resolu_retourne_none(self, service):
        """Signalement resolu retourne None."""
        sig = Mock()
        sig.statut = Mock(est_resolu=True)

        result = service.calculer_prochaine_escalade(sig)
        assert result is None

    def test_signalement_sous_50_prochaine_chef_chantier(self, service):
        """Signalement sous 50% -> prochaine escalade chef chantier."""
        sig = Mock()
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 30.0
        sig.created_at = datetime.now() - timedelta(hours=3)
        sig.date_limite_traitement = datetime.now() + timedelta(hours=7)

        result = service.calculer_prochaine_escalade(sig)

        assert result is not None
        niveau, date_escalade = result
        assert niveau == "chef_chantier"

    def test_signalement_entre_50_100_prochaine_conducteur(self, service):
        """Signalement entre 50% et 100% -> prochaine escalade conducteur."""
        sig = Mock()
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 75.0
        sig.created_at = datetime.now() - timedelta(hours=3)
        sig.date_limite_traitement = datetime.now() + timedelta(hours=1)

        result = service.calculer_prochaine_escalade(sig)

        assert result is not None
        niveau, date_escalade = result
        assert niveau == "conducteur"

    def test_signalement_entre_100_200_prochaine_admin(self, service):
        """Signalement entre 100% et 200% -> prochaine escalade admin."""
        sig = Mock()
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 150.0
        sig.created_at = datetime.now() - timedelta(hours=6)
        sig.date_limite_traitement = datetime.now() - timedelta(hours=2)

        result = service.calculer_prochaine_escalade(sig)

        assert result is not None
        niveau, date_escalade = result
        assert niveau == "admin"

    def test_signalement_au_dela_200_retourne_none(self, service):
        """Signalement au-dela 200% retourne None (plus d'escalade)."""
        sig = Mock()
        sig.statut = Mock(est_resolu=False)
        sig.pourcentage_temps_ecoule = 250.0
        sig.created_at = datetime.now() - timedelta(hours=10)
        sig.date_limite_traitement = datetime.now() - timedelta(hours=6)

        result = service.calculer_prochaine_escalade(sig)
        assert result is None


class TestGenererMessageEscalade:
    """Tests pour generer_message_escalade."""

    @pytest.fixture
    def service(self):
        return EscaladeService()

    def test_message_contient_niveau(self, service):
        """Message contient le niveau d'escalade."""
        sig = Mock()
        sig.id = 42
        sig.titre = "Probleme urgent"
        sig.priorite = Mock(label="Critique")
        sig.temps_restant_formatte = "1h 15min"
        sig.localisation = None

        escalade = EscaladeInfo(
            signalement=sig,
            niveau="conducteur",
            pourcentage_temps=110.0,
            destinataires_roles=["conducteur"],
        )

        message = service.generer_message_escalade(escalade, "Chantier Alpha")

        assert "CONDUCTEUR DE TRAVAUX" in message
        assert "#42" in message
        assert "Probleme urgent" in message
        assert "Chantier Alpha" in message
        assert "Critique" in message
        assert "110%" in message
        assert "1h 15min" in message

    def test_message_avec_localisation(self, service):
        """Message inclut la localisation si presente."""
        sig = Mock()
        sig.id = 1
        sig.titre = "Test"
        sig.priorite = Mock(label="Haute")
        sig.temps_restant_formatte = "2h"
        sig.localisation = "Etage 2, bureau 201"

        escalade = EscaladeInfo(
            signalement=sig,
            niveau="chef_chantier",
            pourcentage_temps=55.0,
            destinataires_roles=["chef_chantier"],
        )

        message = service.generer_message_escalade(escalade, "Chantier Test")

        assert "Etage 2, bureau 201" in message

    def test_message_sans_localisation(self, service):
        """Message n'inclut pas localisation si absente."""
        sig = Mock()
        sig.id = 1
        sig.titre = "Test"
        sig.priorite = Mock(label="Moyenne")
        sig.temps_restant_formatte = "5h"
        sig.localisation = None

        escalade = EscaladeInfo(
            signalement=sig,
            niveau="admin",
            pourcentage_temps=220.0,
            destinataires_roles=["admin"],
        )

        message = service.generer_message_escalade(escalade, "Chantier X")

        assert "Localisation" not in message


class TestGetStatistiquesEscalade:
    """Tests pour get_statistiques_escalade."""

    @pytest.fixture
    def service(self):
        return EscaladeService()

    def test_liste_vide(self, service):
        """Liste vide retourne stats a zero."""
        stats = service.get_statistiques_escalade([])

        assert stats["total"] == 0
        assert stats["en_retard"] == 0
        assert stats["a_50_pct"] == 0
        assert stats["a_100_pct"] == 0
        assert stats["a_200_pct"] == 0
        assert stats["deja_escalades"] == 0

    def test_signalement_resolu_ignore(self, service):
        """Signalement resolu n'est pas compte dans les stats."""
        sig = Mock()
        sig.statut = Mock(est_resolu=True)
        sig.pourcentage_temps_ecoule = 150.0
        sig.nb_escalades = 1

        stats = service.get_statistiques_escalade([sig])

        assert stats["total"] == 1
        assert stats["en_retard"] == 0
        assert stats["a_100_pct"] == 0
        assert stats["deja_escalades"] == 0

    def test_compte_par_seuil(self, service):
        """Compte correctement par seuil."""
        sig_50 = Mock()
        sig_50.statut = Mock(est_resolu=False)
        sig_50.pourcentage_temps_ecoule = 60.0
        sig_50.nb_escalades = 0

        sig_100 = Mock()
        sig_100.statut = Mock(est_resolu=False)
        sig_100.pourcentage_temps_ecoule = 120.0
        sig_100.nb_escalades = 1

        sig_200 = Mock()
        sig_200.statut = Mock(est_resolu=False)
        sig_200.pourcentage_temps_ecoule = 250.0
        sig_200.nb_escalades = 2

        stats = service.get_statistiques_escalade([sig_50, sig_100, sig_200])

        assert stats["total"] == 3
        assert stats["a_50_pct"] == 1  # 60% compte dans 50+
        assert stats["a_100_pct"] == 1  # 120% compte dans 100+
        assert stats["a_200_pct"] == 1  # 250% compte dans 200+
        assert stats["en_retard"] == 2  # 100+ et 200+ sont en retard
        assert stats["deja_escalades"] == 2  # sig_100 et sig_200


class TestGetIndexNiveau:
    """Tests pour _get_index_niveau."""

    @pytest.fixture
    def service(self):
        return EscaladeService()

    def test_chef_chantier_index_0(self, service):
        """Chef chantier a l'index 0."""
        assert service._get_index_niveau("chef_chantier") == 0

    def test_conducteur_index_1(self, service):
        """Conducteur a l'index 1."""
        assert service._get_index_niveau("conducteur") == 1

    def test_admin_index_2(self, service):
        """Admin a l'index 2."""
        assert service._get_index_niveau("admin") == 2

    def test_niveau_inconnu_retourne_moins_1(self, service):
        """Niveau inconnu retourne -1."""
        assert service._get_index_niveau("inconnu") == -1


class TestGetNiveauLabel:
    """Tests pour _get_niveau_label."""

    @pytest.fixture
    def service(self):
        return EscaladeService()

    def test_label_chef_chantier(self, service):
        """Label pour chef_chantier."""
        assert service._get_niveau_label("chef_chantier") == "Chef de Chantier"

    def test_label_conducteur(self, service):
        """Label pour conducteur."""
        assert service._get_niveau_label("conducteur") == "Conducteur de Travaux"

    def test_label_admin(self, service):
        """Label pour admin."""
        assert service._get_niveau_label("admin") == "Administrateur"

    def test_label_inconnu_retourne_valeur(self, service):
        """Niveau inconnu retourne la valeur elle-meme."""
        assert service._get_niveau_label("autre") == "autre"


class TestSeuilsEscalade:
    """Tests pour les constantes SEUILS_ESCALADE."""

    def test_trois_seuils_definis(self):
        """Trois seuils sont definis."""
        assert len(EscaladeService.SEUILS_ESCALADE) == 3

    def test_seuils_ordonnes_croissants(self):
        """Seuils sont dans l'ordre croissant."""
        seuils = [s[0] for s in EscaladeService.SEUILS_ESCALADE]
        assert seuils == [50.0, 100.0, 200.0]

    def test_niveaux_corrects(self):
        """Niveaux sont corrects."""
        niveaux = [s[1] for s in EscaladeService.SEUILS_ESCALADE]
        assert niveaux == ["chef_chantier", "conducteur", "admin"]
