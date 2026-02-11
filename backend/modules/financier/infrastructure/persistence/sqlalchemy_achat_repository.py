"""Implementation SQLAlchemy du repository Achat.

FIN-05: Saisie achat - CRUD et requetes sur les achats.
FIN-06: Suivi achat - Filtrage par statut et agregation.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from ...domain.entities import Achat
from ...domain.repositories import AchatRepository
from ...domain.value_objects import StatutAchat, TypeAchat, UniteMesure
from .models import AchatModel


class SQLAlchemyAchatRepository(AchatRepository):
    """Implementation SQLAlchemy du repository Achat."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: AchatModel) -> Achat:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite Achat correspondante.
        """
        return Achat(
            id=model.id,
            chantier_id=model.chantier_id,
            fournisseur_id=model.fournisseur_id,
            lot_budgetaire_id=model.lot_budgetaire_id,
            type_achat=TypeAchat(model.type_achat),
            libelle=model.libelle,
            quantite=Decimal(str(model.quantite)),
            unite=UniteMesure(model.unite) if model.unite else UniteMesure.U,
            prix_unitaire_ht=Decimal(str(model.prix_unitaire_ht)),
            taux_tva=Decimal(str(model.taux_tva)),
            date_commande=model.date_commande,
            date_livraison_prevue=model.date_livraison_prevue,
            statut=StatutAchat(model.statut),
            numero_facture=model.numero_facture,
            motif_refus=model.motif_refus,
            commentaire=model.commentaire,
            demandeur_id=model.demandeur_id,
            valideur_id=model.valideur_id,
            validated_at=model.validated_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
            # CONN-10: Champs Pennylane
            montant_ht_reel=Decimal(str(model.montant_ht_reel)) if model.montant_ht_reel is not None else None,
            date_facture_reelle=model.date_facture_reelle,
            pennylane_invoice_id=model.pennylane_invoice_id,
            source_donnee=model.source_donnee if model.source_donnee else "HUB",
        )

    def _to_model(self, entity: Achat) -> AchatModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite Achat source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return AchatModel(
            id=entity.id,
            chantier_id=entity.chantier_id,
            fournisseur_id=entity.fournisseur_id,
            lot_budgetaire_id=entity.lot_budgetaire_id,
            type_achat=entity.type_achat.value,
            libelle=entity.libelle,
            quantite=entity.quantite,
            unite=entity.unite.value,
            prix_unitaire_ht=entity.prix_unitaire_ht,
            taux_tva=entity.taux_tva,
            date_commande=entity.date_commande,
            date_livraison_prevue=entity.date_livraison_prevue,
            statut=entity.statut.value,
            numero_facture=entity.numero_facture,
            motif_refus=entity.motif_refus,
            commentaire=entity.commentaire,
            demandeur_id=entity.demandeur_id,
            valideur_id=entity.valideur_id,
            validated_at=entity.validated_at,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            # CONN-10: Champs Pennylane
            montant_ht_reel=entity.montant_ht_reel,
            date_facture_reelle=entity.date_facture_reelle,
            pennylane_invoice_id=entity.pennylane_invoice_id,
            source_donnee=entity.source_donnee,
        )

    def save(self, achat: Achat) -> Achat:
        """Persiste un achat (creation ou mise a jour).

        Args:
            achat: L'achat a persister.

        Returns:
            L'achat avec son ID attribue.
        """
        if achat.id:
            # Mise a jour
            model = (
                self._session.query(AchatModel)
                .filter(AchatModel.id == achat.id)
                .first()
            )
            if model:
                model.fournisseur_id = achat.fournisseur_id
                model.lot_budgetaire_id = achat.lot_budgetaire_id
                model.type_achat = achat.type_achat.value
                model.libelle = achat.libelle
                model.quantite = achat.quantite
                model.unite = achat.unite.value
                model.prix_unitaire_ht = achat.prix_unitaire_ht
                model.taux_tva = achat.taux_tva
                model.date_commande = achat.date_commande
                model.date_livraison_prevue = achat.date_livraison_prevue
                model.statut = achat.statut.value
                model.numero_facture = achat.numero_facture
                model.motif_refus = achat.motif_refus
                model.commentaire = achat.commentaire
                model.valideur_id = achat.valideur_id
                model.validated_at = achat.validated_at
                model.updated_at = datetime.utcnow()
                # CONN-10: Champs Pennylane
                model.montant_ht_reel = achat.montant_ht_reel
                model.date_facture_reelle = achat.date_facture_reelle
                model.pennylane_invoice_id = achat.pennylane_invoice_id
                model.source_donnee = achat.source_donnee
        else:
            # Creation
            model = self._to_model(achat)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, achat_id: int) -> Optional[Achat]:
        """Recherche un achat par son ID (exclut les supprimes).

        Args:
            achat_id: L'ID de l'achat.

        Returns:
            L'achat ou None si non trouve.
        """
        model = (
            self._session.query(AchatModel)
            .filter(AchatModel.id == achat_id)
            .filter(AchatModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_chantier(
        self,
        chantier_id: int,
        statut: Optional[StatutAchat] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats d'un chantier (exclut les supprimes).

        Args:
            chantier_id: L'ID du chantier (0 = tous les chantiers).
            statut: Filtrer par statut (optionnel).
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des achats.
        """
        query = self._session.query(AchatModel).filter(
            AchatModel.deleted_at.is_(None),
        )

        if chantier_id and chantier_id > 0:
            query = query.filter(AchatModel.chantier_id == chantier_id)

        if statut:
            query = query.filter(AchatModel.statut == statut.value)

        query = query.order_by(AchatModel.created_at.desc())
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def find_by_fournisseur(
        self,
        fournisseur_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats d'un fournisseur (exclut les supprimes).

        Args:
            fournisseur_id: L'ID du fournisseur.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des achats.
        """
        query = (
            self._session.query(AchatModel)
            .filter(
                AchatModel.fournisseur_id == fournisseur_id,
                AchatModel.deleted_at.is_(None),
            )
            .order_by(AchatModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return [self._to_entity(model) for model in query.all()]

    def find_by_lot(
        self,
        lot_budgetaire_id: int,
        statuts: Optional[List[StatutAchat]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats d'un lot budgetaire (exclut les supprimes).

        Args:
            lot_budgetaire_id: L'ID du lot budgetaire.
            statuts: Filtrer par statuts (optionnel).
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des achats.
        """
        query = self._session.query(AchatModel).filter(
            AchatModel.lot_budgetaire_id == lot_budgetaire_id,
            AchatModel.deleted_at.is_(None),
        )

        if statuts:
            query = query.filter(
                AchatModel.statut.in_([s.value for s in statuts])
            )

        query = query.order_by(AchatModel.created_at.desc())
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def find_en_attente_validation(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Achat]:
        """Liste les achats en attente de validation (statut = demande).

        Args:
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des achats en attente.
        """
        query = (
            self._session.query(AchatModel)
            .filter(
                AchatModel.statut == StatutAchat.DEMANDE.value,
                AchatModel.deleted_at.is_(None),
            )
            .order_by(AchatModel.created_at)
            .offset(offset)
            .limit(limit)
        )

        return [self._to_entity(model) for model in query.all()]

    def count_by_chantier(
        self,
        chantier_id: int,
        statuts: Optional[List[StatutAchat]] = None,
    ) -> int:
        """Compte les achats d'un chantier (exclut les supprimes).

        Args:
            chantier_id: L'ID du chantier (0 = tous les chantiers).
            statuts: Filtrer par statuts (optionnel).

        Returns:
            Le nombre d'achats.
        """
        query = self._session.query(AchatModel).filter(
            AchatModel.deleted_at.is_(None),
        )

        if chantier_id and chantier_id > 0:
            query = query.filter(AchatModel.chantier_id == chantier_id)

        if statuts:
            query = query.filter(
                AchatModel.statut.in_([s.value for s in statuts])
            )

        return query.count()

    def somme_by_lot(
        self,
        lot_budgetaire_id: int,
        statuts: Optional[List[StatutAchat]] = None,
    ) -> Decimal:
        """Calcule la somme HT des achats d'un lot budgetaire.

        Args:
            lot_budgetaire_id: L'ID du lot budgetaire.
            statuts: Filtrer par statuts (optionnel).

        Returns:
            La somme HT des achats.
        """
        query = self._session.query(
            func.sum(
                func.coalesce(
                    AchatModel.montant_ht_reel,
                    AchatModel.quantite * AchatModel.prix_unitaire_ht,
                )
            )
        ).filter(
            AchatModel.lot_budgetaire_id == lot_budgetaire_id,
            AchatModel.deleted_at.is_(None),
        )

        if statuts:
            query = query.filter(
                AchatModel.statut.in_([s.value for s in statuts])
            )

        result = query.scalar()
        return Decimal(str(result)) if result else Decimal("0")

    def somme_by_chantier(
        self,
        chantier_id: int,
        statuts: Optional[List[StatutAchat]] = None,
    ) -> Decimal:
        """Calcule la somme HT des achats d'un chantier.

        Args:
            chantier_id: L'ID du chantier.
            statuts: Filtrer par statuts (optionnel).

        Returns:
            La somme HT des achats.
        """
        query = self._session.query(
            func.sum(
                func.coalesce(
                    AchatModel.montant_ht_reel,
                    AchatModel.quantite * AchatModel.prix_unitaire_ht,
                )
            )
        ).filter(
            AchatModel.chantier_id == chantier_id,
            AchatModel.deleted_at.is_(None),
        )

        if statuts:
            query = query.filter(
                AchatModel.statut.in_([s.value for s in statuts])
            )

        result = query.scalar()
        return Decimal(str(result)) if result else Decimal("0")

    def delete(self, achat_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un achat (soft delete - H10).

        Args:
            achat_id: L'ID de l'achat a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(AchatModel)
            .filter(AchatModel.id == achat_id)
            .filter(AchatModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True

    def search_suggestions(
        self,
        search: str,
        limit: int = 10,
    ) -> List[dict]:
        """Recherche les libelles d'achats passes pour autocomplete.

        Retourne des suggestions uniques (libelle + dernier prix + fournisseur).

        Args:
            search: Terme de recherche (ILIKE).
            limit: Nombre max de suggestions.

        Returns:
            Liste de dicts avec libelle, prix_unitaire_ht, unite, type_achat, fournisseur_id.
        """
        from sqlalchemy import text

        query = text("""
            SELECT DISTINCT ON (LOWER(a.libelle))
                a.libelle,
                a.prix_unitaire_ht,
                a.unite,
                a.type_achat,
                a.fournisseur_id,
                f.raison_sociale as fournisseur_nom
            FROM achats a
            LEFT JOIN fournisseurs f ON a.fournisseur_id = f.id
            WHERE a.deleted_at IS NULL
              AND a.libelle ILIKE :search
            ORDER BY LOWER(a.libelle), a.created_at DESC
            LIMIT :limit
        """)
        rows = self._session.execute(
            query,
            {"search": f"%{search}%", "limit": limit},
        ).fetchall()
        return [
            {
                "libelle": row.libelle,
                "prix_unitaire_ht": str(row.prix_unitaire_ht),
                "unite": row.unite,
                "type_achat": row.type_achat,
                "fournisseur_id": row.fournisseur_id,
                "fournisseur_nom": row.fournisseur_nom,
            }
            for row in rows
        ]
