"""Tests unitaires pour les Use Cases Alerte du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.financier.domain.entities import AlerteDepassement, Budget
from modules.financier.domain.repositories import (
    BudgetRepository,
    AchatRepository,
    JournalFinancierRepository,
)
from modules.financier.domain.repositories.alerte_repository import AlerteRepository
from modules.financier.domain.repositories.cout_main_oeuvre_repository import (
    CoutMainOeuvreRepository,
)
from modules.financier.domain.repositories.cout_materiel_repository import (
    CoutMaterielRepository,
)
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.use_cases.alerte_use_cases import (
    VerifierDepassementUseCase,
    AcquitterAlerteUseCase,
    ListAlertesUseCase,
    AlerteNotFoundError,
)


class TestVerifierDepassementUseCase:
    """Tests pour le use case de verification de depassement."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        self.mock_cout_materiel_repo = Mock(spec=CoutMaterielRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = VerifierDepassementUseCase(
            alerte_repository=self.mock_alerte_repo,
            budget_repository=self.mock_budget_repo,
            achat_repository=self.mock_achat_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def _setup_budget(self, montant_initial=Decimal("500000"), seuil=Decimal("80")):
        """Configure un budget pour les tests."""
        budget = Budget(
            id=10,
            chantier_id=100,
            montant_initial_ht=montant_initial,
            seuil_alerte_pct=seuil,
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        def save_alerte(alerte):
            alerte.id = 1
            return alerte

        self.mock_alerte_repo.save.side_effect = save_alerte
        return budget

    def test_create_alert_when_threshold_exceeded(self):
        """Test: creation d'alerte quand le seuil engage est depasse."""
        self._setup_budget()

        # Montant engage = 420000 -> 84% > 80% -> alerte
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("420000"),  # engage
            Decimal("300000"),  # realise (achats)
        ]
        self.mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("10000")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("5000")

        result = self.use_case.execute(chantier_id=100)

        # Au moins une alerte creee (seuil engage)
        assert len(result) >= 1
        self.mock_alerte_repo.save.assert_called()
        self.mock_journal.save.assert_called()
        self.mock_event_bus.publish.assert_called()

    def test_no_alert_when_under_threshold(self):
        """Test: pas d'alerte quand en dessous du seuil."""
        self._setup_budget()

        # Montant engage = 200000 -> 40% < 80% -> pas d'alerte
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("200000"),  # engage
            Decimal("100000"),  # realise (achats)
        ]
        self.mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("10000")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("5000")

        result = self.use_case.execute(chantier_id=100)

        assert len(result) == 0
        self.mock_alerte_repo.save.assert_not_called()

    def test_both_alerts_when_both_thresholds_exceeded(self):
        """Test: deux alertes quand les deux seuils sont depasses."""
        self._setup_budget()

        # Engage = 420000 -> 84% > 80%
        # Realise = 100000 + 200000 + 120000 = 420000 -> 84% > 80%
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("420000"),  # engage
            Decimal("100000"),  # realise (achats)
        ]
        self.mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("200000")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("120000")

        result = self.use_case.execute(chantier_id=100)

        assert len(result) == 2

    def test_no_budget_raises_error(self):
        """Test: erreur si pas de budget pour le chantier."""
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(chantier_id=100)
        assert "budget" in str(exc_info.value).lower()

    def test_budget_zero_returns_empty(self):
        """Test: pas d'alerte si budget a zero."""
        budget = Budget(
            id=10,
            chantier_id=100,
            montant_initial_ht=Decimal("0"),
            seuil_alerte_pct=Decimal("80"),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        result = self.use_case.execute(chantier_id=100)

        assert len(result) == 0


class TestAcquitterAlerteUseCase:
    """Tests pour le use case d'acquittement d'alerte."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.use_case = AcquitterAlerteUseCase(
            alerte_repository=self.mock_alerte_repo,
            journal_repository=self.mock_journal,
        )

    def test_acquitter_success(self):
        """Test: acquittement reussi d'une alerte."""
        alerte = AlerteDepassement(
            id=1,
            chantier_id=100,
            budget_id=10,
            type_alerte="seuil_engage",
            message="Test alerte",
            pourcentage_atteint=Decimal("85"),
            seuil_configure=Decimal("80"),
            montant_budget_ht=Decimal("500000"),
            montant_atteint_ht=Decimal("425000"),
            est_acquittee=False,
            created_at=datetime.utcnow(),
        )
        # Premier find_by_id (avant acquittement)
        # Deuxieme find_by_id (apres acquittement - recharger)
        alerte_acquittee = AlerteDepassement(
            id=1,
            chantier_id=100,
            budget_id=10,
            type_alerte="seuil_engage",
            message="Test alerte",
            pourcentage_atteint=Decimal("85"),
            seuil_configure=Decimal("80"),
            montant_budget_ht=Decimal("500000"),
            montant_atteint_ht=Decimal("425000"),
            est_acquittee=True,
            acquittee_par=5,
            acquittee_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        self.mock_alerte_repo.find_by_id.side_effect = [alerte, alerte_acquittee]

        result = self.use_case.execute(alerte_id=1, user_id=5)

        assert result.est_acquittee is True
        assert result.acquittee_par == 5
        self.mock_alerte_repo.acquitter.assert_called_once_with(1, 5)
        self.mock_journal.save.assert_called_once()

    def test_acquitter_not_found(self):
        """Test: erreur si alerte non trouvee."""
        self.mock_alerte_repo.find_by_id.return_value = None

        with pytest.raises(AlerteNotFoundError):
            self.use_case.execute(alerte_id=999, user_id=5)

    def test_acquitter_deja_acquittee(self):
        """Test: erreur si alerte deja acquittee."""
        alerte = AlerteDepassement(
            id=1,
            chantier_id=100,
            budget_id=10,
            type_alerte="seuil_engage",
            message="Test",
            est_acquittee=True,
            acquittee_par=5,
            acquittee_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        self.mock_alerte_repo.find_by_id.return_value = alerte

        with pytest.raises(ValueError):
            self.use_case.execute(alerte_id=1, user_id=10)


class TestListAlertesUseCase:
    """Tests pour le use case de listage des alertes."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.use_case = ListAlertesUseCase(
            alerte_repository=self.mock_alerte_repo,
        )

    def test_list_alertes_all(self):
        """Test: listage de toutes les alertes d'un chantier."""
        alertes = [
            AlerteDepassement(
                id=1,
                chantier_id=100,
                budget_id=10,
                type_alerte="seuil_engage",
                message="Alerte 1",
                est_acquittee=False,
                created_at=datetime.utcnow(),
            ),
            AlerteDepassement(
                id=2,
                chantier_id=100,
                budget_id=10,
                type_alerte="seuil_realise",
                message="Alerte 2",
                est_acquittee=True,
                acquittee_par=5,
                acquittee_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_alerte_repo.find_by_chantier_id.return_value = alertes

        result = self.use_case.execute(chantier_id=100)

        assert len(result) == 2
        self.mock_alerte_repo.find_by_chantier_id.assert_called_once_with(100)

    def test_list_alertes_non_acquittees(self):
        """Test: listage des alertes non acquittees."""
        alertes = [
            AlerteDepassement(
                id=1,
                chantier_id=100,
                budget_id=10,
                type_alerte="seuil_engage",
                message="Alerte 1",
                est_acquittee=False,
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_alerte_repo.find_non_acquittees.return_value = alertes

        result = self.use_case.execute(
            chantier_id=100,
            non_acquittees_seulement=True,
        )

        assert len(result) == 1
        assert result[0].est_acquittee is False
        self.mock_alerte_repo.find_non_acquittees.assert_called_once_with(100)

    def test_list_alertes_vide(self):
        """Test: liste vide si aucune alerte."""
        self.mock_alerte_repo.find_by_chantier_id.return_value = []

        result = self.use_case.execute(chantier_id=100)

        assert len(result) == 0


class TestAlertePerteTerminaison:
    """Tests C2: alerte perte a terminaison (marge negative projetee)."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_alerte_repo = Mock(spec=AlerteRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        self.mock_cout_materiel_repo = Mock(spec=CoutMaterielRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = VerifierDepassementUseCase(
            alerte_repository=self.mock_alerte_repo,
            budget_repository=self.mock_budget_repo,
            achat_repository=self.mock_achat_repo,
            cout_mo_repository=self.mock_cout_mo_repo,
            cout_materiel_repository=self.mock_cout_materiel_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def _setup_budget(self, montant_initial=Decimal("500000"), seuil=Decimal("80")):
        """Configure un budget pour les tests."""
        budget = Budget(
            id=10,
            chantier_id=100,
            montant_initial_ht=montant_initial,
            seuil_alerte_pct=seuil,
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        def save_alerte(alerte):
            alerte.id = 1
            return alerte

        self.mock_alerte_repo.save.side_effect = save_alerte
        return budget

    def test_perte_terminaison_quand_realise_depasse_budget(self):
        """Test C2: alerte perte_terminaison quand montant_realise > budget."""
        self._setup_budget(montant_initial=Decimal("500000"), seuil=Decimal("80"))

        # Engage et realise depassent le budget
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("450000"),   # engage (90% > 80% -> seuil_engage)
            Decimal("300000"),   # realise (achats livres+factures)
        ]
        # MO + materiel = 250000 -> total realise = 550000 > 500000 -> perte_terminaison
        self.mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("200000")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("50000")

        result = self.use_case.execute(chantier_id=100)

        # Doit contenir une alerte perte_terminaison parmi les alertes creees
        types_alertes = [
            call.args[0].type_alerte
            for call in self.mock_alerte_repo.save.call_args_list
        ]
        assert "perte_terminaison" in types_alertes

    def test_pas_de_perte_terminaison_quand_realise_sous_budget(self):
        """Test C2: pas d'alerte perte_terminaison quand realise < budget."""
        self._setup_budget(montant_initial=Decimal("500000"), seuil=Decimal("90"))

        # Engage et realise bien en dessous du budget et du seuil
        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("200000"),  # engage (40% < 90%)
            Decimal("150000"),  # realise (achats)
        ]
        self.mock_cout_mo_repo.calculer_cout_chantier.return_value = Decimal("100000")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("50000")
        # total_realise = 300000 < 500000 -> pas de perte_terminaison
        # engage = 200000 = 40% < 90% -> pas de seuil_engage
        # realise = 300000 = 60% < 90% -> pas de seuil_realise

        result = self.use_case.execute(chantier_id=100)

        # Aucune alerte
        assert len(result) == 0

    def test_alerte_resilience_cout_mo_erreur(self):
        """Test FIX-4: si cout_mo leve une erreur, les alertes continuent."""
        self._setup_budget(montant_initial=Decimal("500000"), seuil=Decimal("80"))

        self.mock_achat_repo.somme_by_chantier.side_effect = [
            Decimal("420000"),  # engage = 84% > 80%
            Decimal("300000"),  # realise (achats)
        ]
        # Erreur MO -> doit continuer avec 0
        self.mock_cout_mo_repo.calculer_cout_chantier.side_effect = ValueError("Erreur MO")
        self.mock_cout_materiel_repo.calculer_cout_chantier.return_value = Decimal("5000")

        # Act - ne doit PAS lever d'exception
        result = self.use_case.execute(chantier_id=100)

        # Assert - au moins l'alerte seuil_engage doit exister
        assert len(result) >= 1
