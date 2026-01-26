"""Tests unitaires pour les use cases de signatures."""

import pytest
from unittest.mock import Mock

from modules.interventions.application.use_cases.signature_use_cases import (
    AddSignatureUseCase,
    ListSignaturesUseCase,
)
from modules.interventions.application.dtos import CreateSignatureDTO
from modules.interventions.domain.entities import SignatureIntervention, TypeSignataire


class TestAddSignatureUseCase:
    """Tests de AddSignatureUseCase."""

    def test_add_signature_client_success(self):
        """Test ajout signature client."""
        mock_repo = Mock()
        mock_repo.get_signature_client.return_value = None
        saved_signature = Mock()
        saved_signature.id = 1
        mock_repo.save.return_value = saved_signature

        use_case = AddSignatureUseCase(repository=mock_repo)
        dto = CreateSignatureDTO(
            type_signataire="client",
            nom_signataire="M. Dupont",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        result = use_case.execute(
            intervention_id=1,
            dto=dto,
            ip_address="192.168.1.1",
        )

        assert result.id == 1
        mock_repo.get_signature_client.assert_called_once_with(1)
        mock_repo.save.assert_called_once()

    def test_add_signature_client_already_exists(self):
        """Test erreur si signature client existe déjà."""
        mock_repo = Mock()
        mock_repo.get_signature_client.return_value = Mock()  # Existe déjà

        use_case = AddSignatureUseCase(repository=mock_repo)
        dto = CreateSignatureDTO(
            type_signataire="client",
            nom_signataire="M. Dupont",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        with pytest.raises(ValueError, match="signature client existe deja"):
            use_case.execute(intervention_id=1, dto=dto)

    def test_add_signature_technicien_success(self):
        """Test ajout signature technicien."""
        mock_repo = Mock()
        mock_repo.get_signature_technicien.return_value = None
        saved_signature = Mock()
        saved_signature.id = 2
        mock_repo.save.return_value = saved_signature

        use_case = AddSignatureUseCase(repository=mock_repo)
        dto = CreateSignatureDTO(
            type_signataire="technicien",
            nom_signataire="Jean Martin",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        result = use_case.execute(
            intervention_id=1,
            dto=dto,
            utilisateur_id=5,
            ip_address="192.168.1.2",
        )

        assert result.id == 2
        mock_repo.get_signature_technicien.assert_called_once_with(1, 5)
        mock_repo.save.assert_called_once()

    def test_add_signature_technicien_without_user_id(self):
        """Test erreur si utilisateur_id manquant pour technicien."""
        mock_repo = Mock()

        use_case = AddSignatureUseCase(repository=mock_repo)
        dto = CreateSignatureDTO(
            type_signataire="technicien",
            nom_signataire="Jean Martin",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        with pytest.raises(ValueError, match="ID utilisateur est obligatoire"):
            use_case.execute(
                intervention_id=1,
                dto=dto,
                utilisateur_id=None,
            )

    def test_add_signature_technicien_already_signed(self):
        """Test erreur si technicien a déjà signé."""
        mock_repo = Mock()
        mock_repo.get_signature_technicien.return_value = Mock()  # Existe déjà

        use_case = AddSignatureUseCase(repository=mock_repo)
        dto = CreateSignatureDTO(
            type_signataire="technicien",
            nom_signataire="Jean Martin",
            signature_data="data:image/png;base64,iVBORw0...",
        )

        with pytest.raises(ValueError, match="technicien a deja signe"):
            use_case.execute(
                intervention_id=1,
                dto=dto,
                utilisateur_id=5,
            )

    def test_add_signature_with_geolocation(self):
        """Test ajout signature avec géolocalisation."""
        mock_repo = Mock()
        mock_repo.get_signature_client.return_value = None
        saved_signature = Mock()
        saved_signature.id = 1
        mock_repo.save.return_value = saved_signature

        use_case = AddSignatureUseCase(repository=mock_repo)
        dto = CreateSignatureDTO(
            type_signataire="client",
            nom_signataire="M. Dupont",
            signature_data="data:image/png;base64,iVBORw0...",
            latitude=48.8566,
            longitude=2.3522,
        )

        use_case.execute(intervention_id=1, dto=dto)

        saved_call = mock_repo.save.call_args[0][0]
        assert saved_call.latitude == 48.8566
        assert saved_call.longitude == 2.3522


class TestListSignaturesUseCase:
    """Tests de ListSignaturesUseCase."""

    def test_list_signatures_empty(self):
        """Test liste vide."""
        mock_repo = Mock()
        mock_repo.list_by_intervention.return_value = []

        use_case = ListSignaturesUseCase(repository=mock_repo)
        result = use_case.execute(intervention_id=1)

        assert result == []
        mock_repo.list_by_intervention.assert_called_once_with(1)

    def test_list_signatures_with_results(self):
        """Test liste avec résultats."""
        mock_repo = Mock()
        mock_sig1 = Mock()
        mock_sig1.type_signataire = TypeSignataire.CLIENT
        mock_sig2 = Mock()
        mock_sig2.type_signataire = TypeSignataire.TECHNICIEN
        mock_repo.list_by_intervention.return_value = [mock_sig1, mock_sig2]

        use_case = ListSignaturesUseCase(repository=mock_repo)
        result = use_case.execute(intervention_id=1)

        assert len(result) == 2

    def test_has_all_signatures_complete(self):
        """Test vérification signatures complètes."""
        mock_repo = Mock()
        mock_repo.has_signature_client.return_value = True
        mock_repo.has_all_signatures_techniciens.return_value = True

        use_case = ListSignaturesUseCase(repository=mock_repo)
        result = use_case.has_all_signatures(intervention_id=1)

        assert result["has_signature_client"] is True
        assert result["has_all_signatures_techniciens"] is True
        assert result["complete"] is True

    def test_has_all_signatures_missing_client(self):
        """Test vérification signatures - client manquant."""
        mock_repo = Mock()
        mock_repo.has_signature_client.return_value = False
        mock_repo.has_all_signatures_techniciens.return_value = True

        use_case = ListSignaturesUseCase(repository=mock_repo)
        result = use_case.has_all_signatures(intervention_id=1)

        assert result["has_signature_client"] is False
        assert result["complete"] is False

    def test_has_all_signatures_missing_technicians(self):
        """Test vérification signatures - techniciens manquants."""
        mock_repo = Mock()
        mock_repo.has_signature_client.return_value = True
        mock_repo.has_all_signatures_techniciens.return_value = False

        use_case = ListSignaturesUseCase(repository=mock_repo)
        result = use_case.has_all_signatures(intervention_id=1)

        assert result["has_all_signatures_techniciens"] is False
        assert result["complete"] is False
