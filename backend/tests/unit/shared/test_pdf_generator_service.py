"""Tests unitaires pour PdfGeneratorService."""

from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from shared.infrastructure.pdf.pdf_generator_service import PdfGeneratorService
from shared.domain import CouleurProgression


@pytest.fixture
def mock_template_dir(tmp_path):
    """Crée un répertoire temporaire de templates."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Créer les templates minimaux
    (templates_dir / "macros.html").write_text("""
{% macro render_tache_row(tache, level) %}
<tr><td>{{ tache.titre }}</td></tr>
{% endmacro %}
    """)

    (templates_dir / "taches_rapport.html").write_text("""
<!DOCTYPE html>
<html>
<head><title>{{ chantier_nom }}</title></head>
<body>
    <h1>{{ chantier_nom }}</h1>
    <p>Généré le: {{ generated_at }}</p>
    <p>Progression: {{ progression }}%</p>
    <p>Couleur: {{ label_progression }}</p>
    <div style="background-color: {{ couleur_progression }};">Barre de progression</div>
    {% for tache in taches %}
        <div>{{ tache.titre }}</div>
    {% endfor %}
</body>
</html>
    """)

    return templates_dir


@pytest.fixture
def service(mock_template_dir):
    """Instance du service avec mock template dir."""
    return PdfGeneratorService(template_dir=mock_template_dir)


@pytest.fixture
def tache_mock():
    """Mock d'une tâche."""
    tache = Mock()
    tache.titre = "Tâche test"
    tache.est_terminee = False
    tache.date_echeance = date(2026, 3, 15)
    tache.heures_estimees = 10.0
    tache.heures_realisees = 5.0
    tache.quantite_estimee = None
    tache.quantite_realisee = None
    tache.unite_mesure = None
    tache.sous_taches = []
    return tache


class TestPdfGeneratorServiceInit:
    """Tests pour l'initialisation du service."""

    def test_should_init_with_custom_template_dir(self, mock_template_dir):
        """Doit initialiser avec un répertoire custom."""
        service = PdfGeneratorService(template_dir=mock_template_dir)
        assert service.template_dir == mock_template_dir
        assert service.env is not None

    def test_should_init_with_default_template_dir(self):
        """Doit initialiser avec le répertoire par défaut."""
        service = PdfGeneratorService()
        assert service.template_dir.name == "pdf"
        assert "templates" in str(service.template_dir)


class TestGenerateTachesPdf:
    """Tests pour la génération de PDF de tâches."""

    @patch('weasyprint.HTML')
    def test_should_generate_pdf_with_valid_data(
        self, mock_html, service, tache_mock
    ):
        """Doit générer un PDF avec des données valides."""
        stats = {
            "total": 5,
            "terminees": 2,
            "en_retard": 1,
            "heures_estimees_total": 100.0,
            "heures_realisees_total": 50.0,
        }

        mock_pdf = MagicMock()
        mock_pdf.write_pdf = MagicMock()
        mock_html.return_value = mock_pdf

        # Mock write_pdf pour écrire dans le buffer
        def write_to_buffer(buffer):
            buffer.write(b"PDF content")

        mock_pdf.write_pdf.side_effect = write_to_buffer

        result = service.generate_taches_pdf(
            taches=[tache_mock],
            chantier_nom="Chantier Test",
            stats=stats,
        )

        assert result == b"PDF content"
        mock_html.assert_called_once()

    @patch('weasyprint.HTML')
    def test_should_handle_zero_hours_not_started(
        self, mock_html, service, tache_mock
    ):
        """Doit gérer progression 0 (non commencé) - couleur grise."""
        stats = {
            "heures_estimees_total": 100.0,
            "heures_realisees_total": 0.0,  # 0% -> Non commencé
        }

        mock_pdf = MagicMock()
        mock_pdf.write_pdf = MagicMock(side_effect=lambda b: b.write(b"PDF"))
        mock_html.return_value = mock_pdf

        service.generate_taches_pdf([tache_mock], "Test", stats)

        # Vérifier que le template a été appelé avec la couleur grise
        html_call = mock_html.call_args[1]['string']
        assert "#9E9E9E" in html_call  # Couleur grise
        assert "Non commencé" in html_call

    @patch('weasyprint.HTML')
    def test_should_handle_progression_in_time(
        self, mock_html, service, tache_mock
    ):
        """Doit gérer progression <= 80% (dans les temps) - couleur verte."""
        stats = {
            "heures_estimees_total": 100.0,
            "heures_realisees_total": 50.0,  # 50% -> Dans les temps
        }

        mock_pdf = MagicMock()
        mock_pdf.write_pdf = MagicMock(side_effect=lambda b: b.write(b"PDF"))
        mock_html.return_value = mock_pdf

        service.generate_taches_pdf([tache_mock], "Test", stats)

        html_call = mock_html.call_args[1]['string']
        assert "#4CAF50" in html_call  # Couleur verte
        assert "Dans les temps" in html_call

    @patch('weasyprint.HTML')
    def test_should_handle_progression_warning(
        self, mock_html, service, tache_mock
    ):
        """Doit gérer progression 80-100% (attention) - couleur jaune."""
        stats = {
            "heures_estimees_total": 100.0,
            "heures_realisees_total": 90.0,  # 90% -> Attention
        }

        mock_pdf = MagicMock()
        mock_pdf.write_pdf = MagicMock(side_effect=lambda b: b.write(b"PDF"))
        mock_html.return_value = mock_pdf

        service.generate_taches_pdf([tache_mock], "Test", stats)

        html_call = mock_html.call_args[1]['string']
        assert "#FFC107" in html_call  # Couleur jaune
        assert "Attention" in html_call

    @patch('weasyprint.HTML')
    def test_should_handle_progression_overrun(
        self, mock_html, service, tache_mock
    ):
        """Doit gérer progression > 100% (dépassement).

        NOTE: Le code actuel cap la progression à 100%, donc 120% affiche jaune "Attention",
        pas rouge "Dépassement". Les lignes 107-109 (else: rouge) sont unreachable.
        """
        stats = {
            "heures_estimees_total": 100.0,
            "heures_realisees_total": 120.0,  # 120% mais cappé à 100%
        }

        mock_pdf = MagicMock()
        mock_pdf.write_pdf = MagicMock(side_effect=lambda b: b.write(b"PDF"))
        mock_html.return_value = mock_pdf

        service.generate_taches_pdf([tache_mock], "Test", stats)

        html_call = mock_html.call_args[1]['string']
        # Code actuel: progression cappée à 100% donc jaune "Attention"
        assert "#FFC107" in html_call  # Couleur jaune (pas rouge car cappée)
        assert "Attention" in html_call


