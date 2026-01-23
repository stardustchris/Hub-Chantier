"""Implementation SQLAlchemy du FormulaireRempliRepository."""

from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import FormulaireRempli, ChampRempli, PhotoFormulaire
from ...domain.repositories import FormulaireRempliRepository
from ...domain.value_objects import StatutFormulaire, TypeChamp
from .formulaire_model import FormulaireRempliModel, ChampRempliModel, PhotoFormulaireModel


class SQLAlchemyFormulaireRempliRepository(FormulaireRempliRepository):
    """Implementation SQLAlchemy du repository des formulaires."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session."""
        self._session = session

    def _to_entity(self, model: FormulaireRempliModel) -> FormulaireRempli:
        """Convertit un modele en entite."""
        champs = [
            ChampRempli(
                nom=c.nom,
                type_champ=TypeChamp.from_string(c.type_champ),
                valeur=c.valeur,
                timestamp=c.timestamp,
            )
            for c in model.champs
        ]

        photos = [
            PhotoFormulaire(
                id=p.id,
                url=p.url,
                nom_fichier=p.nom_fichier,
                champ_nom=p.champ_nom,
                timestamp=p.timestamp,
                latitude=p.latitude,
                longitude=p.longitude,
            )
            for p in model.photos
        ]

        return FormulaireRempli(
            id=model.id,
            template_id=model.template_id,
            chantier_id=model.chantier_id,
            user_id=model.user_id,
            statut=StatutFormulaire.from_string(model.statut),
            champs=champs,
            photos=photos,
            signature_url=model.signature_url,
            signature_nom=model.signature_nom,
            signature_timestamp=model.signature_timestamp,
            localisation_latitude=model.localisation_latitude,
            localisation_longitude=model.localisation_longitude,
            soumis_at=model.soumis_at,
            valide_by=model.valide_by,
            valide_at=model.valide_at,
            version=model.version,
            parent_id=model.parent_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_by_id(self, formulaire_id: int) -> Optional[FormulaireRempli]:
        """Trouve un formulaire par son ID."""
        model = self._session.query(FormulaireRempliModel).filter_by(id=formulaire_id).first()
        return self._to_entity(model) if model else None

    def save(self, formulaire: FormulaireRempli) -> FormulaireRempli:
        """Persiste un formulaire."""
        if formulaire.id:
            # Update
            model = self._session.query(FormulaireRempliModel).filter_by(id=formulaire.id).first()
            if model:
                model.statut = formulaire.statut.value
                model.signature_url = formulaire.signature_url
                model.signature_nom = formulaire.signature_nom
                model.signature_timestamp = formulaire.signature_timestamp
                model.localisation_latitude = formulaire.localisation_latitude
                model.localisation_longitude = formulaire.localisation_longitude
                model.soumis_at = formulaire.soumis_at
                model.valide_by = formulaire.valide_by
                model.valide_at = formulaire.valide_at
                model.version = formulaire.version
                model.updated_at = formulaire.updated_at

                # Supprimer les anciens champs
                self._session.query(ChampRempliModel).filter_by(formulaire_id=model.id).delete()

                # Ajouter les nouveaux champs
                for c in formulaire.champs:
                    champ_model = ChampRempliModel(
                        formulaire_id=model.id,
                        nom=c.nom,
                        type_champ=c.type_champ.value,
                        valeur=c.valeur,
                        timestamp=c.timestamp,
                    )
                    self._session.add(champ_model)

                # Gerer les photos (ajouter les nouvelles)
                existing_photo_ids = {p.id for p in model.photos if p.id}
                for p in formulaire.photos:
                    if p.id not in existing_photo_ids:
                        photo_model = PhotoFormulaireModel(
                            formulaire_id=model.id,
                            url=p.url,
                            nom_fichier=p.nom_fichier,
                            champ_nom=p.champ_nom,
                            timestamp=p.timestamp,
                            latitude=p.latitude,
                            longitude=p.longitude,
                        )
                        self._session.add(photo_model)
        else:
            # Insert
            model = FormulaireRempliModel(
                template_id=formulaire.template_id,
                chantier_id=formulaire.chantier_id,
                user_id=formulaire.user_id,
                statut=formulaire.statut.value,
                signature_url=formulaire.signature_url,
                signature_nom=formulaire.signature_nom,
                signature_timestamp=formulaire.signature_timestamp,
                localisation_latitude=formulaire.localisation_latitude,
                localisation_longitude=formulaire.localisation_longitude,
                soumis_at=formulaire.soumis_at,
                valide_by=formulaire.valide_by,
                valide_at=formulaire.valide_at,
                version=formulaire.version,
                parent_id=formulaire.parent_id,
                created_at=formulaire.created_at,
                updated_at=formulaire.updated_at,
            )
            self._session.add(model)
            self._session.flush()  # Get the ID

            # Ajouter les champs
            for c in formulaire.champs:
                champ_model = ChampRempliModel(
                    formulaire_id=model.id,
                    nom=c.nom,
                    type_champ=c.type_champ.value,
                    valeur=c.valeur,
                    timestamp=c.timestamp,
                )
                self._session.add(champ_model)

            # Ajouter les photos
            for p in formulaire.photos:
                photo_model = PhotoFormulaireModel(
                    formulaire_id=model.id,
                    url=p.url,
                    nom_fichier=p.nom_fichier,
                    champ_nom=p.champ_nom,
                    timestamp=p.timestamp,
                    latitude=p.latitude,
                    longitude=p.longitude,
                )
                self._session.add(photo_model)

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, formulaire_id: int) -> bool:
        """Supprime un formulaire."""
        model = self._session.query(FormulaireRempliModel).filter_by(id=formulaire_id).first()
        if model:
            self._session.delete(model)
            self._session.commit()
            return True
        return False

    def find_by_chantier(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FormulaireRempli]:
        """Trouve les formulaires d'un chantier (FOR-10)."""
        models = (
            self._session.query(FormulaireRempliModel)
            .filter_by(chantier_id=chantier_id)
            .order_by(FormulaireRempliModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_template(
        self,
        template_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FormulaireRempli]:
        """Trouve les formulaires bases sur un template."""
        models = (
            self._session.query(FormulaireRempliModel)
            .filter_by(template_id=template_id)
            .order_by(FormulaireRempliModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FormulaireRempli]:
        """Trouve les formulaires remplis par un utilisateur."""
        models = (
            self._session.query(FormulaireRempliModel)
            .filter_by(user_id=user_id)
            .order_by(FormulaireRempliModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_statut(
        self,
        statut: StatutFormulaire,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FormulaireRempli]:
        """Trouve les formulaires par statut."""
        models = (
            self._session.query(FormulaireRempliModel)
            .filter_by(statut=statut.value)
            .order_by(FormulaireRempliModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_chantier(self, chantier_id: int) -> int:
        """Compte les formulaires d'un chantier."""
        return (
            self._session.query(FormulaireRempliModel)
            .filter_by(chantier_id=chantier_id)
            .count()
        )

    def find_history(self, formulaire_id: int) -> List[FormulaireRempli]:
        """Trouve l'historique d'un formulaire (FOR-08)."""
        result = []

        # Ajouter le formulaire courant
        current = self._session.query(FormulaireRempliModel).filter_by(id=formulaire_id).first()
        if current:
            result.append(self._to_entity(current))

            # Remonter la chaine des parents
            parent_id = current.parent_id
            while parent_id:
                parent = self._session.query(FormulaireRempliModel).filter_by(id=parent_id).first()
                if parent:
                    result.append(self._to_entity(parent))
                    parent_id = parent.parent_id
                else:
                    break

        return result

    def search(
        self,
        chantier_id: Optional[int] = None,
        template_id: Optional[int] = None,
        user_id: Optional[int] = None,
        statut: Optional[StatutFormulaire] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[FormulaireRempli], int]:
        """Recherche des formulaires avec filtres."""
        q = self._session.query(FormulaireRempliModel)

        if chantier_id:
            q = q.filter_by(chantier_id=chantier_id)

        if template_id:
            q = q.filter_by(template_id=template_id)

        if user_id:
            q = q.filter_by(user_id=user_id)

        if statut:
            q = q.filter_by(statut=statut.value)

        if date_debut:
            q = q.filter(FormulaireRempliModel.created_at >= date_debut)

        if date_fin:
            q = q.filter(FormulaireRempliModel.created_at <= date_fin)

        total = q.count()

        models = (
            q.order_by(FormulaireRempliModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [self._to_entity(m) for m in models], total
