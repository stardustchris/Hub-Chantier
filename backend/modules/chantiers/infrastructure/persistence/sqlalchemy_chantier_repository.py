"""Implémentation SQLAlchemy du ChantierRepository."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from sqlalchemy.sql.elements import ColumnElement

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
from .chantier_responsable_model import ChantierConducteurModel, ChantierChefModel


class SQLAlchemyChantierRepository(ChantierRepository):
    """
    Implémentation du ChantierRepository utilisant SQLAlchemy.

    Fait le mapping entre l'entité Chantier (Domain) et ChantierModel (Infrastructure).
    Implémente le soft delete: les chantiers supprimés ont deleted_at != None.

    Attributes:
        session: Session SQLAlchemy pour les opérations DB.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy active.
        """
        self.session = session

    @property
    def _eager_options(self) -> tuple:
        """Options de chargement eager pour éviter N+1 queries.

        Note: Utilise joinedload au lieu de selectinload car les relations
        utilisent des listes Python (conducteur_ids, chef_chantier_ids)
        plutôt que des relations ORM.

        Gap: GAP-CHT-004 - Optimisation N+1 queries
        """
        # Les relations conducteurs/chefs sont stockées comme arrays d'IDs
        # donc pas de eager loading ORM nécessaire ici
        # L'optimisation viendra de la réduction des requêtes dans _to_entity()
        return ()

    def _not_deleted(self) -> ColumnElement[bool]:
        """Filtre pour exclure les enregistrements supprimés (soft delete)."""
        return ChantierModel.deleted_at.is_(None)

    def find_by_id(self, chantier_id: int) -> Optional[Chantier]:
        """
        Trouve un chantier par son ID (excluant les supprimés).

        Args:
            chantier_id: L'identifiant unique.

        Returns:
            L'entité Chantier ou None.
        """
        model = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .filter(ChantierModel.id == chantier_id)
            .filter(self._not_deleted())
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_code(self, code: CodeChantier) -> Optional[Chantier]:
        """
        Trouve un chantier par son code unique (excluant les supprimés).

        Args:
            code: Le code du chantier.

        Returns:
            L'entité Chantier ou None.
        """
        model = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .filter(ChantierModel.code == str(code))
            .filter(self._not_deleted())
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
                model.maitre_ouvrage = chantier.maitre_ouvrage
                model.type_travaux = chantier.type_travaux
                model.batiment_plus_2ans = chantier.batiment_plus_2ans
                model.usage_habitation = chantier.usage_habitation
                model.conducteur_ids = list(chantier.conducteur_ids)
                model.chef_chantier_ids = list(chantier.chef_chantier_ids)
                model.updated_at = chantier.updated_at
        else:
            # Create
            model = self._to_model(chantier)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)

        # Synchroniser les tables de jointure avec les champs JSON
        self.sync_responsables(
            model.id,
            list(chantier.conducteur_ids),
            list(chantier.chef_chantier_ids),
        )

        return self._to_entity(model)

    def delete(self, chantier_id: int) -> bool:
        """
        Supprime un chantier (soft delete - marque deleted_at).

        Le chantier n'est pas supprimé physiquement de la base de données,
        mais marqué comme supprimé. Cela permet de conserver l'historique
        et de respecter les exigences RGPD (droit à l'oubli avec traçabilité).

        Args:
            chantier_id: L'identifiant du chantier.

        Returns:
            True si supprimé, False si non trouvé ou déjà supprimé.
        """
        model = (
            self.session.query(ChantierModel)
            .filter(ChantierModel.id == chantier_id)
            .filter(self._not_deleted())
            .first()
        )
        if model:
            # Soft delete: marquer comme supprimé au lieu de supprimer physiquement
            model.deleted_at = datetime.now()
            self.session.commit()
            return True
        return False

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Chantier]:
        """
        Récupère tous les chantiers avec pagination (excluant les supprimés).

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier.
        """
        models = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .filter(self._not_deleted())
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count(self) -> int:
        """
        Compte le nombre total de chantiers (excluant les supprimés).

        Returns:
            Nombre total de chantiers.
        """
        return self.session.query(ChantierModel).filter(self._not_deleted()).count()

    def find_by_statut(
        self, statut: StatutChantier, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers par statut (excluant les supprimés).

        Args:
            statut: Le statut à filtrer.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier avec ce statut.
        """
        models = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .filter(ChantierModel.statut == str(statut))
            .filter(self._not_deleted())
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_active(self, skip: int = 0, limit: int = 100) -> List[Chantier]:
        """
        Trouve les chantiers actifs (non fermés, excluant les supprimés).

        Args:
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier actifs.
        """
        models = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .filter(ChantierModel.statut != StatutChantierEnum.FERME.value)
            .filter(self._not_deleted())
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
        Trouve les chantiers d'un conducteur (excluant les supprimes).

        Utilise une requete SQL avec JOIN sur la table de jointure
        pour des performances optimales (evite le N+1).

        Args:
            conducteur_id: ID du conducteur.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des entites Chantier du conducteur.
        """
        # Requete optimisee via table de jointure
        models = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .join(
                ChantierConducteurModel,
                ChantierModel.id == ChantierConducteurModel.chantier_id,
            )
            .filter(ChantierConducteurModel.user_id == conducteur_id)
            .filter(self._not_deleted())
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_chef_chantier(
        self, chef_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers d'un chef de chantier (excluant les supprimes).

        Utilise une requete SQL avec JOIN sur la table de jointure
        pour des performances optimales (evite le N+1).

        Args:
            chef_id: ID du chef de chantier.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des entites Chantier du chef.
        """
        # Requete optimisee via table de jointure
        models = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .join(
                ChantierChefModel,
                ChantierModel.id == ChantierChefModel.chantier_id,
            )
            .filter(ChantierChefModel.user_id == chef_id)
            .filter(self._not_deleted())
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_responsable(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Chantier]:
        """
        Trouve les chantiers dont l'utilisateur est responsable (excluant les supprimes).

        Utilise une requete SQL avec UNION sur les tables de jointure
        pour des performances optimales (evite le N+1).

        Args:
            user_id: ID de l'utilisateur.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des entites Chantier de l'utilisateur.
        """
        from sqlalchemy import union, select

        # Sous-requete pour les chantiers ou l'user est conducteur
        conducteur_ids = (
            select(ChantierConducteurModel.chantier_id)
            .where(ChantierConducteurModel.user_id == user_id)
        )

        # Sous-requete pour les chantiers ou l'user est chef
        chef_ids = (
            select(ChantierChefModel.chantier_id)
            .where(ChantierChefModel.user_id == user_id)
        )

        # Union des deux ensembles
        all_chantier_ids = union(conducteur_ids, chef_ids).subquery()

        # Requete finale avec les chantiers
        models = (
            self.session.query(ChantierModel)
            .options(*self._eager_options)
            .filter(ChantierModel.id.in_(select(all_chantier_ids)))
            .filter(self._not_deleted())
            .order_by(ChantierModel.code)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def sync_responsables(self, chantier_id: int, conducteur_ids: List[int], chef_ids: List[int]) -> None:
        """
        Synchronise les tables de jointure avec les listes de responsables.

        Cette methode doit etre appelee apres save() pour maintenir
        les tables de jointure a jour avec les champs JSON legacy.

        Args:
            chantier_id: ID du chantier.
            conducteur_ids: Liste des IDs de conducteurs.
            chef_ids: Liste des IDs de chefs de chantier.
        """
        # Supprimer les anciennes associations
        self.session.query(ChantierConducteurModel).filter(
            ChantierConducteurModel.chantier_id == chantier_id
        ).delete()
        self.session.query(ChantierChefModel).filter(
            ChantierChefModel.chantier_id == chantier_id
        ).delete()

        # Ajouter les nouvelles associations conducteurs
        for user_id in conducteur_ids:
            self.session.add(
                ChantierConducteurModel(chantier_id=chantier_id, user_id=user_id)
            )

        # Ajouter les nouvelles associations chefs
        for user_id in chef_ids:
            self.session.add(
                ChantierChefModel(chantier_id=chantier_id, user_id=user_id)
            )

        self.session.flush()

    def exists_by_code(self, code: CodeChantier) -> bool:
        """
        Vérifie si un code chantier est déjà utilisé (excluant les supprimés).

        Args:
            code: Le code à vérifier.

        Returns:
            True si le code existe.
        """
        return (
            self.session.query(ChantierModel)
            .filter(ChantierModel.code == str(code))
            .filter(self._not_deleted())
            .first()
            is not None
        )

    def get_last_code(self) -> Optional[str]:
        """
        Récupère le dernier code chantier utilisé (incluant les supprimés pour éviter les collisions).

        Returns:
            Le dernier code ou None si aucun chantier.
        """
        # Note: On inclut les supprimés pour éviter de réutiliser un code supprimé
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
        Recherche des chantiers par nom ou code (excluant les supprimés).

        Args:
            query: Terme de recherche.
            statut: Filtre optionnel par statut.
            skip: Nombre d'éléments à sauter.
            limit: Nombre maximum à retourner.

        Returns:
            Liste des entités Chantier correspondantes.
        """
        search_pattern = f"%{query}%"
        base_query = self.session.query(ChantierModel).options(*self._eager_options).filter(
            or_(
                ChantierModel.nom.ilike(search_pattern),
                ChantierModel.code.ilike(search_pattern),
                ChantierModel.adresse.ilike(search_pattern),
            )
        ).filter(self._not_deleted())

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

        # Lire depuis les tables de jointure (source de vérité)
        # Fallback sur JSON si tables vides (données legacy)
        conducteur_ids = [r.user_id for r in model.conducteurs_rel] if model.conducteurs_rel else []
        chef_ids = [r.user_id for r in model.chefs_rel] if model.chefs_rel else []

        # Fallback sur colonnes JSON si tables de jointure vides
        if not conducteur_ids and model.conducteur_ids:
            conducteur_ids = list(model.conducteur_ids)
        if not chef_ids and model.chef_chantier_ids:
            chef_ids = list(model.chef_chantier_ids)

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
            maitre_ouvrage=model.maitre_ouvrage,
            heures_estimees=model.heures_estimees,
            date_debut=model.date_debut,
            date_fin=model.date_fin,
            conducteur_ids=conducteur_ids,
            chef_chantier_ids=chef_ids,
            type_travaux=model.type_travaux,
            batiment_plus_2ans=model.batiment_plus_2ans,
            usage_habitation=model.usage_habitation,
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
            maitre_ouvrage=chantier.maitre_ouvrage,
            heures_estimees=chantier.heures_estimees,
            date_debut=chantier.date_debut,
            date_fin=chantier.date_fin,
            conducteur_ids=list(chantier.conducteur_ids),
            chef_chantier_ids=list(chantier.chef_chantier_ids),
            type_travaux=chantier.type_travaux,
            batiment_plus_2ans=chantier.batiment_plus_2ans,
            usage_habitation=chantier.usage_habitation,
            created_at=chantier.created_at,
            updated_at=chantier.updated_at,
        )
