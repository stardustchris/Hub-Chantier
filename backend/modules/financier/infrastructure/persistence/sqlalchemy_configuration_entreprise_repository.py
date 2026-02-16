"""Implementation SQLAlchemy du repository ConfigurationEntreprise."""

import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from ...domain.entities import ConfigurationEntreprise
from ...domain.repositories import ConfigurationEntrepriseRepository
from .models import ConfigurationEntrepriseModel

# TTL du cache en secondes (5 minutes - la config change rarement)
_CACHE_TTL_SECONDS = 300


class SQLAlchemyConfigurationEntrepriseRepository(ConfigurationEntrepriseRepository):
    """Implementation SQLAlchemy du repository ConfigurationEntreprise.

    Integre un cache TTL par annee pour eviter une requete DB a chaque
    calcul financier. Le cache est invalide automatiquement lors d'un save().
    """

    def __init__(self, session: Session):
        self._session = session
        # Cache: {annee: (entity, timestamp_monotonic)}
        self._cache: Dict[int, Tuple[ConfigurationEntreprise, float]] = {}

    def _to_entity(self, model: ConfigurationEntrepriseModel) -> ConfigurationEntreprise:
        return ConfigurationEntreprise(
            id=model.id,
            couts_fixes_annuels=Decimal(str(model.couts_fixes_annuels)),
            annee=model.annee,
            coeff_frais_generaux=Decimal(str(model.coeff_frais_generaux)),
            coeff_charges_patronales=Decimal(str(model.coeff_charges_patronales)),
            coeff_heures_sup=Decimal(str(model.coeff_heures_sup)),
            coeff_heures_sup_2=Decimal(str(model.coeff_heures_sup_2)),
            coeff_productivite=Decimal(str(model.coeff_productivite)),
            coeff_charges_ouvrier=Decimal(str(model.coeff_charges_ouvrier)) if model.coeff_charges_ouvrier is not None else None,
            coeff_charges_etam=Decimal(str(model.coeff_charges_etam)) if model.coeff_charges_etam is not None else None,
            coeff_charges_cadre=Decimal(str(model.coeff_charges_cadre)) if model.coeff_charges_cadre is not None else None,
            seuil_alerte_budget_pct=Decimal(str(model.seuil_alerte_budget_pct)),
            seuil_alerte_budget_critique_pct=Decimal(str(model.seuil_alerte_budget_critique_pct)),
            notes=model.notes,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    def _get_cached_config(self, annee: int) -> Optional[ConfigurationEntreprise]:
        """Retourne la config depuis le cache si valide, sinon None.

        Args:
            annee: L'annee demandee.

        Returns:
            L'entite en cache ou None si cache absent/expire.
        """
        entry = self._cache.get(annee)
        if entry is None:
            return None
        entity, cached_at = entry
        if (time.monotonic() - cached_at) > _CACHE_TTL_SECONDS:
            del self._cache[annee]
            return None
        return entity

    def find_by_annee(self, annee: int) -> Optional[ConfigurationEntreprise]:
        cached = self._get_cached_config(annee)
        if cached is not None:
            return cached

        model = (
            self._session.query(ConfigurationEntrepriseModel)
            .filter(ConfigurationEntrepriseModel.annee == annee)
            .first()
        )
        if model is None:
            return None

        entity = self._to_entity(model)
        self._cache[annee] = (entity, time.monotonic())
        return entity

    def save(self, config: ConfigurationEntreprise) -> ConfigurationEntreprise:
        # Invalider le cache pour cette annee
        self._cache.pop(config.annee, None)

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
                model.coeff_productivite = config.coeff_productivite
                model.coeff_charges_ouvrier = config.coeff_charges_ouvrier
                model.coeff_charges_etam = config.coeff_charges_etam
                model.coeff_charges_cadre = config.coeff_charges_cadre
                model.seuil_alerte_budget_pct = config.seuil_alerte_budget_pct
                model.seuil_alerte_budget_critique_pct = config.seuil_alerte_budget_critique_pct
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
                coeff_productivite=config.coeff_productivite,
                coeff_charges_ouvrier=config.coeff_charges_ouvrier,
                coeff_charges_etam=config.coeff_charges_etam,
                coeff_charges_cadre=config.coeff_charges_cadre,
                seuil_alerte_budget_pct=config.seuil_alerte_budget_pct,
                seuil_alerte_budget_critique_pct=config.seuil_alerte_budget_critique_pct,
                notes=config.notes,
                updated_at=config.updated_at,
                updated_by=config.updated_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)
