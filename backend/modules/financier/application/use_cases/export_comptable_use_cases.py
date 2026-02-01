"""Use Cases pour l'export comptable.

FIN-13: Export comptable CSV/Excel.
"""

import csv
import io
from datetime import date
from decimal import Decimal
from typing import Optional

from ...domain.repositories.export_comptable_repository import ExportComptableRepository
from ..dtos.export_dtos import ExportLigneComptableDTO, ExportComptableDTO


# Codes comptables par type d'achat
COMPTES_ACHATS = {
    "materiau": "601000",
    "sous_traitance": "604000",
    "service": "615000",
    "materiel": "606000",
}

# Codes comptables pour les ventes
COMPTE_VENTES = "706000"

# Codes TVA
COMPTE_TVA_DEDUCTIBLE = "445660"
COMPTE_TVA_COLLECTEE = "445710"

# Comptes de tiers
COMPTE_FOURNISSEUR = "401000"
COMPTE_CLIENT = "411000"


class GenerateExportComptableUseCase:
    """Use case pour generer les lignes comptables.

    FIN-13: Genere les ecritures comptables a partir des achats factures
    et des factures client emises.
    """

    def __init__(self, export_repository: ExportComptableRepository):
        self._export_repository = export_repository

    def execute(
        self,
        date_debut: date,
        date_fin: date,
        chantier_id: Optional[int] = None,
    ) -> ExportComptableDTO:
        """Genere l'export comptable pour une periode.

        Args:
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.
            chantier_id: ID du chantier (optionnel, None = tous).

        Returns:
            Le DTO d'export comptable avec toutes les lignes.
        """
        lignes = []

        # 1. Traiter les achats factures
        achats = self._export_repository.get_achats_periode(
            chantier_id, date_debut, date_fin
        )
        for achat in achats:
            lignes.extend(self._generer_ecritures_achat(achat))

        # 2. Traiter les factures client emises
        factures = self._export_repository.get_factures_periode(
            chantier_id, date_debut, date_fin
        )
        for facture in factures:
            lignes.extend(self._generer_ecritures_facture(facture))

        # Calculer les totaux
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        for ligne in lignes:
            total_debit += Decimal(ligne.debit)
            total_credit += Decimal(ligne.credit)

        return ExportComptableDTO(
            chantier_id=chantier_id,
            date_debut=date_debut.isoformat(),
            date_fin=date_fin.isoformat(),
            lignes=lignes,
            total_debit=str(total_debit.quantize(Decimal("0.01"))),
            total_credit=str(total_credit.quantize(Decimal("0.01"))),
            nombre_lignes=len(lignes),
        )

    def _generer_ecritures_achat(self, achat: dict) -> list:
        """Genere les ecritures comptables pour un achat facture.

        Pour chaque achat: 3 lignes (charge HT au debit, TVA deductible
        au debit, fournisseur au credit TTC).
        """
        lignes = []
        type_achat = achat.get("type_achat", "materiau")
        montant_ht = Decimal(str(achat.get("montant_ht", 0)))
        taux_tva = Decimal(str(achat.get("taux_tva", 20)))
        montant_tva = (montant_ht * taux_tva / Decimal("100")).quantize(Decimal("0.01"))
        montant_ttc = (montant_ht + montant_tva).quantize(Decimal("0.01"))
        code_chantier = str(achat.get("chantier_id", ""))
        date_achat = achat.get("date_facture", achat.get("date_commande", ""))
        if hasattr(date_achat, "isoformat"):
            date_achat = date_achat.isoformat()
        numero_piece = achat.get("numero_facture", "")
        libelle = achat.get("libelle", "")
        compte_charge = COMPTES_ACHATS.get(type_achat, "601000")
        tva_code = str(taux_tva)

        # Ligne 1: Charge HT au debit
        lignes.append(
            ExportLigneComptableDTO(
                date=str(date_achat),
                code_journal="HA",
                numero_piece=str(numero_piece),
                code_analytique=code_chantier,
                libelle=libelle,
                compte_general=compte_charge,
                debit=str(montant_ht.quantize(Decimal("0.01"))),
                credit="0.00",
                tva_code=tva_code,
            )
        )

        # Ligne 2: TVA deductible au debit
        if montant_tva > 0:
            lignes.append(
                ExportLigneComptableDTO(
                    date=str(date_achat),
                    code_journal="HA",
                    numero_piece=str(numero_piece),
                    code_analytique=code_chantier,
                    libelle=f"TVA deductible - {libelle}",
                    compte_general=COMPTE_TVA_DEDUCTIBLE,
                    debit=str(montant_tva),
                    credit="0.00",
                    tva_code=tva_code,
                )
            )

        # Ligne 3: Fournisseur au credit TTC
        lignes.append(
            ExportLigneComptableDTO(
                date=str(date_achat),
                code_journal="HA",
                numero_piece=str(numero_piece),
                code_analytique=code_chantier,
                libelle=f"Fournisseur - {libelle}",
                compte_general=COMPTE_FOURNISSEUR,
                debit="0.00",
                credit=str(montant_ttc),
                tva_code=tva_code,
            )
        )

        return lignes

    def _generer_ecritures_facture(self, facture: dict) -> list:
        """Genere les ecritures comptables pour une facture client.

        Pour chaque facture: 3 lignes (client au debit TTC, vente HT
        au credit, TVA collectee au credit).
        """
        lignes = []
        montant_ht = Decimal(str(facture.get("montant_ht", 0)))
        montant_tva = Decimal(str(facture.get("montant_tva", 0)))
        montant_ttc = Decimal(str(facture.get("montant_ttc", 0)))
        taux_tva = Decimal(str(facture.get("taux_tva", 20)))
        code_chantier = str(facture.get("chantier_id", ""))
        date_facture = facture.get("date_emission", "")
        if hasattr(date_facture, "isoformat"):
            date_facture = date_facture.isoformat()
        numero_piece = facture.get("numero_facture", "")
        tva_code = str(taux_tva)
        libelle = f"Facture {numero_piece}"

        # Ligne 1: Client au debit TTC
        lignes.append(
            ExportLigneComptableDTO(
                date=str(date_facture),
                code_journal="VE",
                numero_piece=str(numero_piece),
                code_analytique=code_chantier,
                libelle=libelle,
                compte_general=COMPTE_CLIENT,
                debit=str(montant_ttc.quantize(Decimal("0.01"))),
                credit="0.00",
                tva_code=tva_code,
            )
        )

        # Ligne 2: Vente HT au credit
        lignes.append(
            ExportLigneComptableDTO(
                date=str(date_facture),
                code_journal="VE",
                numero_piece=str(numero_piece),
                code_analytique=code_chantier,
                libelle=f"Vente - {libelle}",
                compte_general=COMPTE_VENTES,
                debit="0.00",
                credit=str(montant_ht.quantize(Decimal("0.01"))),
                tva_code=tva_code,
            )
        )

        # Ligne 3: TVA collectee au credit
        if montant_tva > 0:
            lignes.append(
                ExportLigneComptableDTO(
                    date=str(date_facture),
                    code_journal="VE",
                    numero_piece=str(numero_piece),
                    code_analytique=code_chantier,
                    libelle=f"TVA collectee - {libelle}",
                    compte_general=COMPTE_TVA_COLLECTEE,
                    debit="0.00",
                    credit=str(montant_tva.quantize(Decimal("0.01"))),
                    tva_code=tva_code,
                )
            )

        return lignes


