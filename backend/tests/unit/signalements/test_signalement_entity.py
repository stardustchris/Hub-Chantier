"""Tests unitaires pour l'entité Signalement."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from modules.signalements.domain.entities import Signalement
from modules.signalements.domain.value_objects import Priorite, StatutSignalement


class TestSignalementCreation:
    """Tests pour la création d'un signalement."""

    def test_create_signalement_basic(self):
        """Test: création d'un signalement avec données minimales."""
        signalement = Signalement(
            chantier_id=1,
            titre="Fuite d'eau",
            description="Fuite détectée au niveau du sous-sol",
            cree_par=10,
        )

        assert signalement.chantier_id == 1
        assert signalement.titre == "Fuite d'eau"
        assert signalement.description == "Fuite détectée au niveau du sous-sol"
        assert signalement.cree_par == 10
        assert signalement.priorite == Priorite.MOYENNE  # Défaut
        assert signalement.statut == StatutSignalement.OUVERT  # Défaut
        assert signalement.id is None
        assert signalement.assigne_a is None

    def test_create_signalement_with_priorite(self):
        """Test: création avec priorité spécifiée."""
        signalement = Signalement(
            chantier_id=1,
            titre="Problème critique",
            description="Description du problème",
            cree_par=10,
            priorite=Priorite.CRITIQUE,
        )

        assert signalement.priorite == Priorite.CRITIQUE

    def test_create_signalement_strips_whitespace(self):
        """Test: les espaces sont supprimés du titre et description."""
        signalement = Signalement(
            chantier_id=1,
            titre="  Titre avec espaces  ",
            description="  Description avec espaces  ",
            cree_par=10,
            localisation="  Étage 2  ",
        )

        assert signalement.titre == "Titre avec espaces"
        assert signalement.description == "Description avec espaces"
        assert signalement.localisation == "Étage 2"

    def test_create_signalement_empty_titre_error(self):
        """Test: erreur si titre vide."""
        with pytest.raises(ValueError) as exc_info:
            Signalement(
                chantier_id=1,
                titre="",
                description="Description",
                cree_par=10,
            )
        assert "titre" in str(exc_info.value).lower()

    def test_create_signalement_whitespace_titre_error(self):
        """Test: erreur si titre contient uniquement des espaces."""
        with pytest.raises(ValueError) as exc_info:
            Signalement(
                chantier_id=1,
                titre="   ",
                description="Description",
                cree_par=10,
            )
        assert "titre" in str(exc_info.value).lower()

    def test_create_signalement_empty_description_error(self):
        """Test: erreur si description vide."""
        with pytest.raises(ValueError) as exc_info:
            Signalement(
                chantier_id=1,
                titre="Titre",
                description="",
                cree_par=10,
            )
        assert "description" in str(exc_info.value).lower()


