"""Implementation SQLAlchemy du repository ConfigurationEntreprise."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from ...domain.entities import ConfigurationEntreprise
from ...domain.repositories import ConfigurationEntrepriseRepository
from .models import ConfigurationEntrepriseModel


class SQLAlchemyConfigurationEntrepriseRepository(ConfigurationEntrepriseRepository):
    """Implementation SQLAlchemy du repository ConfigurationEntreprise."""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: ConfigurationEntrepriseModel) -> ConfigurationEntreprise:
        return ConfigurationEntreprise(
            id=model.id,
            couts_fixes_annuels=Decimal(str(model.couts_fixes_annuels)),
            annee=model.annee,
            coeff_frais_generaux=Decimal(str(model.coeff_frais_generaux)),
            coeff_charges_patronales=Decimal(str(model.coeff_charges_patronales)),
            coeff_heures_sup=Decimal(str(model.coeff_heures_sup)),
            coeff_heures_sup_2=Decimal(str(model.coeff_heures_sup_2)),
            notes=model.notes,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    def find_by_annee(self, annee: int) -> Optional[ConfigurationEntreprise]:
        model = (
            self._session.query(ConfigurationEntrepriseModel)
            .filter(ConfigurationEntrepriseModel.annee == annee)
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, config: ConfigurationEntreprise) -> ConfigurationEntreprise:
        if config.id:
            model = (
                self._session.query(ConfigurationEntrepriseModel)
                .filter(ConfigurationEntrepriseModel.id == config.id)
                .first()
            )
            if model:
                model.couts_fixes_annuels = config.couts_fixes_annuels
                model.coeff_frais_generaux = config.coeff_frais_generaux
                model.coeff_charges_patronales = config.coeff_charges_patronales
                model.coeff_heures_sup = config.coeff_heures_sup
                model.coeff_heures_sup_2 = config.coeff_heures_sup_2
                model.notes = config.notes
                model.updated_at = config.updated_at or datetime.utcnow()
                model.updated_by = config.updated_by
        else:
            model = ConfigurationEntrepriseModel(
                couts_fixes_annuels=config.couts_fixes_annuels,
                annee=config.annee,
                coeff_frais_generaux=config.coeff_frais_generaux,
                coeff_charges_patronales=config.coeff_charges_patronales,
                coeff_heures_sup=config.coeff_heures_sup,
                coeff_heures_sup_2=config.coeff_heures_sup_2,
                notes=config.notes,
                updated_at=config.updated_at,
                updated_by=config.updated_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)
