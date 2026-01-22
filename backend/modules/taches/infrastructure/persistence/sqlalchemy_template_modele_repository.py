"""Implementation SQLAlchemy du TemplateModeleRepository."""

from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from ...domain.entities import TemplateModele
from ...domain.repositories import TemplateModeleRepository
from .template_modele_model import TemplateModeleModel, SousTacheModeleModel


class SQLAlchemyTemplateModeleRepository(TemplateModeleRepository):
    """
    Implementation SQLAlchemy du repository TemplateModele.

    Gere la persistence des templates de taches (TAC-04).
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def find_by_id(self, template_id: int) -> Optional[TemplateModele]:
        """Trouve un template par son ID."""
        model = (
            self.session.query(TemplateModeleModel)
            .filter(TemplateModeleModel.id == template_id)
            .first()
        )
        return model.to_entity() if model else None

    def find_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateModele]:
        """Recupere tous les templates."""
        query = self.session.query(TemplateModeleModel)

        if active_only:
            query = query.filter(TemplateModeleModel.is_active == True)

        models = query.order_by(TemplateModeleModel.nom).offset(skip).limit(limit).all()
        return [m.to_entity() for m in models]

    def find_by_categorie(
        self,
        categorie: str,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateModele]:
        """Trouve les templates par categorie."""
        query = self.session.query(TemplateModeleModel).filter(
            TemplateModeleModel.categorie == categorie
        )

        if active_only:
            query = query.filter(TemplateModeleModel.is_active == True)

        models = query.order_by(TemplateModeleModel.nom).offset(skip).limit(limit).all()
        return [m.to_entity() for m in models]

    def save(self, template: TemplateModele) -> TemplateModele:
        """Persiste un template."""
        if template.id:
            # Mise a jour
            model = (
                self.session.query(TemplateModeleModel)
                .filter(TemplateModeleModel.id == template.id)
                .first()
            )
            if model:
                model.nom = template.nom
                model.description = template.description
                model.categorie = template.categorie
                model.unite_mesure = template.unite_mesure.value if template.unite_mesure else None
                model.heures_estimees_defaut = template.heures_estimees_defaut
                model.is_active = template.is_active
                model.updated_at = template.updated_at

                # Supprimer les anciennes sous-taches
                self.session.query(SousTacheModeleModel).filter(
                    SousTacheModeleModel.template_id == template.id
                ).delete()

                # Ajouter les nouvelles
                for i, st in enumerate(template.sous_taches):
                    st_model = SousTacheModeleModel(
                        template_id=template.id,
                        titre=st.titre,
                        description=st.description,
                        ordre=st.ordre if st.ordre else i,
                        unite_mesure=st.unite_mesure.value if st.unite_mesure else None,
                        heures_estimees_defaut=st.heures_estimees_defaut,
                    )
                    self.session.add(st_model)
        else:
            # Creation
            model = TemplateModeleModel.from_entity(template)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, template_id: int) -> bool:
        """Supprime un template."""
        model = (
            self.session.query(TemplateModeleModel)
            .filter(TemplateModeleModel.id == template_id)
            .first()
        )
        if not model:
            return False

        self.session.delete(model)
        self.session.commit()
        return True

    def count(self, active_only: bool = True) -> int:
        """Compte le nombre de templates."""
        query = self.session.query(func.count(TemplateModeleModel.id))
        if active_only:
            query = query.filter(TemplateModeleModel.is_active == True)
        return query.scalar()

    def search(
        self,
        query: Optional[str] = None,
        categorie: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[TemplateModele], int]:
        """Recherche des templates avec filtres."""
        base_query = self.session.query(TemplateModeleModel)

        if active_only:
            base_query = base_query.filter(TemplateModeleModel.is_active == True)

        if query:
            search_term = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    TemplateModeleModel.nom.ilike(search_term),
                    TemplateModeleModel.description.ilike(search_term),
                )
            )

        if categorie:
            base_query = base_query.filter(TemplateModeleModel.categorie == categorie)

        # Compter le total
        total = base_query.count()

        # Appliquer pagination
        models = base_query.order_by(TemplateModeleModel.nom).offset(skip).limit(limit).all()

        return [m.to_entity() for m in models], total

    def get_categories(self) -> List[str]:
        """Retourne la liste des categories distinctes."""
        results = (
            self.session.query(TemplateModeleModel.categorie)
            .filter(TemplateModeleModel.categorie.isnot(None))
            .filter(TemplateModeleModel.is_active == True)
            .distinct()
            .all()
        )
        return [r[0] for r in results if r[0]]

    def exists_by_nom(self, nom: str) -> bool:
        """Verifie si un template avec ce nom existe."""
        return (
            self.session.query(TemplateModeleModel)
            .filter(TemplateModeleModel.nom == nom)
            .first()
            is not None
        )
