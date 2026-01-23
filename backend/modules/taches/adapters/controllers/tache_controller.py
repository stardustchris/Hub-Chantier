"""Controller Tache - Orchestration des use cases pour les taches."""

from typing import Optional, List, Callable
from dataclasses import asdict

from ...domain.repositories import (
    TacheRepository,
    TemplateModeleRepository,
    FeuilleTacheRepository,
)
from ...application import (
    # Use Cases
    CreateTacheUseCase,
    UpdateTacheUseCase,
    DeleteTacheUseCase,
    GetTacheUseCase,
    ListTachesUseCase,
    CompleteTacheUseCase,
    ReorderTachesUseCase,
    CreateTemplateUseCase,
    ListTemplatesUseCase,
    ImportTemplateUseCase,
    CreateFeuilleTacheUseCase,
    ValidateFeuilleTacheUseCase,
    ListFeuillesTachesUseCase,
    GetTacheStatsUseCase,
    ExportTachesPDFUseCase,
    # DTOs
    CreateTacheDTO,
    UpdateTacheDTO,
    CreateTemplateModeleDTO,
    SousTacheModeleDTO,
    CreateFeuilleTacheDTO,
    ValidateFeuilleTacheDTO,
)


class TacheController:
    """
    Controller pour la gestion des taches.

    Orchestre les use cases et transforme les donnees pour l'API.

    Attributes:
        tache_repo: Repository pour les taches.
        template_repo: Repository pour les templates.
        feuille_repo: Repository pour les feuilles de taches.
        event_publisher: Fonction pour publier les events.
    """

    def __init__(
        self,
        tache_repo: TacheRepository,
        template_repo: TemplateModeleRepository,
        feuille_repo: FeuilleTacheRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le controller.

        Args:
            tache_repo: Repository taches.
            template_repo: Repository templates.
            feuille_repo: Repository feuilles.
            event_publisher: Fonction pour publier les events.
        """
        self.tache_repo = tache_repo
        self.template_repo = template_repo
        self.feuille_repo = feuille_repo
        self.event_publisher = event_publisher

    # ==========================================================================
    # Taches
    # ==========================================================================

    def create_tache(
        self,
        chantier_id: int,
        titre: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        date_echeance: Optional[str] = None,
        unite_mesure: Optional[str] = None,
        quantite_estimee: Optional[float] = None,
        heures_estimees: Optional[float] = None,
    ) -> dict:
        """Cree une nouvelle tache (TAC-06, TAC-07)."""
        use_case = CreateTacheUseCase(
            tache_repo=self.tache_repo,
            event_publisher=self.event_publisher,
        )

        dto = CreateTacheDTO(
            chantier_id=chantier_id,
            titre=titre,
            description=description,
            parent_id=parent_id,
            date_echeance=date_echeance,
            unite_mesure=unite_mesure,
            quantite_estimee=quantite_estimee,
            heures_estimees=heures_estimees,
        )

        result = use_case.execute(dto)
        return asdict(result)

    def get_tache(self, tache_id: int, include_sous_taches: bool = True) -> dict:
        """Recupere une tache par ID."""
        use_case = GetTacheUseCase(tache_repo=self.tache_repo)
        result = use_case.execute(tache_id, include_sous_taches)
        return asdict(result)

    def update_tache(
        self,
        tache_id: int,
        titre: Optional[str] = None,
        description: Optional[str] = None,
        date_echeance: Optional[str] = None,
        unite_mesure: Optional[str] = None,
        quantite_estimee: Optional[float] = None,
        heures_estimees: Optional[float] = None,
        statut: Optional[str] = None,
        ordre: Optional[int] = None,
    ) -> dict:
        """Met a jour une tache."""
        use_case = UpdateTacheUseCase(
            tache_repo=self.tache_repo,
            event_publisher=self.event_publisher,
        )

        dto = UpdateTacheDTO(
            titre=titre,
            description=description,
            date_echeance=date_echeance,
            unite_mesure=unite_mesure,
            quantite_estimee=quantite_estimee,
            heures_estimees=heures_estimees,
            statut=statut,
            ordre=ordre,
        )

        result = use_case.execute(tache_id, dto)
        return asdict(result)

    def delete_tache(self, tache_id: int) -> bool:
        """Supprime une tache."""
        use_case = DeleteTacheUseCase(
            tache_repo=self.tache_repo,
            event_publisher=self.event_publisher,
        )
        return use_case.execute(tache_id)

    def list_taches(
        self,
        chantier_id: int,
        query: Optional[str] = None,
        statut: Optional[str] = None,
        page: int = 1,
        size: int = 50,
        include_sous_taches: bool = True,
    ) -> dict:
        """Liste les taches d'un chantier (TAC-01, TAC-14)."""
        use_case = ListTachesUseCase(tache_repo=self.tache_repo)
        result = use_case.execute(
            chantier_id=chantier_id,
            query=query,
            statut=statut,
            page=page,
            size=size,
            include_sous_taches=include_sous_taches,
        )
        return asdict(result)

    def complete_tache(self, tache_id: int, terminer: bool = True) -> dict:
        """Marque une tache comme terminee (TAC-13)."""
        use_case = CompleteTacheUseCase(
            tache_repo=self.tache_repo,
            event_publisher=self.event_publisher,
        )
        result = use_case.execute(tache_id, terminer)
        return asdict(result)

    def reorder_tache(self, tache_id: int, nouvel_ordre: int) -> dict:
        """Reordonne une tache (TAC-15)."""
        use_case = ReorderTachesUseCase(tache_repo=self.tache_repo)
        result = use_case.execute(tache_id, nouvel_ordre)
        return asdict(result)

    def reorder_taches_batch(self, ordres: List[dict]) -> List[dict]:
        """Reordonne plusieurs taches."""
        use_case = ReorderTachesUseCase(tache_repo=self.tache_repo)
        results = use_case.execute_batch(ordres)
        return [asdict(r) for r in results]

    def get_tache_stats(self, chantier_id: int) -> dict:
        """Obtient les statistiques des taches (TAC-20)."""
        use_case = GetTacheStatsUseCase(tache_repo=self.tache_repo)
        result = use_case.execute(chantier_id)
        return asdict(result)

    # ==========================================================================
    # Templates
    # ==========================================================================

    def create_template(
        self,
        nom: str,
        description: Optional[str] = None,
        categorie: Optional[str] = None,
        unite_mesure: Optional[str] = None,
        heures_estimees_defaut: Optional[float] = None,
        sous_taches: Optional[List[dict]] = None,
    ) -> dict:
        """Cree un nouveau template (TAC-04)."""
        use_case = CreateTemplateUseCase(template_repo=self.template_repo)

        st_dtos = []
        if sous_taches:
            for st in sous_taches:
                st_dtos.append(SousTacheModeleDTO(
                    titre=st.get("titre"),
                    description=st.get("description"),
                    ordre=st.get("ordre", 0),
                    unite_mesure=st.get("unite_mesure"),
                    heures_estimees_defaut=st.get("heures_estimees_defaut"),
                ))

        dto = CreateTemplateModeleDTO(
            nom=nom,
            description=description,
            categorie=categorie,
            unite_mesure=unite_mesure,
            heures_estimees_defaut=heures_estimees_defaut,
            sous_taches=st_dtos,
        )

        result = use_case.execute(dto)
        return asdict(result)

    def list_templates(
        self,
        query: Optional[str] = None,
        categorie: Optional[str] = None,
        active_only: bool = True,
        page: int = 1,
        size: int = 50,
    ) -> dict:
        """Liste les templates (TAC-04)."""
        use_case = ListTemplatesUseCase(template_repo=self.template_repo)
        result = use_case.execute(
            query=query,
            categorie=categorie,
            active_only=active_only,
            page=page,
            size=size,
        )
        return asdict(result)

    def import_template(self, template_id: int, chantier_id: int) -> List[dict]:
        """Importe un template dans un chantier (TAC-05)."""
        use_case = ImportTemplateUseCase(
            tache_repo=self.tache_repo,
            template_repo=self.template_repo,
            event_publisher=self.event_publisher,
        )
        results = use_case.execute(template_id, chantier_id)
        return [asdict(r) for r in results]

    # ==========================================================================
    # Feuilles de taches
    # ==========================================================================

    def create_feuille_tache(
        self,
        tache_id: int,
        utilisateur_id: int,
        chantier_id: int,
        date_travail: str,
        heures_travaillees: float = 0.0,
        quantite_realisee: float = 0.0,
        commentaire: Optional[str] = None,
    ) -> dict:
        """Cree une feuille de tache (TAC-18)."""
        use_case = CreateFeuilleTacheUseCase(
            feuille_repo=self.feuille_repo,
            tache_repo=self.tache_repo,
            event_publisher=self.event_publisher,
        )

        dto = CreateFeuilleTacheDTO(
            tache_id=tache_id,
            utilisateur_id=utilisateur_id,
            chantier_id=chantier_id,
            date_travail=date_travail,
            heures_travaillees=heures_travaillees,
            quantite_realisee=quantite_realisee,
            commentaire=commentaire,
        )

        result = use_case.execute(dto)
        return asdict(result)

    def validate_feuille_tache(
        self,
        feuille_id: int,
        validateur_id: int,
        valider: bool = True,
        motif_rejet: Optional[str] = None,
    ) -> dict:
        """Valide ou rejette une feuille de tache (TAC-19)."""
        use_case = ValidateFeuilleTacheUseCase(
            feuille_repo=self.feuille_repo,
            tache_repo=self.tache_repo,
            event_publisher=self.event_publisher,
        )

        dto = ValidateFeuilleTacheDTO(
            validateur_id=validateur_id,
            valider=valider,
            motif_rejet=motif_rejet,
        )

        result = use_case.execute(feuille_id, dto)
        return asdict(result)

    def list_feuilles_by_tache(
        self,
        tache_id: int,
        page: int = 1,
        size: int = 50,
    ) -> dict:
        """Liste les feuilles d'une tache."""
        use_case = ListFeuillesTachesUseCase(feuille_repo=self.feuille_repo)
        result = use_case.execute_by_tache(tache_id, page, size)
        return asdict(result)

    def list_feuilles_by_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        statut: Optional[str] = None,
        page: int = 1,
        size: int = 50,
    ) -> dict:
        """Liste les feuilles d'un chantier."""
        use_case = ListFeuillesTachesUseCase(feuille_repo=self.feuille_repo)
        result = use_case.execute_by_chantier(
            chantier_id, date_debut, date_fin, statut, page, size
        )
        return asdict(result)

    def list_feuilles_en_attente(
        self,
        chantier_id: Optional[int] = None,
        page: int = 1,
        size: int = 50,
    ) -> dict:
        """Liste les feuilles en attente de validation."""
        use_case = ListFeuillesTachesUseCase(feuille_repo=self.feuille_repo)
        result = use_case.execute_en_attente(chantier_id, page, size)
        return asdict(result)

    # ==========================================================================
    # Export PDF
    # ==========================================================================

    def export_pdf(
        self,
        chantier_id: int,
        include_completed: bool = True,
    ) -> tuple:
        """
        Exporte les taches d'un chantier en PDF (TAC-16).

        Args:
            chantier_id: ID du chantier.
            include_completed: Inclure les taches terminees.

        Returns:
            Tuple (pdf_bytes, chantier_nom).
        """
        # Recuperer le nom du chantier depuis une tache
        taches = self.tache_repo.find_by_chantier(chantier_id, limit=1)
        chantier_nom = f"chantier-{chantier_id}"
        if taches:
            # On utilise l'ID du chantier comme nom par defaut
            chantier_nom = f"chantier-{chantier_id}"

        use_case = ExportTachesPDFUseCase(tache_repo=self.tache_repo)
        pdf_bytes = use_case.execute(
            chantier_id=chantier_id,
            chantier_nom=chantier_nom,
            include_completed=include_completed,
        )
        return pdf_bytes, chantier_nom
