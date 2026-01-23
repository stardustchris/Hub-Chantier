"""Controller pour les formulaires."""

from datetime import date
from typing import Optional, List

from ...application.use_cases import (
    CreateTemplateUseCase,
    UpdateTemplateUseCase,
    DeleteTemplateUseCase,
    GetTemplateUseCase,
    ListTemplatesUseCase,
    CreateFormulaireUseCase,
    UpdateFormulaireUseCase,
    SubmitFormulaireUseCase,
    GetFormulaireUseCase,
    ListFormulairesUseCase,
    GetFormulaireHistoryUseCase,
    ExportFormulairePDFUseCase,
)
from ...application.dtos import (
    TemplateFormulaireDTO,
    ChampTemplateDTO,
    CreateTemplateDTO,
    UpdateTemplateDTO,
    FormulaireRempliDTO,
    CreateFormulaireDTO,
    UpdateFormulaireDTO,
    SubmitFormulaireDTO,
)
from ...application.use_cases.list_templates import ListTemplatesResult
from ...application.use_cases.list_formulaires import ListFormulairesResult
from ...application.use_cases.export_pdf import PDFContent


class FormulaireController:
    """
    Controller pour les operations sur les formulaires.

    Orchestre les use cases et gere les conversions de donnees.
    """

    def __init__(
        self,
        create_template_uc: CreateTemplateUseCase,
        update_template_uc: UpdateTemplateUseCase,
        delete_template_uc: DeleteTemplateUseCase,
        get_template_uc: GetTemplateUseCase,
        list_templates_uc: ListTemplatesUseCase,
        create_formulaire_uc: CreateFormulaireUseCase,
        update_formulaire_uc: UpdateFormulaireUseCase,
        submit_formulaire_uc: SubmitFormulaireUseCase,
        get_formulaire_uc: GetFormulaireUseCase,
        list_formulaires_uc: ListFormulairesUseCase,
        get_history_uc: GetFormulaireHistoryUseCase,
        export_pdf_uc: ExportFormulairePDFUseCase,
    ):
        """Initialise le controller avec les use cases."""
        self._create_template_uc = create_template_uc
        self._update_template_uc = update_template_uc
        self._delete_template_uc = delete_template_uc
        self._get_template_uc = get_template_uc
        self._list_templates_uc = list_templates_uc
        self._create_formulaire_uc = create_formulaire_uc
        self._update_formulaire_uc = update_formulaire_uc
        self._submit_formulaire_uc = submit_formulaire_uc
        self._get_formulaire_uc = get_formulaire_uc
        self._list_formulaires_uc = list_formulaires_uc
        self._get_history_uc = get_history_uc
        self._export_pdf_uc = export_pdf_uc

    # ===== TEMPLATE OPERATIONS =====

    def create_template(
        self,
        nom: str,
        categorie: str,
        description: Optional[str] = None,
        champs: Optional[List[dict]] = None,
        created_by: Optional[int] = None,
    ) -> TemplateFormulaireDTO:
        """Cree un template de formulaire (FOR-01)."""
        champs_dto = []
        if champs:
            for champ in champs:
                champs_dto.append(ChampTemplateDTO(
                    nom=champ["nom"],
                    label=champ["label"],
                    type_champ=champ["type_champ"],
                    obligatoire=champ.get("obligatoire", False),
                    ordre=champ.get("ordre", 0),
                    placeholder=champ.get("placeholder"),
                    options=champ.get("options", []),
                    valeur_defaut=champ.get("valeur_defaut"),
                    validation_regex=champ.get("validation_regex"),
                    min_value=champ.get("min_value"),
                    max_value=champ.get("max_value"),
                ))

        dto = CreateTemplateDTO(
            nom=nom,
            categorie=categorie,
            description=description,
            champs=champs_dto,
            created_by=created_by,
        )
        return self._create_template_uc.execute(dto)

    def update_template(
        self,
        template_id: int,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        categorie: Optional[str] = None,
        champs: Optional[List[dict]] = None,
        is_active: Optional[bool] = None,
        updated_by: Optional[int] = None,
    ) -> TemplateFormulaireDTO:
        """Met a jour un template de formulaire."""
        champs_dto = None
        if champs is not None:
            champs_dto = []
            for champ in champs:
                champs_dto.append(ChampTemplateDTO(
                    id=champ.get("id"),
                    nom=champ["nom"],
                    label=champ["label"],
                    type_champ=champ["type_champ"],
                    obligatoire=champ.get("obligatoire", False),
                    ordre=champ.get("ordre", 0),
                    placeholder=champ.get("placeholder"),
                    options=champ.get("options", []),
                    valeur_defaut=champ.get("valeur_defaut"),
                    validation_regex=champ.get("validation_regex"),
                    min_value=champ.get("min_value"),
                    max_value=champ.get("max_value"),
                ))

        dto = UpdateTemplateDTO(
            nom=nom,
            description=description,
            categorie=categorie,
            champs=champs_dto,
            is_active=is_active,
        )
        return self._update_template_uc.execute(template_id, dto, updated_by)

    def delete_template(
        self,
        template_id: int,
        deleted_by: Optional[int] = None,
    ) -> bool:
        """Supprime un template de formulaire."""
        return self._delete_template_uc.execute(template_id, deleted_by)

    def get_template(self, template_id: int) -> TemplateFormulaireDTO:
        """Recupere un template par ID."""
        return self._get_template_uc.execute(template_id)

    def list_templates(
        self,
        query: Optional[str] = None,
        categorie: Optional[str] = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> ListTemplatesResult:
        """Liste les templates avec filtres (FOR-01)."""
        return self._list_templates_uc.execute(
            query=query,
            categorie=categorie,
            active_only=active_only,
            skip=skip,
            limit=limit,
        )

    # ===== FORMULAIRE OPERATIONS =====

    def create_formulaire(
        self,
        template_id: int,
        chantier_id: int,
        user_id: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> FormulaireRempliDTO:
        """Cree un formulaire a remplir (FOR-11)."""
        dto = CreateFormulaireDTO(
            template_id=template_id,
            chantier_id=chantier_id,
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
        )
        return self._create_formulaire_uc.execute(dto)

    def update_formulaire(
        self,
        formulaire_id: int,
        champs: Optional[List[dict]] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> FormulaireRempliDTO:
        """Met a jour un formulaire."""
        dto = UpdateFormulaireDTO(
            champs=champs,
            latitude=latitude,
            longitude=longitude,
        )
        return self._update_formulaire_uc.execute(formulaire_id, dto)

    def add_photo(
        self,
        formulaire_id: int,
        url: str,
        nom_fichier: str,
        champ_nom: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> FormulaireRempliDTO:
        """Ajoute une photo au formulaire (FOR-04)."""
        return self._update_formulaire_uc.add_photo(
            formulaire_id=formulaire_id,
            url=url,
            nom_fichier=nom_fichier,
            champ_nom=champ_nom,
            latitude=latitude,
            longitude=longitude,
        )

    def add_signature(
        self,
        formulaire_id: int,
        signature_url: str,
        signature_nom: str,
    ) -> FormulaireRempliDTO:
        """Ajoute une signature au formulaire (FOR-05)."""
        return self._update_formulaire_uc.add_signature(
            formulaire_id=formulaire_id,
            signature_url=signature_url,
            signature_nom=signature_nom,
        )

    def submit_formulaire(
        self,
        formulaire_id: int,
        signature_url: Optional[str] = None,
        signature_nom: Optional[str] = None,
    ) -> FormulaireRempliDTO:
        """Soumet un formulaire (FOR-07)."""
        dto = SubmitFormulaireDTO(
            formulaire_id=formulaire_id,
            signature_url=signature_url,
            signature_nom=signature_nom,
        )
        return self._submit_formulaire_uc.execute(dto)

    def validate_formulaire(
        self,
        formulaire_id: int,
        valideur_id: int,
    ) -> FormulaireRempliDTO:
        """Valide un formulaire soumis."""
        return self._submit_formulaire_uc.validate(formulaire_id, valideur_id)

    def get_formulaire(self, formulaire_id: int) -> FormulaireRempliDTO:
        """Recupere un formulaire par ID."""
        return self._get_formulaire_uc.execute(formulaire_id)

    def list_formulaires(
        self,
        chantier_id: Optional[int] = None,
        template_id: Optional[int] = None,
        user_id: Optional[int] = None,
        statut: Optional[str] = None,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> ListFormulairesResult:
        """Liste les formulaires avec filtres."""
        return self._list_formulaires_uc.execute(
            chantier_id=chantier_id,
            template_id=template_id,
            user_id=user_id,
            statut=statut,
            date_debut=date_debut,
            date_fin=date_fin,
            skip=skip,
            limit=limit,
        )

    def list_formulaires_by_chantier(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FormulaireRempliDTO]:
        """Liste les formulaires d'un chantier (FOR-10)."""
        return self._list_formulaires_uc.execute_by_chantier(
            chantier_id, skip, limit
        )

    def get_formulaire_history(
        self,
        formulaire_id: int,
    ) -> List[FormulaireRempliDTO]:
        """Recupere l'historique d'un formulaire (FOR-08)."""
        return self._get_history_uc.execute(formulaire_id)

    def export_pdf(self, formulaire_id: int) -> PDFContent:
        """Exporte un formulaire en PDF (FOR-09)."""
        return self._export_pdf_uc.execute(formulaire_id)
