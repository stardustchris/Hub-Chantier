"""Tests unitaires pour l'historique des modifications avec avant/apres.

DEV-18: Historique modifications - Suivi detaille des changements.
Teste le tracking avant/apres dans UpdateDevisUseCase et le journal DTO.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, ANY

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.entities.journal_devis import JournalDevis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.domain.repositories.journal_devis_repository import JournalDevisRepository
from modules.devis.application.use_cases.devis_use_cases import (
    UpdateDevisUseCase,
    _serialize_for_journal,
)
from modules.devis.application.dtos.devis_dtos import DevisUpdateDTO
from modules.devis.application.dtos.journal_dtos import (
    JournalDevisDTO,
    ChangementDTO,
)


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation bureau",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("0"),
        "montant_total_ttc": Decimal("0"),
        "taux_marge_global": Decimal("15"),
        "coefficient_frais_generaux": Decimal("12"),
        "taux_tva_defaut": Decimal("20"),
        "retenue_garantie_pct": Decimal("0"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


class TestSerializeForJournal:
    """Tests de la fonction _serialize_for_journal."""

    def test_serialize_none(self):
        assert _serialize_for_journal(None) is None

    def test_serialize_string(self):
        assert _serialize_for_journal("hello") == "hello"

    def test_serialize_decimal(self):
        assert _serialize_for_journal(Decimal("15.50")) == "15.50"

    def test_serialize_date(self):
        assert _serialize_for_journal(date(2026, 1, 15)) == "2026-01-15"

    def test_serialize_datetime(self):
        result = _serialize_for_journal(datetime(2026, 1, 15, 10, 30, 0))
        assert "2026-01-15" in result

    def test_serialize_list(self):
        assert _serialize_for_journal(["a", "b"]) == "['a', 'b']"

    def test_serialize_int(self):
        assert _serialize_for_journal(42) == "42"


class TestUpdateDevisAvantApres:
    """Tests du suivi avant/apres dans UpdateDevisUseCase."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.mock_journal_repo = Mock(spec=JournalDevisRepository)
        self.use_case = UpdateDevisUseCase(
            devis_repository=self.mock_devis_repo,
            journal_repository=self.mock_journal_repo,
        )

    def test_update_simple_field_tracks_change(self):
        """Test: modification d'un champ simple enregistre avant/apres."""
        devis = _make_devis(client_nom="Ancien Client")
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(client_nom="Nouveau Client")
        self.use_case.execute(devis_id=1, dto=dto, updated_by=5)

        # Verifier que le journal contient les changements detailles
        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.action == "modification"
        assert "changements" in journal_call.details_json
        changements = journal_call.details_json["changements"]
        assert "client_nom" in changements
        assert changements["client_nom"]["avant"] == "Ancien Client"
        assert changements["client_nom"]["apres"] == "Nouveau Client"

    def test_update_decimal_field_tracks_change(self):
        """Test: modification d'un champ Decimal enregistre avant/apres."""
        devis = _make_devis(taux_marge_global=Decimal("15"))
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(taux_marge_global=Decimal("20"))
        self.use_case.execute(devis_id=1, dto=dto, updated_by=5)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        changements = journal_call.details_json["changements"]
        assert "taux_marge_global" in changements
        assert changements["taux_marge_global"]["avant"] == "15"
        assert changements["taux_marge_global"]["apres"] == "20"

    def test_update_multiple_fields_tracks_all(self):
        """Test: modification de plusieurs champs enregistre tous les changements."""
        devis = _make_devis(
            client_nom="Ancien Client",
            objet="Ancien Objet",
        )
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(
            client_nom="Nouveau Client",
            objet="Nouveau Objet",
        )
        self.use_case.execute(devis_id=1, dto=dto, updated_by=5)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        changements = journal_call.details_json["changements"]
        assert "client_nom" in changements
        assert "objet" in changements
        assert len(changements) == 2

    def test_update_same_value_no_journal(self):
        """Test: si la valeur ne change pas, pas d'entree journal."""
        devis = _make_devis(client_nom="Greg Construction")
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis

        dto = DevisUpdateDTO(client_nom="Greg Construction")
        self.use_case.execute(devis_id=1, dto=dto, updated_by=5)

        # Pas d'appel au journal si aucun changement reel
        self.mock_journal_repo.save.assert_not_called()

    def test_update_journal_contains_type_modification(self):
        """Test: le journal contient le type de modification."""
        devis = _make_devis(client_nom="Ancien")
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(client_nom="Nouveau")
        self.use_case.execute(devis_id=1, dto=dto, updated_by=5)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        assert journal_call.details_json["type_modification"] == "update_devis"

    def test_update_journal_message_lists_fields(self):
        """Test: le message du journal liste les champs modifies."""
        devis = _make_devis(client_nom="Ancien", objet="Objet ancien")
        self.mock_devis_repo.find_by_id.return_value = devis
        self.mock_devis_repo.save.return_value = devis
        self.mock_journal_repo.save.return_value = Mock()

        dto = DevisUpdateDTO(client_nom="Nouveau", objet="Objet nouveau")
        self.use_case.execute(devis_id=1, dto=dto, updated_by=5)

        journal_call = self.mock_journal_repo.save.call_args[0][0]
        message = journal_call.details_json["message"]
        assert "client_nom" in message
        assert "objet" in message


