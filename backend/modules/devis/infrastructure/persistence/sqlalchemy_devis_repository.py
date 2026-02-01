"""Implementation SQLAlchemy du repository Devis.

DEV-03: Creation devis structure - CRUD des devis.
DEV-15: Suivi statut devis - Filtrage par statut.
DEV-17: Dashboard devis - Agregations pour KPI.
DEV-19: Recherche et filtres - Filtres avances.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import extract, func, or_
from sqlalchemy.orm import Session

from ...domain.entities import Devis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.value_objects import StatutDevis
from .models import DevisModel


class SQLAlchemyDevisRepository(DevisRepository):
    """Implementation SQLAlchemy du repository Devis."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: DevisModel) -> Devis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite Devis correspondante.
        """
        return Devis(
            id=model.id,
            numero=model.numero,
            client_nom=model.client_nom,
            client_adresse=model.client_adresse,
            client_telephone=model.client_telephone,
            client_email=model.client_email,
            chantier_ref=str(model.chantier_id) if model.chantier_id is not None else None,
            objet=model.objet,
            date_creation=None,
            date_validite=model.date_validite,
            statut=StatutDevis(model.statut),
            montant_total_ht=Decimal(str(model.total_ht)),
            montant_total_ttc=Decimal(str(model.total_ttc)),
            taux_marge_global=Decimal(str(model.marge_globale_pct)),
            coefficient_frais_generaux=Decimal(str(model.coeff_frais_generaux)),
            taux_tva_defaut=Decimal(str(model.taux_tva_defaut)),
            retenue_garantie_pct=Decimal(str(model.retenue_garantie_pct)),
            taux_marge_moe=(
                Decimal(str(model.marge_moe_pct))
                if model.marge_moe_pct is not None
                else None
            ),
            taux_marge_materiaux=(
                Decimal(str(model.marge_materiaux_pct))
                if model.marge_materiaux_pct is not None
                else None
            ),
            taux_marge_sous_traitance=(
                Decimal(str(model.marge_sous_traitance_pct))
                if model.marge_sous_traitance_pct is not None
                else None
            ),
            taux_marge_materiel=None,
            taux_marge_deplacement=None,
            notes=model.notes,
            conditions_generales=None,
            commercial_id=model.commercial_id,
            conducteur_id=None,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _update_model(self, model: DevisModel, devis: Devis) -> None:
        """Met a jour les champs du modele depuis l'entite.

        Args:
            model: Le modele SQLAlchemy a mettre a jour.
            devis: L'entite Devis source.
        """
        model.numero = devis.numero
        model.client_nom = devis.client_nom
        model.client_adresse = devis.client_adresse
        model.client_telephone = devis.client_telephone
        model.client_email = devis.client_email
        model.chantier_id = (
            int(devis.chantier_ref)
            if devis.chantier_ref is not None
            else None
        )
        model.objet = devis.objet
        model.date_validite = devis.date_validite
        model.statut = devis.statut.value
        model.total_ht = devis.montant_total_ht
        model.total_ttc = devis.montant_total_ttc
        model.marge_globale_pct = devis.taux_marge_global
        model.marge_moe_pct = devis.taux_marge_moe
        model.marge_materiaux_pct = devis.taux_marge_materiaux
        model.marge_sous_traitance_pct = devis.taux_marge_sous_traitance
        model.coeff_frais_generaux = devis.coefficient_frais_generaux
        model.taux_tva_defaut = devis.taux_tva_defaut
        model.retenue_garantie_pct = devis.retenue_garantie_pct
        model.notes = devis.notes
        model.commercial_id = devis.commercial_id
        model.updated_at = datetime.utcnow()

    def generate_numero(self) -> str:
        """Genere un numero unique pour un nouveau devis.

        Format: DEV-YYYY-NNN (ex: DEV-2026-001).

        Returns:
            Le numero genere.
        """
        current_year = datetime.utcnow().year
        count = (
            self._session.query(func.count(DevisModel.id))
            .filter(extract("year", DevisModel.created_at) == current_year)
            .scalar()
        ) or 0
        next_number = count + 1
        return f"DEV-{current_year}-{next_number:03d}"

    def save(self, devis: Devis) -> Devis:
        """Persiste un devis (creation ou mise a jour).

        Args:
            devis: Le devis a persister.

        Returns:
            Le devis avec son ID attribue.
        """
        if devis.id:
            model = (
                self._session.query(DevisModel)
                .filter(DevisModel.id == devis.id)
                .first()
            )
            if model:
                self._update_model(model, devis)
        else:
            model = DevisModel(
                numero=devis.numero,
                client_nom=devis.client_nom,
                client_adresse=devis.client_adresse,
                client_telephone=devis.client_telephone,
                client_email=devis.client_email,
                chantier_id=(
                    int(devis.chantier_ref)
                    if devis.chantier_ref is not None
                    else None
                ),
                objet=devis.objet,
                date_validite=devis.date_validite,
                statut=devis.statut.value,
                total_ht=devis.montant_total_ht,
                total_ttc=devis.montant_total_ttc,
                debourse_sec_total=Decimal("0"),
                marge_globale_pct=devis.taux_marge_global,
                marge_moe_pct=devis.taux_marge_moe,
                marge_materiaux_pct=devis.taux_marge_materiaux,
                marge_sous_traitance_pct=devis.taux_marge_sous_traitance,
                coeff_frais_generaux=devis.coefficient_frais_generaux,
                taux_tva_defaut=devis.taux_tva_defaut,
                retenue_garantie_pct=devis.retenue_garantie_pct,
                notes=devis.notes,
                commercial_id=devis.commercial_id,
                created_at=devis.created_at or datetime.utcnow(),
                created_by=devis.created_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, devis_id: int) -> Optional[Devis]:
        """Recherche un devis par son ID (exclut les supprimes).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le devis ou None si non trouve.
        """
        model = (
            self._session.query(DevisModel)
            .filter(DevisModel.id == devis_id)
            .filter(DevisModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_numero(self, numero: str) -> Optional[Devis]:
        """Recherche un devis par son numero (exclut les supprimes).

        Args:
            numero: Le numero du devis.

        Returns:
            Le devis ou None si non trouve.
        """
        model = (
            self._session.query(DevisModel)
            .filter(DevisModel.numero == numero)
            .filter(DevisModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all(
        self,
        statut: Optional[StatutDevis] = None,
        statuts: Optional[List[StatutDevis]] = None,
        commercial_id: Optional[int] = None,
        conducteur_id: Optional[int] = None,
        client_nom: Optional[str] = None,
        date_creation_min: Optional[date] = None,
        date_creation_max: Optional[date] = None,
        montant_min: Optional[Decimal] = None,
        montant_max: Optional[Decimal] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Devis]:
        """Liste les devis avec filtres avances (DEV-19).

        Args:
            statut: Filtrer par statut unique (optionnel).
            statuts: Filtrer par liste de statuts (optionnel).
            commercial_id: Filtrer par commercial assigne (optionnel).
            conducteur_id: Filtrer par conducteur assigne (optionnel).
            client_nom: Filtrer par nom client (recherche partielle).
            date_creation_min: Date de creation minimale.
            date_creation_max: Date de creation maximale.
            montant_min: Montant HT minimum.
            montant_max: Montant HT maximum.
            search: Recherche textuelle sur numero/client/objet.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des devis.
        """
        query = self._session.query(DevisModel).filter(
            DevisModel.deleted_at.is_(None)
        )

        if statut is not None:
            query = query.filter(DevisModel.statut == statut.value)

        if statuts:
            statut_values = [s.value for s in statuts]
            query = query.filter(DevisModel.statut.in_(statut_values))

        if commercial_id is not None:
            query = query.filter(DevisModel.commercial_id == commercial_id)

        # conducteur_id is not in the model, so we skip filtering by it

        if client_nom is not None:
            query = query.filter(
                DevisModel.client_nom.ilike(f"%{client_nom}%")
            )

        if date_creation_min is not None:
            query = query.filter(DevisModel.created_at >= datetime.combine(
                date_creation_min, datetime.min.time()
            ))

        if date_creation_max is not None:
            query = query.filter(DevisModel.created_at <= datetime.combine(
                date_creation_max, datetime.max.time()
            ))

        if montant_min is not None:
            query = query.filter(DevisModel.total_ht >= montant_min)

        if montant_max is not None:
            query = query.filter(DevisModel.total_ht <= montant_max)

        if search is not None:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    DevisModel.numero.ilike(search_pattern),
                    DevisModel.client_nom.ilike(search_pattern),
                    DevisModel.objet.ilike(search_pattern),
                )
            )

        query = query.order_by(DevisModel.created_at.desc())
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def count(
        self,
        statut: Optional[StatutDevis] = None,
        statuts: Optional[List[StatutDevis]] = None,
        commercial_id: Optional[int] = None,
    ) -> int:
        """Compte le nombre de devis avec filtres.

        Args:
            statut: Filtrer par statut unique (optionnel).
            statuts: Filtrer par liste de statuts (optionnel).
            commercial_id: Filtrer par commercial assigne (optionnel).

        Returns:
            Le nombre de devis.
        """
        query = self._session.query(DevisModel).filter(
            DevisModel.deleted_at.is_(None)
        )

        if statut is not None:
            query = query.filter(DevisModel.statut == statut.value)

        if statuts:
            statut_values = [s.value for s in statuts]
            query = query.filter(DevisModel.statut.in_(statut_values))

        if commercial_id is not None:
            query = query.filter(DevisModel.commercial_id == commercial_id)

        return query.count()

    def count_by_statut(self) -> Dict[str, int]:
        """Compte les devis par statut (DEV-17: KPI pipeline).

        Returns:
            Dictionnaire {statut: count}.
        """
        results = (
            self._session.query(
                DevisModel.statut,
                func.count(DevisModel.id),
            )
            .filter(DevisModel.deleted_at.is_(None))
            .group_by(DevisModel.statut)
            .all()
        )
        return {statut: count for statut, count in results}

    def somme_montant_by_statut(self) -> Dict[str, Decimal]:
        """Somme des montants HT par statut (DEV-17: KPI pipeline).

        Returns:
            Dictionnaire {statut: somme_montant_ht}.
        """
        results = (
            self._session.query(
                DevisModel.statut,
                func.coalesce(func.sum(DevisModel.total_ht), 0),
            )
            .filter(DevisModel.deleted_at.is_(None))
            .group_by(DevisModel.statut)
            .all()
        )
        return {statut: Decimal(str(total)) for statut, total in results}

    def find_expires(self) -> List[Devis]:
        """Trouve les devis dont la date de validite est depassee
        et qui sont dans un statut pouvant expirer.

        Returns:
            Liste des devis a marquer comme expires.
        """
        today = date.today()
        expirable_statuts = [
            StatutDevis.ENVOYE.value,
            StatutDevis.VU.value,
        ]
        query = (
            self._session.query(DevisModel)
            .filter(DevisModel.deleted_at.is_(None))
            .filter(DevisModel.date_validite < today)
            .filter(DevisModel.date_validite.isnot(None))
            .filter(DevisModel.statut.in_(expirable_statuts))
        )
        return [self._to_entity(model) for model in query.all()]

    def delete(self, devis_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un devis (soft delete - H10).

        Args:
            devis_id: L'ID du devis a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(DevisModel)
            .filter(DevisModel.id == devis_id)
            .filter(DevisModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
