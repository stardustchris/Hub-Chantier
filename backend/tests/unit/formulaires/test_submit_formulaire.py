"""Tests unitaires pour SubmitFormulaireUseCase."""

import pytest
from unittest.mock import Mock
from datetime import datetime

from modules.formulaires.application.use_cases.submit_formulaire import (
    SubmitFormulaireUseCase,
    FormulaireNotFoundError,
    FormulaireNotSubmittableError,
)
from modules.formulaires.application.dtos import SubmitFormulaireDTO
from modules.formulaires.domain.value_objects import StatutFormulaire


def create_mock_formulaire(
    formulaire_id=1,
    statut=StatutFormulaire.BROUILLON,
    est_brouillon=True,
):
    """Helper pour créer un mock de formulaire."""
    mock = Mock()
    mock.id = formulaire_id
    mock.template_id = 10
    mock.chantier_id = 5
    mock.user_id = 3
    mock.statut = statut
    mock.est_brouillon = est_brouillon
    mock.est_soumis = not est_brouillon
    mock.champs = []
    mock.photos = []
    mock.est_signe = False
    mock.signature_url = None
    mock.signature_nom = None
    mock.signature_timestamp = None
    mock.soumis_at = None
    mock.valide_par = None
    mock.valide_at = None
    mock.version = 1
    mock.created_at = datetime.now()
    mock.updated_at = datetime.now()
    return mock


class TestSubmitFormulaireUseCase:
    """Tests pour SubmitFormulaireUseCase."""

    def test_submit_formulaire_success(self):
        """Test soumission réussie."""
        mock_repo = Mock()
        mock_formulaire = create_mock_formulaire()
        mock_repo.find_by_id.return_value = mock_formulaire
        mock_repo.save.return_value = mock_formulaire

        dto = SubmitFormulaireDTO(formulaire_id=1)

        use_case = SubmitFormulaireUseCase(mock_repo)
        result = use_case.execute(dto)

        assert result is not None
        mock_formulaire.soumettre.assert_called_once()
        mock_repo.save.assert_called_once()

    def test_submit_formulaire_not_found(self):
        """Test erreur si formulaire non trouvé."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        dto = SubmitFormulaireDTO(formulaire_id=999)

        use_case = SubmitFormulaireUseCase(mock_repo)

        with pytest.raises(FormulaireNotFoundError, match="non trouve"):
            use_case.execute(dto)

    def test_submit_formulaire_already_submitted(self):
        """Test erreur si formulaire déjà soumis."""
        mock_repo = Mock()
        mock_formulaire = create_mock_formulaire(est_brouillon=False)
        mock_repo.find_by_id.return_value = mock_formulaire

        dto = SubmitFormulaireDTO(formulaire_id=1)

        use_case = SubmitFormulaireUseCase(mock_repo)

        with pytest.raises(FormulaireNotSubmittableError, match="deja ete soumis"):
            use_case.execute(dto)

    def test_submit_formulaire_with_signature(self):
        """Test soumission avec signature."""
        mock_repo = Mock()
        mock_formulaire = create_mock_formulaire()
        mock_formulaire.signature_timestamp = datetime.now()
        mock_repo.find_by_id.return_value = mock_formulaire
        mock_repo.save.return_value = mock_formulaire

        dto = SubmitFormulaireDTO(
            formulaire_id=1,
            signature_url="https://example.com/sig.png",
            signature_nom="M. Dupont",
        )

        use_case = SubmitFormulaireUseCase(mock_repo)
        result = use_case.execute(dto)

        assert result is not None
        mock_formulaire.signer.assert_called_once_with(
            "https://example.com/sig.png", "M. Dupont"
        )

    def test_submit_formulaire_with_event_publisher(self):
        """Test soumission avec publication d'événement."""
        mock_repo = Mock()
        mock_formulaire = create_mock_formulaire()
        mock_formulaire.soumis_at = datetime.now()
        mock_repo.find_by_id.return_value = mock_formulaire
        mock_repo.save.return_value = mock_formulaire
        mock_publisher = Mock()

        dto = SubmitFormulaireDTO(formulaire_id=1)

        use_case = SubmitFormulaireUseCase(mock_repo, event_publisher=mock_publisher)
        use_case.execute(dto)

        mock_publisher.assert_called_once()
        event = mock_publisher.call_args[0][0]
        assert event.formulaire_id == 1

    def test_submit_formulaire_signature_event(self):
        """Test publication événement signature."""
        mock_repo = Mock()
        mock_formulaire = create_mock_formulaire()
        mock_formulaire.signature_timestamp = datetime.now()
        mock_repo.find_by_id.return_value = mock_formulaire
        mock_repo.save.return_value = mock_formulaire
        mock_publisher = Mock()

        dto = SubmitFormulaireDTO(
            formulaire_id=1,
            signature_url="https://example.com/sig.png",
            signature_nom="M. Dupont",
        )

        use_case = SubmitFormulaireUseCase(mock_repo, event_publisher=mock_publisher)
        use_case.execute(dto)

        # Deux événements: signature + soumission
        assert mock_publisher.call_count == 2


class TestValidateFormulaire:
    """Tests pour la validation de formulaire."""

    def test_validate_formulaire_success(self):
        """Test validation réussie."""
        mock_repo = Mock()
        mock_formulaire = create_mock_formulaire(est_brouillon=False)
        mock_formulaire.est_soumis = True
        mock_repo.find_by_id.return_value = mock_formulaire
        mock_repo.save.return_value = mock_formulaire

        use_case = SubmitFormulaireUseCase(mock_repo)
        result = use_case.validate(formulaire_id=1, valideur_id=5)

        assert result is not None
        mock_formulaire.valider.assert_called_once_with(5)

    def test_validate_formulaire_not_found(self):
        """Test erreur si formulaire non trouvé."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        use_case = SubmitFormulaireUseCase(mock_repo)

        with pytest.raises(FormulaireNotFoundError, match="non trouve"):
            use_case.validate(formulaire_id=999, valideur_id=5)
