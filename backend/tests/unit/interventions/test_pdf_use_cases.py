"""Tests unitaires pour GenerateInterventionPDFUseCase.

INT-14: Rapport PDF - Generation automatique.
INT-15: Selection posts pour rapport.
"""

import pytest
from datetime import datetime, date, time
from unittest.mock import MagicMock, patch

from modules.interventions.application.use_cases.pdf_use_cases import (
    GenerateInterventionPDFUseCase,
    GenerateInterventionPDFError,
    InterventionPDFOptionsDTO,
)
from modules.interventions.domain.entities import (
    Intervention,
    AffectationIntervention,
    InterventionMessage,
    TypeMessage,
    SignatureIntervention,
    TypeSignataire,
)
from modules.interventions.domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _make_intervention(**kwargs) -> Intervention:
    """Factory pour creer une intervention de test."""
    defaults = {
        "id": 1,
        "code": "INT-2026-0001",
        "type_intervention": TypeIntervention.SAV,
        "statut": StatutIntervention.TERMINEE,
        "priorite": PrioriteIntervention.NORMALE,
        "client_nom": "M. Dupont",
        "client_adresse": "15 rue des Lilas, 69003 Lyon",
        "client_telephone": "06 12 34 56 78",
        "client_email": "dupont@email.com",
        "description": "Fuite sur canalisation cuisine",
        "travaux_realises": "Remplacement joint + resserrage raccord",
        "anomalies": None,
        "date_planifiee": date(2026, 2, 10),
        "heure_debut": time(9, 0),
        "heure_fin": time(12, 0),
        "heure_debut_reelle": time(9, 15),
        "heure_fin_reelle": time(11, 45),
        "created_by": 1,
    }
    defaults.update(kwargs)
    return Intervention(**defaults)


def _make_affectation(
    intervention_id: int = 1,
    utilisateur_id: int = 10,
    est_principal: bool = True,
) -> AffectationIntervention:
    """Factory pour creer une affectation de test."""
    return AffectationIntervention(
        id=1,
        intervention_id=intervention_id,
        utilisateur_id=utilisateur_id,
        est_principal=est_principal,
        created_by=1,
    )


def _make_message(
    intervention_id: int = 1,
    type_msg: TypeMessage = TypeMessage.COMMENTAIRE,
    contenu: str = "Travaux en cours",
    photos: list = None,
    inclure_rapport: bool = True,
) -> InterventionMessage:
    """Factory pour creer un message de test."""
    msg = InterventionMessage(
        id=1,
        intervention_id=intervention_id,
        auteur_id=10,
        type_message=type_msg,
        contenu=contenu,
        photos_urls=photos or [],
        inclure_rapport=inclure_rapport,
    )
    return msg


def _make_signature(
    intervention_id: int = 1,
    type_sig: TypeSignataire = TypeSignataire.CLIENT,
    nom: str = "M. Dupont",
) -> SignatureIntervention:
    """Factory pour creer une signature de test."""
    kwargs = {
        "id": 1,
        "intervention_id": intervention_id,
        "type_signataire": type_sig,
        "nom_signataire": nom,
        "signature_data": "data:image/png;base64,iVBOR...",
    }
    if type_sig == TypeSignataire.TECHNICIEN:
        kwargs["utilisateur_id"] = 10
    return SignatureIntervention(**kwargs)


