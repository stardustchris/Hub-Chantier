"""Tests unitaires pour les Use Cases de recherche de devis.

DEV-19: Filtres avances.
Couche Application - search_use_cases.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

from modules.devis.domain.entities.devis import Devis
from modules.devis.domain.value_objects.statut_devis import StatutDevis
from modules.devis.domain.repositories.devis_repository import DevisRepository
from modules.devis.application.use_cases.search_use_cases import SearchDevisUseCase
from modules.devis.application.dtos.devis_dtos import DevisListDTO


def _make_devis(**kwargs):
    """Cree un devis valide avec valeurs par defaut."""
    defaults = {
        "id": 1,
        "numero": "DEV-2026-001",
        "client_nom": "Greg Construction",
        "objet": "Renovation",
        "statut": StatutDevis.BROUILLON,
        "date_creation": date(2026, 1, 15),
        "montant_total_ht": Decimal("50000"),
        "montant_total_ttc": Decimal("60000"),
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(kwargs)
    return Devis(**defaults)


class TestSearchDevisUseCase:
    """Tests pour la recherche avancee de devis."""

    def setup_method(self):
        self.mock_devis_repo = Mock(spec=DevisRepository)
        self.use_case = SearchDevisUseCase(
            devis_repository=self.mock_devis_repo,
        )

    def test_search_sans_filtre(self):
        """Test: recherche sans filtre retourne tous les devis."""
        devis_list = [_make_devis(id=i, numero=f"DEV-{i:03d}") for i in range(1, 4)]
        self.mock_devis_repo.find_all.return_value = devis_list
        self.mock_devis_repo.count.return_value = 3

        result = self.use_case.execute()

        assert isinstance(result, DevisListDTO)
        assert len(result.items) == 3
        assert result.total == 3

    def test_search_par_client_nom(self):
        """Test: recherche par nom de client."""
        devis_list = [_make_devis()]
        self.mock_devis_repo.find_all.return_value = devis_list
        self.mock_devis_repo.count.return_value = 1

        result = self.use_case.execute(client_nom="Greg")

        self.mock_devis_repo.find_all.assert_called_once()
        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["client_nom"] == "Greg"

    def test_search_par_statut_unique(self):
        """Test: recherche par statut unique."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute(statut=StatutDevis.ENVOYE)

        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["statut"] == StatutDevis.ENVOYE

    def test_search_par_statuts_multiples(self):
        """Test: recherche par plusieurs statuts."""
        statuts = [StatutDevis.ENVOYE, StatutDevis.VU]
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute(statuts=statuts)

        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["statuts"] == statuts

    def test_search_par_date_creation(self):
        """Test: recherche par plage de dates."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute(
            date_creation_min=date(2026, 1, 1),
            date_creation_max=date(2026, 6, 30),
        )

        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["date_creation_min"] == date(2026, 1, 1)
        assert call_kwargs["date_creation_max"] == date(2026, 6, 30)

    def test_search_par_montant(self):
        """Test: recherche par plage de montants."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute(
            montant_min=Decimal("10000"),
            montant_max=Decimal("100000"),
        )

        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["montant_min"] == Decimal("10000")
        assert call_kwargs["montant_max"] == Decimal("100000")

    def test_search_par_commercial(self):
        """Test: recherche par commercial assigne."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute(commercial_id=5)

        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["commercial_id"] == 5

    def test_search_par_conducteur(self):
        """Test: recherche par conducteur assigne."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute(conducteur_id=3)

        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["conducteur_id"] == 3

    def test_search_textuelle(self):
        """Test: recherche textuelle sur numero/client/objet."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 0

        result = self.use_case.execute(search="renovation")

        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["search"] == "renovation"

    def test_search_avec_pagination(self):
        """Test: recherche avec pagination personnalisee."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 50

        result = self.use_case.execute(limit=10, offset=20)

        assert result.limit == 10
        assert result.offset == 20
        call_kwargs = self.mock_devis_repo.find_all.call_args[1]
        assert call_kwargs["limit"] == 10
        assert call_kwargs["offset"] == 20

    def test_search_count_with_filters(self):
        """Test: le count passe les filtres pertinents."""
        self.mock_devis_repo.find_all.return_value = []
        self.mock_devis_repo.count.return_value = 5

        result = self.use_case.execute(
            statut=StatutDevis.ENVOYE,
            commercial_id=2,
        )

        count_kwargs = self.mock_devis_repo.count.call_args[1]
        assert count_kwargs["statut"] == StatutDevis.ENVOYE
        assert count_kwargs["commercial_id"] == 2
