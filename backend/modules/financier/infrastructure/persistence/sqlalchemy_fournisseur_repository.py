"""Implementation SQLAlchemy du repository Fournisseur.

FIN-14: Repertoire fournisseurs - CRUD des fournisseurs.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import Fournisseur
from ...domain.repositories import FournisseurRepository
from ...domain.value_objects import TypeFournisseur
from .models import FournisseurModel


class SQLAlchemyFournisseurRepository(FournisseurRepository):
    """Implementation SQLAlchemy du repository Fournisseur."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: FournisseurModel) -> Fournisseur:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite Fournisseur correspondante.
        """
        return Fournisseur(
            id=model.id,
            raison_sociale=model.raison_sociale,
            type=TypeFournisseur(model.type),
            siret=model.siret,
            adresse=model.adresse,
            contact_principal=model.contact_principal,
            telephone=model.telephone,
            email=model.email,
            conditions_paiement=model.conditions_paiement,
            notes=model.notes,
            actif=model.actif,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _to_model(self, entity: Fournisseur) -> FournisseurModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite Fournisseur source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return FournisseurModel(
            id=entity.id,
            raison_sociale=entity.raison_sociale,
            type=entity.type.value,
            siret=entity.siret,
            adresse=entity.adresse,
            contact_principal=entity.contact_principal,
            telephone=entity.telephone,
            email=entity.email,
            conditions_paiement=entity.conditions_paiement,
            notes=entity.notes,
            actif=entity.actif,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )

    def save(self, fournisseur: Fournisseur) -> Fournisseur:
        """Persiste un fournisseur (creation ou mise a jour).

        Args:
            fournisseur: Le fournisseur a persister.

        Returns:
            Le fournisseur avec son ID attribue.
        """
        if fournisseur.id:
            # Mise a jour
            model = (
                self._session.query(FournisseurModel)
                .filter(FournisseurModel.id == fournisseur.id)
                .first()
            )
            if model:
                model.raison_sociale = fournisseur.raison_sociale
                model.type = fournisseur.type.value
                model.siret = fournisseur.siret
                model.adresse = fournisseur.adresse
                model.contact_principal = fournisseur.contact_principal
                model.telephone = fournisseur.telephone
                model.email = fournisseur.email
                model.conditions_paiement = fournisseur.conditions_paiement
                model.notes = fournisseur.notes
                model.actif = fournisseur.actif
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(fournisseur)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, fournisseur_id: int) -> Optional[Fournisseur]:
        """Recherche un fournisseur par son ID (exclut les supprimes).

        Args:
            fournisseur_id: L'ID du fournisseur.

        Returns:
            Le fournisseur ou None si non trouve.
        """
        model = (
            self._session.query(FournisseurModel)
            .filter(FournisseurModel.id == fournisseur_id)
            .filter(FournisseurModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_siret(self, siret: str) -> Optional[Fournisseur]:
        """Recherche un fournisseur par son SIRET (exclut les supprimes).

        Args:
            siret: Le numero SIRET (14 chiffres).

        Returns:
            Le fournisseur ou None si non trouve.
        """
        model = (
            self._session.query(FournisseurModel)
            .filter(FournisseurModel.siret == siret)
            .filter(FournisseurModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all(
        self,
        type: Optional[TypeFournisseur] = None,
        actif_seulement: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Fournisseur]:
        """Liste les fournisseurs avec filtres (exclut les supprimes).

        Args:
            type: Filtrer par type de fournisseur.
            actif_seulement: Ne retourner que les fournisseurs actifs.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des fournisseurs correspondants.
        """
        query = self._session.query(FournisseurModel)
        query = query.filter(FournisseurModel.deleted_at.is_(None))

        if type:
            query = query.filter(FournisseurModel.type == type.value)
        if actif_seulement:
            query = query.filter(FournisseurModel.actif.is_(True))

        query = query.order_by(FournisseurModel.raison_sociale)
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def count(
        self,
        type: Optional[TypeFournisseur] = None,
        actif_seulement: bool = True,
    ) -> int:
        """Compte le nombre de fournisseurs (exclut les supprimes).

        Args:
            type: Filtrer par type de fournisseur.
            actif_seulement: Ne compter que les fournisseurs actifs.

        Returns:
            Le nombre de fournisseurs.
        """
        query = self._session.query(FournisseurModel)
        query = query.filter(FournisseurModel.deleted_at.is_(None))

        if type:
            query = query.filter(FournisseurModel.type == type.value)
        if actif_seulement:
            query = query.filter(FournisseurModel.actif.is_(True))

        return query.count()

    def delete(self, fournisseur_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un fournisseur (soft delete - H10).

        Args:
            fournisseur_id: L'ID du fournisseur a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(FournisseurModel)
            .filter(FournisseurModel.id == fournisseur_id)
            .filter(FournisseurModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