def _make_use_case():
    """Cree un use case avec des mocks."""
    intervention_repo = MagicMock()
    affectation_repo = MagicMock()
    message_repo = MagicMock()
    signature_repo = MagicMock()
    pdf_generator = MagicMock()

    use_case = GenerateInterventionPDFUseCase(
        intervention_repo=intervention_repo,
        affectation_repo=affectation_repo,
        message_repo=message_repo,
        signature_repo=signature_repo,
        pdf_generator=pdf_generator,
    )

    return use_case, intervention_repo, affectation_repo, message_repo, signature_repo, pdf_generator


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestGenerateInterventionPDFUseCase:
    """Tests pour GenerateInterventionPDFUseCase."""

    def test_execute_basic_success(self):
        """Test: generation PDF basique avec options par defaut."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        intervention = _make_intervention()
        techniciens = [_make_affectation()]
        messages = [_make_message()]
        signatures = [_make_signature()]

        int_repo.get_by_id.return_value = intervention
        aff_repo.list_by_intervention.return_value = techniciens
        msg_repo.list_for_rapport.return_value = messages
        sig_repo.list_by_intervention.return_value = signatures
        pdf_gen.generate_intervention_pdf.return_value = b"%PDF-fake-content"

        pdf_bytes, filename = use_case.execute(1)

        assert pdf_bytes == b"%PDF-fake-content"
        assert filename == "rapport_INT-2026-0001.pdf"

        # Verifie les appels aux repositories
        int_repo.get_by_id.assert_called_once_with(1)
        aff_repo.list_by_intervention.assert_called_once_with(1)
        msg_repo.list_for_rapport.assert_called_once_with(1)
        sig_repo.list_by_intervention.assert_called_once_with(1)

        # Verifie l'appel au generateur PDF
        pdf_gen.generate_intervention_pdf.assert_called_once()
        call_kwargs = pdf_gen.generate_intervention_pdf.call_args
        assert call_kwargs.kwargs["intervention"] == intervention
        assert call_kwargs.kwargs["techniciens"] == techniciens
        assert call_kwargs.kwargs["signatures"] == signatures

    def test_execute_intervention_not_found(self):
        """Test: ValueError si l'intervention n'existe pas."""
        use_case, int_repo, *_ = _make_use_case()
        int_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="non trouvee"):
            use_case.execute(999)

    def test_execute_pdf_generation_error(self):
        """Test: GenerateInterventionPDFError si la generation echoue."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        int_repo.get_by_id.return_value = _make_intervention()
        aff_repo.list_by_intervention.return_value = []
        msg_repo.list_for_rapport.return_value = []
        sig_repo.list_by_intervention.return_value = []
        pdf_gen.generate_intervention_pdf.side_effect = RuntimeError("WeasyPrint error")

        with pytest.raises(GenerateInterventionPDFError):
            use_case.execute(1)

    def test_execute_without_code_uses_id(self):
        """Test: le nom de fichier utilise l'ID si pas de code."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        intervention = _make_intervention(code=None)
        int_repo.get_by_id.return_value = intervention
        aff_repo.list_by_intervention.return_value = []
        msg_repo.list_for_rapport.return_value = []
        sig_repo.list_by_intervention.return_value = []
        pdf_gen.generate_intervention_pdf.return_value = b"%PDF"

        _, filename = use_case.execute(1)
        assert filename == "rapport_INT-1.pdf"

    def test_execute_options_exclude_photos(self):
        """INT-15: exclure les photos du rapport."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        msg_with_photo = _make_message(
            type_msg=TypeMessage.PHOTO,
            contenu="Photo chantier",
            photos=["http://example.com/photo1.jpg"],
        )
        msg_text = _make_message(contenu="Commentaire texte")

        int_repo.get_by_id.return_value = _make_intervention()
        aff_repo.list_by_intervention.return_value = []
        msg_repo.list_for_rapport.return_value = [msg_with_photo, msg_text]
        sig_repo.list_by_intervention.return_value = []
        pdf_gen.generate_intervention_pdf.return_value = b"%PDF"

        options = InterventionPDFOptionsDTO(inclure_photos=False)
        use_case.execute(1, options=options)

        # Verifie que les messages avec photos sont filtres
        call_kwargs = pdf_gen.generate_intervention_pdf.call_args
        passed_messages = call_kwargs.kwargs["messages"]
        assert len(passed_messages) == 1
        assert passed_messages[0].contenu == "Commentaire texte"

    def test_execute_options_exclude_signatures(self):
        """INT-15: exclure les signatures du rapport."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        int_repo.get_by_id.return_value = _make_intervention()
        aff_repo.list_by_intervention.return_value = []
        msg_repo.list_for_rapport.return_value = []
        pdf_gen.generate_intervention_pdf.return_value = b"%PDF"

        options = InterventionPDFOptionsDTO(inclure_signatures=False)
        use_case.execute(1, options=options)

        # Le repo signatures ne doit PAS etre appele
        sig_repo.list_by_intervention.assert_not_called()

        # Le generateur doit recevoir une liste vide de signatures
        call_kwargs = pdf_gen.generate_intervention_pdf.call_args
        assert call_kwargs.kwargs["signatures"] == []

    def test_execute_options_exclude_messages(self):
        """INT-15: exclure les messages mais garder les photos."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        msg_text = _make_message(contenu="Commentaire")
        msg_photo = _make_message(
            type_msg=TypeMessage.PHOTO,
            contenu="Photo",
            photos=["http://example.com/photo.jpg"],
        )

        int_repo.get_by_id.return_value = _make_intervention()
        aff_repo.list_by_intervention.return_value = []
        msg_repo.list_for_rapport.return_value = [msg_text, msg_photo]
        sig_repo.list_by_intervention.return_value = []
        pdf_gen.generate_intervention_pdf.return_value = b"%PDF"

        # inclure_photos=True, inclure_messages=False -> garder seulement les photos
        options = InterventionPDFOptionsDTO(inclure_messages=False, inclure_photos=True)
        use_case.execute(1, options=options)

        call_kwargs = pdf_gen.generate_intervention_pdf.call_args
        passed_messages = call_kwargs.kwargs["messages"]
        assert len(passed_messages) == 1
        assert passed_messages[0].a_photos is True

    def test_execute_options_exclude_all_messages_and_photos(self):
        """INT-15: exclure messages ET photos."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        int_repo.get_by_id.return_value = _make_intervention()
        aff_repo.list_by_intervention.return_value = []
        sig_repo.list_by_intervention.return_value = []
        pdf_gen.generate_intervention_pdf.return_value = b"%PDF"

        options = InterventionPDFOptionsDTO(inclure_messages=False, inclure_photos=False)
        use_case.execute(1, options=options)

        # Le repo messages ne doit PAS etre appele
        msg_repo.list_for_rapport.assert_not_called()

        call_kwargs = pdf_gen.generate_intervention_pdf.call_args
        assert call_kwargs.kwargs["messages"] == []

    def test_execute_passes_options_to_generator(self):
        """Test: les options sont passees au generateur."""
        use_case, int_repo, aff_repo, msg_repo, sig_repo, pdf_gen = _make_use_case()

        int_repo.get_by_id.return_value = _make_intervention()
        aff_repo.list_by_intervention.return_value = []
        msg_repo.list_for_rapport.return_value = []
        sig_repo.list_by_intervention.return_value = []
        pdf_gen.generate_intervention_pdf.return_value = b"%PDF"

        options = InterventionPDFOptionsDTO(
            inclure_travaux=False,
            inclure_anomalies=False,
        )
        use_case.execute(1, options=options)

        call_kwargs = pdf_gen.generate_intervention_pdf.call_args
        passed_options = call_kwargs.kwargs["options"]
        assert passed_options.inclure_travaux is False
        assert passed_options.inclure_anomalies is False


class TestInterventionPDFOptionsDTO:
    """Tests pour InterventionPDFOptionsDTO."""

    def test_default_values(self):
        """Test: toutes les options sont True par defaut."""
        options = InterventionPDFOptionsDTO()
        assert options.inclure_photos is True
        assert options.inclure_signatures is True
        assert options.inclure_travaux is True
        assert options.inclure_anomalies is True
        assert options.inclure_messages is True

    def test_custom_values(self):
        """Test: les options peuvent etre personnalisees."""
        options = InterventionPDFOptionsDTO(
            inclure_photos=False,
            inclure_signatures=False,
            inclure_travaux=True,
            inclure_anomalies=False,
            inclure_messages=True,
        )
        assert options.inclure_photos is False
        assert options.inclure_signatures is False
        assert options.inclure_travaux is True
        assert options.inclure_anomalies is False
        assert options.inclure_messages is True
