"""Tests unitaires pour les Use Cases Achat du module Financier."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, call

from modules.financier.domain.entities import (
    Achat,
    Fournisseur,
    Budget,
    AchatValidationError,
    TransitionStatutAchatInvalideError,
)
from modules.financier.domain.repositories import (
    AchatRepository,
    FournisseurRepository,
    BudgetRepository,
    JournalFinancierRepository,
)
from modules.financier.domain.value_objects import (
    TypeAchat,
    StatutAchat,
    UniteMesure,
    TypeFournisseur,
)
from modules.financier.application.ports.event_bus import EventBus
from modules.financier.application.dtos import (
    AchatCreateDTO,
    AchatUpdateDTO,
)
from modules.financier.application.use_cases.achat_use_cases import (
    CreateAchatUseCase,
    UpdateAchatUseCase,
    ValiderAchatUseCase,
    RefuserAchatUseCase,
    PasserCommandeAchatUseCase,
    MarquerLivreAchatUseCase,
    MarquerFactureAchatUseCase,
    GetAchatUseCase,
    ListAchatsUseCase,
    ListAchatsEnAttenteUseCase,
    AchatNotFoundError,
    FournisseurInactifError,
)
from modules.financier.application.use_cases.fournisseur_use_cases import (
    FournisseurNotFoundError,
)


class TestCreateAchatUseCase:
    """Tests pour le use case de creation d'achat."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_fournisseur_repo = Mock(spec=FournisseurRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateAchatUseCase(
            achat_repository=self.mock_achat_repo,
            fournisseur_repository=self.mock_fournisseur_repo,
            budget_repository=self.mock_budget_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def _make_dto(self, **kwargs):
        """Cree un AchatCreateDTO avec des valeurs par defaut."""
        defaults = {
            "chantier_id": 100,
            "libelle": "Ciment CEM II 25kg",
            "quantite": Decimal("10"),
            "prix_unitaire_ht": Decimal("8.50"),
            "taux_tva": Decimal("20"),
        }
        defaults.update(kwargs)
        return AchatCreateDTO(**defaults)

    def test_create_achat_success(self):
        """Test: creation reussie d'un achat."""
        dto = self._make_dto()

        # Pas de fournisseur
        # Budget avec seuil validation = 1000 (montant 85 < 1000 -> auto-valide)
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            seuil_validation_achat=Decimal("1000"),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        def save_side_effect(achat):
            achat.id = 1
            return achat

        self.mock_achat_repo.save.side_effect = save_side_effect
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("85")

        result = self.use_case.execute(dto, demandeur_id=10)

        assert result.id == 1
        assert result.libelle == "Ciment CEM II 25kg"
        # Auto-validation car montant (85) < seuil (1000)
        assert result.statut == "valide"
        self.mock_achat_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()

    def test_create_achat_necessitant_validation(self):
        """Test: achat au-dessus du seuil reste en demande."""
        dto = self._make_dto(
            quantite=Decimal("200"),
            prix_unitaire_ht=Decimal("10"),
        )
        # Montant = 2000 >= seuil 1000 -> pas d'auto-validation
        budget = Budget(
            id=1,
            chantier_id=100,
            montant_initial_ht=Decimal("500000"),
            seuil_validation_achat=Decimal("1000"),
        )
        self.mock_budget_repo.find_by_chantier_id.return_value = budget

        def save_side_effect(achat):
            achat.id = 1
            return achat

        self.mock_achat_repo.save.side_effect = save_side_effect
        self.mock_achat_repo.somme_by_chantier.return_value = Decimal("2000")

        result = self.use_case.execute(dto, demandeur_id=10)

        assert result.statut == "demande"

    def test_create_achat_with_fournisseur(self):
        """Test: creation avec fournisseur actif."""
        dto = self._make_dto(fournisseur_id=5)

        fournisseur = Fournisseur(
            id=5,
            raison_sociale="Materiaux du Sud",
            actif=True,
        )
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        def save_side_effect(achat):
            achat.id = 1
            return achat

        self.mock_achat_repo.save.side_effect = save_side_effect

        result = self.use_case.execute(dto, demandeur_id=10)

        assert result.fournisseur_nom == "Materiaux du Sud"

    def test_create_achat_fournisseur_not_found(self):
        """Test: erreur si fournisseur non trouve."""
        dto = self._make_dto(fournisseur_id=999)

        self.mock_fournisseur_repo.find_by_id.return_value = None

        with pytest.raises(FournisseurNotFoundError):
            self.use_case.execute(dto, demandeur_id=10)

    def test_create_achat_fournisseur_inactif(self):
        """Test: erreur si fournisseur inactif."""
        dto = self._make_dto(fournisseur_id=5)

        fournisseur = Fournisseur(
            id=5,
            raison_sociale="Inactif SARL",
            actif=False,
        )
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        with pytest.raises(FournisseurInactifError):
            self.use_case.execute(dto, demandeur_id=10)

    def test_create_achat_sans_budget_pas_auto_validation(self):
        """Test: pas d'auto-validation si pas de budget pour le chantier."""
        dto = self._make_dto()

        self.mock_budget_repo.find_by_chantier_id.return_value = None

        def save_side_effect(achat):
            achat.id = 1
            return achat

        self.mock_achat_repo.save.side_effect = save_side_effect

        result = self.use_case.execute(dto, demandeur_id=10)

        assert result.statut == "demande"


