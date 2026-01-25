"""Tests pour les Use Cases du module Taches."""

import pytest
from datetime import date

from modules.taches.application import (
    CreateTacheUseCase,
    GetTacheUseCase,
    ListTachesUseCase,
    CompleteTacheUseCase,
    ImportTemplateUseCase,
    CreateFeuilleTacheUseCase,
    ValidateFeuilleTacheUseCase,
    TacheNotFoundError,
    TemplateNotFoundError,
)
from modules.taches.application.dtos import (
    CreateTacheDTO,
    CreateFeuilleTacheDTO,
    ValidateFeuilleTacheDTO,
)


class TestCreateTacheUseCase:
    """Tests pour CreateTacheUseCase."""

    def test_create_tache_success(self, tache_repo):
        """Test creation de tache reussie (TAC-06)."""
        use_case = CreateTacheUseCase(tache_repo=tache_repo)
        dto = CreateTacheDTO(
            chantier_id=1,
            titre="Nouvelle tache",
            description="Description",
            heures_estimees=8.0,
        )

        result = use_case.execute(dto)

        assert result.id is not None
        assert result.titre == "Nouvelle tache"
        assert result.heures_estimees == 8.0
        assert result.statut == "a_faire"

    def test_create_tache_with_unite_mesure(self, tache_repo):
        """Test creation avec unite de mesure (TAC-09)."""
        use_case = CreateTacheUseCase(tache_repo=tache_repo)
        dto = CreateTacheDTO(
            chantier_id=1,
            titre="Coffrage",
            unite_mesure="m2",
            quantite_estimee=50.0,
        )

        result = use_case.execute(dto)

        assert result.unite_mesure == "m2"
        assert result.quantite_estimee == 50.0

    def test_create_sous_tache(self, tache_repo):
        """Test creation de sous-tache (TAC-02)."""
        use_case = CreateTacheUseCase(tache_repo=tache_repo)

        # Creer tache parente
        parent_dto = CreateTacheDTO(chantier_id=1, titre="Tache principale")
        parent_result = use_case.execute(parent_dto)

        # Creer sous-tache
        child_dto = CreateTacheDTO(
            chantier_id=1,
            titre="Sous-tache",
            parent_id=parent_result.id,
        )
        child_result = use_case.execute(child_dto)

        assert child_result.parent_id == parent_result.id


class TestGetTacheUseCase:
    """Tests pour GetTacheUseCase."""

    def test_get_tache_success(self, tache_repo, sample_tache):
        """Test recuperation de tache reussie."""
        saved = tache_repo.save(sample_tache)
        use_case = GetTacheUseCase(tache_repo=tache_repo)

        result = use_case.execute(saved.id)

        assert result.id == saved.id
        assert result.titre == "Test Tache"

    def test_get_tache_not_found(self, tache_repo):
        """Test erreur si tache non trouvee."""
        use_case = GetTacheUseCase(tache_repo=tache_repo)

        with pytest.raises(TacheNotFoundError):
            use_case.execute(999)


class TestListTachesUseCase:
    """Tests pour ListTachesUseCase."""

    def test_list_taches_by_chantier(self, tache_repo):
        """Test liste des taches par chantier (TAC-01)."""
        use_case_create = CreateTacheUseCase(tache_repo=tache_repo)
        use_case_list = ListTachesUseCase(tache_repo=tache_repo)

        # Creer des taches
        for i in range(3):
            dto = CreateTacheDTO(chantier_id=1, titre=f"Tache {i}")
            use_case_create.execute(dto)

        result = use_case_list.execute(chantier_id=1)

        assert result.total == 3
        assert len(result.items) == 3

    def test_list_taches_with_search(self, tache_repo):
        """Test recherche de taches (TAC-14)."""
        use_case_create = CreateTacheUseCase(tache_repo=tache_repo)
        use_case_list = ListTachesUseCase(tache_repo=tache_repo)

        # Creer des taches
        use_case_create.execute(CreateTacheDTO(chantier_id=1, titre="Coffrage voiles"))
        use_case_create.execute(CreateTacheDTO(chantier_id=1, titre="Ferraillage"))
        use_case_create.execute(CreateTacheDTO(chantier_id=1, titre="Coffrage dalle"))

        result = use_case_list.execute(chantier_id=1, query="Coffrage")

        assert result.total == 2


