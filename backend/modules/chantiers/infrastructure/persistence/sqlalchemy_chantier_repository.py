"""Implémentation SQLAlchemy du ChantierRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_

from shared.domain.value_objects import Couleur

from ...domain.entities import Chantier
from ...domain.repositories import ChantierRepository
from ...domain.value_objects import (
    CodeChantier,
    StatutChantier,
    CoordonneesGPS,
    ContactChantier,
    StatutChantierEnum,
)
from .chantier_model import ChantierModel
from .contact_chantier_model import ContactChantierModel


class SQLAlchemyChantierRepository(ChantierRepository):
    """
    Implémentation du ChantierRepository utilisant SQLAlchemy.

    Fait le mapping entre l'entité Chantier (Domain) et ChantierModel (Infrastructure).

    Attributes:
        session: Session SQLAlchemy pour les opérations DB.
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy active.
        """
        self.session = session

    def find_by_id(self, chantier_id: int) -> Optional[Chantier]:
        """
        Trouve un chantier par son ID.

        Args:
            chantier_id: L'identifiant unique.

        Returns:
            L'entité Chantier ou None.
        """
        model = (
            self.session.query(ChantierModel)
            .filter(ChantierModel.id == chantier_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_code(self, code: CodeChantier) -> Optional[Chantier]:
        """
        Trouve un chantier par son code unique.

        Args:
            code: Le code du chantier.

        Returns:
            L'entité Chantier ou None.
        """
        model = (
            self.session.query(ChantierModel)
            .filter(ChantierModel.code == str(code))
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, chantier: Chantier) -> Chantier:
        """
        Persiste un chantier (création ou mise à jour).

        Args:
            chantier: L'entité Chantier à sauvegarder.

        Returns:
            L'entité Chantier avec ID (si création).
        """
        if chantier.id:
            # Update
            model = (
                self.session.query(ChantierModel)
                .filter(ChantierModel.id == chantier.id)
                .first()
            )
            if model:
                model.code = str(chantier.code)
                model.nom = chantier.nom
                model.adresse = chantier.adresse
                model.description = chantier.description
                model.statut = str(chantier.statut)
                model.couleur = (
                    str(chantier.couleur) if chantier.couleur else Couleur.DEFAULT
                )
                model.latitude = (
                    chantier.coordonnees_gps.latitude
                    if chantier.coordonnees_gps
                    else None
                )
                model.longitude = (
                    chantier.coordonnees_gps.longitude
                    if chantier.coordonnees_gps
                    else None
                )
                model.photo_couverture = chantier.photo_couverture
                model.contact_nom = (
                    chantier.contact.nom if chantier.contact else None
                )
                model.contact_telephone = (
                    chantier.contact.telephone if chantier.contact else None
                )
                model.heures_estimees = chantier.heures_estimees
                model.date_debut = chantier.date_debut
                model.date_fin = chantier.date_fin
                model.conducteur_ids = list(chantier.conducteur_ids)
                model.chef_chantier_ids = list(chantier.chef_chantier_ids)
                model.updated_at = chantier.updated_at
        else:
            # Create
            model = self._to_model(chantier)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, chantier_id: int) -> bool:
        """
        Supprime un chantier.

        Args:
            chantier_id: L'identifiant du chantier.

        Returns:
            True si supprimé, False si non trouvé.
        """
        model = (
            self.session.query(ChantierModel)
            .filter(ChantierModel.id == chantier_id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Chantier]:
        """
        Récupère tous les chantiers avec pagination.

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier.
        """
        models = (
            self.session.query(ChantierModel)
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count(self) -> int:
        """
        Compte le nombre total de chantiers.

        Returns:
            Nombre total de chantiers.
        """
        return self.session.query(ChantierModel).count()

    def find_by_statut(
        self, statut: StatutChantier, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers par statut.

        Args:
            statut: Le statut à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier avec ce statut.
        """
        models = (
            self.session.query(ChantierModel)
            .filter(ChantierModel.statut == str(statut))
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_active(self, skip: int = 0, limit: int = 100) -> List[Chantier]:
        """
        Trouve les chantiers actifs (non fermés).

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier actifs.
        """
        models = (
            self.session.query(ChantierModel)
            .filter(ChantierModel.statut != StatutChantierEnum.FERME.value)
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_conducteur(
        self, conducteur_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers d'un conducteur.

        Args:
            conducteur_id: ID du conducteur.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier du conducteur.
        """
        # Note: Pour PostgreSQL, on utiliserait l'opérateur JSON contains
        # Pour SQLite, on fait une recherche dans le JSON sérialisé
        models = self.session.query(ChantierModel).all()
        filtered = [
            m for m in models if conducteur_id in (m.conducteur_ids or [])
        ]
        return [self._to_entity(m) for m in filtered[skip : skip + limit]]

    def find_by_chef_chantier(
        self, chef_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers d'un chef de chantier.

        Args:
            chef_id: ID du chef de chantier.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier du chef.
        """
        models = self.session.query(ChantierModel).all()
        filtered = [
            m for m in models if chef_id in (m.chef_chantier_ids or [])
        ]
        return [self._to_entity(m) for m in filtered[skip : skip + limit]]

    def find_by_responsable(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers dont l'utilisateur est responsable.

        Args:
            user_id: ID de l'utilisateur.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier de l'utilisateur.
        """
        models = self.session.query(ChantierModel).all()
        filtered = [
            m
            for m in models
            if user_id in (m.conducteur_ids or [])
            or user_id in (m.chef_chantier_ids or [])
        ]
        return [self._to_entity(m) for m in filtered[skip : skip + limit]]

    def exists_by_code(self, code: CodeChantier) -> bool:
        """
        Vérifie si un code chantier est déjà utilisé.

        Args:
            code: Le code à vérifier.

        Returns:
            True si le code existe.
        """
        return (
            self.session.query(ChantierModel)
            .filter(ChantierModel.code == str(code))
            .first()
            is not None
        )

    def get_last_code(self) -> Optional[str]:
        """
        Récupère le dernier code chantier utilisé.

        Returns:
            Le dernier code ou None si aucun chantier.
        """
        model = (
            self.session.query(ChantierModel)
            .order_by(ChantierModel.code.desc())
            .first()
        )
        return model.code if model else None

    def search(
        self,
        query: str,
        statut: Optional[StatutChantier] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Chantier]:
        """
        Recherche des chantiers par nom ou code.

        Args:
            query: Terme de recherche.
            statut: Filtre optionnel par statut.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier correspondantes.
        """
        search_pattern = f"%{query}%"
        base_query = self.session.query(ChantierModel).filter(
            or_(
                ChantierModel.nom.ilike(search_pattern),
                ChantierModel.code.ilike(search_pattern),
                ChantierModel.adresse.ilike(search_pattern),
            )
        )

        if statut:
            base_query = base_query.filter(ChantierModel.statut == str(statut))

        models = (
            base_query.order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: ChantierModel) -> Chantier:
        """
        Convertit un modèle SQLAlchemy en entité Domain.

        Args:
            model: Le modèle SQLAlchemy.

        Returns:
            L'entité Chantier.
        """
        # Reconstruire les coordonnées GPS
        coordonnees_gps = None
        if model.latitude is not None and model.longitude is not None:
            coordonnees_gps = CoordonneesGPS(
                latitude=model.latitude,
                longitude=model.longitude,
            )

        # Reconstruire le contact
        contact = None
        if model.contact_nom and model.contact_telephone:
            contact = ContactChantier(
                nom=model.contact_nom,
                telephone=model.contact_telephone,
            )

        return Chantier(
            id=model.id,
            code=CodeChantier(model.code),
            nom=model.nom,
            adresse=model.adresse,
            description=model.description,
            statut=StatutChantier.from_string(model.statut),
            couleur=Couleur(model.couleur) if model.couleur else Couleur.default(),
            coordonnees_gps=coordonnees_gps,
            photo_couverture=model.photo_couverture,
            contact=contact,
            heures_estimees=model.heures_estimees,
            date_debut=model.date_debut,
            date_fin=model.date_fin,
            conducteur_ids=list(model.conducteur_ids or []),
            chef_chantier_ids=list(model.chef_chantier_ids or []),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, chantier: Chantier) -> ChantierModel:
        """
        Convertit une entité Domain en modèle SQLAlchemy.

        Args:
            chantier: L'entité Chantier.

        Returns:
            Le modèle ChantierModel.
        """
        return ChantierModel(
            id=chantier.id,
            code=str(chantier.code),
            nom=chantier.nom,
            adresse=chantier.adresse,
            description=chantier.description,
            statut=str(chantier.statut),
            couleur=str(chantier.couleur) if chantier.couleur else Couleur.DEFAULT,
            latitude=(
                chantier.coordonnees_gps.latitude
                if chantier.coordonnees_gps
                else None
            ),
            longitude=(
                chantier.coordonnees_gps.longitude
                if chantier.coordonnees_gps
                else None
            ),
            photo_couverture=chantier.photo_couverture,
            contact_nom=chantier.contact.nom if chantier.contact else None,
            contact_telephone=(
                chantier.contact.telephone if chantier.contact else None
            ),
            heures_estimees=chantier.heures_estimees,
            date_debut=chantier.date_debut,
            date_fin=chantier.date_fin,
            conducteur_ids=list(chantier.conducteur_ids),
            chef_chantier_ids=list(chantier.chef_chantier_ids),
            created_at=chantier.created_at,
            updated_at=chantier.updated_at,
        )
