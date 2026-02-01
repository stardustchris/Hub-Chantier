"""Implementation SQLAlchemy du repository ExportComptable.

FIN-13: Export comptable CSV/Excel - requetes cross-tables pour
generer les ecritures comptables a partir des achats et factures.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from ...domain.repositories.export_comptable_repository import ExportComptableRepository


class SQLAlchemyExportComptableRepository(ExportComptableRepository):
    """Implementation SQLAlchemy du repository ExportComptable.

    Utilise des requetes SQL brutes (text()) pour interroger les tables
    achats et factures_client.
    """

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def get_achats_periode(
        self,
        chantier_id: Optional[int],
        date_debut: date,
        date_fin: date,
    ) -> List[dict]:
        """Recupere les achats factures sur une periode.

        Seuls les achats au statut 'facture' sont inclus dans l'export.

        Args:
            chantier_id: ID du chantier (optionnel, None = tous).
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.

        Returns:
            Liste de dictionnaires avec les donnees des achats.
        """
        query_str = """
            SELECT
                a.id,
                a.chantier_id,
                a.type_achat,
                a.libelle,
                a.quantite,
                a.prix_unitaire_ht,
                (a.quantite * a.prix_unitaire_ht) as montant_ht,
                a.taux_tva,
                a.date_commande,
                a.numero_facture,
                a.created_at as date_facture,
                f.raison_sociale as fournisseur_nom
            FROM achats a
            LEFT JOIN fournisseurs f ON a.fournisseur_id = f.id
            WHERE a.statut = 'facture'
              AND a.deleted_at IS NULL
              AND a.date_commande >= :date_debut
              AND a.date_commande <= :date_fin
        """
        params = {
            "date_debut": date_debut,
            "date_fin": date_fin,
        }

        if chantier_id is not None:
            query_str += " AND a.chantier_id = :chantier_id"
            params["chantier_id"] = chantier_id

        query_str += " ORDER BY a.date_commande, a.id"

        rows = self._session.execute(text(query_str), params).fetchall()

        return [
            {
                "id": row.id,
                "chantier_id": row.chantier_id,
                "type_achat": row.type_achat,
                "libelle": row.libelle,
                "quantite": row.quantite,
                "prix_unitaire_ht": row.prix_unitaire_ht,
                "montant_ht": row.montant_ht,
                "taux_tva": row.taux_tva,
                "date_commande": row.date_commande,
                "date_facture": row.date_facture,
                "numero_facture": row.numero_facture or f"ACH-{row.id}",
                "fournisseur_nom": row.fournisseur_nom,
            }
            for row in rows
        ]

    def get_factures_periode(
        self,
        chantier_id: Optional[int],
        date_debut: date,
        date_fin: date,
    ) -> List[dict]:
        """Recupere les factures client emises sur une periode.

        Seules les factures au statut 'emise', 'envoyee' ou 'payee' sont incluses.

        Args:
            chantier_id: ID du chantier (optionnel, None = tous).
            date_debut: Date de debut de la periode.
            date_fin: Date de fin de la periode.

        Returns:
            Liste de dictionnaires avec les donnees des factures.
        """
        query_str = """
            SELECT
                fc.id,
                fc.chantier_id,
                fc.numero_facture,
                fc.type_facture,
                fc.montant_ht,
                fc.taux_tva,
                fc.montant_tva,
                fc.montant_ttc,
                fc.date_emission,
                fc.statut
            FROM factures_client fc
            WHERE fc.statut IN ('emise', 'envoyee', 'payee')
              AND fc.deleted_at IS NULL
              AND fc.date_emission >= :date_debut
              AND fc.date_emission <= :date_fin
        """
        params = {
            "date_debut": date_debut,
            "date_fin": date_fin,
        }

        if chantier_id is not None:
            query_str += " AND fc.chantier_id = :chantier_id"
            params["chantier_id"] = chantier_id

        query_str += " ORDER BY fc.date_emission, fc.id"

        rows = self._session.execute(text(query_str), params).fetchall()

        return [
            {
                "id": row.id,
                "chantier_id": row.chantier_id,
                "numero_facture": row.numero_facture,
                "type_facture": row.type_facture,
                "montant_ht": row.montant_ht,
                "taux_tva": row.taux_tva,
                "montant_tva": row.montant_tva,
                "montant_ttc": row.montant_ttc,
                "date_emission": row.date_emission,
                "statut": row.statut,
            }
            for row in rows
        ]