class TestJournalDevisDTOAvantApres:
    """Tests du JournalDevisDTO avec extraction avant/apres."""

    def test_dto_extracts_changements(self):
        """Test: le DTO extrait les changements du details_json."""
        journal = JournalDevis(
            id=1,
            devis_id=1,
            action="modification",
            details_json={
                "message": "Modification des champs: client_nom",
                "type_modification": "update_devis",
                "changements": {
                    "client_nom": {"avant": "Ancien", "apres": "Nouveau"},
                },
            },
            auteur_id=5,
            created_at=datetime(2026, 1, 15, 10, 0, 0),
        )

        dto = JournalDevisDTO.from_entity(journal)

        assert len(dto.changements) == 1
        assert dto.changements[0].champ == "client_nom"
        assert dto.changements[0].avant == "Ancien"
        assert dto.changements[0].apres == "Nouveau"
        assert dto.type_modification == "update_devis"

    def test_dto_extracts_statut_transition(self):
        """Test: le DTO extrait les transitions de statut."""
        journal = JournalDevis(
            id=2,
            devis_id=1,
            action="soumission",
            details_json={
                "message": "Devis soumis pour validation",
                "ancien_statut": "brouillon",
                "nouveau_statut": "en_validation",
            },
            auteur_id=3,
            created_at=datetime(2026, 1, 15, 11, 0, 0),
        )

        dto = JournalDevisDTO.from_entity(journal)

        assert dto.ancien_statut == "brouillon"
        assert dto.nouveau_statut == "en_validation"
        assert dto.details == "Devis soumis pour validation"

    def test_dto_extracts_motif(self):
        """Test: le DTO extrait le motif de refus."""
        journal = JournalDevis(
            id=3,
            devis_id=1,
            action="refus",
            details_json={
                "message": "Devis refuse",
                "ancien_statut": "envoye",
                "nouveau_statut": "refuse",
                "motif": "Trop cher",
            },
            auteur_id=3,
            created_at=datetime(2026, 1, 15, 12, 0, 0),
        )

        dto = JournalDevisDTO.from_entity(journal)

        assert dto.motif == "Trop cher"

    def test_dto_to_dict_includes_changements(self):
        """Test: to_dict inclut les changements si presents."""
        journal = JournalDevis(
            id=1,
            devis_id=1,
            action="modification",
            details_json={
                "message": "Modification",
                "changements": {
                    "objet": {"avant": "A", "apres": "B"},
                },
            },
            auteur_id=5,
            created_at=datetime(2026, 1, 15, 10, 0, 0),
        )

        dto = JournalDevisDTO.from_entity(journal)
        d = dto.to_dict()

        assert "changements" in d
        assert d["changements"][0]["champ"] == "objet"
        assert d["changements"][0]["avant"] == "A"
        assert d["changements"][0]["apres"] == "B"

    def test_dto_to_dict_excludes_empty_changements(self):
        """Test: to_dict n'inclut pas les changements si vides."""
        journal = JournalDevis(
            id=1,
            devis_id=1,
            action="creation",
            details_json={"message": "Devis cree"},
            auteur_id=5,
            created_at=datetime(2026, 1, 15, 10, 0, 0),
        )

        dto = JournalDevisDTO.from_entity(journal)
        d = dto.to_dict()

        assert "changements" not in d

    def test_dto_backward_compatible(self):
        """Test: le DTO reste compatible avec les anciennes entrees sans changements."""
        journal = JournalDevis(
            id=1,
            devis_id=1,
            action="creation",
            details_json={"message": "Ancien format simple"},
            auteur_id=1,
            created_at=datetime(2026, 1, 15, 10, 0, 0),
        )

        dto = JournalDevisDTO.from_entity(journal)

        assert dto.details == "Ancien format simple"
        assert dto.changements == []
        assert dto.ancien_statut is None
        assert dto.nouveau_statut is None
