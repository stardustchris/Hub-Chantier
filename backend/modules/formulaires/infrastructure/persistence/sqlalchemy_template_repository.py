"""Implementation SQLAlchemy du TemplateFormulaireRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session

from ...domain.entities import TemplateFormulaire, ChampTemplate
from ...domain.repositories import TemplateFormulaireRepository
from ...domain.value_objects import CategorieFormulaire, TypeChamp
from .template_model import TemplateFormulaireModel, ChampTemplateModel


class SQLAlchemyTemplateFormulaireRepository(TemplateFormulaireRepository):
    """Implementation SQLAlchemy du repository des templates."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session."""
        self._session = session

    def _to_entity(self, model: TemplateFormulaireModel) -> TemplateFormulaire:
        """Convertit un modele en entite."""
        champs = [
            ChampTemplate(
                id=c.id,
                nom=c.nom,
                label=c.label,
                type_champ=TypeChamp.from_string(c.type_champ),
                obligatoire=c.obligatoire,
                ordre=c.ordre,
                placeholder=c.placeholder,
                options=c.options or [],
                valeur_defaut=c.valeur_defaut,
                validation_regex=c.validation_regex,
                min_value=c.min_value,
                max_value=c.max_value,
            )
            for c in model.champs
        ]

        return TemplateFormulaire(
            id=model.id,
            nom=model.nom,
            description=model.description,
            categorie=CategorieFormulaire.from_string(model.categorie),
            champs=champs,
            is_active=model.is_active,
            version=model.version,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: TemplateFormulaire) -> TemplateFormulaireModel:
        """Convertit une entite en modele."""
        model = TemplateFormulaireModel(
            id=entity.id,
            nom=entity.nom,
            description=entity.description,
            categorie=entity.categorie.value,
            is_active=entity.is_active,
            version=entity.version,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        model.champs = [
            ChampTemplateModel(
                id=c.id,
                nom=c.nom,
                label=c.label,
                type_champ=c.type_champ.value,
                obligatoire=c.obligatoire,
                ordre=c.ordre,
                placeholder=c.placeholder,
                options=c.options,
                valeur_defaut=c.valeur_defaut,
                validation_regex=c.validation_regex,
                min_value=c.min_value,
                max_value=c.max_value,
            )
            for c in entity.champs
        ]

        return model

    def find_by_id(self, template_id: int) -> Optional[TemplateFormulaire]:
        """Trouve un template par son ID."""
        model = self._session.query(TemplateFormulaireModel).filter_by(id=template_id).first()
        return self._to_entity(model) if model else None

    def find_by_nom(self, nom: str) -> Optional[TemplateFormulaire]:
        """Trouve un template par son nom."""
        model = self._session.query(TemplateFormulaireModel).filter_by(nom=nom).first()
        return self._to_entity(model) if model else None

    def save(self, template: TemplateFormulaire) -> TemplateFormulaire:
        """Persiste un template."""
        if template.id:
            # Update
            model = self._session.query(TemplateFormulaireModel).filter_by(id=template.id).first()
            if model:
                model.nom = template.nom
                model.description = template.description
                model.categorie = template.categorie.value
                model.is_active = template.is_active
                model.version = template.version
                model.updated_at = template.updated_at

                # Supprimer les anciens champs
                self._session.query(ChampTemplateModel).filter_by(template_id=model.id).delete()

                # Ajouter les nouveaux champs
                for c in template.champs:
                    champ_model = ChampTemplateModel(
                        template_id=model.id,
                        nom=c.nom,
                        label=c.label,
                        type_champ=c.type_champ.value,
                        obligatoire=c.obligatoire,
                        ordre=c.ordre,
                        placeholder=c.placeholder,
                        options=c.options,
                        valeur_defaut=c.valeur_defaut,
                        validation_regex=c.validation_regex,
                        min_value=c.min_value,
                        max_value=c.max_value,
                    )
                    self._session.add(champ_model)
        else:
            # Insert
            model = self._to_model(template)
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, template_id: int) -> bool:
        """Supprime un template."""
        model = self._session.query(TemplateFormulaireModel).filter_by(id=template_id).first()
        if model:
            self._session.delete(model)
            self._session.commit()
            return True
        return False

    def find_all(self, skip: int = 0, limit: int = 100) -> List[TemplateFormulaire]:
        """Recupere tous les templates."""
        models = (
            self._session.query(TemplateFormulaireModel)
            .order_by(TemplateFormulaireModel.nom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count(self) -> int:
        """Compte le nombre total de templates."""
        return self._session.query(TemplateFormulaireModel).count()

    def find_by_categorie(
        self,
        categorie: CategorieFormulaire,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateFormulaire]:
        """Trouve les templates par categorie."""
        models = (
            self._session.query(TemplateFormulaireModel)
            .filter_by(categorie=categorie.value)
            .order_by(TemplateFormulaireModel.nom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_active(self, skip: int = 0, limit: int = 100) -> List[TemplateFormulaire]:
        """Trouve les templates actifs."""
        models = (
            self._session.query(TemplateFormulaireModel)
            .filter_by(is_active=True)
            .order_by(TemplateFormulaireModel.nom)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def exists_by_nom(self, nom: str) -> bool:
        """Verifie si un nom de template existe."""
        return (
            self._session.query(TemplateFormulaireModel)
            .filter_by(nom=nom)
            .first() is not None
        )

    def search(
        self,
        query: Optional[str] = None,
        categorie: Optional[CategorieFormulaire] = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[TemplateFormulaire], int]:
        """Recherche des templates avec filtres."""
        q = self._session.query(TemplateFormulaireModel)

        if query:
            pattern = f"%{query}%"
            q = q.filter(
                (TemplateFormulaireModel.nom.ilike(pattern)) |
                (TemplateFormulaireModel.description.ilike(pattern))
            )

        if categorie:
            q = q.filter_by(categorie=categorie.value)

        if active_only:
            q = q.filter_by(is_active=True)

        total = q.count()

        models = (
            q.order_by(TemplateFormulaireModel.nom)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [self._to_entity(m) for m in models], total
