"""Tests d'integration avec donnees realistes BTP gros oeuvre.

Chantier: Residence Les Cedres - R+3, 24 logements, 2 400 m2 SHAB
Prix de vente: 1 200 000 EUR HT
Budget: 1 080 000 EUR
Marge cible: 10%
Duree previsionnelle: 10 mois

Snapshot financier a M+6 (avancement 70%):
- CA HT (situation #3): 840 000 EUR
- Achats factures: 370 000 EUR
- Cout MO: 138 000 EUR (230k x 60%)
- Cout materiel: 42 000 EUR (70k x 60%)
- Total engage: 455 000 EUR
- Cout de revient complet: 550 000 EUR

Decomposition par lot:
- TF-01 Terrassement/Fondations: 120 000 EUR
- GO-01 Gros oeuvre beton: 380 000 EUR
- MAC-01 Maconnerie: 130 000 EUR
- ST-01 Sous-traitance etancheite: 80 000 EUR (autoliquidation TVA)
- MO-01 Main d'oeuvre: 230 000 EUR
- MAT-01 Materiel location: 70 000 EUR
- FG-01 Frais generaux repartis: 70 000 EUR
Total: 1 080 000 EUR
"""

import pytest
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from unittest.mock import Mock, MagicMock, patch

from modules.financier.domain.entities import (
    Achat,
    Budget,
    LotBudgetaire,
    SituationTravaux,
    FactureClient,
)
from modules.financier.domain.repositories import (
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    SituationRepository,
    CoutMainOeuvreRepository,
    CoutMaterielRepository,
    AlerteRepository,
    AvenantRepository,
    FactureRepository,
)
from modules.financier.domain.value_objects import StatutAchat, UniteMesure
from modules.financier.domain.value_objects.type_achat import TypeAchat
from modules.financier.application.use_cases.dashboard_use_cases import (
    GetDashboardFinancierUseCase,
)
from modules.financier.application.use_cases.consolidation_use_cases import (
    GetVueConsolideeFinancesUseCase,
)
from modules.financier.application.use_cases.pnl_use_cases import (
    GetPnLChantierUseCase,
)
from modules.financier.application.use_cases.bilan_cloture_use_cases import (
    GetBilanClotureUseCase,
)
from modules.financier.application.use_cases.suggestions_use_cases import (
    GetSuggestionsFinancieresUseCase,
)
from modules.financier.application.use_cases.budget_use_cases import (
    BudgetNotFoundError,
)
from shared.application.ports.chantier_info_port import (
    ChantierInfoPort,
    ChantierInfoDTO,
)
from shared.domain.calcul_financier import (
    calculer_marge_chantier,
    calculer_quote_part_frais_generaux,
    arrondir_pct,
    arrondir_montant,
    calculer_tva,
    COEFF_FRAIS_GENERAUX,
)


# ===========================================================================
# Fixture de base : Residence Les Cedres
# ===========================================================================