class TestUpdateAchatUseCase:
    """Tests pour le use case de mise a jour d'achat."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_fournisseur_repo = Mock(spec=FournisseurRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        # Par défaut, pas de fournisseur (pas de lookup)
        self.mock_fournisseur_repo.find_by_id.return_value = None
        self.use_case = UpdateAchatUseCase(
            achat_repository=self.mock_achat_repo,
            fournisseur_repository=self.mock_fournisseur_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def _make_achat(self, statut=StatutAchat.DEMANDE):
        """Cree un achat existant pour les tests."""
        return Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("8.50"),
            taux_tva=Decimal("20"),
            statut=statut,
            created_at=datetime.utcnow(),
        )

    def test_update_achat_success(self):
        """Test: mise a jour reussie d'un achat en statut demande."""
        existing = self._make_achat()
        self.mock_achat_repo.find_by_id.return_value = existing
        self.mock_achat_repo.save.return_value = existing

        dto = AchatUpdateDTO(libelle="Ciment modifie")
        result = self.use_case.execute(1, dto, updated_by=10)

        assert result.libelle == "Ciment modifie"
        self.mock_achat_repo.save.assert_called_once()

    def test_update_achat_not_found(self):
        """Test: erreur si achat non trouve."""
        self.mock_achat_repo.find_by_id.return_value = None

        dto = AchatUpdateDTO(libelle="Test")

        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(999, dto, updated_by=10)

    def test_update_achat_statut_valide_interdit(self):
        """Test: erreur si achat deja valide."""
        existing = self._make_achat(statut=StatutAchat.VALIDE)
        self.mock_achat_repo.find_by_id.return_value = existing

        dto = AchatUpdateDTO(libelle="Test")

        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(1, dto, updated_by=10)
        assert "demande" in str(exc_info.value).lower()

    def test_update_achat_statut_commande_interdit(self):
        """Test: erreur si achat en commande."""
        existing = self._make_achat(statut=StatutAchat.COMMANDE)
        self.mock_achat_repo.find_by_id.return_value = existing

        dto = AchatUpdateDTO(libelle="Test")

        with pytest.raises(ValueError):
            self.use_case.execute(1, dto, updated_by=10)


