"""Use Cases pour les macros de paie (FDH-18).

CRUD des macros de paie + calcul automatique sur période.
"""

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any

from ...domain.entities import MacroPaie
from ...domain.entities.macro_paie import TypeMacroPaie
from ...domain.repositories import MacroPaieRepository, PointageRepository

logger = logging.getLogger(__name__)


class MacroNotFoundError(Exception):
    """Erreur levée quand une macro n'est pas trouvée."""
    pass


@dataclass
class MacroPaieDTO:
    """DTO pour une macro de paie."""
    id: int
    nom: str
    type_macro: str
    type_macro_label: str
    description: Optional[str]
    formule: str
    parametres: Dict[str, Any]
    active: bool
    created_by: Optional[int]
    created_at: str
    updated_at: str

    @classmethod
    def from_entity(cls, entity: MacroPaie) -> "MacroPaieDTO":
        return cls(
            id=entity.id,  # type: ignore
            nom=entity.nom,
            type_macro=entity.type_macro.value,
            type_macro_label=entity.type_macro.label,
            description=entity.description,
            formule=entity.formule,
            parametres=entity.parametres,
            active=entity.active,
            created_by=entity.created_by,
            created_at=entity.created_at.isoformat(),
            updated_at=entity.updated_at.isoformat(),
        )


@dataclass
class MacroPaieCreateDTO:
    """DTO pour la création d'une macro."""
    nom: str
    type_macro: str
    formule: str
    description: Optional[str] = None
    parametres: Optional[Dict[str, Any]] = None
    created_by: Optional[int] = None


@dataclass
class MacroPaieUpdateDTO:
    """DTO pour la mise à jour d'une macro."""
    nom: Optional[str] = None
    description: Optional[str] = None
    formule: Optional[str] = None
    parametres: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


@dataclass
class CalculMacroResultDTO:
    """DTO pour le résultat d'un calcul de macro."""
    macro_id: int
    macro_nom: str
    type_macro: str
    resultat: float
    formule: str
    contexte: Dict[str, Any]


@dataclass
class CalculPeriodeResultDTO:
    """DTO pour le résultat d'un calcul sur une période."""
    utilisateur_id: int
    date_debut: str
    date_fin: str
    resultats: List[CalculMacroResultDTO]
    total: float


class CreateMacroPaieUseCase:
    """Use case pour créer une macro de paie."""

    def __init__(self, macro_repository: MacroPaieRepository):
        self._macro_repo = macro_repository

    def execute(self, dto: MacroPaieCreateDTO) -> MacroPaieDTO:
        """Crée une nouvelle macro de paie.

        Args:
            dto: Données de création.

        Returns:
            La macro créée.
        """
        type_macro = TypeMacroPaie.from_string(dto.type_macro)

        macro = MacroPaie(
            nom=dto.nom,
            type_macro=type_macro,
            formule=dto.formule,
            description=dto.description,
            parametres=dto.parametres or {},
            created_by=dto.created_by,
        )

        # Valider la formule avec un contexte de test
        try:
            macro.calculer({"jours_travailles": 1, "montant_unitaire": 1})
        except ValueError as e:
            raise ValueError(f"Formule invalide: {e}")

        macro = self._macro_repo.save(macro)
        logger.info(f"Macro de paie créée: #{macro.id} '{macro.nom}'")

        return MacroPaieDTO.from_entity(macro)


class GetMacroPaieUseCase:
    """Use case pour récupérer une macro de paie."""

    def __init__(self, macro_repository: MacroPaieRepository):
        self._macro_repo = macro_repository

    def execute(self, macro_id: int) -> MacroPaieDTO:
        macro = self._macro_repo.find_by_id(macro_id)
        if not macro:
            raise MacroNotFoundError(f"Macro #{macro_id} non trouvée")
        return MacroPaieDTO.from_entity(macro)


