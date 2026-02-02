"""Implementation SQLAlchemy du repository Comparatif.

DEV-08: Variantes et revisions - Persistance des comparatifs.
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ...domain.entities.comparatif_devis import ComparatifDevis
from ...domain.entities.comparatif_ligne import ComparatifLigne
from ...domain.repositories.comparatif_repository import ComparatifRepository
from ...domain.value_objects.type_ecart import TypeEcart
from .models import ComparatifDevisModel, ComparatifLigneModel


class SQLAlchemyComparatifRepository(ComparatifRepository):
    """Implementation SQLAlchemy du repository Comparatif."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(
        self, model: ComparatifDevisModel, lignes: Optional[List[ComparatifLigneModel]] = None
    ) -> ComparatifDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.
            lignes: Les lignes du comparatif (optionnel).

        Returns:
            L'entite ComparatifDevis correspondante.
        """
        lignes_entities = []
        if lignes:
            for l in lignes:
                lignes_entities.append(
                    ComparatifLigne(
                        id=l.id,
                        comparatif_id=l.comparatif_id,
                        type_ecart=TypeEcart(l.type_ecart),
                        lot_titre=l.lot_titre,
                        designation=l.designation,
                        article_id=l.article_id,
                        source_quantite=Decimal(str(l.source_quantite)) if l.source_quantite is not None else None,
                        source_prix_unitaire=Decimal(str(l.source_prix_unitaire)) if l.source_prix_unitaire is not None else None,
                        source_montant_ht=Decimal(str(l.source_montant_ht)) if l.source_montant_ht is not None else None,
                        source_debourse_sec=Decimal(str(l.source_debourse_sec)) if l.source_debourse_sec is not None else None,
                        cible_quantite=Decimal(str(l.cible_quantite)) if l.cible_quantite is not None else None,
                        cible_prix_unitaire=Decimal(str(l.cible_prix_unitaire)) if l.cible_prix_unitaire is not None else None,
                        cible_montant_ht=Decimal(str(l.cible_montant_ht)) if l.cible_montant_ht is not None else None,
                        cible_debourse_sec=Decimal(str(l.cible_debourse_sec)) if l.cible_debourse_sec is not None else None,
                        ecart_quantite=Decimal(str(l.ecart_quantite)) if l.ecart_quantite is not None else None,
                        ecart_prix_unitaire=Decimal(str(l.ecart_prix_unitaire)) if l.ecart_prix_unitaire is not None else None,
                        ecart_montant_ht=Decimal(str(l.ecart_montant_ht)) if l.ecart_montant_ht is not None else None,
                        ecart_debourse_sec=Decimal(str(l.ecart_debourse_sec)) if l.ecart_debourse_sec is not None else None,
                    )
                )

        return ComparatifDevis(
            id=model.id,
            devis_source_id=model.devis_source_id,
            devis_cible_id=model.devis_cible_id,
            ecart_montant_ht=Decimal(str(model.ecart_montant_ht)),
            ecart_montant_ttc=Decimal(str(model.ecart_montant_ttc)),
            ecart_marge_pct=Decimal(str(model.ecart_marge_pct)),
            ecart_debourse_total=Decimal(str(model.ecart_debourse_total)),
            nb_lignes_ajoutees=model.nb_lignes_ajoutees,
            nb_lignes_supprimees=model.nb_lignes_supprimees,
            nb_lignes_modifiees=model.nb_lignes_modifiees,
            nb_lignes_identiques=model.nb_lignes_identiques,
            lignes=lignes_entities,
            genere_par=model.genere_par,
            created_at=model.created_at,
        )

    def save(self, comparatif: ComparatifDevis) -> ComparatifDevis:
        """Persiste un comparatif avec ses lignes.

        Si un comparatif existe deja pour la meme paire (source, cible),
        il est remplace (suppression + recreation).

        Args:
            comparatif: Le comparatif a persister.

        Returns:
            Le comparatif avec son ID attribue.
        """
        # Supprimer l'ancien comparatif s'il existe
        existing = (
            self._session.query(ComparatifDevisModel)
            .filter(
                ComparatifDevisModel.devis_source_id == comparatif.devis_source_id,
                ComparatifDevisModel.devis_cible_id == comparatif.devis_cible_id,
            )
            .first()
        )
        if existing:
            # Supprimer les lignes associees (cascade devrait le faire, mais explicite)
            self._session.query(ComparatifLigneModel).filter(
                ComparatifLigneModel.comparatif_id == existing.id
            ).delete()
            self._session.delete(existing)
            self._session.flush()

        # Creer le nouveau comparatif
        model = ComparatifDevisModel(
            devis_source_id=comparatif.devis_source_id,
            devis_cible_id=comparatif.devis_cible_id,
            ecart_montant_ht=comparatif.ecart_montant_ht,
            ecart_montant_ttc=comparatif.ecart_montant_ttc,
            ecart_marge_pct=comparatif.ecart_marge_pct,
            ecart_debourse_total=comparatif.ecart_debourse_total,
            nb_lignes_ajoutees=comparatif.nb_lignes_ajoutees,
            nb_lignes_supprimees=comparatif.nb_lignes_supprimees,
            nb_lignes_modifiees=comparatif.nb_lignes_modifiees,
            nb_lignes_identiques=comparatif.nb_lignes_identiques,
            genere_par=comparatif.genere_par,
            created_at=comparatif.created_at,
        )
        self._session.add(model)
        self._session.flush()

        # Persister les lignes
        ligne_models = []
        for ligne in comparatif.lignes:
            ligne_model = ComparatifLigneModel(
                comparatif_id=model.id,
                type_ecart=ligne.type_ecart.value,
                lot_titre=ligne.lot_titre,
                designation=ligne.designation,
                article_id=ligne.article_id,
                source_quantite=ligne.source_quantite,
                source_prix_unitaire=ligne.source_prix_unitaire,
                source_montant_ht=ligne.source_montant_ht,
                source_debourse_sec=ligne.source_debourse_sec,
                cible_quantite=ligne.cible_quantite,
                cible_prix_unitaire=ligne.cible_prix_unitaire,
                cible_montant_ht=ligne.cible_montant_ht,
                cible_debourse_sec=ligne.cible_debourse_sec,
                ecart_quantite=ligne.ecart_quantite,
                ecart_prix_unitaire=ligne.ecart_prix_unitaire,
                ecart_montant_ht=ligne.ecart_montant_ht,
                ecart_debourse_sec=ligne.ecart_debourse_sec,
            )
            self._session.add(ligne_model)
            ligne_models.append(ligne_model)

        self._session.flush()

        # Recharger les lignes pour obtenir les IDs
        lignes_db = (
            self._session.query(ComparatifLigneModel)
            .filter(ComparatifLigneModel.comparatif_id == model.id)
            .all()
        )

        return self._to_entity(model, lignes_db)

    def find_by_id(self, comparatif_id: int) -> Optional[ComparatifDevis]:
        """Recherche un comparatif par son ID avec ses lignes.

        Args:
            comparatif_id: L'ID du comparatif.

        Returns:
            Le comparatif avec ses lignes ou None si non trouve.
        """
        model = (
            self._session.query(ComparatifDevisModel)
            .filter(ComparatifDevisModel.id == comparatif_id)
            .first()
        )
        if not model:
            return None

        lignes = (
            self._session.query(ComparatifLigneModel)
            .filter(ComparatifLigneModel.comparatif_id == comparatif_id)
            .all()
        )

        return self._to_entity(model, lignes)

    def find_by_devis(self, devis_id: int) -> List[ComparatifDevis]:
        """Liste les comparatifs impliquant un devis (sans les lignes).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des comparatifs (sans les lignes pour performance).
        """
        models = (
            self._session.query(ComparatifDevisModel)
            .filter(
                or_(
                    ComparatifDevisModel.devis_source_id == devis_id,
                    ComparatifDevisModel.devis_cible_id == devis_id,
                )
            )
            .order_by(ComparatifDevisModel.created_at.desc())
            .all()
        )

        return [self._to_entity(model) for model in models]

    def find_by_pair(
        self, devis_source_id: int, devis_cible_id: int
    ) -> Optional[ComparatifDevis]:
        """Recherche un comparatif existant entre deux devis.

        Args:
            devis_source_id: L'ID du devis source.
            devis_cible_id: L'ID du devis cible.

        Returns:
            Le comparatif avec ses lignes ou None si non trouve.
        """
        model = (
            self._session.query(ComparatifDevisModel)
            .filter(
                ComparatifDevisModel.devis_source_id == devis_source_id,
                ComparatifDevisModel.devis_cible_id == devis_cible_id,
            )
            .first()
        )
        if not model:
            return None

        lignes = (
            self._session.query(ComparatifLigneModel)
            .filter(ComparatifLigneModel.comparatif_id == model.id)
            .all()
        )

        return self._to_entity(model, lignes)
