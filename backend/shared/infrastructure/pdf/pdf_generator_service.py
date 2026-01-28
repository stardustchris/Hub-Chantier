"""Service de génération de PDF à partir de templates Jinja2.

Ce service centralise la logique de génération de PDF pour éviter
la duplication de code HTML inline dans les use cases.
"""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from shared.application.ports import PdfGeneratorPort
from shared.domain import CouleurProgression


class PdfGeneratorService(PdfGeneratorPort):
    """Service de génération de PDF à partir de templates Jinja2.

    Utilise Jinja2 pour générer le HTML puis WeasyPrint pour convertir en PDF.
    Les templates sont stockés dans backend/templates/pdf/.

    Attributes:
        template_dir: Répertoire contenant les templates Jinja2.
        env: Environnement Jinja2 configuré.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialise le service de génération PDF.

        Args:
            template_dir: Répertoire des templates (optionnel).
                         Par défaut: backend/templates/pdf/
        """
        if template_dir is None:
            # Déterminer le chemin du répertoire templates
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent.parent.parent
            template_dir = backend_dir / "templates" / "pdf"

        self.template_dir = template_dir

        # Configurer Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Charger les macros
        self.env.globals['render_tache_row'] = self._get_macro('macros.html', 'render_tache_row')

    def _get_macro(self, template_name: str, macro_name: str) -> Any:
        """Récupère une macro Jinja2 depuis un template.

        Args:
            template_name: Nom du fichier template.
            macro_name: Nom de la macro.

        Returns:
            La macro Jinja2.
        """
        template = self.env.get_template(template_name)
        return getattr(template.module, macro_name)

    def generate_taches_pdf(
        self,
        taches: list,
        chantier_nom: str,
        stats: Dict[str, Any],
    ) -> bytes:
        """Génère un PDF de rapport de tâches.

        Args:
            taches: Liste des tâches à inclure dans le rapport.
            chantier_nom: Nom du chantier pour le titre.
            stats: Statistiques globales (total, terminées, en_retard, heures).

        Returns:
            Contenu PDF en bytes.

        Example:
            >>> service = PdfGeneratorService()
            >>> pdf_bytes = service.generate_taches_pdf(taches, "Villa Lyon", stats)
        """
        # Préparer les données pour le template
        heures_estimees = stats.get("heures_estimees_total", 0) or 0
        heures_realisees = stats.get("heures_realisees_total", 0) or 0

        # Calculer la progression
        progression = 0
        if heures_estimees > 0:
            progression = min((heures_realisees / heures_estimees) * 100, 100)

        # Déterminer la couleur de progression
        if heures_realisees == 0:
            couleur = "#9E9E9E"
            label_couleur = "Non commencé"
        elif progression <= 80:
            couleur = "#4CAF50"
            label_couleur = "Dans les temps"
        elif progression <= 100:
            couleur = "#FFC107"
            label_couleur = "Attention"
        else:
            couleur = "#F44336"
            label_couleur = "Dépassement"

        # Enrichir les tâches avec couleur_hex
        taches_enriched = self._enrich_taches_with_color(taches)

        # Générer le HTML
        template = self.env.get_template('taches_rapport.html')
        html_content = template.render(
            chantier_nom=chantier_nom,
            generated_at=datetime.now().strftime("%d/%m/%Y %H:%M"),
            stats=stats,
            progression=progression,
            couleur_progression=couleur,
            label_progression=label_couleur,
            taches=taches_enriched,
        )

        # Convertir en PDF
        return self._html_to_pdf(html_content)

    def _enrich_taches_with_color(self, taches: list) -> list:
        """Enrichit les tâches avec des informations de couleur.

        Calcule la couleur de progression pour chaque tâche basée sur
        les heures réalisées vs estimées.

        Args:
            taches: Liste des tâches.

        Returns:
            Liste des tâches enrichies.
        """
        enriched = []
        for tache in taches:
            # Créer un dict avec les attributs nécessaires
            tache_dict = {
                'titre': tache.titre,
                'est_terminee': tache.est_terminee,
                'date_echeance': tache.date_echeance,
                'heures_estimees': tache.heures_estimees,
                'heures_realisees': tache.heures_realisees,
                'quantite_estimee': tache.quantite_estimee,
                'quantite_realisee': tache.quantite_realisee,
                'unite_mesure': tache.unite_mesure,
                'sous_taches': [],
            }

            # Calculer la couleur de progression
            couleur_info = CouleurProgression.from_progression(
                tache.heures_realisees, tache.heures_estimees or 0
            )
            tache_dict['couleur_hex'] = couleur_info.hex_code

            # Traiter récursivement les sous-tâches
            if hasattr(tache, 'sous_taches') and tache.sous_taches:
                tache_dict['sous_taches'] = self._enrich_taches_with_color(tache.sous_taches)

            enriched.append(type('TacheEnriched', (), tache_dict)())

        return enriched

    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convertit du HTML en PDF en utilisant WeasyPrint.

        Args:
            html_content: Contenu HTML à convertir.

        Returns:
            Contenu PDF en bytes.

        Raises:
            ImportError: Si WeasyPrint n'est pas installé.
        """
        try:
            from weasyprint import HTML
            pdf_buffer = BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            return pdf_buffer.getvalue()
        except ImportError as e:
            raise ImportError(
                "WeasyPrint est requis pour générer des PDF. "
                "Installez-le avec: pip install weasyprint"
            ) from e