class TestSignalementRetard:
    """Tests pour la gestion des retards (SIG-15, SIG-16)."""

    def test_est_en_retard_false_when_resolved(self):
        """Test: un signalement résolu n'est jamais en retard."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.CLOTURE,
        )

        assert signalement.est_en_retard is False

    def test_est_en_retard_based_on_priorite(self):
        """Test: retard basé sur le délai de la priorité."""
        # Créé il y a 5 heures avec priorité critique (4h)
        with patch.object(Signalement, '__post_init__', lambda self: None):
            signalement = Signalement(
                chantier_id=1,
                titre="Test",
                description="Test",
                cree_par=10,
                priorite=Priorite.CRITIQUE,
            )
            signalement.created_at = datetime.now() - timedelta(hours=5)

        assert signalement.est_en_retard is True

    def test_est_en_retard_based_on_date_souhaitee(self):
        """Test: retard basé sur la date de résolution souhaitée."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            date_resolution_souhaitee=datetime.now() - timedelta(hours=1),
        )

        assert signalement.est_en_retard is True

    def test_not_en_retard_within_delay(self):
        """Test: pas en retard si dans le délai."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            priorite=Priorite.BASSE,  # 72h
        )

        assert signalement.est_en_retard is False


class TestSignalementEscalade:
    """Tests pour le système d'escalade (SIG-16, SIG-17)."""

    def test_pourcentage_temps_ecoule_zero_when_resolved(self):
        """Test: pourcentage à 0 si résolu."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.CLOTURE,
        )

        assert signalement.pourcentage_temps_ecoule == 0.0

    def test_niveau_escalade_none_when_resolved(self):
        """Test: pas d'escalade requise si résolu."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.TRAITE,
        )

        assert signalement.niveau_escalade_requis is None

    def test_niveau_escalade_chef_chantier_at_50_percent(self):
        """Test: escalade chef chantier à 50%."""
        with patch.object(Signalement, '__post_init__', lambda self: None):
            signalement = Signalement(
                chantier_id=1,
                titre="Test",
                description="Test",
                cree_par=10,
                priorite=Priorite.HAUTE,  # 24h
            )
            # 12h écoulées = 50%
            signalement.created_at = datetime.now() - timedelta(hours=12)

        assert signalement.niveau_escalade_requis == "chef_chantier"

    def test_niveau_escalade_conducteur_at_100_percent(self):
        """Test: escalade conducteur à 100%."""
        with patch.object(Signalement, '__post_init__', lambda self: None):
            signalement = Signalement(
                chantier_id=1,
                titre="Test",
                description="Test",
                cree_par=10,
                priorite=Priorite.HAUTE,  # 24h
            )
            # 25h écoulées > 100%
            signalement.created_at = datetime.now() - timedelta(hours=25)

        assert signalement.niveau_escalade_requis == "conducteur"

    def test_niveau_escalade_admin_at_200_percent(self):
        """Test: escalade admin à 200%."""
        with patch.object(Signalement, '__post_init__', lambda self: None):
            signalement = Signalement(
                chantier_id=1,
                titre="Test",
                description="Test",
                cree_par=10,
                priorite=Priorite.HAUTE,  # 24h
            )
            # 50h écoulées > 200%
            signalement.created_at = datetime.now() - timedelta(hours=50)

        assert signalement.niveau_escalade_requis == "admin"

    def test_enregistrer_escalade(self):
        """Test: enregistrement d'une escalade."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.nb_escalades == 0
        assert signalement.derniere_escalade_at is None

        signalement.enregistrer_escalade()

        assert signalement.nb_escalades == 1
        assert signalement.derniere_escalade_at is not None


class TestSignalementWorkflow:
    """Tests pour le workflow du signalement."""

    def test_assigner_change_status_to_en_cours(self):
        """Test: l'assignation passe le statut à EN_COURS."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        signalement.assigner(user_id=5)

        assert signalement.assigne_a == 5
        assert signalement.statut == StatutSignalement.EN_COURS

    def test_assigner_keeps_status_if_not_ouvert(self):
        """Test: l'assignation ne change pas le statut si pas OUVERT."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.TRAITE,
        )

        signalement.assigner(user_id=5)

        assert signalement.assigne_a == 5
        assert signalement.statut == StatutSignalement.TRAITE

    def test_marquer_traite_success(self):
        """Test: marquer comme traité avec succès."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        signalement.marquer_traite("Problème résolu")

        assert signalement.statut == StatutSignalement.TRAITE
        assert signalement.commentaire_traitement == "Problème résolu"
        assert signalement.date_traitement is not None

    def test_marquer_traite_empty_comment_error(self):
        """Test: erreur si commentaire vide."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        with pytest.raises(ValueError) as exc_info:
            signalement.marquer_traite("")
        assert "commentaire" in str(exc_info.value).lower()

    def test_marquer_traite_from_cloture_error(self):
        """Test: impossible de marquer traité depuis CLOTURE."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.CLOTURE,
        )

        with pytest.raises(ValueError):
            signalement.marquer_traite("Commentaire")

    def test_cloturer_success(self):
        """Test: clôturer avec succès."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.TRAITE,
        )

        signalement.cloturer()

        assert signalement.statut == StatutSignalement.CLOTURE
        assert signalement.date_cloture is not None

    def test_cloturer_from_ouvert_success(self):
        """Test: peut clôturer directement depuis OUVERT."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.OUVERT,
        )

        signalement.cloturer()

        assert signalement.statut == StatutSignalement.CLOTURE

    def test_reouvrir_success(self):
        """Test: réouvrir avec succès."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.CLOTURE,
        )
        signalement.date_traitement = datetime.now()
        signalement.date_cloture = datetime.now()
        signalement.commentaire_traitement = "Test"

        signalement.reouvrir()

        assert signalement.statut == StatutSignalement.OUVERT
        assert signalement.date_traitement is None
        assert signalement.date_cloture is None
        assert signalement.commentaire_traitement is None

    def test_changer_priorite(self):
        """Test: changer la priorité."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            priorite=Priorite.BASSE,
        )

        signalement.changer_priorite(Priorite.CRITIQUE)

        assert signalement.priorite == Priorite.CRITIQUE


