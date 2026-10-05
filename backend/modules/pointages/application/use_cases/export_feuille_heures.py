"""Use Case: Exporter les feuilles d'heures (FDH-03, FDH-17)."""

import csv
import io
from datetime import date, timedelta
from typing import Optional, List

from shared.application.ports.entity_info_service import EntityInfoService

from ...domain.repositories import PointageRepository, FeuilleHeuresRepository
from ...domain.events import FeuilleHeuresExportedEvent
from ...domain.value_objects import StatutPointage
from ..services import enrichir_pointages
from ..dtos import (
    ExportFeuilleHeuresDTO,
    ExportResultDTO,
    FormatExport,
    FeuilleRouteDTO,
    ChantierRouteDTO,
)
from ..ports import EventBus, NullEventBus


JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


class ExportFeuilleHeuresUseCase:
    """
    Exporte les feuilles d'heures dans différents formats.

    Implémente:
    - FDH-03: Bouton Exporter
    - FDH-17: Export ERP manuel
    - FDH-19: Feuilles de route PDF
    """

    def __init__(
        self,
        feuille_repo: FeuilleHeuresRepository,
        pointage_repo: PointageRepository,
        event_bus: Optional[EventBus] = None,
        entity_info_service: Optional[EntityInfoService] = None,
    ):
        """
        Initialise le use case.

        Args:
            feuille_repo: Repository des feuilles d'heures.
            pointage_repo: Repository des pointages.
            event_bus: Bus d'événements (optionnel).
            entity_info_service: Service fournissant les noms d'utilisateurs
                et de chantiers (optionnel). Sans lui, les colonnes de noms
                du fichier exporte restent vides.
        """
        self.feuille_repo = feuille_repo
        self.pointage_repo = pointage_repo
        self.event_bus = event_bus or NullEventBus()
        self.entity_info_service = entity_info_service

    def execute(
        self, dto: ExportFeuilleHeuresDTO, exported_by: int
    ) -> ExportResultDTO:
        """
        Exécute l'export des feuilles d'heures.

        Args:
            dto: Les critères d'export.
            exported_by: ID de l'utilisateur qui exporte.

        Returns:
            Le résultat de l'export.
        """
        try:
            # Récupère les pointages VALIDÉS de la période : l'export alimente
            # la paie, les brouillons, soumis et rejetés n'y ont pas leur place.
            pointages, total = self.pointage_repo.search(
                date_debut=dto.date_debut,
                date_fin=dto.date_fin,
                statut=StatutPointage.VALIDE,
                skip=0,
                limit=100000,  # Pas de limite pour l'export
            )

            # Filtre par utilisateurs si spécifié
            if dto.utilisateur_ids:
                pointages = [p for p in pointages if p.utilisateur_id in dto.utilisateur_ids]

            # Filtre par chantiers si spécifié
            if dto.chantier_ids:
                pointages = [p for p in pointages if p.chantier_id in dto.chantier_ids]

            if not pointages:
                return ExportResultDTO(
                    success=False,
                    format_export=dto.format_export.value,
                    error_message="Aucune heure validée à exporter pour les critères sélectionnés",
                )

            # Renseigne les noms d'utilisateurs et de chantiers : le depot ne
            # remonte que les identifiants, inexploitables pour la paie.
            # Place apres les filtres pour n'interroger que le perimetre exporte.
            enrichir_pointages(pointages, self.entity_info_service)

            # Génère l'export selon le format
            if dto.format_export == FormatExport.CSV:
                return self._export_csv(pointages, dto, exported_by)
            elif dto.format_export == FormatExport.XLSX:
                return self._export_xlsx(pointages, dto, exported_by)
            elif dto.format_export == FormatExport.ERP:
                return self._export_erp(pointages, dto, exported_by)
            else:
                return ExportResultDTO(
                    success=False,
                    format_export=dto.format_export.value,
                    error_message=f"Format {dto.format_export.value} non encore implémenté",
                )

        except Exception as e:
            return ExportResultDTO(
                success=False,
                format_export=dto.format_export.value,
                error_message=str(e),
            )

    def _export_csv(
        self, pointages: List, dto: ExportFeuilleHeuresDTO, exported_by: int
    ) -> ExportResultDTO:
        """Génère un export CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")

        # En-tête
        headers = [
            "Date",
            "Utilisateur ID",
            "Utilisateur",
            "Chantier ID",
            "Chantier",
            "Heures Normales",
            "Heures Sup",
            "Total",
            "Statut",
        ]
        if dto.inclure_signatures:
            headers.extend(["Signé", "Date Signature"])
        writer.writerow(headers)

        # Données
        for p in pointages:
            row = [
                p.date_pointage.isoformat(),
                p.utilisateur_id,
                p.utilisateur_nom or "",
                p.chantier_id,
                p.chantier_nom or "",
                str(p.heures_normales),
                str(p.heures_supplementaires),
                str(p.total_heures),
                p.statut.value,
            ]
            if dto.inclure_signatures:
                row.extend([
                    "Oui" if p.signature_utilisateur else "Non",
                    p.signature_date.isoformat() if p.signature_date else "",
                ])
            writer.writerow(row)

        content = output.getvalue().encode("utf-8-sig")  # BOM pour Excel
        filename = f"feuilles_heures_{dto.date_debut}_{dto.date_fin}.csv"

        # Publie l'événement
        self._publish_export_event(pointages[0], dto, exported_by)

        return ExportResultDTO(
            success=True,
            format_export=FormatExport.CSV.value,
            filename=filename,
            file_content=content,
            records_count=len(pointages),
        )

    @staticmethod
    def _heures_decimal(duree) -> float:
        """
        Convertit une duree en nombre d'heures decimal.

        Le classeur recoit des nombres et non du texte "08:30", pour que les
        heures restent sommables dans Excel.

        Args:
            duree: Duree du domaine, ou None.

        Returns:
            Le nombre d'heures en decimal (0.0 si duree absente).
        """
        if duree is None:
            return 0.0
        decimal = getattr(duree, "decimal", None)
        if decimal is not None:
            return round(float(decimal), 2)
        # Filet de securite si la duree n'expose pas .decimal (mock, DTO brut)
        try:
            return round(float(duree), 2)
        except (TypeError, ValueError):
            return 0.0

    def _export_xlsx(
        self, pointages: List, dto: ExportFeuilleHeuresDTO, exported_by: int
    ) -> ExportResultDTO:
        """
        Genere un export Excel (FDH-03).

        Reprend les colonnes de l'export CSV, avec une mise en forme
        exploitable directement par l'assistante de direction : en-tetes
        figees, filtre automatique, heures en decimal et ligne de totaux.

        Args:
            pointages: Les pointages a exporter.
            dto: Les criteres d'export.
            exported_by: ID de l'utilisateur qui exporte.

        Returns:
            Le resultat de l'export avec le classeur en binaire.
        """
        # Import local : openpyxl n'est charge que lors d'un export Excel.
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Feuilles d'heures"

        headers = [
            "Date",
            "Utilisateur ID",
            "Utilisateur",
            "Chantier ID",
            "Chantier",
            "Heures Normales",
            "Heures Sup",
            "Total",
            "Statut",
        ]
        if dto.inclure_signatures:
            headers.extend(["Signé", "Date Signature"])

        sheet.append(headers)

        # Colonnes d'heures (1-indexe) : utilisees pour le format et les totaux
        colonnes_heures = (6, 7, 8)

        for pointage in pointages:
            row = [
                pointage.date_pointage,
                pointage.utilisateur_id,
                pointage.utilisateur_nom or "",
                pointage.chantier_id,
                pointage.chantier_nom or "",
                self._heures_decimal(pointage.heures_normales),
                self._heures_decimal(pointage.heures_supplementaires),
                self._heures_decimal(pointage.total_heures),
                pointage.statut.value,
            ]
            if dto.inclure_signatures:
                row.extend([
                    "Oui" if pointage.signature_utilisateur else "Non",
                    pointage.signature_date if pointage.signature_date else "",
                ])
            sheet.append(row)

        # Mise en forme de l'en-tete
        entete_fond = PatternFill("solid", fgColor="1F3A5F")
        entete_police = Font(bold=True, color="FFFFFF")
        bordure_bas = Border(bottom=Side(style="thin", color="BFBFBF"))
        for cellule in sheet[1]:
            cellule.fill = entete_fond
            cellule.font = entete_police
            cellule.alignment = Alignment(horizontal="center", vertical="center")
            cellule.border = bordure_bas
        sheet.row_dimensions[1].height = 22

        nb_lignes = len(pointages)
        derniere_ligne_donnees = nb_lignes + 1

        # Formats des colonnes de donnees
        colonne_date_signature = len(headers) if dto.inclure_signatures else None
        for ligne in sheet.iter_rows(
            min_row=2, max_row=derniere_ligne_donnees, max_col=len(headers)
        ):
            for cellule in ligne:
                if cellule.column == 1:
                    cellule.number_format = "DD/MM/YYYY"
                elif cellule.column in colonnes_heures:
                    cellule.number_format = "0.00"
                elif cellule.column == colonne_date_signature:
                    cellule.number_format = "DD/MM/YYYY HH:MM"

        # Ligne de totaux : somme Excel, donc recalculee si l'assistante filtre
        if nb_lignes > 0:
            ligne_total = derniere_ligne_donnees + 1
            sheet.cell(row=ligne_total, column=1, value="TOTAL")
            for colonne in colonnes_heures:
                lettre = get_column_letter(colonne)
                cellule = sheet.cell(row=ligne_total, column=colonne)
                cellule.value = f"=SUM({lettre}2:{lettre}{derniere_ligne_donnees})"
                cellule.number_format = "0.00"
            for cellule in sheet[ligne_total]:
                cellule.font = Font(bold=True)

        # Filtre automatique et en-tete figee
        sheet.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{derniere_ligne_donnees}"
        sheet.freeze_panes = "A2"

        # Largeur des colonnes ajustee au contenu
        for index, entete in enumerate(headers, start=1):
            largeur_max = len(entete)
            for cellule in sheet[get_column_letter(index)][1:derniere_ligne_donnees]:
                if cellule.value is not None:
                    largeur_max = max(largeur_max, len(str(cellule.value)))
            sheet.column_dimensions[get_column_letter(index)].width = min(largeur_max + 3, 40)

        buffer = io.BytesIO()
        workbook.save(buffer)
        content = buffer.getvalue()
        filename = f"feuilles_heures_{dto.date_debut}_{dto.date_fin}.xlsx"

        # Publie l'événement
        self._publish_export_event(pointages[0], dto, exported_by)

        return ExportResultDTO(
            success=True,
            format_export=FormatExport.XLSX.value,
            filename=filename,
            file_content=content,
            records_count=len(pointages),
        )

    def _export_erp(
        self, pointages: List, dto: ExportFeuilleHeuresDTO, exported_by: int
    ) -> ExportResultDTO:
        """Génère un export ERP (FDH-17)."""
        # Format simplifié pour ERP - à adapter selon l'ERP cible
        output = io.StringIO()
        writer = csv.writer(output, delimiter="|")

        # En-tête ERP
        writer.writerow([
            "CODE_UTILISATEUR",
            "DATE",
            "CODE_CHANTIER",
            "HEURES_NORMALES",
            "HEURES_SUP",
            "PANIER",
            "TRANSPORT",
        ])

        # Données - format ERP
        for p in pointages:
            writer.writerow([
                f"USER{p.utilisateur_id:05d}",  # Code utilisateur format ERP
                p.date_pointage.strftime("%Y%m%d"),
                f"CHT{p.chantier_id:05d}",  # Code chantier format ERP
                f"{p.heures_normales.decimal:.2f}",
                f"{p.heures_supplementaires.decimal:.2f}",
                "",  # TODO: Variables de paie
                "",
            ])

        content = output.getvalue().encode("utf-8")
        filename = f"export_erp_{dto.date_debut}_{dto.date_fin}.txt"

        # Publie l'événement
        self._publish_export_event(pointages[0], dto, exported_by)

        return ExportResultDTO(
            success=True,
            format_export=FormatExport.ERP.value,
            filename=filename,
            file_content=content,
            records_count=len(pointages),
        )

    def generate_feuille_route(
        self, utilisateur_id: int, semaine_debut: date
    ) -> FeuilleRouteDTO:
        """
        Génère une feuille de route pour un utilisateur (FDH-19).

        Args:
            utilisateur_id: ID de l'utilisateur.
            semaine_debut: Date du lundi de la semaine.

        Returns:
            DTO de la feuille de route.
        """
        # Assure que c'est un lundi
        if semaine_debut.weekday() != 0:
            days_since_monday = semaine_debut.weekday()
            semaine_debut = semaine_debut - timedelta(days=days_since_monday)

        # Récupère les pointages de la semaine
        pointages = self.pointage_repo.find_by_utilisateur_and_semaine(
            utilisateur_id=utilisateur_id,
            semaine_debut=semaine_debut,
        )

        # Nom utilisateur
        utilisateur_nom = "Utilisateur"
        if pointages:
            utilisateur_nom = pointages[0].utilisateur_nom or f"Utilisateur {utilisateur_id}"

        # Groupe par chantier
        from collections import defaultdict
        by_chantier = defaultdict(list)
        for p in pointages:
            by_chantier[p.chantier_id].append(p)

        # Construit les chantiers
        chantiers = []
        total_minutes = 0

        for chantier_id, chantier_pointages in by_chantier.items():
            first_p = chantier_pointages[0]
            chantier_nom = first_p.chantier_nom or f"Chantier {chantier_id}"

            jours = []
            heures_par_jour = {}
            chantier_total = 0

            for i in range(7):
                jour_date = semaine_debut + timedelta(days=i)
                jour_nom = JOURS_SEMAINE[i]
                jour_pointage = next(
                    (p for p in chantier_pointages if p.date_pointage == jour_date),
                    None,
                )

                if jour_pointage:
                    jours.append(jour_nom)
                    heures_par_jour[jour_nom] = str(jour_pointage.total_heures)
                    chantier_total += jour_pointage.total_heures.total_minutes

            from ...domain.value_objects import Duree
            total_minutes += chantier_total

            chantiers.append(
                ChantierRouteDTO(
                    chantier_id=chantier_id,
                    chantier_nom=chantier_nom,
                    adresse=None,  # TODO: Charger depuis module chantiers
                    jours=jours,
                    heures_par_jour=heures_par_jour,
                    total_heures=str(Duree.from_minutes(chantier_total)),
                )
            )

        from ...domain.value_objects import Duree
        iso_cal = semaine_debut.isocalendar()

        return FeuilleRouteDTO(
            utilisateur_id=utilisateur_id,
            utilisateur_nom=utilisateur_nom,
            semaine=f"Semaine {iso_cal[1]} - {iso_cal[0]}",
            chantiers=chantiers,
            total_heures=str(Duree.from_minutes(total_minutes)),
        )

    def _publish_export_event(
        self, first_pointage, dto: ExportFeuilleHeuresDTO, exported_by: int
    ) -> None:
        """Publie l'événement d'export."""
        # Récupère la feuille pour l'événement
        days_since_monday = first_pointage.date_pointage.weekday()
        semaine_debut = first_pointage.date_pointage - timedelta(days=days_since_monday)

        feuille = self.feuille_repo.find_by_utilisateur_and_semaine(
            utilisateur_id=first_pointage.utilisateur_id,
            semaine_debut=semaine_debut,
        )

        if feuille:
            event = FeuilleHeuresExportedEvent(
                feuille_id=feuille.id,
                utilisateur_id=feuille.utilisateur_id,
                semaine_debut=semaine_debut,
                format_export=dto.format_export.value,
                destination=dto.destination_erp,
                exported_by=exported_by,
            )
            self.event_bus.publish(event)
