"""Service de génération de PDF à partir de templates Jinja2.

Ce service centralise la logique de génération de PDF pour éviter
la duplication de code HTML inline dans les use cases.
"""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    def generate_formulaire_pdf(
        self,
        titre: str,
        chantier_nom: Optional[str],
        categorie: str,
        statut: str,
        version: int,
        user_nom: Optional[str],
        created_at: datetime,
        soumis_at: Optional[datetime],
        valide_at: Optional[datetime],
        valideur_nom: Optional[str],
        champs: list[Dict[str, Any]],
        commentaires: Optional[str] = None,
    ) -> bytes:
        """Génère un PDF de formulaire rempli.

        Args:
            titre: Titre du formulaire.
            chantier_nom: Nom du chantier (optionnel).
            categorie: Catégorie du formulaire.
            statut: Statut (brouillon, soumis, valide, refuse).
            version: Version du formulaire.
            user_nom: Nom de l'utilisateur ayant rempli le formulaire.
            created_at: Date de création.
            soumis_at: Date de soumission (optionnel).
            valide_at: Date de validation (optionnel).
            valideur_nom: Nom du valideur (optionnel).
            champs: Liste des champs avec leurs valeurs.
            commentaires: Commentaires généraux (optionnel).

        Returns:
            Contenu PDF en bytes.
        """
        # Mapping des statuts
        statut_labels = {
            "brouillon": "Brouillon",
            "soumis": "Soumis",
            "valide": "Validé",
            "refuse": "Refusé",
        }

        # Formater les dates
        def format_date(dt: Optional[datetime]) -> str:
            return dt.strftime("%d/%m/%Y %H:%M") if dt else "-"

        # Préparer le contexte pour le template
        context = {
            "titre": titre,
            "chantier_nom": chantier_nom,
            "categorie": categorie,
            "statut_label": statut_labels.get(statut, statut),
            "version": version,
            "user_nom": user_nom,
            "created_at": format_date(created_at),
            "soumis_at": format_date(soumis_at) if soumis_at else None,
            "valide_at": format_date(valide_at) if valide_at else None,
            "valideur_nom": valideur_nom,
            "champs": champs,
            "commentaires": commentaires,
            "generation_date": datetime.now().strftime("%d/%m/%Y à %H:%M"),
        }

        # Charger le template
        template = self.env.get_template("formulaire_rapport.html")

        # Générer le HTML
        html_content = template.render(**context)

        # Convertir en PDF
        return self._html_to_pdf(html_content)

    def generate_intervention_pdf(
        self,
        intervention,
        techniciens: list,
        messages: list,
        signatures: list,
        options=None,
    ) -> bytes:
        """Genere un PDF de rapport d'intervention.

        INT-14: Rapport PDF - Generation automatique.
        INT-15: Selection posts pour rapport.

        Args:
            intervention: L'entite Intervention.
            techniciens: Liste des AffectationIntervention.
            messages: Messages filtres pour le rapport.
            signatures: Signatures (client + technicien).
            options: InterventionPDFOptionsDTO (sections a inclure).

        Returns:
            Contenu PDF en bytes.
        """
        # Importer ici pour eviter les imports circulaires
        from modules.interventions.application.use_cases.pdf_use_cases import (
            InterventionPDFOptionsDTO,
        )

        if options is None:
            options = InterventionPDFOptionsDTO()

        # Mapping statut -> classe CSS
        statut_classes = {
            "a_planifier": "a-planifier",
            "planifiee": "planifiee",
            "en_cours": "en-cours",
            "terminee": "terminee",
            "annulee": "annulee",
        }

        # Mapping priorite -> classe CSS
        priorite_classes = {
            "urgente": "urgente",
            "haute": "haute",
            "normale": "normale",
            "basse": "basse",
        }

        # Formater les horaires
        horaires_planifies = None
        if intervention.heure_debut and intervention.heure_fin:
            horaires_planifies = (
                f"{intervention.heure_debut.strftime('%H:%M')} - "
                f"{intervention.heure_fin.strftime('%H:%M')}"
            )

        horaires_reels = None
        if intervention.heure_debut_reelle and intervention.heure_fin_reelle:
            horaires_reels = (
                f"{intervention.heure_debut_reelle.strftime('%H:%M')} - "
                f"{intervention.heure_fin_reelle.strftime('%H:%M')}"
            )

        # Duree reelle
        duree_reelle = None
        if intervention.duree_reelle_minutes is not None:
            heures = intervention.duree_reelle_minutes // 60
            minutes = intervention.duree_reelle_minutes % 60
            if heures > 0:
                duree_reelle = f"{heures}h{minutes:02d}"
            else:
                duree_reelle = f"{minutes} min"

        # Date planifiee formatee
        date_planifiee = None
        if intervention.date_planifiee:
            date_planifiee = intervention.date_planifiee.strftime("%d/%m/%Y")

        # Enrichir les messages avec infos affichables
        messages_enriched = []
        for msg in messages:
            type_labels = {
                "commentaire": "Commentaire",
                "photo": "Photo",
                "action": "Action",
                "systeme": "Systeme",
            }
            messages_enriched.append({
                "type_message_label": type_labels.get(msg.type_message.value, msg.type_message.value),
                "created_at_str": msg.created_at.strftime("%d/%m/%Y %H:%M") if msg.created_at else "",
                "contenu": msg.contenu,
                "a_photos": msg.a_photos,
                "photos_urls": msg.photos_urls if msg.a_photos else [],
            })

        # Enrichir les signatures
        signatures_enriched = []
        for sig in signatures:
            signatures_enriched.append({
                "type_label": sig.type_signataire.label,
                "nom_signataire": sig.nom_signataire,
                "signature_data": sig.signature_data,
                "horodatage_str": sig.horodatage_str,
            })

        # Contexte du template
        context = {
            "intervention_code": intervention.code or f"INT-{intervention.id}",
            "generated_at": datetime.now().strftime("%d/%m/%Y a %H:%M"),
            # Client
            "client_nom": intervention.client_nom,
            "client_adresse": intervention.client_adresse,
            "client_telephone": intervention.client_telephone,
            "client_email": intervention.client_email,
            # Intervention
            "type_intervention": intervention.type_intervention.label,
            "statut_label": intervention.statut.label,
            "statut_class": statut_classes.get(intervention.statut.value, ""),
            "priorite_label": intervention.priorite.label,
            "priorite_class": priorite_classes.get(intervention.priorite.value, ""),
            "date_planifiee": date_planifiee,
            # Horaires
            "horaires_planifies": horaires_planifies,
            "horaires_reels": horaires_reels,
            "duree_reelle": duree_reelle,
            # Techniciens
            "techniciens": techniciens,
            # Description
            "description": intervention.description,
            # Travaux et anomalies
            "travaux_realises": intervention.travaux_realises,
            "anomalies": intervention.anomalies,
            "inclure_travaux": options.inclure_travaux,
            "inclure_anomalies": options.inclure_anomalies,
            # Messages
            "messages": messages_enriched,
            "inclure_photos": options.inclure_photos,
            # Signatures
            "signatures": signatures_enriched,
            "inclure_signatures": options.inclure_signatures,
        }

        template = self.env.get_template("intervention_rapport.html")
        html_content = template.render(**context)

        return self._html_to_pdf(html_content)