class TestSignalementPermissions:
    """Tests pour les permissions."""

    def test_admin_peut_modifier(self):
        """Test: admin peut toujours modifier."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_modifier(user_id=99, user_role="admin") is True

    def test_conducteur_peut_modifier(self):
        """Test: conducteur peut toujours modifier."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_modifier(user_id=99, user_role="conducteur") is True

    def test_chef_chantier_peut_modifier(self):
        """Test: chef de chantier peut modifier."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_modifier(user_id=99, user_role="chef_chantier") is True

    def test_compagnon_peut_modifier_son_signalement(self):
        """Test: compagnon peut modifier son propre signalement non clôturé."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_modifier(user_id=10, user_role="compagnon") is True

    def test_compagnon_ne_peut_pas_modifier_signalement_autre(self):
        """Test: compagnon ne peut pas modifier le signalement d'un autre."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_modifier(user_id=20, user_role="compagnon") is False

    def test_compagnon_ne_peut_pas_modifier_signalement_cloture(self):
        """Test: compagnon ne peut pas modifier un signalement clôturé."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
            statut=StatutSignalement.CLOTURE,
        )

        assert signalement.peut_modifier(user_id=10, user_role="compagnon") is False

    def test_admin_peut_cloturer(self):
        """Test: admin peut clôturer."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_cloturer(user_role="admin") is True

    def test_conducteur_peut_cloturer(self):
        """Test: conducteur peut clôturer."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_cloturer(user_role="conducteur") is True

    def test_chef_chantier_peut_cloturer(self):
        """Test: chef de chantier peut clôturer."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_cloturer(user_role="chef_chantier") is True

    def test_compagnon_ne_peut_pas_cloturer(self):
        """Test: compagnon ne peut pas clôturer."""
        signalement = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert signalement.peut_cloturer(user_role="compagnon") is False


class TestSignalementEquality:
    """Tests pour l'égalité et le hash."""

    def test_equality_by_id(self):
        """Test: égalité basée sur l'ID."""
        sig1 = Signalement(
            id=1,
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )
        sig2 = Signalement(
            id=1,
            chantier_id=2,  # Différent
            titre="Autre",  # Différent
            description="Autre",  # Différent
            cree_par=20,  # Différent
        )

        assert sig1 == sig2

    def test_inequality_different_ids(self):
        """Test: inégalité si IDs différents."""
        sig1 = Signalement(
            id=1,
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )
        sig2 = Signalement(
            id=2,
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert sig1 != sig2

    def test_inequality_with_none_id(self):
        """Test: inégalité si un ID est None."""
        sig1 = Signalement(
            id=1,
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )
        sig2 = Signalement(
            chantier_id=1,
            titre="Test",
            description="Test",
            cree_par=10,
        )

        assert sig1 != sig2