class TestCompleteTacheUseCase:
    """Tests pour CompleteTacheUseCase."""

    def test_complete_tache(self, tache_repo, sample_tache):
        """Test marquer une tache comme terminee (TAC-13)."""
        saved = tache_repo.save(sample_tache)
        use_case = CompleteTacheUseCase(tache_repo=tache_repo)

        result = use_case.execute(saved.id, terminer=True)

        assert result.est_terminee
        assert result.statut == "termine"

    def test_reopen_tache(self, tache_repo, sample_tache):
        """Test rouvrir une tache terminee."""
        sample_tache.terminer()
        saved = tache_repo.save(sample_tache)
        use_case = CompleteTacheUseCase(tache_repo=tache_repo)

        result = use_case.execute(saved.id, terminer=False)

        assert not result.est_terminee
        assert result.statut == "a_faire"


class TestImportTemplateUseCase:
    """Tests pour ImportTemplateUseCase."""

    def test_import_template_success(self, tache_repo, template_repo, sample_template):
        """Test import de template reussi (TAC-05)."""
        saved_template = template_repo.save(sample_template)
        use_case = ImportTemplateUseCase(
            tache_repo=tache_repo,
            template_repo=template_repo,
        )

        results = use_case.execute(
            template_id=saved_template.id,
            chantier_id=1,
        )

        # Tache principale + sous-taches
        assert len(results) == 3  # 1 principale + 2 sous-taches
        assert results[0].titre == "Coffrage voiles"
        assert results[0].template_id == saved_template.id

    def test_import_template_not_found(self, tache_repo, template_repo):
        """Test erreur si template non trouve."""
        use_case = ImportTemplateUseCase(
            tache_repo=tache_repo,
            template_repo=template_repo,
        )

        with pytest.raises(TemplateNotFoundError):
            use_case.execute(template_id=999, chantier_id=1)


class TestCreateFeuilleTacheUseCase:
    """Tests pour CreateFeuilleTacheUseCase."""

    def test_create_feuille_success(self, tache_repo, feuille_repo, sample_tache):
        """Test creation de feuille reussie (TAC-18)."""
        saved_tache = tache_repo.save(sample_tache)
        use_case = CreateFeuilleTacheUseCase(
            feuille_repo=feuille_repo,
            tache_repo=tache_repo,
        )

        dto = CreateFeuilleTacheDTO(
            tache_id=saved_tache.id,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today().isoformat(),
            heures_travaillees=8.0,
        )

        result = use_case.execute(dto)

        assert result.id is not None
        assert result.heures_travaillees == 8.0
        assert result.est_en_attente


class TestValidateFeuilleTacheUseCase:
    """Tests pour ValidateFeuilleTacheUseCase."""

    def test_validate_feuille_success(self, tache_repo, feuille_repo, sample_tache):
        """Test validation de feuille reussie (TAC-19)."""
        saved_tache = tache_repo.save(sample_tache)

        # Creer une feuille
        create_uc = CreateFeuilleTacheUseCase(
            feuille_repo=feuille_repo,
            tache_repo=tache_repo,
        )
        feuille = create_uc.execute(CreateFeuilleTacheDTO(
            tache_id=saved_tache.id,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today().isoformat(),
            heures_travaillees=8.0,
        ))

        # Valider
        validate_uc = ValidateFeuilleTacheUseCase(
            feuille_repo=feuille_repo,
            tache_repo=tache_repo,
        )
        dto = ValidateFeuilleTacheDTO(validateur_id=2, valider=True)

        result = validate_uc.execute(feuille.id, dto)

        assert result.est_validee
        assert result.validateur_id == 2

        # Verifier que les heures sont ajoutees a la tache
        tache = tache_repo.find_by_id(saved_tache.id)
        assert tache.heures_realisees == 8.0

    def test_reject_feuille(self, tache_repo, feuille_repo, sample_tache):
        """Test rejet de feuille."""
        saved_tache = tache_repo.save(sample_tache)

        # Creer une feuille
        create_uc = CreateFeuilleTacheUseCase(
            feuille_repo=feuille_repo,
            tache_repo=tache_repo,
        )
        feuille = create_uc.execute(CreateFeuilleTacheDTO(
            tache_id=saved_tache.id,
            utilisateur_id=1,
            chantier_id=1,
            date_travail=date.today().isoformat(),
            heures_travaillees=8.0,
        ))

        # Rejeter
        validate_uc = ValidateFeuilleTacheUseCase(
            feuille_repo=feuille_repo,
            tache_repo=tache_repo,
        )
        dto = ValidateFeuilleTacheDTO(
            validateur_id=2,
            valider=False,
            motif_rejet="Heures incorrectes",
        )

        result = validate_uc.execute(feuille.id, dto)

        assert result.est_rejetee
        assert result.motif_rejet == "Heures incorrectes"

        # Verifier que les heures ne sont pas ajoutees
        tache = tache_repo.find_by_id(saved_tache.id)
        assert tache.heures_realisees == 0.0
