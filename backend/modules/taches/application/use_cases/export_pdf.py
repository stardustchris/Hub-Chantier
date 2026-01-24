"""Use Case ExportTachesPDF - Export PDF des taches (TAC-16)."""

from datetime import datetime
from io import BytesIO

from ...domain.repositories import TacheRepository
from ...domain.value_objects import CouleurProgression


class ExportTachesPDFUseCase:
    """
    Cas d'utilisation : Exporter les taches en PDF.

    Selon CDC Section 13 - TAC-16: Export rapport PDF.

    Attributes:
        tache_repo: Repository pour les taches.
    """

    def __init__(self, tache_repo: TacheRepository):
        """
        Initialise le use case.

        Args:
            tache_repo: Repository taches (interface).
        """
        self.tache_repo = tache_repo

    def execute(
        self,
        chantier_id: int,
        chantier_nom: str,
        include_completed: bool = True,
    ) -> bytes:
        """
        Genere un PDF des taches d'un chantier.

        Args:
            chantier_id: ID du chantier.
            chantier_nom: Nom du chantier pour le titre.
            include_completed: Inclure les taches terminees.

        Returns:
            Contenu PDF en bytes.
        """
        # Recuperer les taches
        taches = self.tache_repo.find_by_chantier(
            chantier_id=chantier_id,
            include_sous_taches=True,
        )

        # Filtrer si necessaire
        if not include_completed:
            taches = [t for t in taches if not t.est_terminee]

        # Calculer les stats
        stats = self.tache_repo.get_stats_chantier(chantier_id)

        # Generer le HTML puis le convertir en PDF
        html_content = self._generate_html(
            taches=taches,
            chantier_nom=chantier_nom,
            stats=stats,
        )

        # Convertir en PDF (utilise une approche simple sans dependance lourde)
        pdf_bytes = self._html_to_pdf(html_content)

        return pdf_bytes

    def _generate_html(
        self,
        taches: list,
        chantier_nom: str,
        stats: dict,
    ) -> str:
        """Genere le contenu HTML du rapport."""
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Calculer progression
        heures_estimees = stats.get("heures_estimees_total", 0) or 0
        heures_realisees = stats.get("heures_realisees_total", 0) or 0
        progression = 0
        if heures_estimees > 0:
            progression = min((heures_realisees / heures_estimees) * 100, 100)

        # Couleur progression
        if heures_realisees == 0:
            couleur = "#9E9E9E"
            label_couleur = "Non commence"
        elif progression <= 80:
            couleur = "#4CAF50"
            label_couleur = "Dans les temps"
        elif progression <= 100:
            couleur = "#FFC107"
            label_couleur = "Attention"
        else:
            couleur = "#F44336"
            label_couleur = "Depassement"

        # Generer les lignes de taches
        taches_html = ""
        for tache in taches:
            taches_html += self._render_tache_row(tache, level=0)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rapport Taches - {chantier_nom}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 12px;
            color: #333;
            margin: 20px;
        }}
        h1 {{
            color: #2C3E50;
            font-size: 18px;
            margin-bottom: 5px;
        }}
        .header {{
            border-bottom: 2px solid #3498DB;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .meta {{
            color: #666;
            font-size: 10px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            padding: 10px;
            background: #F8F9FA;
            border-radius: 5px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 10px;
            color: #666;
        }}
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #E0E0E0;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background: #3498DB;
            color: white;
            padding: 8px;
            text-align: left;
            font-size: 11px;
        }}
        td {{
            padding: 6px 8px;
            border-bottom: 1px solid #E0E0E0;
            font-size: 11px;
        }}
        tr:hover {{
            background: #F8F9FA;
        }}
        .status-done {{
            color: #4CAF50;
        }}
        .status-todo {{
            color: #9E9E9E;
        }}
        .subtask {{
            padding-left: 20px;
            color: #666;
        }}
        .color-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 10px;
            border-top: 1px solid #E0E0E0;
            font-size: 10px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Rapport des Taches</h1>
        <p style="font-size: 14px; margin: 5px 0;">{chantier_nom}</p>
        <p class="meta">Genere le {now}</p>
    </div>

    <div class="stats">
        <div class="stat-item">
            <div class="stat-value">{stats.get('total', 0)}</div>
            <div class="stat-label">Total taches</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: #4CAF50;">{stats.get('terminees', 0)}</div>
            <div class="stat-label">Terminees</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: #F44336;">{stats.get('en_retard', 0)}</div>
            <div class="stat-label">En retard</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{heures_realisees:.1f}h</div>
            <div class="stat-label">Heures realisees</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{heures_estimees:.1f}h</div>
            <div class="stat-label">Heures estimees</div>
        </div>
    </div>

    <div>
        <strong>Progression globale: {progression:.0f}%</strong>
        <span style="color: {couleur};"> ({label_couleur})</span>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progression:.0f}%; background: {couleur};"></div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 5%;">Statut</th>
                <th style="width: 40%;">Tache</th>
                <th style="width: 15%;">Echeance</th>
                <th style="width: 15%;">Heures</th>
                <th style="width: 15%;">Quantite</th>
                <th style="width: 10%;">Progression</th>
            </tr>
        </thead>
        <tbody>
            {taches_html}
        </tbody>
    </table>

    <div class="footer">
        Hub Chantier - Greg Construction
    </div>
