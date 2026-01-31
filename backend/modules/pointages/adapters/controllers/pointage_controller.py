"""Controller pour les pointages et feuilles d'heures."""

from datetime import date
from typing import Optional, List, Dict, Any

from ...application import (
    CreatePointageUseCase,
    UpdatePointageUseCase,
    DeletePointageUseCase,
    SignPointageUseCase,
    SubmitPointageUseCase,
    ValidatePointageUseCase,
    RejectPointageUseCase,
    CorrectPointageUseCase,
    GetPointageUseCase,
    ListPointagesUseCase,
    GetFeuilleHeuresUseCase,
    ListFeuillesHeuresUseCase,
    GetVueSemaineUseCase,
    BulkCreateFromPlanningUseCase,
    CreateVariablePaieUseCase,
    ExportFeuilleHeuresUseCase,
    GetJaugeAvancementUseCase,
    CompareEquipesUseCase,
    BulkValidatePointagesUseCase,
    GenerateMonthlyRecapUseCase,
    LockMonthlyPeriodUseCase,
)
from ...application.dtos import (
    CreatePointageDTO,
    UpdatePointageDTO,
    SignPointageDTO,
    ValidatePointageDTO,
    RejectPointageDTO,
    PointageSearchDTO,
    FeuilleHeuresSearchDTO,
    BulkCreatePointageDTO,
    AffectationSourceDTO,
    CreateVariablePaieDTO,
    ExportFeuilleHeuresDTO,
    FormatExport,
    BulkValidatePointagesDTO,
    GenerateMonthlyRecapDTO,
    LockMonthlyPeriodDTO,
)
from ...domain.repositories import (
    PointageRepository,
    FeuilleHeuresRepository,
    VariablePaieRepository,
)
from ...application.ports import EventBus


