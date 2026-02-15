"""Tests unitaires pour CheckSignalementsRetardUseCase (SIG-16, SIG-17)."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from modules.signalements.domain.entities import Signalement, EscaladeHistorique
from modules.signalements.domain.value_objects import Priorite, StatutSignalement
from modules.signalements.domain.services.escalade_service import (
    EscaladeService,
    EscaladeInfo,
)
from modules.signalements.application.use_cases.check_retard_use_case import (
    CheckSignalementsRetardUseCase,
    RetardAlertResult,
)


def _make_signalement(
    id: int = 1,
    priorite: Priorite = Priorite.HAUTE,
    statut: StatutSignalement = StatutSignalement.OUVERT,
    created_at: datetime = None,
    nb_escalades: int = 0,
) -> Signalement:
    """Factory helper pour créer un signalement de test."""
    sig = Signalement(
        chantier_id=1,
        titre=f"Signalement test #{id}",
        description="Description test",
        cree_par=10,
        priorite=priorite,
        statut=statut,
    )
    sig.id = id
    sig.nb_escalades = nb_escalades
    if created_at:
        sig.created_at = created_at
    return sig


class TestCheckSignalementsRetardUseCase:
    """Tests pour le use case de vérification des retards."""

    def setup_method(self):
        """Setup des mocks."""
        self.signalement_repo = MagicMock()
        self.escalade_repo = MagicMock()
        self.escalade_service = MagicMock(spec=EscaladeService)

        self.use_case = CheckSignalementsRetardUseCase(
            signalement_repository=self.signalement_repo,
            escalade_repository=self.escalade_repo,
            escalade_service=self.escalade_service,
        )

    def test_execute_no_signalements(self):
        """Test: aucun signalement à escalader."""
        self.signalement_repo.find_a_escalader.return_value = []

        result = self.use_case.execute()

        assert isinstance(result, RetardAlertResult)
        assert result.signalements_verifies == 0
        assert result.escalades_effectuees == 0
        assert result.erreurs == 0

    def test_execute_with_escalade(self):
        """Test: escalade effectuée pour un signalement en retard."""
        sig = _make_signalement(
            id=1,
            priorite=Priorite.HAUTE,
            created_at=datetime.now() - timedelta(hours=25),
        )
        self.signalement_repo.find_a_escalader.return_value = [sig]

        escalade_info = EscaladeInfo(
            signalement=sig,
            niveau="chef_chantier",
            pourcentage_temps=104.0,
            destinataires_roles=["createur", "chef_chantier"],
        )
        self.escalade_service.determiner_escalades.return_value = [escalade_info]
        self.escalade_service.generer_message_escalade.return_value = "Message test"
        self.escalade_repo.find_last_by_signalement.return_value = None

        result = self.use_case.execute()

        assert result.signalements_verifies == 1
        assert result.escalades_effectuees == 1
        assert result.erreurs == 0
        assert len(result.details) == 1
        assert result.details[0]["niveau"] == "chef_chantier"

    def test_execute_skip_already_escaladed(self):
        """Test: ne pas re-escalader un signalement déjà escaladé au même niveau."""
        sig = _make_signalement(id=1, nb_escalades=1)
        self.signalement_repo.find_a_escalader.return_value = [sig]

        escalade_info = EscaladeInfo(
            signalement=sig,
            niveau="chef_chantier",
            pourcentage_temps=55.0,
            destinataires_roles=["createur", "chef_chantier"],
        )
        self.escalade_service.determiner_escalades.return_value = [escalade_info]

        # Dernière escalade est déjà chef_chantier
        last = EscaladeHistorique(
            signalement_id=1,
            niveau="chef_chantier",
            pourcentage_temps=51.0,
        )
        self.escalade_repo.find_last_by_signalement.return_value = last

        result = self.use_case.execute()

        assert result.escalades_effectuees == 0
        assert result.erreurs == 0

    def test_execute_escalade_next_level(self):
        """Test: escalade au niveau supérieur quand le niveau précédent est déjà fait."""
        sig = _make_signalement(id=1, nb_escalades=1)
        self.signalement_repo.find_a_escalader.return_value = [sig]

        escalade_info = EscaladeInfo(
            signalement=sig,
            niveau="conducteur",
            pourcentage_temps=110.0,
            destinataires_roles=["conducteur"],
        )
        self.escalade_service.determiner_escalades.return_value = [escalade_info]
        self.escalade_service.generer_message_escalade.return_value = "Message"

        # Dernière escalade est chef_chantier -> conducteur autorisé
        last = EscaladeHistorique(
            signalement_id=1,
            niveau="chef_chantier",
            pourcentage_temps=51.0,
        )
        self.escalade_repo.find_last_by_signalement.return_value = last

        result = self.use_case.execute()

        assert result.escalades_effectuees == 1
        assert result.details[0]["niveau"] == "conducteur"

    def test_execute_handles_error_gracefully(self):
        """Test: gestion des erreurs sans crash."""
        self.signalement_repo.find_a_escalader.side_effect = Exception("DB error")

        result = self.use_case.execute()

        assert result.erreurs == 1
        assert result.signalements_verifies == 0

    def test_execute_multiple_signalements(self):
        """Test: traitement de plusieurs signalements."""
        sig1 = _make_signalement(id=1)
        sig2 = _make_signalement(id=2)
        self.signalement_repo.find_a_escalader.return_value = [sig1, sig2]

        escalade_info1 = EscaladeInfo(
            signalement=sig1, niveau="chef_chantier",
            pourcentage_temps=60.0, destinataires_roles=["createur", "chef_chantier"],
        )
        escalade_info2 = EscaladeInfo(
            signalement=sig2, niveau="conducteur",
            pourcentage_temps=120.0, destinataires_roles=["conducteur"],
        )
        self.escalade_service.determiner_escalades.return_value = [
            escalade_info1, escalade_info2,
        ]
        self.escalade_service.generer_message_escalade.return_value = "Message"
        self.escalade_repo.find_last_by_signalement.return_value = None

        result = self.use_case.execute()

        assert result.signalements_verifies == 2
        assert result.escalades_effectuees == 2


class TestEscaladeHistorique:
    """Tests pour l'entité EscaladeHistorique."""

    def test_create_valid(self):
        """Test: création d'un historique valide."""
        hist = EscaladeHistorique(
            signalement_id=1,
            niveau="chef_chantier",
            pourcentage_temps=55.0,
            destinataires_roles=["createur", "chef_chantier"],
            message="Escalade test",
        )
        assert hist.signalement_id == 1
        assert hist.niveau == "chef_chantier"
        assert hist.pourcentage_temps == 55.0

    def test_create_invalid_niveau(self):
        """Test: erreur si niveau invalide."""
        with pytest.raises(ValueError, match="Niveau d'escalade invalide"):
            EscaladeHistorique(
                signalement_id=1,
                niveau="invalid",
                pourcentage_temps=50.0,
            )

    def test_create_negative_pourcentage(self):
        """Test: erreur si pourcentage négatif."""
        with pytest.raises(ValueError, match="négatif"):
            EscaladeHistorique(
                signalement_id=1,
                niveau="chef_chantier",
                pourcentage_temps=-10.0,
            )

    def test_equality_by_id(self):
        """Test: égalité basée sur l'ID."""
        h1 = EscaladeHistorique(
            id=1, signalement_id=1, niveau="chef_chantier", pourcentage_temps=50.0,
        )
        h2 = EscaladeHistorique(
            id=1, signalement_id=2, niveau="conducteur", pourcentage_temps=100.0,
        )
        assert h1 == h2

    def test_inequality_different_ids(self):
        """Test: inégalité si IDs différents."""
        h1 = EscaladeHistorique(
            id=1, signalement_id=1, niveau="chef_chantier", pourcentage_temps=50.0,
        )
        h2 = EscaladeHistorique(
            id=2, signalement_id=1, niveau="chef_chantier", pourcentage_temps=50.0,
        )
        assert h1 != h2