</body>
</html>
        """

    def _render_tache_row(self, tache, level: int = 0) -> str:
        """Rend une ligne de tache en HTML."""
        indent = "&nbsp;" * (level * 4)
        status_class = "status-done" if tache.est_terminee else "status-todo"
        status_icon = "✓" if tache.est_terminee else "○"

        # Couleur progression
        couleur_info = CouleurProgression.from_progression(
            tache.heures_realisees, tache.heures_estimees or 0
        )

        echeance = ""
        if tache.date_echeance:
            echeance = tache.date_echeance.strftime("%d/%m/%Y") if hasattr(tache.date_echeance, 'strftime') else str(tache.date_echeance)

        heures = ""
        if tache.heures_estimees:
            heures = f"{tache.heures_realisees:.1f}/{tache.heures_estimees:.1f}h"

        quantite = ""
        if tache.quantite_estimee and tache.unite_mesure:
            quantite = f"{tache.quantite_realisee:.1f}/{tache.quantite_estimee:.1f} {tache.unite_mesure.value}"

        progression = ""
        if tache.heures_estimees and tache.heures_estimees > 0:
            pct = min((tache.heures_realisees / tache.heures_estimees) * 100, 100)
            progression = f"{pct:.0f}%"

        row = f"""
        <tr class="{'subtask' if level > 0 else ''}">
            <td class="{status_class}">{status_icon}</td>
            <td>{indent}<span class="color-indicator" style="background: {couleur_info.hex_code};"></span>{tache.titre}</td>
            <td>{echeance}</td>
            <td>{heures}</td>
            <td>{quantite}</td>
            <td>{progression}</td>
        </tr>
        """

        # Sous-taches
        if hasattr(tache, 'sous_taches') and tache.sous_taches:
            for sous_tache in tache.sous_taches:
                row += self._render_tache_row(sous_tache, level + 1)

        return row

    def _html_to_pdf(self, html_content: str) -> bytes:
        """
        Convertit le HTML en PDF.

        Utilise une approche simple qui retourne le HTML encode
        pour compatibilite maximale. En production, utiliser weasyprint ou wkhtmltopdf.
        """
        try:
            # Essayer d'utiliser weasyprint si disponible
            from weasyprint import HTML
            pdf_buffer = BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            return pdf_buffer.getvalue()
        except ImportError:
            # Fallback: retourner le HTML comme "PDF" (pour dev/test)
            # En production, installer weasyprint
            return html_content.encode('utf-8')