class ListMacrosPaieUseCase:
    """Use case pour lister les macros de paie."""

    def __init__(self, macro_repository: MacroPaieRepository):
        self._macro_repo = macro_repository

    def execute(
        self,
        active_only: bool = True,
        type_macro: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[MacroPaieDTO]:
        """Liste les macros de paie.

        Args:
            active_only: Filtrer les macros actives uniquement.
            type_macro: Filtrer par type.
            skip: Offset pagination.
            limit: Limite pagination.

        Returns:
            Liste des macros.
        """
        if type_macro:
            type_vo = TypeMacroPaie.from_string(type_macro)
            macros = self._macro_repo.find_by_type(type_vo, active_only)
        else:
            macros = self._macro_repo.find_all(active_only, skip, limit)

        return [MacroPaieDTO.from_entity(m) for m in macros]


class UpdateMacroPaieUseCase:
    """Use case pour mettre à jour une macro de paie."""

    def __init__(self, macro_repository: MacroPaieRepository):
        self._macro_repo = macro_repository

    def execute(self, macro_id: int, dto: MacroPaieUpdateDTO) -> MacroPaieDTO:
        """Met à jour une macro.

        Args:
            macro_id: ID de la macro.
            dto: Données de mise à jour.

        Returns:
            La macro mise à jour.
        """
        macro = self._macro_repo.find_by_id(macro_id)
        if not macro:
            raise MacroNotFoundError(f"Macro #{macro_id} non trouvée")

        if dto.nom is not None:
            macro.nom = dto.nom.strip()
        if dto.description is not None:
            macro.description = dto.description.strip() if dto.description else None
        if dto.formule is not None:
            macro.modifier_formule(dto.formule)
        if dto.parametres is not None:
            macro.modifier_parametres(dto.parametres)
        if dto.active is not None:
            if dto.active:
                macro.activer()
            else:
                macro.desactiver()

        macro = self._macro_repo.save(macro)
        logger.info(f"Macro de paie mise à jour: #{macro.id} '{macro.nom}'")

        return MacroPaieDTO.from_entity(macro)


class DeleteMacroPaieUseCase:
    """Use case pour supprimer une macro de paie."""

    def __init__(self, macro_repository: MacroPaieRepository):
        self._macro_repo = macro_repository

    def execute(self, macro_id: int) -> bool:
        macro = self._macro_repo.find_by_id(macro_id)
        if not macro:
            raise MacroNotFoundError(f"Macro #{macro_id} non trouvée")

        result = self._macro_repo.delete(macro_id)
        if result:
            logger.info(f"Macro de paie supprimée: #{macro_id}")
        return result


class CalculerMacrosPeriodeUseCase:
    """Use case pour calculer les macros sur une période (FDH-18).

    Applique toutes les macros actives sur les pointages d'un utilisateur
    pour une période donnée et retourne les résultats.
    """

    def __init__(
        self,
        macro_repository: MacroPaieRepository,
        pointage_repository: PointageRepository,
    ):
        self._macro_repo = macro_repository
        self._pointage_repo = pointage_repository

    def execute(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
        contexte_supplementaire: Optional[Dict[str, Any]] = None,
    ) -> CalculPeriodeResultDTO:
        """Calcule toutes les macros actives sur une période.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de début.
            date_fin: Date de fin.
            contexte_supplementaire: Variables additionnelles.

        Returns:
            Résultats de calcul pour chaque macro.
        """
        # Récupérer les macros actives
        macros = self._macro_repo.find_all(active_only=True)
        if not macros:
            return CalculPeriodeResultDTO(
                utilisateur_id=utilisateur_id,
                date_debut=date_debut.isoformat(),
                date_fin=date_fin.isoformat(),
                resultats=[],
                total=0.0,
            )

        # Construire le contexte de calcul à partir des pointages
        contexte = self._construire_contexte(
            utilisateur_id, date_debut, date_fin
        )
        if contexte_supplementaire:
            contexte.update(contexte_supplementaire)

        # Calculer chaque macro
        resultats = []
        total = Decimal("0.00")

        for macro in macros:
            try:
                resultat = macro.calculer(contexte)
                resultats.append(CalculMacroResultDTO(
                    macro_id=macro.id,  # type: ignore
                    macro_nom=macro.nom,
                    type_macro=macro.type_macro.value,
                    resultat=float(resultat),
                    formule=macro.formule,
                    contexte=contexte,
                ))
                total += resultat
            except ValueError as e:
                logger.warning(
                    f"Erreur calcul macro #{macro.id} '{macro.nom}': {e}"
                )

        return CalculPeriodeResultDTO(
            utilisateur_id=utilisateur_id,
            date_debut=date_debut.isoformat(),
            date_fin=date_fin.isoformat(),
            resultats=resultats,
            total=float(total),
        )

    def _construire_contexte(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ) -> Dict[str, Any]:
        """Construit le contexte de calcul à partir des pointages.

        Utilise PointageRepository.search pour récupérer les pointages
        sur la période et calcule les variables de contexte.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de début.
            date_fin: Date de fin.

        Returns:
            Variables de contexte pour les formules.
        """
        pointages, _ = self._pointage_repo.search(
            utilisateur_id=utilisateur_id,
            date_debut=date_debut,
            date_fin=date_fin,
            limit=1000,
        )

        jours_travailles = len(pointages)
        # Duree.decimal retourne les heures en float
        heures_normales = sum(p.heures_normales.decimal for p in pointages)
        heures_supplementaires = sum(
            p.heures_supplementaires.decimal for p in pointages
        )
        heures_totales = heures_normales + heures_supplementaires

        return {
            "jours_travailles": jours_travailles,
            "heures_normales": heures_normales,
            "heures_supplementaires": heures_supplementaires,
            "heures_totales": heures_totales,
            "montant_unitaire": 0.0,  # Sera surchargé par les paramètres macro
            "distance_chantier": 0.0,  # Sera surchargé par contexte_supplementaire
            "jours_intemperies": 0,  # Sera surchargé par contexte_supplementaire
            "tarif_km": 0.0,
            "plafond_journalier": 0.0,
            "montant_journalier": 0.0,
            "seuil_declenchement": 0.0,
        }
