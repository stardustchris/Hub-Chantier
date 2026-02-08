"""Generateur PDF de devis client avec fpdf2.

DEV-12: Generation PDF devis client.

Ce module implemente le port IPDFGenerator en utilisant fpdf2.
Le PDF genere est une VUE CLIENT : il ne contient ni debourses,
ni marges, ni informations internes.

Format: A4 portrait, police Helvetica, montants en EUR.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from fpdf import FPDF

from ...application.dtos.devis_dtos import DevisDetailDTO, VentilationTVADTO
from ...application.dtos.lot_dtos import LotDevisDTO
from ...application.dtos.ligne_dtos import LigneDevisDTO
from ...application.ports.pdf_generator import IPDFGenerator


# ─────────────────────────────────────────────────────────────────────────────
# Constantes entreprise (a externaliser en config si besoin)
# ─────────────────────────────────────────────────────────────────────────────
ENTREPRISE_NOM = "Greg Constructions"
ENTREPRISE_ADRESSE = "12 rue des Batisseurs\n69001 Lyon"
ENTREPRISE_TELEPHONE = "04 72 00 00 00"
ENTREPRISE_SIRET = "123 456 789 00012"
ENTREPRISE_TVA_INTRA = "FR 12 123456789"
ENTREPRISE_RCS = "RCS Lyon 123 456 789"

# ─────────────────────────────────────────────────────────────────────────────
# Couleurs et dimensions
# ─────────────────────────────────────────────────────────────────────────────
COULEUR_PRIMAIRE = (41, 65, 122)       # Bleu fonce
COULEUR_ENTETE_LOT = (230, 235, 245)   # Bleu clair (fond lot)
COULEUR_LIGNE_ALTERNE = (245, 247, 250)  # Gris tres clair
COULEUR_BORDURE = (180, 190, 200)      # Gris moyen
COULEUR_TEXTE = (33, 37, 41)           # Quasi-noir

MARGE_GAUCHE = 15
MARGE_DROITE = 15
LARGEUR_UTILE = 210 - MARGE_GAUCHE - MARGE_DROITE  # 180mm

# Mapping echeances lisibles
ECHEANCES_LABELS = {
    "comptant": "Comptant",
    "30_jours": "30 jours",
    "30_jours_fin_mois": "30 jours fin de mois",
    "45_jours": "45 jours",
    "45_jours_fin_mois": "45 jours fin de mois",
    "60_jours": "60 jours",
    "60_jours_fin_mois": "60 jours fin de mois",
}


def _format_montant(valeur: str) -> str:
    """Formate un montant en EUR francais (1 234,56).

    Args:
        valeur: Le montant sous forme de string (ex: "1234.56").

    Returns:
        Le montant formate (ex: "1 234,56").
    """
    try:
        d = Decimal(valeur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return valeur

    signe = "-" if d < 0 else ""
    d = abs(d)
    partie_entiere = int(d)
    partie_decimale = str(d).split(".")[1] if "." in str(d) else "00"

    # Formater avec espaces comme separateur de milliers
    s = str(partie_entiere)
    groups = []
    while s:
        groups.append(s[-3:])
        s = s[:-3]
    partie_entiere_fmt = " ".join(reversed(groups))

    return f"{signe}{partie_entiere_fmt},{partie_decimale}"


def _format_montant_eur(valeur: str) -> str:
    """Formate un montant avec le symbole EUR.

    Args:
        valeur: Le montant sous forme de string.

    Returns:
        Le montant formate suivi de " EUR" (ex: "1 234,56 EUR").
    """
    return f"{_format_montant(valeur)} EUR"


def _format_date_fr(date_iso: Optional[str]) -> str:
    """Formate une date ISO en format francais JJ/MM/AAAA.

    Args:
        date_iso: Date au format ISO (ex: "2026-02-08").

    Returns:
        La date formatee (ex: "08/02/2026") ou "-" si None.
    """
    if not date_iso:
        return "-"
    try:
        parts = date_iso.split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except (IndexError, ValueError):
        return date_iso


def _format_pourcentage(valeur: str) -> str:
    """Formate un pourcentage (ex: "5.5" -> "5,50 %").

    Args:
        valeur: Le pourcentage sous forme de string.

    Returns:
        Le pourcentage formate.
    """
    try:
        d = Decimal(valeur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{str(d).replace('.', ',')} %"
    except Exception:
        return f"{valeur} %"


class DevisPDFGenerator(IPDFGenerator):
    """Implementation du generateur PDF devis client avec fpdf2.

    Genere un PDF A4 portrait professionnel contenant :
    - En-tete entreprise + infos devis
    - Coordonnees client
    - Objet des travaux
    - Tableau des lots et lignes (vue client)
    - Recapitulatif (HT, TVA, TTC, retenue de garantie, net a payer)
    - Conditions de paiement
    - Mentions legales TVA reduite (si applicable)
    - Zone de signature client
    """

    def generate(self, devis: DevisDetailDTO) -> bytes:
        """Genere le PDF du devis.

        Args:
            devis: Le DTO detaille du devis.

        Returns:
            Le contenu du PDF en bytes.
        """
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=25)
        pdf.set_margins(left=MARGE_GAUCHE, top=15, right=MARGE_DROITE)
        pdf.add_page()

        self._draw_header(pdf, devis)
        self._draw_client_block(pdf, devis)
        self._draw_objet(pdf, devis)
        self._draw_lots_table(pdf, devis)
        self._draw_recapitulatif(pdf, devis)
        self._draw_conditions(pdf, devis)

        if devis.mention_tva_reduite:
            self._draw_mention_tva_reduite(pdf, devis.mention_tva_reduite)

        self._draw_signature_block(pdf, devis)
        self._draw_footer(pdf)

        return pdf.output()

    # ─────────────────────────────────────────────────────────────────
    # Sections du PDF
    # ─────────────────────────────────────────────────────────────────

    def _draw_header(self, pdf: FPDF, devis: DevisDetailDTO) -> None:
        """Dessine l'en-tete avec les infos entreprise et le numero de devis."""
        y_start = pdf.get_y()

        # Bloc entreprise (gauche)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=90, h=8, text=ENTREPRISE_NOM, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*COULEUR_TEXTE)
        for line in ENTREPRISE_ADRESSE.split("\n"):
            pdf.cell(w=90, h=4.5, text=line, new_x="LMARGIN", new_y="NEXT")
        pdf.cell(w=90, h=4.5, text=f"Tel : {ENTREPRISE_TELEPHONE}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(w=90, h=4.5, text=f"SIRET : {ENTREPRISE_SIRET}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(w=90, h=4.5, text=f"TVA : {ENTREPRISE_TVA_INTRA}", new_x="LMARGIN", new_y="NEXT")

        y_after_entreprise = pdf.get_y()

        # Bloc devis (droite)
        pdf.set_y(y_start)

        # Cadre colore pour le numero
        pdf.set_x(MARGE_GAUCHE + 100)
        pdf.set_fill_color(*COULEUR_PRIMAIRE)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(w=80, h=10, text="DEVIS", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_x(MARGE_GAUCHE + 100)
        pdf.set_fill_color(*COULEUR_ENTETE_LOT)
        pdf.set_text_color(*COULEUR_TEXTE)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(w=80, h=8, text=devis.numero, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

        # Infos devis
        pdf.set_font("Helvetica", "", 9)
        infos = [
            ("Date", _format_date_fr(devis.date_creation)),
            ("Validite", _format_date_fr(devis.date_validite)),
        ]
        for label, value in infos:
            pdf.set_x(MARGE_GAUCHE + 100)
            pdf.cell(w=30, h=5, text=f"{label} :", new_x="RIGHT")
            pdf.cell(w=50, h=5, text=value, align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(max(y_after_entreprise, pdf.get_y()) + 5)

        # Trait de separation
        pdf.set_draw_color(*COULEUR_PRIMAIRE)
        pdf.set_line_width(0.5)
        pdf.line(MARGE_GAUCHE, pdf.get_y(), 210 - MARGE_DROITE, pdf.get_y())
        pdf.ln(5)

    def _draw_client_block(self, pdf: FPDF, devis: DevisDetailDTO) -> None:
        """Dessine le bloc d'informations client."""
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=LARGEUR_UTILE, h=6, text="CLIENT", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*COULEUR_TEXTE)

        # Cadre client
        y_start = pdf.get_y()
        pdf.set_fill_color(*COULEUR_ENTETE_LOT)
        pdf.rect(MARGE_GAUCHE, y_start, LARGEUR_UTILE, 0, style="")  # placeholder, hauteur calculee apres

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(w=LARGEUR_UTILE, h=6, text=devis.client_nom, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        if devis.client_adresse:
            for line in devis.client_adresse.split("\n"):
                pdf.cell(w=LARGEUR_UTILE, h=4.5, text=line, new_x="LMARGIN", new_y="NEXT")
        if devis.client_telephone:
            pdf.cell(w=LARGEUR_UTILE, h=4.5, text=f"Tel : {devis.client_telephone}", new_x="LMARGIN", new_y="NEXT")
        if devis.client_email:
            pdf.cell(w=LARGEUR_UTILE, h=4.5, text=f"Email : {devis.client_email}", new_x="LMARGIN", new_y="NEXT")

        y_end = pdf.get_y()
        # Dessiner le cadre autour du bloc client
        pdf.set_draw_color(*COULEUR_BORDURE)
        pdf.set_line_width(0.3)
        pdf.rect(MARGE_GAUCHE, y_start - 1, LARGEUR_UTILE, y_end - y_start + 3)

        pdf.ln(8)

    def _draw_objet(self, pdf: FPDF, devis: DevisDetailDTO) -> None:
        """Dessine la section objet des travaux."""
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=30, h=6, text="Objet :", new_x="RIGHT")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*COULEUR_TEXTE)
        pdf.multi_cell(w=LARGEUR_UTILE - 30, h=6, text=devis.objet or "-")
        pdf.ln(5)

    def _draw_lots_table(self, pdf: FPDF, devis: DevisDetailDTO) -> None:
        """Dessine le tableau des lots et lignes (vue client)."""
        # En-tete du tableau
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=LARGEUR_UTILE, h=7, text="DETAIL DES TRAVAUX", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Colonnes : Designation(80) | Unite(15) | Qte(20) | PU HT(30) | Total HT(35)
        col_widths = [80, 15, 20, 30, 35]
        col_headers = ["Designation", "Unite", "Qte", "PU HT", "Total HT"]
        col_aligns = ["L", "C", "R", "R", "R"]

        # En-tete colonnes
        pdf.set_fill_color(*COULEUR_PRIMAIRE)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_draw_color(*COULEUR_PRIMAIRE)

        for i, (w, header, align) in enumerate(zip(col_widths, col_headers, col_aligns)):
            pdf.cell(w=w, h=7, text=header, align=align, border=1, fill=True,
                     new_x="RIGHT" if i < len(col_widths) - 1 else "LMARGIN",
                     new_y="TOP" if i < len(col_widths) - 1 else "NEXT")

        # Lots et lignes
        for lot in devis.lots:
            self._draw_lot(pdf, lot, col_widths, col_aligns)

        pdf.ln(3)

    def _draw_lot(
        self,
        pdf: FPDF,
        lot: LotDevisDTO,
        col_widths: list[int],
        col_aligns: list[str],
    ) -> None:
        """Dessine un lot et ses lignes dans le tableau."""
        # Verifier saut de page avant le lot
        if pdf.get_y() > 255:
            pdf.add_page()

        # Titre du lot (bande coloree)
        titre_lot = f"Lot {lot.numero} - {lot.titre}" if lot.numero else lot.titre
        pdf.set_fill_color(*COULEUR_ENTETE_LOT)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_draw_color(*COULEUR_BORDURE)

        total_width = sum(col_widths)
        pdf.cell(w=total_width, h=7, text=titre_lot, border=1, fill=True,
                 new_x="LMARGIN", new_y="NEXT")

        # Lignes du lot
        pdf.set_text_color(*COULEUR_TEXTE)
        pdf.set_font("Helvetica", "", 8)

        for idx, ligne in enumerate(lot.lignes):
            self._draw_ligne(pdf, ligne, col_widths, col_aligns, idx % 2 == 1)

        # Sous-total lot
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(*COULEUR_ENTETE_LOT)

        stl_label_w = col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3]
        pdf.cell(w=stl_label_w, h=6, text=f"Sous-total {lot.titre}",
                 border="TB", fill=True, align="R", new_x="RIGHT")
        pdf.cell(w=col_widths[4], h=6,
                 text=_format_montant_eur(lot.total_ht),
                 border="TB", fill=True, align="R",
                 new_x="LMARGIN", new_y="NEXT")

    def _draw_ligne(
        self,
        pdf: FPDF,
        ligne: LigneDevisDTO,
        col_widths: list[int],
        col_aligns: list[str],
        alternate: bool,
    ) -> None:
        """Dessine une ligne de devis dans le tableau."""
        # Verifier saut de page
        if pdf.get_y() > 265:
            pdf.add_page()
            # Re-dessiner l'en-tete du tableau apres saut de page
            self._redraw_table_header(pdf, col_widths)

        if alternate:
            pdf.set_fill_color(*COULEUR_LIGNE_ALTERNE)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.set_draw_color(*COULEUR_BORDURE)

        values = [
            ligne.designation,
            ligne.unite,
            _format_montant(ligne.quantite),
            _format_montant_eur(ligne.prix_unitaire_ht),
            _format_montant_eur(ligne.montant_ht),
        ]

        for i, (w, val, align) in enumerate(zip(col_widths, values, col_aligns)):
            pdf.cell(w=w, h=5.5, text=val, align=align,
                     border="LR", fill=True,
                     new_x="RIGHT" if i < len(col_widths) - 1 else "LMARGIN",
                     new_y="TOP" if i < len(col_widths) - 1 else "NEXT")

    def _redraw_table_header(self, pdf: FPDF, col_widths: list[int]) -> None:
        """Re-dessine l'en-tete du tableau apres un saut de page."""
        col_headers = ["Designation", "Unite", "Qte", "PU HT", "Total HT"]
        col_aligns = ["L", "C", "R", "R", "R"]

        pdf.set_fill_color(*COULEUR_PRIMAIRE)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_draw_color(*COULEUR_PRIMAIRE)

        for i, (w, header, align) in enumerate(zip(col_widths, col_headers, col_aligns)):
            pdf.cell(w=w, h=7, text=header, align=align, border=1, fill=True,
                     new_x="RIGHT" if i < len(col_widths) - 1 else "LMARGIN",
                     new_y="TOP" if i < len(col_widths) - 1 else "NEXT")

        pdf.set_text_color(*COULEUR_TEXTE)
        pdf.set_font("Helvetica", "", 8)

    def _draw_recapitulatif(self, pdf: FPDF, devis: DevisDetailDTO) -> None:
        """Dessine le bloc recapitulatif (HT, TVA, TTC, retenue, net a payer)."""
        # Verifier saut de page
        if pdf.get_y() > 230:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=LARGEUR_UTILE, h=7, text="RECAPITULATIF", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Bloc a droite (largeur 90mm)
        recap_x = MARGE_GAUCHE + LARGEUR_UTILE - 90
        recap_w_label = 50
        recap_w_value = 40
        line_h = 6

        pdf.set_draw_color(*COULEUR_BORDURE)
        pdf.set_line_width(0.3)

        # Total HT
        pdf.set_x(recap_x)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*COULEUR_TEXTE)
        pdf.cell(w=recap_w_label, h=line_h, text="Total HT", border="TB", new_x="RIGHT")
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(w=recap_w_value, h=line_h, text=_format_montant_eur(devis.montant_total_ht),
                 align="R", border="TB", new_x="LMARGIN", new_y="NEXT")

        # Ventilation TVA
        for vtva in devis.ventilation_tva:
            pdf.set_x(recap_x)
            pdf.set_font("Helvetica", "", 9)
            taux_label = _format_pourcentage(vtva.taux)
            pdf.cell(w=recap_w_label, h=line_h,
                     text=f"TVA {taux_label} (base {_format_montant_eur(vtva.base_ht)})",
                     border="B", new_x="RIGHT")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(w=recap_w_value, h=line_h,
                     text=_format_montant_eur(vtva.montant_tva),
                     align="R", border="B", new_x="LMARGIN", new_y="NEXT")

        # Total TTC
        pdf.set_x(recap_x)
        pdf.set_fill_color(*COULEUR_PRIMAIRE)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(w=recap_w_label, h=line_h + 1, text="Total TTC",
                 border=1, fill=True, new_x="RIGHT")
        pdf.cell(w=recap_w_value, h=line_h + 1,
                 text=_format_montant_eur(devis.montant_total_ttc),
                 align="R", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_text_color(*COULEUR_TEXTE)

        # Retenue de garantie (si > 0%)
        retenue_pct = Decimal(str(devis.retenue_garantie_pct or 0))
        if retenue_pct > 0:
            pdf.set_x(recap_x)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(w=recap_w_label, h=line_h,
                     text=f"Retenue de garantie ({_format_pourcentage(devis.retenue_garantie_pct)})",
                     border="B", new_x="RIGHT")
            pdf.cell(w=recap_w_value, h=line_h,
                     text=f"- {_format_montant_eur(devis.montant_retenue_garantie)}",
                     align="R", border="B", new_x="LMARGIN", new_y="NEXT")

            # Net a payer
            pdf.set_x(recap_x)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(*COULEUR_ENTETE_LOT)
            pdf.cell(w=recap_w_label, h=line_h + 1, text="Net a payer",
                     border=1, fill=True, new_x="RIGHT")
            pdf.cell(w=recap_w_value, h=line_h + 1,
                     text=_format_montant_eur(devis.montant_net_a_payer),
                     align="R", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(8)

    def _draw_conditions(self, pdf: FPDF, devis: DevisDetailDTO) -> None:
        """Dessine les conditions de paiement et informations complementaires."""
        # Verifier saut de page
        if pdf.get_y() > 240:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=LARGEUR_UTILE, h=7, text="CONDITIONS", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*COULEUR_TEXTE)

        # Conditions de paiement
        echeance_label = ECHEANCES_LABELS.get(devis.echeance, devis.echeance)
        pdf.cell(w=45, h=5, text="Conditions de paiement :", new_x="RIGHT")
        pdf.cell(w=LARGEUR_UTILE - 45, h=5, text=echeance_label, new_x="LMARGIN", new_y="NEXT")

        # Acompte
        acompte_pct = Decimal(str(devis.acompte_pct or 0))
        if acompte_pct > 0:
            pdf.cell(w=45, h=5, text="Acompte a la commande :", new_x="RIGHT")
            pdf.cell(w=LARGEUR_UTILE - 45, h=5,
                     text=f"{_format_pourcentage(devis.acompte_pct)} du montant TTC",
                     new_x="LMARGIN", new_y="NEXT")

        # Moyens de paiement
        if devis.moyens_paiement:
            moyens = ", ".join(m.replace("_", " ").capitalize() for m in devis.moyens_paiement)
            pdf.cell(w=45, h=5, text="Moyens de paiement :", new_x="RIGHT")
            pdf.cell(w=LARGEUR_UTILE - 45, h=5, text=moyens, new_x="LMARGIN", new_y="NEXT")

        # Duree estimee
        if devis.duree_estimee_jours:
            pdf.cell(w=45, h=5, text="Duree estimee :", new_x="RIGHT")
            pdf.cell(w=LARGEUR_UTILE - 45, h=5,
                     text=f"{devis.duree_estimee_jours} jours",
                     new_x="LMARGIN", new_y="NEXT")

        # Date debut travaux
        if devis.date_debut_travaux:
            pdf.cell(w=45, h=5, text="Debut des travaux :", new_x="RIGHT")
            pdf.cell(w=LARGEUR_UTILE - 45, h=5,
                     text=_format_date_fr(devis.date_debut_travaux),
                     new_x="LMARGIN", new_y="NEXT")

        # Notes de bas de page
        if devis.notes_bas_page:
            pdf.ln(3)
            pdf.set_font("Helvetica", "I", 8)
            pdf.multi_cell(w=LARGEUR_UTILE, h=4.5, text=devis.notes_bas_page)

        # Conditions generales
        if devis.conditions_generales:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(w=LARGEUR_UTILE, h=5, text="Conditions generales :", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 8)
            pdf.multi_cell(w=LARGEUR_UTILE, h=4, text=devis.conditions_generales)

        pdf.ln(5)

    def _draw_mention_tva_reduite(self, pdf: FPDF, mention: str) -> None:
        """Dessine la mention legale TVA reduite.

        Obligation legale pour les taux de TVA < 20% (reforme 01/2025).
        """
        # Verifier saut de page
        if pdf.get_y() > 245:
            pdf.add_page()

        pdf.set_draw_color(*COULEUR_BORDURE)
        pdf.set_fill_color(255, 250, 240)  # Fond jaune pale
        pdf.set_line_width(0.3)

        y_start = pdf.get_y()
        pdf.set_x(MARGE_GAUCHE)

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=LARGEUR_UTILE, h=5, text="MENTION LEGALE - TVA A TAUX REDUIT",
                 new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*COULEUR_TEXTE)
        pdf.multi_cell(w=LARGEUR_UTILE, h=3.5, text=mention)

        y_end = pdf.get_y()
        pdf.rect(MARGE_GAUCHE - 1, y_start - 1, LARGEUR_UTILE + 2, y_end - y_start + 3, style="D")

        pdf.ln(5)

    def _draw_signature_block(self, pdf: FPDF, devis: DevisDetailDTO) -> None:
        """Dessine le bloc de signature client."""
        # Verifier si besoin de nouvelle page pour la signature
        needed_height = 50
        if pdf.get_y() + needed_height > 280:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*COULEUR_PRIMAIRE)
        pdf.cell(w=LARGEUR_UTILE, h=7, text="ACCEPTATION DU DEVIS", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Cadre signature
        sig_x = MARGE_GAUCHE + LARGEUR_UTILE / 2
        sig_w = LARGEUR_UTILE / 2

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*COULEUR_TEXTE)

        pdf.set_x(sig_x)
        pdf.cell(w=sig_w, h=5, text=f"Date : ....../....../...........", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(sig_x)
        pdf.cell(w=sig_w, h=5, text="Lieu : ...................................", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)
        pdf.set_x(sig_x)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(w=sig_w, h=5, text='"Lu et approuve, bon pour accord"', new_x="LMARGIN", new_y="NEXT")

        pdf.ln(2)
        pdf.set_x(sig_x)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(w=sig_w, h=5, text="Signature du client :", new_x="LMARGIN", new_y="NEXT")

        # Zone de signature vide (cadre)
        pdf.set_draw_color(*COULEUR_BORDURE)
        pdf.set_line_width(0.3)
        pdf.rect(sig_x, pdf.get_y() + 1, sig_w, 25)
        pdf.ln(28)

    def _draw_footer(self, pdf: FPDF) -> None:
        """Dessine le pied de page sur toutes les pages."""
        total_pages = pdf.pages_count
        for page_num in range(1, total_pages + 1):
            pdf.page = page_num

            pdf.set_y(-20)
            pdf.set_draw_color(*COULEUR_BORDURE)
            pdf.set_line_width(0.2)
            pdf.line(MARGE_GAUCHE, pdf.get_y(), 210 - MARGE_DROITE, pdf.get_y())

            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(130, 130, 130)

            footer_text = f"{ENTREPRISE_NOM} - {ENTREPRISE_SIRET} - {ENTREPRISE_RCS}"
            pdf.cell(w=LARGEUR_UTILE / 2, h=4, text=footer_text, new_x="RIGHT")
            pdf.cell(w=LARGEUR_UTILE / 2, h=4,
                     text=f"Page {page_num}/{total_pages}",
                     align="R", new_x="LMARGIN", new_y="NEXT")