class LesCedresBaseFixture:
    """Donnees de base du chantier Les Cedres pour tous les tests.

    Chantier gros oeuvre R+3, 24 logements.
    Snapshot a M+6 (avancement 70%).
    """

    # -- Identifiants -------------------------------------------------------
    CHANTIER_ID = 100
    BUDGET_ID = 1

    # -- Donnees financieres ------------------------------------------------
    PRIX_VENTE_HT = Decimal("1200000")
    BUDGET_PREVISIONNEL = Decimal("1080000")
    DUREE_PREVUE_MOIS = 10
    RETENUE_GARANTIE_PCT = Decimal("5")

    # -- Situation M+6 (70% avancement) ------------------------------------
    CA_HT_M6 = Decimal("840000")

    # -- Achats a M+6 ------------------------------------------------------
    # STATUTS_ENGAGES = VALIDE + COMMANDE + LIVRE + FACTURE
    # STATUTS_REALISES = FACTURE uniquement
    TOTAL_ENGAGE = Decimal("455000")  # 180k+95k+45k+35k+60k+25k+15k
    TOTAL_REALISE_ACHATS = Decimal("370000")  # 180k+95k+35k+60k (FACTURE)

    # -- Couts MO et materiel a M+6 (60% de la duree prevue) ---------------
    COUT_MO = Decimal("138000")  # 230k x 60%
    COUT_MATERIEL = Decimal("42000")  # 70k x 60%

    # -- Derives -----------------------------------------------------------
    TOTAL_REALISE_COMPLET = TOTAL_REALISE_ACHATS + COUT_MO + COUT_MATERIEL  # 550 000

    # -- Budget lots --------------------------------------------------------
    LOTS = [
        {"id": 1, "code": "TF-01", "libelle": "Terrassement/Fondations",
         "quantite": Decimal("1"), "prix_unitaire": Decimal("120000")},
        {"id": 2, "code": "GO-01", "libelle": "Gros oeuvre beton",
         "quantite": Decimal("1"), "prix_unitaire": Decimal("380000")},
        {"id": 3, "code": "MAC-01", "libelle": "Maconnerie",
         "quantite": Decimal("1"), "prix_unitaire": Decimal("130000")},
        {"id": 4, "code": "ST-01", "libelle": "Sous-traitance etancheite",
         "quantite": Decimal("1"), "prix_unitaire": Decimal("80000")},
        {"id": 5, "code": "MO-01", "libelle": "Main d'oeuvre",
         "quantite": Decimal("1"), "prix_unitaire": Decimal("230000")},
        {"id": 6, "code": "MAT-01", "libelle": "Materiel location",
         "quantite": Decimal("1"), "prix_unitaire": Decimal("70000")},
        {"id": 7, "code": "FG-01", "libelle": "Frais generaux repartis",
         "quantite": Decimal("1"), "prix_unitaire": Decimal("70000")},
    ]

    # -- KPI attendus a M+6 ------------------------------------------------
    # Debourse sec = achats + MO + materiel = 550 000 EUR
    DEBOURSE_SEC_M6 = TOTAL_REALISE_ACHATS + COUT_MO + COUT_MATERIEL  # 550 000
    # Quote-part FG = debourse_sec * COEFF_FRAIS_GENERAUX / 100
    # = 550 000 * 19 / 100 = 104 500.00 EUR
    QUOTE_PART_FG = calculer_quote_part_frais_generaux(DEBOURSE_SEC_M6)
    # Marge sans FG = (840k - 550k) / 840k * 100 = 34.52%
    MARGE_SANS_FG = calculer_marge_chantier(
        ca_ht=CA_HT_M6,
        cout_achats=TOTAL_REALISE_ACHATS,
        cout_mo=COUT_MO,
        cout_materiel=COUT_MATERIEL,
    )
    # Marge avec FG = (840k - 654 500) / 840k * 100 = 22.08%
    MARGE_AVEC_FG = calculer_marge_chantier(
        ca_ht=CA_HT_M6,
        cout_achats=TOTAL_REALISE_ACHATS,
        cout_mo=COUT_MO,
        cout_materiel=COUT_MATERIEL,
        quote_part_frais_generaux=QUOTE_PART_FG,
    )

    @classmethod
    def make_budget(cls) -> Budget:
        """Cree le Budget du chantier Les Cedres."""
        return Budget(
            id=cls.BUDGET_ID,
            chantier_id=cls.CHANTIER_ID,
            montant_initial_ht=cls.BUDGET_PREVISIONNEL,
            montant_avenants_ht=Decimal("0"),
            retenue_garantie_pct=cls.RETENUE_GARANTIE_PCT,
            created_at=datetime(2025, 5, 1),
        )

    @classmethod
    def make_situation_m6(cls) -> SituationTravaux:
        """Cree la situation de travaux #3 (M+6, 70%)."""
        return SituationTravaux(
            id=3,
            chantier_id=cls.CHANTIER_ID,
            budget_id=cls.BUDGET_ID,
            numero="SIT-2025-03",
            periode_debut=date(2025, 9, 1),
            periode_fin=date(2025, 10, 31),
            montant_cumule_precedent_ht=Decimal("540000"),
            montant_periode_ht=Decimal("300000"),
            montant_cumule_ht=cls.CA_HT_M6,
            retenue_garantie_pct=cls.RETENUE_GARANTIE_PCT,
            taux_tva=Decimal("20.00"),
            statut="emise",
            created_at=datetime(2025, 11, 1),
        )

    @classmethod
    def make_lots(cls) -> list:
        """Cree les lots budgetaires du chantier."""
        lots = []
        for lot_data in cls.LOTS:
            lots.append(LotBudgetaire(
                id=lot_data["id"],
                budget_id=cls.BUDGET_ID,
                code_lot=lot_data["code"],
                libelle=lot_data["libelle"],
                quantite_prevue=lot_data["quantite"],
                prix_unitaire_ht=lot_data["prix_unitaire"],
                created_at=datetime(2025, 5, 1),
            ))
        return lots

    @classmethod
    def make_achats_m6(cls) -> list:
        """Cree les 7 achats realistes du chantier a M+6.

        Chaque achat a des quantites et prix unitaires BTP realistes.
        """
        now = datetime(2025, 11, 1)
        return [
            Achat(
                id=1,
                chantier_id=cls.CHANTIER_ID,
                lot_budgetaire_id=2,  # GO-01
                type_achat=TypeAchat.MATERIAU,
                libelle="Beton B25 pret a l'emploi",
                quantite=Decimal("400"),
                unite=UniteMesure.M3,
                prix_unitaire_ht=Decimal("450"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.FACTURE,
                created_at=now,
            ),
            Achat(
                id=2,
                chantier_id=cls.CHANTIER_ID,
                lot_budgetaire_id=2,  # GO-01
                type_achat=TypeAchat.MATERIAU,
                libelle="Acier HA Fe500",
                quantite=Decimal("95"),
                unite=UniteMesure.T,
                prix_unitaire_ht=Decimal("1000"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.FACTURE,
                created_at=now,
            ),
            Achat(
                id=3,
                chantier_id=cls.CHANTIER_ID,
                lot_budgetaire_id=2,  # GO-01
                type_achat=TypeAchat.MATERIEL,
                libelle="Coffrage metallique (location+achat)",
                quantite=Decimal("900"),
                unite=UniteMesure.M2,
                prix_unitaire_ht=Decimal("50"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.COMMANDE,
                created_at=now,
            ),
            Achat(
                id=4,
                chantier_id=cls.CHANTIER_ID,
                lot_budgetaire_id=3,  # MAC-01
                type_achat=TypeAchat.MATERIAU,
                libelle="Agglos creux 20x20x50",
                quantite=Decimal("7000"),
                unite=UniteMesure.U,
                prix_unitaire_ht=Decimal("5"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.FACTURE,
                created_at=now,
            ),
            Achat(
                id=5,
                chantier_id=cls.CHANTIER_ID,
                lot_budgetaire_id=4,  # ST-01
                type_achat=TypeAchat.SOUS_TRAITANCE,
                libelle="Etancheite toiture terrasse - sous-traitance",
                quantite=Decimal("600"),
                unite=UniteMesure.M2,
                prix_unitaire_ht=Decimal("100"),
                taux_tva=Decimal("0"),  # Autoliquidation CGI art. 283-2 nonies
                statut=StatutAchat.FACTURE,
                created_at=now,
            ),
            Achat(
                id=6,
                chantier_id=cls.CHANTIER_ID,
                lot_budgetaire_id=3,  # MAC-01
                type_achat=TypeAchat.MATERIAU,
                libelle="Ciment CEM II 32.5 R",
                quantite=Decimal("500"),
                unite=UniteMesure.T,
                prix_unitaire_ht=Decimal("50"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.LIVRE,
                created_at=now,
            ),
            Achat(
                id=7,
                chantier_id=cls.CHANTIER_ID,
                lot_budgetaire_id=3,  # MAC-01
                type_achat=TypeAchat.MATERIAU,
                libelle="Enduit monocouche facade",
                quantite=Decimal("300"),
                unite=UniteMesure.M2,
                prix_unitaire_ht=Decimal("50"),
                taux_tva=Decimal("20"),
                statut=StatutAchat.VALIDE,
                created_at=now,
            ),
        ]

    @classmethod
    def make_facture_m6(cls) -> FactureClient:
        """Cree une facture client correspondant a la situation #3."""
        tva, ttc, retenue, net = FactureClient.calculer_montants(
            montant_ht=cls.CA_HT_M6,
            taux_tva=Decimal("20"),
            retenue_garantie_pct=cls.RETENUE_GARANTIE_PCT,
        )
        return FactureClient(
            id=1,
            chantier_id=cls.CHANTIER_ID,
            situation_id=3,
            numero_facture="FAC-2025-03",
            type_facture="situation",
            montant_ht=cls.CA_HT_M6,
            taux_tva=Decimal("20.00"),
            montant_tva=tva,
            montant_ttc=ttc,
            retenue_garantie_montant=retenue,
            montant_net=net,
            statut="emise",
            created_at=datetime(2025, 11, 5),
        )


# ===========================================================================
# Helpers pour les mocks
# ===========================================================================

def _make_dashboard_mocks(fixture_cls=LesCedresBaseFixture):
    """Cree les mocks pour le dashboard use case.

    Returns:
        Tuple (use_case, mocks_dict) pour acceder aux mocks si besoin.
    """
    budget_repo = Mock(spec=BudgetRepository)
    lot_repo = Mock(spec=LotBudgetaireRepository)
    achat_repo = Mock(spec=AchatRepository)
    situation_repo = Mock(spec=SituationRepository)
    cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
    cout_materiel_repo = Mock(spec=CoutMaterielRepository)

    # Budget
    budget_repo.find_by_chantier_id.return_value = fixture_cls.make_budget()

    # Achats: somme_by_chantier est appele 2 fois (engage puis realise)
    achat_repo.somme_by_chantier.side_effect = [
        fixture_cls.TOTAL_ENGAGE,
        fixture_cls.TOTAL_REALISE_ACHATS,
    ]
    achats = fixture_cls.make_achats_m6()
    achat_repo.find_by_chantier.return_value = achats[:5]

    # Lots
    lots = fixture_cls.make_lots()
    lot_repo.find_by_budget_id.return_value = lots
    # somme_by_lot est appele 2 fois par lot (engage, realise) : 7 lots x 2 = 14 appels
    lot_engage_realise = []
    for _ in lots:
        lot_engage_realise.append(Decimal("0"))  # engage par lot (simplifie)
        lot_engage_realise.append(Decimal("0"))  # realise par lot (simplifie)
    achat_repo.somme_by_lot.side_effect = lot_engage_realise

    # Situation
    situation_repo.find_derniere_situation.return_value = fixture_cls.make_situation_m6()

    # Couts MO et materiel
    cout_mo_repo.calculer_cout_chantier.return_value = fixture_cls.COUT_MO
    cout_materiel_repo.calculer_cout_chantier.return_value = fixture_cls.COUT_MATERIEL

    use_case = GetDashboardFinancierUseCase(
        budget_repository=budget_repo,
        lot_repository=lot_repo,
        achat_repository=achat_repo,
        situation_repository=situation_repo,
        cout_mo_repository=cout_mo_repo,
        cout_materiel_repository=cout_materiel_repo,
    )

    return use_case, {
        "budget_repo": budget_repo,
        "lot_repo": lot_repo,
        "achat_repo": achat_repo,
        "situation_repo": situation_repo,
        "cout_mo_repo": cout_mo_repo,
        "cout_materiel_repo": cout_materiel_repo,
    }


def _make_consolidation_mocks(fixture_cls=LesCedresBaseFixture):
    """Cree les mocks pour le consolidation use case (chantier unique)."""
    budget_repo = Mock(spec=BudgetRepository)
    lot_repo = Mock(spec=LotBudgetaireRepository)
    achat_repo = Mock(spec=AchatRepository)
    alerte_repo = Mock(spec=AlerteRepository)
    situation_repo = Mock(spec=SituationRepository)
    cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
    cout_materiel_repo = Mock(spec=CoutMaterielRepository)
    chantier_info_port = Mock(spec=ChantierInfoPort)

    # ChantierInfo
    chantier_info = ChantierInfoDTO(
        id=fixture_cls.CHANTIER_ID,
        nom="Residence Les Cedres",
        statut="en_cours",
    )
    chantier_info_port.get_chantiers_info_batch.return_value = {
        fixture_cls.CHANTIER_ID: chantier_info,
    }

    # Budget
    budget_repo.find_by_chantier_id.return_value = fixture_cls.make_budget()

    # Achats
    achat_repo.somme_by_chantier.side_effect = [
        fixture_cls.TOTAL_ENGAGE,
        fixture_cls.TOTAL_REALISE_ACHATS,
    ]

    # Situation
    situation_repo.find_derniere_situation.return_value = fixture_cls.make_situation_m6()

    # Couts
    cout_mo_repo.calculer_cout_chantier.return_value = fixture_cls.COUT_MO
    cout_materiel_repo.calculer_cout_chantier.return_value = fixture_cls.COUT_MATERIEL

    # Alertes
    alerte_repo.find_non_acquittees.return_value = []

    use_case = GetVueConsolideeFinancesUseCase(
        budget_repository=budget_repo,
        lot_repository=lot_repo,
        achat_repository=achat_repo,
        alerte_repository=alerte_repo,
        chantier_info_port=chantier_info_port,
        situation_repository=situation_repo,
        cout_mo_repository=cout_mo_repo,
        cout_materiel_repository=cout_materiel_repo,
    )

    return use_case, {
        "budget_repo": budget_repo,
        "achat_repo": achat_repo,
        "situation_repo": situation_repo,
        "cout_mo_repo": cout_mo_repo,
        "cout_materiel_repo": cout_materiel_repo,
        "alerte_repo": alerte_repo,
        "chantier_info_port": chantier_info_port,
    }


# ===========================================================================
# Tests: Coherence Dashboard / Consolidation (meme chantier, meme marge)
# ===========================================================================

class TestLesCedresCoherenceDashboardConsolidation:
    """Verifie que le dashboard et la consolidation calculent la meme marge
    pour le chantier Les Cedres, a partir des memes donnees.

    C'est le test le plus important : les 2 vues doivent etre coherentes
    car elles utilisent toutes les deux calculer_marge_chantier.
    """

    def test_marge_dashboard_egale_marge_consolidation(self):
        """La marge BTP du dashboard = la marge de la consolidation.

        Les deux use cases utilisent calculer_marge_chantier avec les memes
        parametres (CA, cout_achats, cout_mo, cout_materiel, quote_part_FG).
        """
        F = LesCedresBaseFixture

        # -- Dashboard
        dashboard_uc, _ = _make_dashboard_mocks()
        dashboard_result = dashboard_uc.execute(
            chantier_id=F.CHANTIER_ID,
        )
        marge_dashboard = dashboard_result.kpi.marge_estimee

        # -- Consolidation
        conso_uc, _ = _make_consolidation_mocks()
        conso_result = conso_uc.execute(
            user_accessible_chantier_ids=[F.CHANTIER_ID],
        )
        assert len(conso_result.chantiers) == 1
        marge_consolidation = conso_result.chantiers[0].marge_estimee_pct

        # Les deux marges doivent etre identiques
        assert marge_dashboard == marge_consolidation, (
            f"Dashboard ({marge_dashboard}) != Consolidation ({marge_consolidation})"
        )

        # Et elles doivent correspondre a la valeur attendue (avec FG)
        assert marge_dashboard == str(F.MARGE_AVEC_FG), (
            f"Marge {marge_dashboard} != attendu {F.MARGE_AVEC_FG}"
        )


# ===========================================================================
# Tests: Dashboard financier
# ===========================================================================

class TestLesCedresDashboard:
    """Tests du dashboard financier avec les donnees Les Cedres a M+6."""

    def test_kpi_montants_de_base(self):
        """KPI: montant revise, engage, realise, reste a depenser."""
        F = LesCedresBaseFixture
        uc, _ = _make_dashboard_mocks()

        result = uc.execute(
            chantier_id=F.CHANTIER_ID,
        )

        assert result.kpi.montant_revise_ht == str(F.BUDGET_PREVISIONNEL)
        assert result.kpi.total_engage == str(F.TOTAL_ENGAGE)
        # Dashboard total_realise inclut MO + materiel
        assert result.kpi.total_realise == str(F.TOTAL_REALISE_COMPLET)
        # Reste a depenser inclut MO + materiel (negatif = depassement)
        reste = F.BUDGET_PREVISIONNEL - F.TOTAL_ENGAGE - F.COUT_MO - F.COUT_MATERIEL
        assert result.kpi.reste_a_depenser == str(reste)

    def test_total_realise_inclut_mo_et_materiel(self):
        """Le total realise du dashboard = achats factures + MO + materiel.

        C'est une verification essentielle: 370k + 138k + 42k = 550k.
        """
        F = LesCedresBaseFixture
        uc, _ = _make_dashboard_mocks()

        result = uc.execute(chantier_id=F.CHANTIER_ID)

        total_realise = Decimal(result.kpi.total_realise)
        assert total_realise == F.TOTAL_REALISE_COMPLET
        assert total_realise == Decimal("550000")
        # Verification composante par composante
        assert total_realise == (
            F.TOTAL_REALISE_ACHATS + F.COUT_MO + F.COUT_MATERIEL
        )

    def test_kpi_pourcentages(self):
        """Pourcentages engage, realise, reste par rapport au budget."""
        F = LesCedresBaseFixture
        uc, _ = _make_dashboard_mocks()

        result = uc.execute(chantier_id=F.CHANTIER_ID)

        # pct_engage = 455000 / 1080000 * 100 = 42.13%
        expected_pct_engage = arrondir_pct(
            F.TOTAL_ENGAGE / F.BUDGET_PREVISIONNEL * Decimal("100")
        )
        assert result.kpi.pct_engage == str(expected_pct_engage)

        # pct_realise = 550000 / 1080000 * 100 = 50.93%
        expected_pct_realise = arrondir_pct(
            F.TOTAL_REALISE_COMPLET / F.BUDGET_PREVISIONNEL * Decimal("100")
        )
        assert result.kpi.pct_realise == str(expected_pct_realise)

    def test_marge_btp_avec_frais_generaux(self):
        """Marge BTP avec frais generaux (coefficient unique sur debourse sec).

        Debourse sec = 370k + 138k + 42k = 550 000 EUR
        Quote-part FG = 550 000 * 19% = 104 500.00 EUR
        Cout revient = 550 000 + 104 500 = 654 500 EUR
        Marge = (840k - 654 500) / 840k * 100 = 22.08%
        """
        F = LesCedresBaseFixture
        uc, _ = _make_dashboard_mocks()

        result = uc.execute(
            chantier_id=F.CHANTIER_ID,
        )

        assert result.kpi.marge_estimee == str(F.MARGE_AVEC_FG)
        assert result.kpi.marge_statut == "calculee"

    def test_repartition_par_lot_7_lots(self):
        """Les 7 lots budgetaires sont retournes dans la repartition."""
        F = LesCedresBaseFixture
        uc, _ = _make_dashboard_mocks()

        result = uc.execute(chantier_id=F.CHANTIER_ID)

        assert len(result.repartition_par_lot) == 7
        codes = [lot.code_lot for lot in result.repartition_par_lot]
        assert "TF-01" in codes
        assert "GO-01" in codes
        assert "ST-01" in codes
        assert "FG-01" in codes


# ===========================================================================
# Tests: Consolidation
# ===========================================================================

class TestLesCedresConsolidation:
    """Tests de la vue consolidee avec le chantier Les Cedres."""

    def test_kpi_globaux_chantier_unique(self):
        """KPI globaux quand il n'y a qu'un seul chantier."""
        F = LesCedresBaseFixture
        uc, _ = _make_consolidation_mocks()

        result = uc.execute(
            user_accessible_chantier_ids=[F.CHANTIER_ID],
        )

        assert result.kpi_globaux.nb_chantiers == 1
        assert result.kpi_globaux.total_budget_revise == str(
            arrondir_montant(F.BUDGET_PREVISIONNEL)
        )

    def test_consolidation_marge_statut_calculee(self):
        """La marge a le statut 'calculee' quand une situation existe."""
        F = LesCedresBaseFixture
        uc, _ = _make_consolidation_mocks()

        result = uc.execute(
            user_accessible_chantier_ids=[F.CHANTIER_ID],
        )

        chantier_summary = result.chantiers[0]
        assert chantier_summary.marge_statut == "calculee"
        assert chantier_summary.marge_estimee_pct is not None

    def test_consolidation_statut_financier_ok(self):
        """Chantier a 42% d'engagement => statut 'ok' (< 80%)."""
        F = LesCedresBaseFixture
        uc, _ = _make_consolidation_mocks()

        result = uc.execute(
            user_accessible_chantier_ids=[F.CHANTIER_ID],
        )

        chantier_summary = result.chantiers[0]
        assert chantier_summary.statut == "ok"


# ===========================================================================
# Tests: P&L (Profit & Loss)
# ===========================================================================

class TestLesCedresPnL:
    """Tests du P&L avec les donnees Les Cedres."""

    def test_pnl_marge_brute_avec_frais_generaux(self):
        """P&L: marge brute avec FG (coefficient unique sur debourse sec).

        CA (factures) = 840 000 EUR
        Debourse sec = achats(370k) + MO(138k) + materiel(42k) = 550 000 EUR
        Quote-part FG = 550 000 * 19% = 104 500 EUR
        Total couts = 654 500 EUR
        Marge = (840k - 654 500) / 840k * 100 = 22.08%
        """
        F = LesCedresBaseFixture

        budget_repo = Mock(spec=BudgetRepository)
        achat_repo = Mock(spec=AchatRepository)
        facture_repo = Mock(spec=FactureRepository)
        cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        cout_materiel_repo = Mock(spec=CoutMaterielRepository)

        budget_repo.find_by_chantier_id.return_value = F.make_budget()
        achat_repo.somme_by_chantier.return_value = F.TOTAL_REALISE_ACHATS
        facture_repo.find_by_chantier_id.return_value = [F.make_facture_m6()]
        cout_mo_repo.calculer_cout_chantier.return_value = F.COUT_MO
        cout_materiel_repo.calculer_cout_chantier.return_value = F.COUT_MATERIEL

        uc = GetPnLChantierUseCase(
            facture_repository=facture_repo,
            achat_repository=achat_repo,
            budget_repository=budget_repo,
            cout_mo_repository=cout_mo_repo,
            cout_materiel_repository=cout_materiel_repo,
        )
        result = uc.execute(chantier_id=F.CHANTIER_ID)

        assert result.chiffre_affaires_ht == str(F.CA_HT_M6)
        assert result.cout_achats == str(F.TOTAL_REALISE_ACHATS)
        assert result.cout_main_oeuvre == str(F.COUT_MO)
        assert result.cout_materiel == str(F.COUT_MATERIEL)
        # Marge brute avec FG coefficient unique
        assert result.marge_brute_pct == str(F.MARGE_AVEC_FG)

    def test_pnl_marge_brute_ht(self):
        """P&L: marge brute HT = CA - total couts (avec FG).

        Total couts = 550 000 + 104 500 = 654 500 EUR
        Marge brute HT = 840 000 - 654 500 = 185 500 EUR
        """
        F = LesCedresBaseFixture

        budget_repo = Mock(spec=BudgetRepository)
        achat_repo = Mock(spec=AchatRepository)
        facture_repo = Mock(spec=FactureRepository)
        cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        cout_materiel_repo = Mock(spec=CoutMaterielRepository)

        budget_repo.find_by_chantier_id.return_value = F.make_budget()
        achat_repo.somme_by_chantier.return_value = F.TOTAL_REALISE_ACHATS
        facture_repo.find_by_chantier_id.return_value = [F.make_facture_m6()]
        cout_mo_repo.calculer_cout_chantier.return_value = F.COUT_MO
        cout_materiel_repo.calculer_cout_chantier.return_value = F.COUT_MATERIEL

        uc = GetPnLChantierUseCase(
            facture_repository=facture_repo,
            achat_repository=achat_repo,
            budget_repository=budget_repo,
            cout_mo_repository=cout_mo_repo,
            cout_materiel_repository=cout_materiel_repo,
        )
        result = uc.execute(chantier_id=F.CHANTIER_ID)

        expected_marge_ht = F.CA_HT_M6 - (F.TOTAL_REALISE_COMPLET + F.QUOTE_PART_FG)
        assert result.marge_brute_ht == str(expected_marge_ht)
        assert Decimal(result.marge_brute_ht) == Decimal("185500.00")


# ===========================================================================
# Tests: Bilan de cloture
# ===========================================================================

class TestLesCedresBilanCloture:
    """Tests du bilan de cloture avec les donnees Les Cedres."""

    def test_bilan_cloture_montants(self):
        """Bilan de cloture: verifie les montants de base."""
        F = LesCedresBaseFixture

        budget_repo = Mock(spec=BudgetRepository)
        lot_repo = Mock(spec=LotBudgetaireRepository)
        achat_repo = Mock(spec=AchatRepository)
        avenant_repo = Mock(spec=AvenantRepository)
        situation_repo = Mock(spec=SituationRepository)
        chantier_info_port = Mock(spec=ChantierInfoPort)
        facture_repo = Mock(spec=FactureRepository)
        cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        cout_materiel_repo = Mock(spec=CoutMaterielRepository)

        # Chantier en cours (pas ferme)
        chantier_info_port.get_chantier_info.return_value = ChantierInfoDTO(
            id=F.CHANTIER_ID, nom="Residence Les Cedres", statut="en_cours",
        )

        budget_repo.find_by_chantier_id.return_value = F.make_budget()
        avenant_repo.count_by_budget_id.return_value = 0

        achat_repo.somme_by_chantier.side_effect = [
            F.TOTAL_ENGAGE,
            F.TOTAL_REALISE_ACHATS,
        ]
        achat_repo.count_by_chantier.return_value = 7

        cout_mo_repo.calculer_cout_chantier.return_value = F.COUT_MO
        cout_materiel_repo.calculer_cout_chantier.return_value = F.COUT_MATERIEL

        # Facture pour le CA reel
        facture_repo.find_by_chantier_id.return_value = [F.make_facture_m6()]

        situation_repo.count_by_chantier_id.return_value = 3
        situation_repo.find_derniere_situation.return_value = F.make_situation_m6()

        # Lots pour ecarts
        lot_repo.find_by_budget_id.return_value = F.make_lots()
        achat_repo.somme_by_lot.return_value = Decimal("0")

        uc = GetBilanClotureUseCase(
            budget_repository=budget_repo,
            lot_repository=lot_repo,
            achat_repository=achat_repo,
            avenant_repository=avenant_repo,
            situation_repository=situation_repo,
            chantier_info_port=chantier_info_port,
            facture_repository=facture_repo,
            cout_mo_repository=cout_mo_repo,
            cout_materiel_repository=cout_materiel_repo,
        )
        result = uc.execute(
            chantier_id=F.CHANTIER_ID,
        )

        assert result.budget_initial_ht == str(F.BUDGET_PREVISIONNEL)
        assert result.budget_revise_ht == str(F.BUDGET_PREVISIONNEL)
        assert result.total_engage_ht == str(F.TOTAL_ENGAGE)
        # BK-05: total_realise_ht inclut MO + materiel dans le DTO
        assert result.total_realise_ht == str(F.TOTAL_REALISE_COMPLET)
        assert result.nb_achats == 7
        assert result.nb_situations == 3
        assert result.est_definitif is False  # pas ferme

    def test_bilan_cloture_marge_avec_fg(self):
        """Bilan de cloture: marge avec frais generaux (coefficient unique)."""
        F = LesCedresBaseFixture

        budget_repo = Mock(spec=BudgetRepository)
        lot_repo = Mock(spec=LotBudgetaireRepository)
        achat_repo = Mock(spec=AchatRepository)
        avenant_repo = Mock(spec=AvenantRepository)
        situation_repo = Mock(spec=SituationRepository)
        chantier_info_port = Mock(spec=ChantierInfoPort)
        facture_repo = Mock(spec=FactureRepository)
        cout_mo_repo = Mock(spec=CoutMainOeuvreRepository)
        cout_materiel_repo = Mock(spec=CoutMaterielRepository)

        chantier_info_port.get_chantier_info.return_value = ChantierInfoDTO(
            id=F.CHANTIER_ID, nom="Residence Les Cedres", statut="en_cours",
        )

        budget_repo.find_by_chantier_id.return_value = F.make_budget()
        avenant_repo.count_by_budget_id.return_value = 0

        achat_repo.somme_by_chantier.side_effect = [
            F.TOTAL_ENGAGE,
            F.TOTAL_REALISE_ACHATS,
        ]
        achat_repo.count_by_chantier.return_value = 7

        cout_mo_repo.calculer_cout_chantier.return_value = F.COUT_MO
        cout_materiel_repo.calculer_cout_chantier.return_value = F.COUT_MATERIEL

        facture_repo.find_by_chantier_id.return_value = [F.make_facture_m6()]

        situation_repo.count_by_chantier_id.return_value = 3
        situation_repo.find_derniere_situation.return_value = F.make_situation_m6()
        lot_repo.find_by_budget_id.return_value = []

        uc = GetBilanClotureUseCase(
            budget_repository=budget_repo,
            lot_repository=lot_repo,
            achat_repository=achat_repo,
            avenant_repository=avenant_repo,
            situation_repository=situation_repo,
            chantier_info_port=chantier_info_port,
            facture_repository=facture_repo,
            cout_mo_repository=cout_mo_repo,
            cout_materiel_repository=cout_materiel_repo,
        )
        result = uc.execute(
            chantier_id=F.CHANTIER_ID,
        )

        assert result.marge_finale_pct == str(F.MARGE_AVEC_FG)


# ===========================================================================
# Tests: Suggestions financieres et burn rate
# ===========================================================================

class TestLesCedresSuggestionsBurnRate:
    """Tests des suggestions et indicateurs predictifs (burn rate).

    Note: le code actuel utilise duree_prevue_mois=12 par defaut
    (pas les 10 mois prevus pour Les Cedres). Le burn rate compare
    le rythme de depense au budget moyen mensuel sur 12 mois.
    """

    def _make_suggestions_uc(self):
        """Cree le use case suggestions avec mocks Les Cedres."""
        F = LesCedresBaseFixture

        budget_repo = Mock(spec=BudgetRepository)
        achat_repo = Mock(spec=AchatRepository)
        lot_repo = Mock(spec=LotBudgetaireRepository)
        alerte_repo = Mock(spec=AlerteRepository)

        # Budget avec created_at fixe pour calcul burn rate deterministe.
        # On utilise le budget tel quel ; le nombre de mois ecoules
        # depend de date.today() au moment du test.
        budget = F.make_budget()
        budget_repo.find_by_chantier_id.return_value = budget

        # Achats: somme_by_chantier appele 2 fois (engage, realise)
        achat_repo.somme_by_chantier.side_effect = [
            F.TOTAL_ENGAGE,
            F.TOTAL_REALISE_ACHATS,
        ]

        # Lots
        lot_repo.find_by_budget_id.return_value = F.make_lots()
        # somme_by_lot pour chaque lot (check ecart > 30%)
        achat_repo.somme_by_lot.return_value = Decimal("0")

        # Alertes
        alerte_repo.find_non_acquittees.return_value = []
        alerte_repo.find_by_chantier_id.return_value = []

        uc = GetSuggestionsFinancieresUseCase(
            budget_repository=budget_repo,
            achat_repository=achat_repo,
            lot_repository=lot_repo,
            alerte_repository=alerte_repo,
        )

        return uc, budget

    def test_burn_rate_sous_budget(self):
        """Burn rate < budget moyen => pas d'alerte ALERT_BURN_RATE.

        A M+6, les depenses sont sous le rythme budgetaire (bon signe).
        """
        F = LesCedresBaseFixture
        uc, budget = self._make_suggestions_uc()

        result = uc.execute(chantier_id=F.CHANTIER_ID)

        # Verifier qu'il n'y a PAS d'alerte ALERT_BURN_RATE
        types_suggestions = [s.type for s in result.suggestions]
        assert "ALERT_BURN_RATE" not in types_suggestions, (
            "Le burn rate est sous le budget, pas d'alerte attendue"
        )

    def test_indicateurs_predictifs_burn_rate(self):
        """Les indicateurs predictifs calculent le burn rate correctement.

        Le burn rate = total_realise / nb_mois_ecoules.
        Le budget moyen = montant_revise / 12 (duree par defaut).
        L'ecart doit etre negatif (on depense moins que prevu).
        """
        F = LesCedresBaseFixture
        uc, budget = self._make_suggestions_uc()

        result = uc.execute(chantier_id=F.CHANTIER_ID)
        indicateurs = result.indicateurs

        # Le budget moyen est fixe : 1 080 000 / 12 = 90 000 EUR/mois
        assert indicateurs.budget_moyen_mensuel == "90000.00"

        # Le burn rate depend du nombre de mois ecoules
        # Calcul dynamique pour que le test passe quelle que soit la date
        today = date.today()
        debut = budget.created_at.date()
        nb_mois = max(
            1,
            (today.year - debut.year) * 12 + (today.month - debut.month) + 1,
        )
        expected_burn_rate = F.TOTAL_REALISE_ACHATS / Decimal(str(nb_mois))
        assert indicateurs.burn_rate_mensuel == str(
            expected_burn_rate.quantize(Decimal("0.01"))
        )

        # L'ecart doit etre negatif (on depense moins que prevu)
        ecart = Decimal(indicateurs.ecart_burn_rate_pct)
        assert ecart < Decimal("0"), (
            f"Ecart burn rate devrait etre negatif, got {ecart}"
        )

    def test_suggestion_create_situation_pour_gros_budget(self):
        """Suggestion INFO 'creer une situation' car budget > 100k."""
        F = LesCedresBaseFixture
        uc, _ = self._make_suggestions_uc()

        result = uc.execute(chantier_id=F.CHANTIER_ID)

        types_suggestions = [s.type for s in result.suggestions]
        assert "CREATE_SITUATION" in types_suggestions

    def test_pas_alerte_avenant_budget_sain(self):
        """Pas d'alerte CREATE_AVENANT car engage < 90% et marge > 10%."""
        F = LesCedresBaseFixture
        uc, _ = self._make_suggestions_uc()

        result = uc.execute(chantier_id=F.CHANTIER_ID)

        types_suggestions = [s.type for s in result.suggestions]
        assert "CREATE_AVENANT" not in types_suggestions


# ===========================================================================
# Tests: Entites - Autoliquidation TVA
# ===========================================================================

class TestLesCedresAutoliquidationTVA:
    """Tests de l'autoliquidation TVA pour les sous-traitants.

    CGI art. 283-2 nonies : le donneur d'ordre (Greg Construction)
    autoliquide la TVA pour les achats de sous-traitance.
    L'achat est enregistre avec taux_tva = 0%.
    """

    def test_achat_sous_traitant_tva_zero(self):
        """Un achat sous-traitance avec TVA 0% est valide."""
        achat = Achat(
            id=5,
            chantier_id=LesCedresBaseFixture.CHANTIER_ID,
            lot_budgetaire_id=4,  # ST-01
            type_achat=TypeAchat.SOUS_TRAITANCE,
            libelle="Etancheite toiture terrasse - sous-traitance",
            quantite=Decimal("600"),
            unite=UniteMesure.M2,
            prix_unitaire_ht=Decimal("100"),
            taux_tva=Decimal("0"),  # Autoliquidation
            statut=StatutAchat.FACTURE,
        )

        # TVA = 0 EUR
        assert achat.montant_tva == Decimal("0")
        # Total HT = 600 x 100 = 60 000 EUR
        assert achat.total_ht == Decimal("60000")
        # TTC = HT + TVA = 60 000 + 0 = 60 000 EUR
        assert achat.total_ttc == Decimal("60000")

    def test_achat_sous_traitant_vs_achat_normal(self):
        """Compare un achat autoliquide (TVA 0%) vs un achat normal (TVA 20%).

        Le total HT est le meme, mais le TTC differe.
        """
        base_args = dict(
            chantier_id=LesCedresBaseFixture.CHANTIER_ID,
            libelle="Prestation",
            quantite=Decimal("1"),
            prix_unitaire_ht=Decimal("60000"),
            statut=StatutAchat.FACTURE,
        )

        # Sous-traitant : autoliquidation
        st = Achat(id=10, taux_tva=Decimal("0"), **base_args)
        # Normal : TVA 20%
        normal = Achat(id=11, taux_tva=Decimal("20"), **base_args)

        assert st.total_ht == normal.total_ht == Decimal("60000")
        assert st.montant_tva == Decimal("0")
        assert normal.montant_tva == Decimal("12000")
        assert st.total_ttc == Decimal("60000")
        assert normal.total_ttc == Decimal("72000")

    def test_achat_etancheite_les_cedres(self):
        """Verifie l'achat d'etancheite specifique du chantier Les Cedres."""
        achats = LesCedresBaseFixture.make_achats_m6()
        etancheite = [a for a in achats if a.type_achat == TypeAchat.SOUS_TRAITANCE]

        assert len(etancheite) == 1
        achat = etancheite[0]
        assert achat.taux_tva == Decimal("0")
        assert achat.total_ht == Decimal("60000")
        assert achat.montant_tva == Decimal("0")
        assert achat.statut == StatutAchat.FACTURE


# ===========================================================================
# Tests: Retenue de garantie sur HT
# ===========================================================================

class TestLesCedresRetenueGarantie:
    """Tests de la retenue de garantie.

    Loi 71-584 : la retenue de garantie s'applique sur le montant HT,
    pas sur le TTC. Taux standard : 5%.
    """

    def test_retenue_garantie_situation_m6(self):
        """Retenue de garantie sur la situation #3 (840 000 EUR HT).

        Retenue = 840 000 x 5% = 42 000 EUR
        """
        situation = LesCedresBaseFixture.make_situation_m6()

        assert situation.montant_retenue_garantie == Decimal("42000.00")
        assert situation.retenue_garantie_pct == Decimal("5.00")

    def test_retenue_garantie_sur_ht_pas_ttc(self):
        """La retenue est calculee sur le HT (loi 71-584), pas le TTC.

        HT = 840 000 EUR
        TVA = 168 000 EUR
        TTC = 1 008 000 EUR
        Retenue (sur HT) = 42 000 EUR (et non 50 400 sur TTC)
        """
        situation = LesCedresBaseFixture.make_situation_m6()

        retenue_sur_ht = arrondir_montant(
            situation.montant_cumule_ht * situation.retenue_garantie_pct / Decimal("100")
        )
        retenue_sur_ttc = arrondir_montant(
            situation.montant_ttc * situation.retenue_garantie_pct / Decimal("100")
        )

        assert situation.montant_retenue_garantie == retenue_sur_ht
        assert retenue_sur_ht == Decimal("42000.00")
        # La retenue sur TTC serait differente (50 400)
        assert retenue_sur_ttc == Decimal("50400.00")
        assert retenue_sur_ht != retenue_sur_ttc

    def test_facture_client_retenue_garantie(self):
        """Retenue de garantie sur la facture client (meme logique).

        montant_ht = 840 000 EUR
        retenue = 42 000 EUR (5% du HT)
        montant_net = TTC - retenue = 1 008 000 - 42 000 = 966 000 EUR
        """
        tva, ttc, retenue, net = FactureClient.calculer_montants(
            montant_ht=Decimal("840000"),
            taux_tva=Decimal("20"),
            retenue_garantie_pct=Decimal("5"),
        )

        assert tva == Decimal("168000.00")
        assert ttc == Decimal("1008000.00")
        assert retenue == Decimal("42000.00")
        assert net == Decimal("966000.00")

    def test_montant_net_situation_m6(self):
        """Montant net de la situation = TTC - retenue."""
        situation = LesCedresBaseFixture.make_situation_m6()

        expected_tva = calculer_tva(Decimal("840000"), Decimal("20"))
        expected_ttc = Decimal("840000") + expected_tva
        expected_net = expected_ttc - situation.montant_retenue_garantie

        assert situation.montant_tva == expected_tva
        assert situation.montant_ttc == expected_ttc
        assert situation.montant_net == expected_net


# ===========================================================================
# Tests: Marge cible ~10%
# ===========================================================================

class TestLesCedresMargeCible:
    """Tests de la marge cible 10%.

    Le chantier Les Cedres est concu pour une marge de 10% :
    Prix de vente (1.2M) - Budget (1.08M) = 120k de marge
    120k / 1.2M = 10%

    A M+6 (avancement partiel), la marge reelle est differente
    car les couts ne sont pas lineaires vs le CA facture.
    """

    def test_marge_cible_design_10_pourcent(self):
        """La marge de conception = (prix_vente - budget) / prix_vente = 10%."""
        F = LesCedresBaseFixture

        marge_design = (
            (F.PRIX_VENTE_HT - F.BUDGET_PREVISIONNEL) / F.PRIX_VENTE_HT
        ) * Decimal("100")

        assert arrondir_pct(marge_design) == Decimal("10.00")

    def test_marge_finale_si_execution_parfaite_sans_fg(self):
        """Si le chantier s'execute parfaitement (couts = budget), marge = 10%.

        Simulation fin de chantier:
        - CA = 1 200 000 EUR (prix de vente integral)
        - Cout de revient total = 1 080 000 EUR (= budget)
        - Marge = (1.2M - 1.08M) / 1.2M = 10.00%

        Pour ce test, on decompose le budget en:
        - Achats factures: 710 000 EUR (TF+GO+MAC+ST = 120k+380k+130k+80k)
        - MO: 230 000 EUR
        - Materiel: 70 000 EUR
        - FG budget: 70 000 EUR (inclus dans achats ici pour atteindre 1.08M)
        Total achats = 710k + 70k = 780k
        Marge sans quote_part = (1.2M - (780k + 230k + 70k)) / 1.2M = 10%
        """
        F = LesCedresBaseFixture

        # Budget lots hors MO et materiel = 120k+380k+130k+80k+70k(FG) = 780k
        achats_finaux = Decimal("780000")
        mo_final = Decimal("230000")
        materiel_final = Decimal("70000")
        ca_final = F.PRIX_VENTE_HT

        # Verification: achats + MO + materiel = budget
        assert achats_finaux + mo_final + materiel_final == F.BUDGET_PREVISIONNEL

        marge = calculer_marge_chantier(
            ca_ht=ca_final,
            cout_achats=achats_finaux,
            cout_mo=mo_final,
            cout_materiel=materiel_final,
        )

        assert marge == Decimal("10.00")

    def test_marge_finale_si_execution_parfaite_avec_fg(self):
        """Avec FG (coefficient unique 19%), la marge est inferieure a 10%.

        Debourse sec final = 780k + 230k + 70k = 1 080 000 EUR
        Quote-part FG = 1 080 000 * 19% = 205 200 EUR
        Cout total = 1 080 000 + 205 200 = 1 285 200 EUR
        Marge = (1.2M - 1 285 200) / 1.2M = -7.10% (deficitaire!)

        C'est normal : les 70k de FG budgetes ne couvrent pas les 205k
        de frais generaux reels. Greg Construction doit ajuster son prix
        de vente ou reduire les couts fixes pour rester rentable.
        """
        F = LesCedresBaseFixture

        achats_finaux = Decimal("780000")
        mo_final = Decimal("230000")
        materiel_final = Decimal("70000")
        ca_final = F.PRIX_VENTE_HT

        debourse_sec_final = achats_finaux + mo_final + materiel_final
        quote_part = calculer_quote_part_frais_generaux(debourse_sec_final)

        marge = calculer_marge_chantier(
            ca_ht=ca_final,
            cout_achats=achats_finaux,
            cout_mo=mo_final,
            cout_materiel=materiel_final,
            quote_part_frais_generaux=quote_part,
        )

        # La marge est negative car les FG reels (205k) > FG budgetes (70k)
        assert marge is not None
        assert Decimal(str(marge)) < Decimal("10")

    def test_marge_m6_intermediaire_sans_fg(self):
        """A M+6, la marge sans FG est de 34.52%.

        Plus elevee que la cible car le CA facture est proportionnellement
        plus avance que les couts (les couts sont en retard sur le CA).
        """
        F = LesCedresBaseFixture

        marge = F.MARGE_SANS_FG
        assert marge == Decimal("34.52")
        # Verification manuelle
        assert marge == arrondir_pct(
            (F.CA_HT_M6 - F.TOTAL_REALISE_COMPLET) / F.CA_HT_M6 * Decimal("100")
        )

    def test_marge_m6_intermediaire_avec_fg(self):
        """A M+6, la marge avec FG est de 22.08%.

        Toujours superieure a la cible de 10% grace au decalage
        couts/CA, mais reduite par les frais generaux (coeff 19%).
        """
        F = LesCedresBaseFixture

        marge = F.MARGE_AVEC_FG
        assert marge == Decimal("22.08")
        assert F.QUOTE_PART_FG == Decimal("104500.00")


# ===========================================================================
# Tests: Coherence entre calculs partages
# ===========================================================================

class TestLesCedresCoherenceCalculs:
    """Verifie que les calculs sont coherents entre les differents modules.

    Tous les use cases doivent utiliser calculer_marge_chantier
    (source unique de verite) pour le calcul de la marge.
    """

    def test_quote_part_fg_calcul(self):
        """Quote-part FG = debourse_sec * COEFF_FRAIS_GENERAUX / 100.

        550 000 * 19 / 100 = 104 500.00 EUR
        """
        F = LesCedresBaseFixture

        qp = calculer_quote_part_frais_generaux(F.DEBOURSE_SEC_M6)

        assert qp == Decimal("104500.00")

    def test_quote_part_fg_zero_si_debourse_zero(self):
        """Quote-part = 0 si debourse sec = 0."""
        qp = calculer_quote_part_frais_generaux(Decimal("0"))
        assert qp == Decimal("0")

    def test_cout_revient_complet_m6(self):
        """Cout de revient complet a M+6 avec FG.

        Achats factures (370k) + MO (138k) + materiel (42k) + FG (104 500)
        = 654 500.00 EUR
        """
        F = LesCedresBaseFixture

        cout_revient = (
            F.TOTAL_REALISE_ACHATS + F.COUT_MO + F.COUT_MATERIEL + F.QUOTE_PART_FG
        )

        assert cout_revient == Decimal("654500.00")

    def test_arrondi_round_half_up(self):
        """Verifie que l'arrondi ROUND_HALF_UP est bien utilise.

        PCG art. 120-2 : arrondi bancaire ROUND_HALF_UP.
        2.5 -> 3, 3.5 -> 4 (contrairement a ROUND_HALF_EVEN).
        """
        assert arrondir_montant(Decimal("2.5"), "1") == Decimal("3")
        assert arrondir_montant(Decimal("3.5"), "1") == Decimal("4")
        assert arrondir_pct(Decimal("34.525")) == Decimal("34.53")

    def test_tva_beton(self):
        """TVA sur l'achat de beton : 180 000 * 20% = 36 000 EUR."""
        achats = LesCedresBaseFixture.make_achats_m6()
        beton = achats[0]  # Beton B25

        assert beton.total_ht == Decimal("180000")
        assert beton.taux_tva == Decimal("20")
        assert beton.montant_tva == Decimal("36000.00")
        assert beton.total_ttc == Decimal("216000.00")

    def test_statuts_engages_corrects(self):
        """Verifie que les statuts engages du chantier sont corrects.

        VALIDE + COMMANDE + LIVRE + FACTURE = 15k + 45k + 25k + 370k = 455k
        """
        from modules.financier.domain.value_objects.statuts_financiers import (
            STATUTS_ENGAGES,
            STATUTS_REALISES,
        )

        achats = LesCedresBaseFixture.make_achats_m6()

        total_engage = sum(
            a.total_ht for a in achats if a.statut in STATUTS_ENGAGES
        )
        total_realise = sum(
            a.total_ht for a in achats if a.statut in STATUTS_REALISES
        )

        assert total_engage == Decimal("455000")
        assert total_realise == Decimal("395000")

    def test_statut_demande_exclu_des_engages(self):
        """Les achats en statut DEMANDE ne sont PAS engages.

        STATUTS_ENGAGES = [VALIDE, COMMANDE, LIVRE, FACTURE]
        DEMANDE est exclu intentionnellement.
        """
        from modules.financier.domain.value_objects.statuts_financiers import (
            STATUTS_ENGAGES,
        )

        assert StatutAchat.DEMANDE not in STATUTS_ENGAGES