class TestValiderAchatUseCase:
    """Tests pour le use case de validation d'achat."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = ValiderAchatUseCase(
            achat_repository=self.mock_achat_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_valider_achat_success(self):
        """Test: validation reussie d'un achat (demande -> valide)."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.DEMANDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat
        self.mock_achat_repo.save.return_value = achat

        result = self.use_case.execute(achat_id=1, valideur_id=5)

        assert result.statut == "valide"
        self.mock_achat_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_valider_achat_not_found(self):
        """Test: erreur si achat non trouve."""
        self.mock_achat_repo.find_by_id.return_value = None

        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(achat_id=999, valideur_id=5)

    def test_valider_achat_deja_valide(self):
        """Test: erreur si achat deja valide."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.VALIDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        with pytest.raises(TransitionStatutAchatInvalideError):
            self.use_case.execute(achat_id=1, valideur_id=5)


class TestRefuserAchatUseCase:
    """Tests pour le use case de refus d'achat."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = RefuserAchatUseCase(
            achat_repository=self.mock_achat_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_refuser_achat_success(self):
        """Test: refus reussi d'un achat avec motif."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.DEMANDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat
        self.mock_achat_repo.save.return_value = achat

        result = self.use_case.execute(
            achat_id=1,
            valideur_id=5,
            motif="Trop cher",
        )

        assert result.statut == "refuse"
        assert result.motif_refus == "Trop cher"
        self.mock_achat_repo.save.assert_called_once()
        self.mock_journal.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()

    def test_refuser_achat_not_found(self):
        """Test: erreur si achat non trouve."""
        self.mock_achat_repo.find_by_id.return_value = None

        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(achat_id=999, valideur_id=5, motif="Motif")

    def test_refuser_achat_sans_motif(self):
        """Test: erreur si motif vide."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.DEMANDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        with pytest.raises(AchatValidationError):
            self.use_case.execute(achat_id=1, valideur_id=5, motif="")

    def test_refuser_achat_deja_commande(self):
        """Test: erreur si achat en statut commande."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.COMMANDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        with pytest.raises(TransitionStatutAchatInvalideError):
            self.use_case.execute(achat_id=1, valideur_id=5, motif="Motif")


class TestPasserCommandeAchatUseCase:
    """Tests pour le use case de passage en commande."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = PasserCommandeAchatUseCase(
            achat_repository=self.mock_achat_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_passer_commande_success(self):
        """Test: passage en commande reussi (valide -> commande)."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.VALIDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat
        self.mock_achat_repo.save.return_value = achat

        result = self.use_case.execute(achat_id=1, user_id=10)

        assert result.statut == "commande"
        assert result.date_commande is not None
        self.mock_achat_repo.save.assert_called_once()

    def test_passer_commande_not_found(self):
        """Test: erreur si achat non trouve."""
        self.mock_achat_repo.find_by_id.return_value = None

        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(achat_id=999, user_id=10)

    def test_passer_commande_depuis_demande(self):
        """Test: erreur si achat en statut demande."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.DEMANDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        with pytest.raises(TransitionStatutAchatInvalideError):
            self.use_case.execute(achat_id=1, user_id=10)


class TestMarquerLivreAchatUseCase:
    """Tests pour le use case de marquage comme livre."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = MarquerLivreAchatUseCase(
            achat_repository=self.mock_achat_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_marquer_livre_success(self):
        """Test: marquage comme livre reussi (commande -> livre)."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.COMMANDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat
        self.mock_achat_repo.save.return_value = achat

        result = self.use_case.execute(achat_id=1, user_id=10)

        assert result.statut == "livre"

    def test_marquer_livre_not_found(self):
        """Test: erreur si achat non trouve."""
        self.mock_achat_repo.find_by_id.return_value = None

        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(achat_id=999, user_id=10)

    def test_marquer_livre_depuis_valide(self):
        """Test: erreur si achat en statut valide."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.VALIDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        with pytest.raises(TransitionStatutAchatInvalideError):
            self.use_case.execute(achat_id=1, user_id=10)


class TestMarquerFactureAchatUseCase:
    """Tests pour le use case de marquage comme facture."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = MarquerFactureAchatUseCase(
            achat_repository=self.mock_achat_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

    def test_marquer_facture_success(self):
        """Test: marquage comme facture reussi (livre -> facture)."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.LIVRE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat
        self.mock_achat_repo.save.return_value = achat

        result = self.use_case.execute(
            achat_id=1,
            numero_facture="FAC-2026-001",
            user_id=10,
        )

        assert result.statut == "facture"
        assert result.numero_facture == "FAC-2026-001"

    def test_marquer_facture_not_found(self):
        """Test: erreur si achat non trouve."""
        self.mock_achat_repo.find_by_id.return_value = None

        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(
                achat_id=999,
                numero_facture="FAC-001",
                user_id=10,
            )

    def test_marquer_facture_sans_numero(self):
        """Test: erreur si numero de facture vide."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.LIVRE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        with pytest.raises(AchatValidationError):
            self.use_case.execute(
                achat_id=1,
                numero_facture="",
                user_id=10,
            )

    def test_marquer_facture_depuis_commande(self):
        """Test: erreur si achat en statut commande."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            statut=StatutAchat.COMMANDE,
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        with pytest.raises(TransitionStatutAchatInvalideError):
            self.use_case.execute(
                achat_id=1,
                numero_facture="FAC-001",
                user_id=10,
            )


class TestGetAchatUseCase:
    """Tests pour le use case de recuperation d'un achat."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.use_case = GetAchatUseCase(
            achat_repository=self.mock_achat_repo,
        )

    def test_get_achat_success(self):
        """Test: recuperation reussie d'un achat."""
        achat = Achat(
            id=1,
            chantier_id=100,
            libelle="Ciment",
            quantite=Decimal("10"),
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("20"),
            created_at=datetime.utcnow(),
        )
        self.mock_achat_repo.find_by_id.return_value = achat

        result = self.use_case.execute(1)

        assert result.id == 1
        assert result.libelle == "Ciment"

    def test_get_achat_not_found(self):
        """Test: erreur si achat non trouve."""
        self.mock_achat_repo.find_by_id.return_value = None

        with pytest.raises(AchatNotFoundError):
            self.use_case.execute(999)