class PointageController:
    """
    Controller pour les opérations sur les pointages.

    Orchestre les use cases et formate les réponses pour l'API.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        feuille_repo: FeuilleHeuresRepository,
        variable_repo: VariablePaieRepository,
        event_bus: Optional[EventBus] = None,
        entity_info_service: Optional["EntityInfoService"] = None,
    ):
        """
        Initialise le controller.

        Args:
            pointage_repo: Repository des pointages.
            feuille_repo: Repository des feuilles d'heures.
            variable_repo: Repository des variables de paie.
            event_bus: Bus d'événements (optionnel).
            entity_info_service: Service pour enrichir les données (noms utilisateurs/chantiers).
        """
        self.pointage_repo = pointage_repo
        self.feuille_repo = feuille_repo
        self.variable_repo = variable_repo
        self.event_bus = event_bus
        self.entity_info_service = entity_info_service

        # Initialise les use cases
        self._create_uc = CreatePointageUseCase(pointage_repo, feuille_repo, event_bus)
        self._update_uc = UpdatePointageUseCase(pointage_repo, event_bus)
        self._delete_uc = DeletePointageUseCase(pointage_repo, event_bus)
        self._sign_uc = SignPointageUseCase(pointage_repo, event_bus)
        self._submit_uc = SubmitPointageUseCase(pointage_repo, event_bus)
        self._validate_uc = ValidatePointageUseCase(pointage_repo, event_bus)
        self._reject_uc = RejectPointageUseCase(pointage_repo, event_bus)
        self._correct_uc = CorrectPointageUseCase(pointage_repo, event_bus)
        self._get_uc = GetPointageUseCase(pointage_repo)
        self._list_uc = ListPointagesUseCase(pointage_repo, entity_info_service)
        self._get_feuille_uc = GetFeuilleHeuresUseCase(feuille_repo, pointage_repo, entity_info_service)
        self._list_feuille_uc = ListFeuillesHeuresUseCase(feuille_repo, pointage_repo)
        self._vue_semaine_uc = GetVueSemaineUseCase(pointage_repo, entity_info_service)
        self._bulk_create_uc = BulkCreateFromPlanningUseCase(
            pointage_repo, feuille_repo, event_bus
        )
        self._create_variable_uc = CreateVariablePaieUseCase(
            variable_repo, pointage_repo, event_bus
        )
        self._export_uc = ExportFeuilleHeuresUseCase(feuille_repo, pointage_repo, event_bus)
        self._jauge_uc = GetJaugeAvancementUseCase(pointage_repo)
        self._bulk_validate_uc = BulkValidatePointagesUseCase(pointage_repo, event_bus)
        self._monthly_recap_uc = GenerateMonthlyRecapUseCase(pointage_repo, variable_repo)
        self._lock_period_uc = LockMonthlyPeriodUseCase(event_bus)
        self._compare_uc = CompareEquipesUseCase(pointage_repo)

    # ===== Pointage CRUD =====

    def create_pointage(
        self,
        utilisateur_id: int,
        chantier_id: int,
        date_pointage: date,
        heures_normales: str,
        heures_supplementaires: str = "00:00",
        commentaire: Optional[str] = None,
        affectation_id: Optional[int] = None,
        created_by: int = None,
    ) -> Dict[str, Any]:
        """Crée un pointage."""
        dto = CreatePointageDTO(
            utilisateur_id=utilisateur_id,
            chantier_id=chantier_id,
            date_pointage=date_pointage,
            heures_normales=heures_normales,
            heures_supplementaires=heures_supplementaires,
            commentaire=commentaire,
            affectation_id=affectation_id,
        )
        result = self._create_uc.execute(dto, created_by or utilisateur_id)
        return self._pointage_to_dict(result)

    def update_pointage(
        self,
        pointage_id: int,
        heures_normales: Optional[str] = None,
        heures_supplementaires: Optional[str] = None,
        commentaire: Optional[str] = None,
        updated_by: int = None,
    ) -> Dict[str, Any]:
        """Met à jour un pointage."""
        dto = UpdatePointageDTO(
            pointage_id=pointage_id,
            heures_normales=heures_normales,
            heures_supplementaires=heures_supplementaires,
            commentaire=commentaire,
        )
        result = self._update_uc.execute(dto, updated_by)
        return self._pointage_to_dict(result)

    def delete_pointage(self, pointage_id: int, deleted_by: int) -> bool:
        """Supprime un pointage."""
        return self._delete_uc.execute(pointage_id, deleted_by)

    def get_pointage(self, pointage_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un pointage par ID."""
        result = self._get_uc.execute(pointage_id)
        return self._pointage_to_dict(result) if result else None

    def list_pointages(
        self,
        utilisateur_id: Optional[int] = None,
        chantier_id: Optional[int] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statut: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Liste les pointages avec filtres."""
        dto = PointageSearchDTO(
            utilisateur_id=utilisateur_id,
            chantier_id=chantier_id,
            date_debut=date_debut,
            date_fin=date_fin,
            statut=statut,
            page=page,
            page_size=page_size,
        )
        result = self._list_uc.execute(dto)
        return {
            "items": [self._pointage_to_dict(p) for p in result.items],
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
        }

    # ===== Workflow Validation =====

    def sign_pointage(self, pointage_id: int, signature: str) -> Dict[str, Any]:
        """Signe un pointage."""
        dto = SignPointageDTO(pointage_id=pointage_id, signature=signature)
        result = self._sign_uc.execute(dto)
        return self._pointage_to_dict(result)

    def submit_pointage(self, pointage_id: int) -> Dict[str, Any]:
        """Soumet un pointage pour validation."""
        result = self._submit_uc.execute(pointage_id)
        return self._pointage_to_dict(result)

    def validate_pointage(self, pointage_id: int, validateur_id: int) -> Dict[str, Any]:
        """Valide un pointage."""
        dto = ValidatePointageDTO(pointage_id=pointage_id, validateur_id=validateur_id)
        result = self._validate_uc.execute(dto)
        return self._pointage_to_dict(result)

    def reject_pointage(
        self, pointage_id: int, validateur_id: int, motif: str
    ) -> Dict[str, Any]:
        """Rejette un pointage."""
        dto = RejectPointageDTO(
            pointage_id=pointage_id, validateur_id=validateur_id, motif=motif
        )
        result = self._reject_uc.execute(dto)
        return self._pointage_to_dict(result)

    def correct_pointage(self, pointage_id: int) -> Dict[str, Any]:
        """
        Repasse un pointage rejeté en brouillon pour correction.

        Args:
            pointage_id: ID du pointage à corriger.

        Returns:
            Le pointage remis en brouillon.
        """
        result = self._correct_uc.execute(pointage_id)
        return self._pointage_to_dict(result)

    # ===== Feuilles d'heures =====

    def get_feuille_heures(self, feuille_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une feuille d'heures par ID."""
        result = self._get_feuille_uc.execute(feuille_id)
        return self._feuille_to_dict(result) if result else None

    def get_feuille_heures_semaine(
        self, utilisateur_id: int, semaine_debut: date
    ) -> Dict[str, Any]:
        """Récupère la feuille d'heures d'un utilisateur pour une semaine."""
        result = self._get_feuille_uc.execute_by_utilisateur_semaine(
            utilisateur_id, semaine_debut
        )
        return self._feuille_to_dict(result) if result else {}

    def get_navigation_semaine(self, semaine_debut: date) -> Dict[str, Any]:
        """Retourne les infos de navigation semaine."""
        result = self._get_feuille_uc.get_navigation(semaine_debut)
        return {
            "semaine_courante": result.semaine_courante.isoformat(),
            "semaine_precedente": result.semaine_precedente.isoformat(),
            "semaine_suivante": result.semaine_suivante.isoformat(),
            "numero_semaine": result.numero_semaine,
            "annee": result.annee,
            "label": result.label,
        }

    def list_feuilles_heures(
        self,
        utilisateur_id: Optional[int] = None,
        annee: Optional[int] = None,
        numero_semaine: Optional[int] = None,
        statut: Optional[str] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """Liste les feuilles d'heures avec filtres."""
        dto = FeuilleHeuresSearchDTO(
            utilisateur_id=utilisateur_id,
            annee=annee,
            numero_semaine=numero_semaine,
            statut=statut,
            date_debut=date_debut,
            date_fin=date_fin,
            page=page,
            page_size=page_size,
        )
        result = self._list_feuille_uc.execute(dto)
        return {
            "items": [self._feuille_to_dict(f) for f in result.items],
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
        }

    # ===== Vues (FDH-01) =====

    def get_vue_chantiers(
        self, semaine_debut: date, chantier_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """Retourne la vue par chantiers (enrichie par le Use Case)."""
        result = self._vue_semaine_uc.get_vue_chantiers(semaine_debut, chantier_ids)

        # Conversion DTO → dict (les DTOs sont déjà enrichis par le Use Case)
        return [
            {
                "chantier_id": v.chantier_id,
                "chantier_nom": v.chantier_nom,
                "chantier_couleur": v.chantier_couleur,
                "total_heures": v.total_heures,
                "total_heures_decimal": v.total_heures_decimal,
                "pointages_par_jour": {
                    jour: [
                        {
                            "pointage_id": p.pointage_id,
                            "utilisateur_id": p.utilisateur_id,
                            "utilisateur_nom": p.utilisateur_nom,
                            "heures_normales": p.heures_normales,
                            "heures_supplementaires": p.heures_supplementaires,
                            "total_heures": p.total_heures,
                            "statut": p.statut,
                        }
                        for p in pointages
                    ]
                    for jour, pointages in v.pointages_par_jour.items()
                },
                "total_par_jour": v.total_par_jour,
            }
            for v in result
        ]

    def get_vue_compagnons(
        self, semaine_debut: date, utilisateur_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """Retourne la vue par compagnons (enrichie par le Use Case)."""
        result = self._vue_semaine_uc.get_vue_compagnons(semaine_debut, utilisateur_ids)

        # Conversion DTO → dict (les DTOs sont déjà enrichis par le Use Case)
        return [
            {
                "utilisateur_id": v.utilisateur_id,
                "utilisateur_nom": v.utilisateur_nom,
                "total_heures": v.total_heures,
                "total_heures_decimal": v.total_heures_decimal,
                "chantiers": [
                    {
                        "chantier_id": c.chantier_id,
                        "chantier_nom": c.chantier_nom,
                        "chantier_couleur": c.chantier_couleur,
                        "total_heures": c.total_heures,
                        "pointages_par_jour": {
                            jour: [
                                {
                                    "id": p.id,
                                    "utilisateur_id": p.utilisateur_id,
                                    "chantier_id": p.chantier_id,
                                    "date_pointage": p.date_pointage,
                                    "heures_normales": p.heures_normales,
                                    "heures_supplementaires": p.heures_supplementaires,
                                    "total_heures": p.total_heures,
                                    "statut": p.statut,
                                    "is_editable": p.is_editable,
                                    "commentaire": p.commentaire,
                                }
                                for p in pointages_list
                            ]
                            for jour, pointages_list in c.pointages_par_jour.items()
                        },
                    }
                    for c in v.chantiers
                ],
                "totaux_par_jour": v.totaux_par_jour,
            }
            for v in result
        ]

    # ===== Planning Integration (FDH-10) =====

    def bulk_create_from_planning(
        self,
        utilisateur_id: int,
        semaine_debut: date,
        affectations: List[Dict[str, Any]],
        created_by: int,
    ) -> List[Dict[str, Any]]:
        """Crée des pointages depuis les affectations du planning."""
        dto = BulkCreatePointageDTO(
            utilisateur_id=utilisateur_id,
            semaine_debut=semaine_debut,
            affectations=[
                AffectationSourceDTO(
                    affectation_id=a["affectation_id"],
                    chantier_id=a["chantier_id"],
                    date_affectation=a["date_affectation"],
                    heures_prevues=a["heures_prevues"],
                )
                for a in affectations
            ],
        )
        result = self._bulk_create_uc.execute(dto, created_by)
        return [self._pointage_to_dict(p) for p in result]

    # ===== Variables de paie (FDH-13) =====

    def create_variable_paie(
        self,
        pointage_id: int,
        type_variable: str,
        valeur: float,
        date_application: date,
        commentaire: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Crée une variable de paie."""
        from decimal import Decimal

        dto = CreateVariablePaieDTO(
            pointage_id=pointage_id,
            type_variable=type_variable,
            valeur=Decimal(str(valeur)),
            date_application=date_application,
            commentaire=commentaire,
        )
        result = self._create_variable_uc.execute(dto)
        return {
            "id": result.id,
            "pointage_id": result.pointage_id,
            "type_variable": result.type_variable,
            "type_variable_libelle": result.type_variable_libelle,
            "valeur": result.valeur,
            "date_application": result.date_application.isoformat(),
            "commentaire": result.commentaire,
            "created_at": result.created_at.isoformat(),
        }

    # ===== Export (FDH-03, FDH-17, FDH-19) =====

    def export_feuilles_heures(
        self,
        format_export: str,
        date_debut: date,
        date_fin: date,
        utilisateur_ids: List[int] = None,
        chantier_ids: List[int] = None,
        inclure_variables_paie: bool = True,
        inclure_signatures: bool = False,
        exported_by: int = None,
    ) -> Dict[str, Any]:
        """Exporte les feuilles d'heures."""
        dto = ExportFeuilleHeuresDTO(
            format_export=FormatExport(format_export),
            date_debut=date_debut,
            date_fin=date_fin,
            utilisateur_ids=utilisateur_ids,
            chantier_ids=chantier_ids,
            inclure_variables_paie=inclure_variables_paie,
            inclure_signatures=inclure_signatures,
        )
        result = self._export_uc.execute(dto, exported_by)
        return {
            "success": result.success,
            "format_export": result.format_export,
            "filename": result.filename,
            "file_content": result.file_content,  # bytes
            "error_message": result.error_message,
            "records_count": result.records_count,
            "exported_at": result.exported_at.isoformat(),
        }

    def generate_feuille_route(
        self, utilisateur_id: int, semaine_debut: date
    ) -> Dict[str, Any]:
        """Génère une feuille de route (FDH-19)."""
        result = self._export_uc.generate_feuille_route(utilisateur_id, semaine_debut)
        return {
            "utilisateur_id": result.utilisateur_id,
            "utilisateur_nom": result.utilisateur_nom,
            "semaine": result.semaine,
            "total_heures": result.total_heures,
            "chantiers": [
                {
                    "chantier_id": c.chantier_id,
                    "chantier_nom": c.chantier_nom,
                    "adresse": c.adresse,
                    "jours": c.jours,
                    "heures_par_jour": c.heures_par_jour,
                    "total_heures": c.total_heures,
                }
                for c in result.chantiers
            ],
            "generated_at": result.generated_at.isoformat(),
        }

    # ===== Statistiques (FDH-14, FDH-15) =====

    def get_jauge_avancement(
        self,
        utilisateur_id: int,
        semaine_debut: date,
        heures_planifiees: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Retourne la jauge d'avancement (FDH-14)."""
        result = self._jauge_uc.execute(utilisateur_id, semaine_debut, heures_planifiees)
        return {
            "utilisateur_id": result.utilisateur_id,
            "semaine": result.semaine,
            "heures_planifiees": result.heures_planifiees,
            "heures_realisees": result.heures_realisees,
            "taux_completion": result.taux_completion,
            "status": result.status,
        }

    def compare_equipes(
        self,
        semaine_debut: date,
        heures_planifiees_par_chantier: Dict[int, float] = None,
    ) -> Dict[str, Any]:
        """Compare les équipes (FDH-15)."""
        result = self._compare_uc.execute(semaine_debut, heures_planifiees_par_chantier)
        return {
            "semaine": result.semaine,
            "equipes": [
                {
                    "chantier_id": e.chantier_id,
                    "chantier_nom": e.chantier_nom,
                    "total_heures_planifiees": e.total_heures_planifiees,
                    "total_heures_realisees": e.total_heures_realisees,
                    "taux_completion": e.taux_completion,
                    "nombre_utilisateurs": e.nombre_utilisateurs,
                }
                for e in result.equipes
            ],
            "ecarts_detectes": [
                {
                    "type_ecart": ec.type_ecart,
                    "chantier_id": ec.chantier_id,
                    "chantier_nom": ec.chantier_nom,
                    "heures_planifiees": ec.heures_planifiees,
                    "heures_realisees": ec.heures_realisees,
                    "ecart_heures": ec.ecart_heures,
                    "ecart_pourcentage": ec.ecart_pourcentage,
                }
                for ec in result.ecarts_detectes
            ],
        }

    # ===== Helpers =====

    def _pointage_to_dict(self, dto) -> Dict[str, Any]:
        """Convertit un PointageDTO en dictionnaire."""
        return {
            "id": dto.id,
            "utilisateur_id": dto.utilisateur_id,
            "chantier_id": dto.chantier_id,
            "date_pointage": dto.date_pointage.isoformat(),
            "heures_normales": dto.heures_normales,
            "heures_supplementaires": dto.heures_supplementaires,
            "total_heures": dto.total_heures,
            "total_heures_decimal": dto.total_heures_decimal,
            "statut": dto.statut,
            "commentaire": dto.commentaire,
            "signature_utilisateur": dto.signature_utilisateur,
            "signature_date": dto.signature_date.isoformat() if dto.signature_date else None,
            "validateur_id": dto.validateur_id,
            "validation_date": (
                dto.validation_date.isoformat() if dto.validation_date else None
            ),
            "motif_rejet": dto.motif_rejet,
            "affectation_id": dto.affectation_id,
            "created_by": dto.created_by,
            "created_at": dto.created_at.isoformat(),
            "updated_at": dto.updated_at.isoformat(),
            "utilisateur_nom": dto.utilisateur_nom,
            "chantier_nom": dto.chantier_nom,
            "chantier_couleur": dto.chantier_couleur,
        }

    def _feuille_to_dict(self, dto) -> Dict[str, Any]:
        """Convertit un FeuilleHeuresDTO en dictionnaire."""
        return {
            "id": dto.id,
            "utilisateur_id": dto.utilisateur_id,
            "semaine_debut": dto.semaine_debut.isoformat(),
            "semaine_fin": dto.semaine_fin.isoformat(),
            "annee": dto.annee,
            "numero_semaine": dto.numero_semaine,
            "label_semaine": dto.label_semaine,
            "statut_global": dto.statut_global,
            "total_heures_normales": dto.total_heures_normales,
            "total_heures_supplementaires": dto.total_heures_supplementaires,
            "total_heures": dto.total_heures,
            "total_heures_decimal": dto.total_heures_decimal,
            "commentaire_global": dto.commentaire_global,
            "is_complete": dto.is_complete,
            "is_all_validated": dto.is_all_validated,
            "created_at": dto.created_at.isoformat(),
            "updated_at": dto.updated_at.isoformat(),
            "utilisateur_nom": dto.utilisateur_nom,
            "pointages": [
                {
                    "id": p.id,
                    "chantier_id": p.chantier_id,
                    "chantier_nom": p.chantier_nom,
                    "chantier_couleur": p.chantier_couleur,
                    "date_pointage": p.date_pointage.isoformat(),
                    "jour_semaine": p.jour_semaine,
                    "heures_normales": p.heures_normales,
                    "heures_supplementaires": p.heures_supplementaires,
                    "total_heures": p.total_heures,
                    "statut": p.statut,
                    "is_editable": p.is_editable,
                }
                for p in dto.pointages
            ],
            "variables_paie": [
                {
                    "type_variable": v.type_variable,
                    "type_variable_libelle": v.type_variable_libelle,
                    "total": v.total,
                }
                for v in dto.variables_paie
            ],
            "totaux_par_jour": dto.totaux_par_jour,
            "totaux_par_chantier": {
                str(k): v for k, v in dto.totaux_par_chantier.items()
            },
        }

    # === Phase 2 GAPs ===

    def bulk_validate_pointages(
        self, pointage_ids: List[int], validateur_id: int
    ) -> Dict[str, Any]:
        """
        Valide plusieurs pointages en une seule opération (GAP-FDH-004).

        Args:
            pointage_ids: Liste des IDs de pointages à valider.
            validateur_id: ID du validateur.

        Returns:
            Dictionnaire avec les résultats détaillés.
        """
        dto = BulkValidatePointagesDTO(
            pointage_ids=pointage_ids, validateur_id=validateur_id
        )
        result = self._bulk_validate_uc.execute(dto)

        return {
            "validated": result.validated,
            "failed": [
                {"pointage_id": f.pointage_id, "error": f.error} for f in result.failed
            ],
            "total_count": result.total_count,
            "success_count": result.success_count,
            "failure_count": result.failure_count,
        }

    def generate_monthly_recap(
        self, utilisateur_id: int, year: int, month: int, export_pdf: bool = False
    ) -> Dict[str, Any]:
        """
        Génère un récapitulatif mensuel (GAP-FDH-008).

        Args:
            utilisateur_id: ID de l'utilisateur.
            year: Année.
            month: Mois.
            export_pdf: True pour générer un PDF.

        Returns:
            Dictionnaire avec le récapitulatif complet.
        """
        dto = GenerateMonthlyRecapDTO(
            utilisateur_id=utilisateur_id, year=year, month=month, export_pdf=export_pdf
        )
        result = self._monthly_recap_uc.execute(dto)

        return {
            "utilisateur_id": result.utilisateur_id,
            "utilisateur_nom": result.utilisateur_nom,
            "year": result.year,
            "month": result.month,
            "month_label": result.month_label,
            "weekly_summaries": [
                {
                    "semaine_debut": ws.semaine_debut.isoformat(),
                    "numero_semaine": ws.numero_semaine,
                    "heures_normales": ws.heures_normales,
                    "heures_supplementaires": ws.heures_supplementaires,
                    "total_heures": ws.total_heures,
                    "heures_normales_decimal": ws.heures_normales_decimal,
                    "heures_supplementaires_decimal": ws.heures_supplementaires_decimal,
                    "total_heures_decimal": ws.total_heures_decimal,
                    "statut": ws.statut,
                }
                for ws in result.weekly_summaries
            ],
            "heures_normales_total": result.heures_normales_total,
            "heures_supplementaires_total": result.heures_supplementaires_total,
            "total_heures_month": result.total_heures_month,
            "heures_normales_total_decimal": result.heures_normales_total_decimal,
            "heures_supplementaires_total_decimal": result.heures_supplementaires_total_decimal,
            "total_heures_month_decimal": result.total_heures_month_decimal,
            "variables_paie": [
                {
                    "type_variable": vp.type_variable,
                    "type_variable_libelle": vp.type_variable_libelle,
                    "nombre_occurrences": vp.nombre_occurrences,
                    "valeur_unitaire": str(vp.valeur_unitaire)
                    if vp.valeur_unitaire
                    else None,
                    "montant_total": str(vp.montant_total),
                }
                for vp in result.variables_paie
            ],
            "variables_paie_total": str(result.variables_paie_total),
            "absences": [
                {
                    "type_absence": a.type_absence,
                    "type_absence_libelle": a.type_absence_libelle,
                    "nombre_jours": a.nombre_jours,
                    "total_heures": a.total_heures,
                    "total_heures_decimal": a.total_heures_decimal,
                }
                for a in result.absences
            ],
            "all_validated": result.all_validated,
            "pdf_path": result.pdf_path,
        }

    def lock_monthly_period(
        self, year: int, month: int, locked_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verrouille une période de paie (GAP-FDH-009).

        Args:
            year: Année.
            month: Mois.
            locked_by: ID de l'utilisateur (None si auto).

        Returns:
            Dictionnaire avec le résultat du verrouillage.
        """
        dto = LockMonthlyPeriodDTO(year=year, month=month)
        result = self._lock_period_uc.execute(
            dto, auto_locked=(locked_by is None), locked_by=locked_by
        )

        return {
            "year": result.year,
            "month": result.month,
            "lockdown_date": result.lockdown_date.isoformat(),
            "success": result.success,
            "message": result.message,
            "notified_users": result.notified_users,
        }