class ExportCSVUseCase:
    """Use case pour generer un fichier CSV a partir de l'export comptable.

    FIN-13: Format CSV compatible avec les logiciels de comptabilite.
    """

    def execute(self, export_dto: ExportComptableDTO) -> str:
        """Genere le contenu CSV.

        Args:
            export_dto: Le DTO d'export comptable.

        Returns:
            Le contenu CSV sous forme de chaine de caracteres.
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        # En-tete
        writer.writerow([
            "Date",
            "Code Journal",
            "Numero Piece",
            "Code Analytique",
            "Libelle",
            "Compte General",
            "Debit",
            "Credit",
            "Code TVA",
        ])

        # Lignes
        for ligne in export_dto.lignes:
            writer.writerow([
                ligne.date,
                ligne.code_journal,
                ligne.numero_piece,
                ligne.code_analytique,
                ligne.libelle,
                ligne.compte_general,
                ligne.debit,
                ligne.credit,
                ligne.tva_code,
            ])

        # Ligne de totaux
        writer.writerow([])
        writer.writerow([
            "", "", "", "", "TOTAUX", "",
            export_dto.total_debit,
            export_dto.total_credit,
            "",
        ])

        return output.getvalue()


class ExportExcelUseCase:
    """Use case pour generer un fichier Excel a partir de l'export comptable.

    FIN-13: Format Excel (openpyxl) compatible avec les logiciels de comptabilite.
    """

    def execute(self, export_dto: ExportComptableDTO) -> bytes:
        """Genere le contenu Excel.

        Args:
            export_dto: Le DTO d'export comptable.

        Returns:
            Le contenu Excel sous forme de bytes.
        """
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

        wb = Workbook()
        ws = wb.active
        ws.title = "Export Comptable"

        # Styles
        header_font = Font(bold=True, size=11)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font_white = Font(bold=True, size=11, color="FFFFFF")
        total_font = Font(bold=True, size=11)
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        # Titre
        ws.merge_cells("A1:I1")
        title_cell = ws["A1"]
        title_cell.value = (
            f"Export Comptable - Periode du {export_dto.date_debut} au {export_dto.date_fin}"
        )
        title_cell.font = Font(bold=True, size=14)
        title_cell.alignment = Alignment(horizontal="center")

        if export_dto.chantier_id:
            ws.merge_cells("A2:I2")
            ws["A2"].value = f"Chantier: {export_dto.chantier_id}"
            ws["A2"].font = Font(size=11)
            ws["A2"].alignment = Alignment(horizontal="center")

        # En-tetes (ligne 4)
        headers = [
            "Date", "Code Journal", "Numero Piece", "Code Analytique",
            "Libelle", "Compte General", "Debit", "Credit", "Code TVA",
        ]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_idx)
            cell.value = header
            cell.font = header_font_white
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border

        # Lignes de donnees
        for row_idx, ligne in enumerate(export_dto.lignes, 5):
            values = [
                ligne.date, ligne.code_journal, ligne.numero_piece,
                ligne.code_analytique, ligne.libelle, ligne.compte_general,
                ligne.debit, ligne.credit, ligne.tva_code,
            ]
            for col_idx, value in enumerate(values, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.value = value
                cell.border = thin_border
                if col_idx in (7, 8):  # Debit et Credit
                    cell.alignment = Alignment(horizontal="right")

        # Ligne de totaux
        total_row = 5 + len(export_dto.lignes) + 1
        ws.cell(row=total_row, column=5).value = "TOTAUX"
        ws.cell(row=total_row, column=5).font = total_font
        ws.cell(row=total_row, column=7).value = export_dto.total_debit
        ws.cell(row=total_row, column=7).font = total_font
        ws.cell(row=total_row, column=7).alignment = Alignment(horizontal="right")
        ws.cell(row=total_row, column=8).value = export_dto.total_credit
        ws.cell(row=total_row, column=8).font = total_font
        ws.cell(row=total_row, column=8).alignment = Alignment(horizontal="right")

        # Ajuster les largeurs de colonnes
        column_widths = [12, 14, 18, 16, 40, 16, 14, 14, 10]
        for col_idx, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + col_idx)].width = width

        # Sauvegarder en bytes
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
