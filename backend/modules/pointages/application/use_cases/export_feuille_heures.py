"""Use Case: Exporter les feuilles d'heures (FDH-03, FDH-17)."""

import csv
import io
from datetime import datetime, date, timedelta
from typing import Optional, List

from ...domain.repositories import PointageRepository, FeuilleHeuresRepository
from ...domain.events import FeuilleHeuresExportedEvent
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
    ):
        """
        Initialise le use case.

        Args:
            feuille_repo: Repository des feuilles d'heures.
            pointage_repo: Repository des pointages.
            event_bus: Bus d'événements (optionnel).
        """
        self.feuille_repo = feuille_repo
        self.pointage_repo = pointage_repo
        self.event_bus = event_bus or NullEventBus()

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
            # Récupère les pointages pour la période
            pointages, total = self.pointage_repo.search(
                date_debut=dto.date_debut,
                date_fin=dto.date_fin,
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
                    error_message="Aucune donnée à exporter pour les critères sélectionnés",
                )

            # Génère l'export selon le format
            if dto.format_export == FormatExport.CSV:
                return self._export_csv(pointages, dto, exported_by)
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