class TestEnrichTachesWithColor:
    """Tests pour l'enrichissement des tâches avec couleurs."""

    def test_should_enrich_simple_tache(self, service, tache_mock):
        """Doit enrichir une tâche simple avec sa couleur."""
        result = service._enrich_taches_with_color([tache_mock])

        assert len(result) == 1
        assert result[0].titre == "Tâche test"
        assert hasattr(result[0], 'couleur_hex')
        assert result[0].couleur_hex.startswith('#')

    def test_should_enrich_tache_with_sous_taches(self, service):
        """Doit enrichir récursivement les sous-tâches (ligne 163)."""
        # Tâche parente
        parent = Mock()
        parent.titre = "Tâche parent"
        parent.est_terminee = False
        parent.date_echeance = None
        parent.heures_estimees = 20.0
        parent.heures_realisees = 10.0
        parent.quantite_estimee = None
        parent.quantite_realisee = None
        parent.unite_mesure = None

        # Sous-tâche
        sous_tache = Mock()
        sous_tache.titre = "Sous-tâche"
        sous_tache.est_terminee = True
        sous_tache.date_echeance = None
        sous_tache.heures_estimees = 5.0
        sous_tache.heures_realisees = 5.0
        sous_tache.quantite_estimee = None
        sous_tache.quantite_realisee = None
        sous_tache.unite_mesure = None
        sous_tache.sous_taches = []

        parent.sous_taches = [sous_tache]

        result = service._enrich_taches_with_color([parent])

        assert len(result) == 1
        assert result[0].titre == "Tâche parent"
        assert len(result[0].sous_taches) == 1
        assert result[0].sous_taches[0].titre == "Sous-tâche"
        assert hasattr(result[0].sous_taches[0], 'couleur_hex')


class TestHtmlToPdf:
    """Tests pour la conversion HTML vers PDF."""

    @patch('weasyprint.HTML')
    def test_should_convert_html_to_pdf(self, mock_html, service):
        """Doit convertir du HTML en PDF."""
        mock_pdf = MagicMock()
        mock_pdf.write_pdf = MagicMock(side_effect=lambda b: b.write(b"PDF data"))
        mock_html.return_value = mock_pdf

        result = service._html_to_pdf("<html><body>Test</body></html>")

        assert result == b"PDF data"
        mock_html.assert_called_once_with(string="<html><body>Test</body></html>")

    def test_should_raise_import_error_when_weasyprint_missing(self, service):
        """Doit lever ImportError si WeasyPrint n'est pas installé (lignes 186-187)."""
        with patch('weasyprint.HTML') as mock_html:
            mock_html.side_effect = ImportError("No module named 'weasyprint'")

            with pytest.raises(ImportError) as exc_info:
                service._html_to_pdf("<html></html>")

            assert "WeasyPrint est requis" in str(exc_info.value)
            assert "pip install weasyprint" in str(exc_info.value)


class TestGetMacro:
    """Tests pour la récupération de macros."""

    def test_should_load_macro_from_template(self, service):
        """Doit charger une macro depuis un template."""
        macro = service._get_macro('macros.html', 'render_tache_row')
        assert macro is not None
        assert callable(macro)