class TestListAchatsUseCase:
    """Tests pour le use case de listage des achats."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.use_case = ListAchatsUseCase(
            achat_repository=self.mock_achat_repo,
        )

    def test_list_achats_by_chantier(self):
        """Test: listage des achats par chantier."""
        achats = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Ciment",
                quantite=Decimal("10"),
                prix_unitaire_ht=Decimal("100"),
                taux_tva=Decimal("20"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_achat_repo.find_by_chantier.return_value = achats
        self.mock_achat_repo.count_by_chantier.return_value = 1

        result = self.use_case.execute(chantier_id=100)

        assert len(result.items) == 1
        assert result.total == 1

    def test_list_achats_by_fournisseur(self):
        """Test: listage des achats par fournisseur."""
        achats = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Ciment",
                quantite=Decimal("10"),
                prix_unitaire_ht=Decimal("100"),
                taux_tva=Decimal("20"),
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_achat_repo.find_by_fournisseur.return_value = achats

        result = self.use_case.execute(fournisseur_id=5)

        assert len(result.items) == 1
        self.mock_achat_repo.find_by_fournisseur.assert_called_once()


class TestListAchatsEnAttenteUseCase:
    """Tests pour le use case de listage des achats en attente."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.use_case = ListAchatsEnAttenteUseCase(
            achat_repository=self.mock_achat_repo,
        )

    def test_list_achats_en_attente(self):
        """Test: listage des achats en attente de validation."""
        achats = [
            Achat(
                id=1,
                chantier_id=100,
                libelle="Ciment",
                quantite=Decimal("10"),
                prix_unitaire_ht=Decimal("100"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.DEMANDE,
                created_at=datetime.utcnow(),
            ),
        ]
        self.mock_achat_repo.find_en_attente_validation.return_value = achats

        result = self.use_case.execute()

        assert len(result.items) == 1
        assert result.items[0].statut == "demande"

    def test_list_achats_en_attente_vide(self):
        """Test: listage vide si aucun achat en attente."""
        self.mock_achat_repo.find_en_attente_validation.return_value = []

        result = self.use_case.execute()

        assert len(result.items) == 0


class TestAutoliquidationTVA:
    """Tests pour l'autoliquidation TVA (CGI art. 283-2 nonies).

    Quand un fournisseur est un sous-traitant, le taux de TVA doit etre
    force a 0% lors de la creation d'un achat (autoliquidation).
    """

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_fournisseur_repo = Mock(spec=FournisseurRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateAchatUseCase(
            achat_repository=self.mock_achat_repo,
            fournisseur_repository=self.mock_fournisseur_repo,
            budget_repository=self.mock_budget_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

        # Pas de budget -> pas d'auto-validation
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        def save_side_effect(achat):
            achat.id = 1
            return achat

        self.mock_achat_repo.save.side_effect = save_side_effect

    def _make_dto(self, **kwargs):
        """Cree un AchatCreateDTO avec des valeurs par defaut."""
        defaults = {
            "chantier_id": 100,
            "libelle": "Prestation sous-traitance",
            "quantite": Decimal("1"),
            "prix_unitaire_ht": Decimal("5000"),
            "taux_tva": Decimal("20"),
        }
        defaults.update(kwargs)
        return AchatCreateDTO(**defaults)

    def test_achat_sous_traitant_force_tva_zero(self):
        """Test: achat avec fournisseur sous-traitant -> taux_tva force a 0%.

        CGI art. 283-2 nonies : le sous-traitant facture HT,
        le donneur d'ordre autoliquide la TVA.
        """
        dto = self._make_dto(fournisseur_id=10, taux_tva=Decimal("20"))

        fournisseur = Fournisseur(
            id=10,
            raison_sociale="BTP Sous-Traitance SARL",
            type=TypeFournisseur.SOUS_TRAITANT,
            actif=True,
        )
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        result = self.use_case.execute(dto, demandeur_id=1)

        assert result.taux_tva == "0"

    def test_achat_negoce_garde_tva_normale(self):
        """Test: achat avec fournisseur negoce -> taux_tva reste a 20%."""
        dto = self._make_dto(fournisseur_id=20, taux_tva=Decimal("20"))

        fournisseur = Fournisseur(
            id=20,
            raison_sociale="Materiaux du Sud",
            type=TypeFournisseur.NEGOCE_MATERIAUX,
            actif=True,
        )
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        result = self.use_case.execute(dto, demandeur_id=1)

        assert result.taux_tva == "20"

    def test_achat_sans_fournisseur_garde_tva(self):
        """Test: achat sans fournisseur -> taux_tva reste celle passee."""
        dto = self._make_dto(taux_tva=Decimal("10"))

        result = self.use_case.execute(dto, demandeur_id=1)

        assert result.taux_tva == "10"


# ============================================================
# Item 6 - Tests autoliquidation TVA au niveau use case
# ============================================================


class TestCreerAchatAutoliquidationTVA:
    """Tests supplementaires pour l'autoliquidation TVA (CGI art. 283-2 nonies).

    Verifie que lors de la creation d'un achat :
    - Le taux TVA est force a 0% pour les sous-traitants
    - Le type d'achat est automatiquement SOUS_TRAITANCE
    - Les fournisseurs normaux gardent leur TVA
    """

    def setup_method(self):
        """Configuration avant chaque test."""
        self.mock_achat_repo = Mock(spec=AchatRepository)
        self.mock_fournisseur_repo = Mock(spec=FournisseurRepository)
        self.mock_budget_repo = Mock(spec=BudgetRepository)
        self.mock_journal = Mock(spec=JournalFinancierRepository)
        self.mock_event_bus = Mock(spec=EventBus)
        self.use_case = CreateAchatUseCase(
            achat_repository=self.mock_achat_repo,
            fournisseur_repository=self.mock_fournisseur_repo,
            budget_repository=self.mock_budget_repo,
            journal_repository=self.mock_journal,
            event_bus=self.mock_event_bus,
        )

        # Pas de budget -> pas d'auto-validation
        self.mock_budget_repo.find_by_chantier_id.return_value = None

        def save_side_effect(achat):
            achat.id = 1
            return achat

        self.mock_achat_repo.save.side_effect = save_side_effect

    def _make_dto(self, **kwargs):
        """Cree un AchatCreateDTO avec des valeurs par defaut."""
        defaults = {
            "chantier_id": 100,
            "libelle": "Prestation sous-traitance gros oeuvre",
            "quantite": Decimal("1"),
            "prix_unitaire_ht": Decimal("5000"),
            "taux_tva": Decimal("20"),
        }
        defaults.update(kwargs)
        return AchatCreateDTO(**defaults)

    def test_creer_achat_sous_traitant_force_tva_zero(self):
        """Test: creer un achat avec fournisseur sous-traitant -> taux_tva == 0.

        CGI art. 283-2 nonies : le sous-traitant facture HT,
        le donneur d'ordre autoliquide la TVA.
        """
        dto = self._make_dto(fournisseur_id=10, taux_tva=Decimal("20"))

        fournisseur = Fournisseur(
            id=10,
            raison_sociale="Maconnerie Dupont",
            type=TypeFournisseur.SOUS_TRAITANT,
            actif=True,
        )
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        result = self.use_case.execute(dto, demandeur_id=1)

        assert result.taux_tva == "0"

    def test_creer_achat_sous_traitant_force_type_sous_traitance(self):
        """Test: creer un achat avec fournisseur sous-traitant -> type_achat == SOUS_TRAITANCE.

        Quand le fournisseur est un sous-traitant, le type d'achat
        est automatiquement force a SOUS_TRAITANCE, meme si le DTO
        contenait un autre type.
        """
        # Le DTO ne specifie pas de type_achat -> default MATERIAU
        dto = self._make_dto(fournisseur_id=10)

        fournisseur = Fournisseur(
            id=10,
            raison_sociale="Maconnerie Dupont",
            type=TypeFournisseur.SOUS_TRAITANT,
            actif=True,
        )
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        result = self.use_case.execute(dto, demandeur_id=1)

        assert result.type_achat == "sous_traitance"

    def test_creer_achat_fournisseur_normal_garde_tva(self):
        """Test: creer un achat avec fournisseur non sous-traitant -> taux_tva reste a 20%.

        Un fournisseur de type negoce materiaux facture normalement avec TVA.
        """
        dto = self._make_dto(fournisseur_id=20, taux_tva=Decimal("20"))

        fournisseur = Fournisseur(
            id=20,
            raison_sociale="Materiaux du Sud",
            type=TypeFournisseur.NEGOCE_MATERIAUX,
            actif=True,
        )
        self.mock_fournisseur_repo.find_by_id.return_value = fournisseur

        result = self.use_case.execute(dto, demandeur_id=1)

        assert result.taux_tva == "20"
