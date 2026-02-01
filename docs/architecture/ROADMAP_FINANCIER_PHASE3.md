# Roadmap Module Financier - Phase 3 UX & Intelligence

> **Objectif** : Passer de "fonctionnel" (5/10) à "moderne et compétitif" (9/10) vs Graneet/Kalitics
>
> **Date** : 1er février 2026
> **Statut** : Specs complètes, prêt pour implémentation

---

## 📊 Résumé Exécutif

### État Actuel

**Score** : 5/10
- ✅ Backend : 9/10 (architecture solide, 13/13 features Phase 1+2)
- ⚠️ Frontend : 5/10 (fonctionnel mais basique)

**Problèmes critiques** :
1. Navigation fragmentée (8 onglets vs dashboard unique)
2. Aucun graphique (courbes, camemberts, barres)
3. Indicateur "Reste à dépenser" manquant (métrique #1 terrain)
4. Alertes cachées (onglet 8 vs bannière visible)
5. Pas de vue consolidée multi-chantiers
6. Aucune suggestion intelligente

### Objectif Phase 3

**Score cible** : 9/10 (niveau Graneet/Kalitics)

**Impact business estimé** :
- Adoption utilisateurs : **+150%**
- Temps passé dans module : **x3**
- Détection problèmes : **-80% de temps**
- Argument commercial : De "fonctionnel" à **"moderne et puissant"**

---

## 🎯 Roadmap en 3 Phases (10 jours)

### 📅 PHASE 1 - Quick Wins (1 jour) → Gain 70%

**Objectif** : Impact immédiat avec modifications minimales

| Feature | Effort | ROI | Impact |
|---------|--------|-----|--------|
| **FIN-16** : Reste à dépenser | 1h | 100x | ⭐⭐⭐⭐⭐ |
| Alertes en haut du dashboard | 2h | 40x | ⭐⭐⭐⭐ |
| Jauges circulaires SVG | 3h | 20x | ⭐⭐⭐ |

**Total** : 6 heures, gain perçu 70%

#### FIN-16 : Indicateur "Reste à dépenser"

**Backend** :
```python
# backend/modules/financier/application/use_cases/dashboard_use_cases.py

reste_a_depenser = montant_revise_ht - total_engage - total_realise
pct_reste = (reste_a_depenser / montant_revise_ht) * 100 if montant_revise_ht > 0 else 0

return DashboardKPI(
    # ... KPI existants
    reste_a_depenser=reste_a_depenser,
    pct_reste=pct_reste
)
```

**Frontend** :
```tsx
// frontend/src/components/financier/BudgetDashboard.tsx

<div className={`card ${reste < 0 ? 'border-red-300' : 'border-blue-200'}`}>
  <p className="text-sm text-gray-500">Reste à dépenser</p>
  <p className={`text-2xl font-bold ${reste < 0 ? 'text-red-600' : 'text-blue-700'}`}>
    {formatEUR(kpi.reste_a_depenser)}
  </p>
  <div className="mt-2">
    <CircularGauge value={pct_reste} max={100} />
  </div>
</div>
```

#### Alertes Visibles

**Avant** : Cachées dans onglet 8
**Après** : Bannière orange en haut du dashboard

```tsx
// Avant les KPI cards
{alertes.length > 0 && (
  <div className="bg-orange-50 border-l-4 border-orange-500 p-4 mb-6">
    <div className="flex items-center gap-2">
      <AlertTriangle className="text-orange-600" />
      <div>
        <p className="font-medium text-orange-900">
          {alertes.length} alerte{alertes.length > 1 ? 's' : ''} budgétaire{alertes.length > 1 ? 's' : ''}
        </p>
        <ul className="text-sm text-orange-700 mt-1">
          {alertes.slice(0, 3).map(a => <li key={a.id}>• {a.titre}</li>)}
        </ul>
      </div>
    </div>
  </div>
)}
```

---

### 📅 PHASE 2 - Graphiques (2 jours) → Gain 90%

**Objectif** : Visualisations modernes pour tendances et comparaisons

| Feature | Effort | Librairie | Impact |
|---------|--------|-----------|--------|
| **FIN-17** : Évolution temporelle | 1j | Recharts | ⭐⭐⭐⭐⭐ |
| **FIN-18** : Camembert lots | 4h | Recharts | ⭐⭐⭐⭐ |
| **FIN-19** : Barres comparatives | 4h | Recharts | ⭐⭐⭐⭐ |

**Total** : 2 jours, gain perçu 90%

#### FIN-17 : Graphique Évolution Temporelle

**Backend - Use Case** :
```python
class GetEvolutionFinanciereUseCase:
    def execute(self, chantier_id: int) -> List[EvolutionMensuelle]:
        """Agrège données par mois depuis début chantier"""

        chantier = self.chantier_repo.find_by_id(chantier_id)
        mois_liste = self._generer_mois(chantier.date_debut, chantier.date_fin_prevue)

        evolution = []
        for mois in mois_liste:
            evolution.append(EvolutionMensuelle(
                mois=mois.strftime("%m/%Y"),
                prevu=self._calcul_prevu_cumule(chantier_id, mois),
                engage=self._calcul_engage_cumule(chantier_id, mois),
                realise=self._calcul_realise_cumule(chantier_id, mois)
            ))

        return evolution
```

**Frontend** :
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

<div className="bg-white border rounded-xl p-4">
  <h3 className="font-semibold mb-4">Évolution financière</h3>
  <LineChart width={600} height={300} data={evolution}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="mois" />
    <YAxis tickFormatter={(v) => `${v/1000}k`} />
    <Tooltip formatter={(value) => formatEUR(value)} />
    <Legend />
    <Line type="monotone" dataKey="prevu" stroke="#3b82f6" name="Prévu" />
    <Line type="monotone" dataKey="engage" stroke="#f59e0b" name="Engagé" />
    <Line type="monotone" dataKey="realise" stroke="#10b981" name="Réalisé" />
  </LineChart>
</div>
```

#### FIN-18 : Camembert Répartition Lots

```tsx
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

<PieChart width={400} height={300}>
  <Pie
    data={lots.map(l => ({ name: l.libelle, value: l.total_prevu_ht }))}
    cx={200}
    cy={150}
    labelLine={false}
    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
    outerRadius={80}
    fill="#8884d8"
    dataKey="value"
  >
    {lots.map((entry, index) => (
      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
    ))}
  </Pie>
  <Tooltip formatter={(value) => formatEUR(value)} />
</PieChart>
```

#### FIN-19 : Barres Comparatives par Lot

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'

<BarChart width={800} height={400} data={lots}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="code_lot" />
  <YAxis tickFormatter={(v) => `${v/1000}k`} />
  <Tooltip formatter={(value) => formatEUR(value)} />
  <Legend />
  <Bar dataKey="total_prevu_ht" fill="#3b82f6" name="Prévu" />
  <Bar dataKey="engage" fill="#f59e0b" name="Engagé" />
  <Bar dataKey="realise" fill="#10b981" name="Réalisé" />
</BarChart>
```

---

### 📅 PHASE 3 - Refonte UX + IA (7 jours) → Gain 100%

**Objectif** : Dashboard unique + vue consolidée + suggestions intelligentes

| Feature | Effort | Techno | Impact |
|---------|--------|--------|--------|
| **Dashboard unique** | 3j | React refactor | ⭐⭐⭐⭐⭐ |
| **FIN-20** : Vue consolidée | 2j | Nouvelle route | ⭐⭐⭐⭐⭐ |
| **FIN-21** : Suggestions IA | 2j | Gemini Flash | ⭐⭐⭐⭐⭐ |
| **FIN-22** : Indicateurs prédictifs | (inclus) | Calculs | ⭐⭐⭐⭐ |

**Total** : 7 jours, niveau Graneet atteint

#### Dashboard Unique (Refactorisation BudgetTab)

**Objectif** : Toutes les infos en 1 écran, sans clic

**Nouvelle structure** :
```
┌─────────────────────────────────────────────┐
│ SECTION 1 : Bannière alertes (si existantes)│
├─────────────────────────────────────────────┤
│ SECTION 2 : 5 KPI Cards                    │
│ [Budget] [Engagé] [Réalisé] [Reste] [Marge]│
├─────────────────────────────────────────────┤
│ SECTION 3 : Graphiques (2 colonnes)        │
│ ┌──────────────┬──────────────┐            │
│ │ Évolution    │ Camembert    │            │
│ │ temporelle   │ lots         │            │
│ └──────────────┴──────────────┘            │
├─────────────────────────────────────────────┤
│ SECTION 4 : Barres comparatives par lot    │
├─────────────────────────────────────────────┤
│ SECTION 5 : Top 5 lots (tableau)           │
├─────────────────────────────────────────────┤
│ SECTION 6 : Dernières opérations (2 col)   │
│ ┌──────────────┬──────────────┐            │
│ │ 5 achats     │ 3 situations │            │
│ └──────────────┴──────────────┘            │
├─────────────────────────────────────────────┤
│ SECTION 7 : Actions rapides                │
│ [+ Lot] [+ Achat] [+ Avenant] [+ Situation]│
└─────────────────────────────────────────────┘
```

**Effort** : 3 jours
- Jour 1 : Refactor BudgetTab + sections 1-2
- Jour 2 : Sections 3-4 (graphiques)
- Jour 3 : Sections 5-7 + polish responsive

#### FIN-20 : Vue Consolidée Multi-Chantiers

**Route** : `/finances` (nouvelle page au niveau `/dashboard`, `/chantiers`)

**Backend - Use Case** :
```python
class GetVueConsolideeFinancesUseCase:
    def execute(self, user_id: int) -> VueConsolidee:
        # Récupérer chantiers selon rôle
        chantiers = self._get_chantiers_accessibles(user_id)

        # Agréger KPI globaux
        kpi_globaux = KPIGlobaux(
            total_budget_revise=sum(c.montant_revise_ht for c in chantiers),
            total_engage=sum(c.total_engage for c in chantiers),
            total_realise=sum(c.total_realise for c in chantiers),
            marge_moyenne_pct=self._calcul_marge_moyenne_ponderee(chantiers)
        )

        # Top/Flop
        top_rentables = sorted(chantiers, key=lambda c: c.marge_pct, reverse=True)[:3]
        top_derives = sorted(chantiers, key=lambda c: c.depassement_pct, reverse=True)[:3]

        return VueConsolidee(
            kpi_globaux=kpi_globaux,
            chantiers=[self._to_summary(c) for c in chantiers],
            top_rentables=top_rentables,
            top_derives=top_derives
        )
```

**Frontend - Nouvelle Page** :
```tsx
// frontend/src/pages/FinancesPage.tsx

export default function FinancesPage() {
  const { data, loading } = useConsolidationFinanciere()

  if (loading) return <Loader />

  return (
    <div className="space-y-6">
      {/* KPI globaux entreprise */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard title="Budget Total" value={data.kpi_globaux.total_budget_revise} />
        <KPICard title="Engagé Total" value={data.kpi_globaux.total_engage} />
        <KPICard title="Réalisé Total" value={data.kpi_globaux.total_realise} />
        <KPICard title="Marge Moyenne" value={`${data.kpi_globaux.marge_moyenne_pct}%`} />
      </div>

      {/* Tableau comparatif */}
      <ChantiersTable chantiers={data.chantiers} />

      {/* Top/Flop */}
      <div className="grid grid-cols-2 gap-4">
        <TopRentables chantiers={data.top_rentables} />
        <TopDerives chantiers={data.top_derives} />
      </div>
    </div>
  )
}
```

**Effort** : 2 jours
- Jour 1 : Backend (use case + route + tests)
- Jour 2 : Frontend (page + composants + intégration)

#### FIN-21 : Suggestions Intelligentes (IA Gemini Flash)

**Choix technologique** : **Google Gemini 1.5 Flash**

**Pourquoi Gemini Flash** :
- ✅ **Gratuit** : 1500 req/jour (0 EUR/mois pour Hub-Chantier)
- ✅ **Excellente qualité** : Niveau GPT-4o-mini
- ✅ **Rapide** : Latence 400ms
- ✅ **Simple** : 1 pip install `google-generativeai`
- ✅ **Fiable** : API Google stable, SLA 99.9%

**Alternatives évaluées** :
| Solution | Coût/mois | Qualité | Latence | RGPD | Verdict |
|----------|-----------|---------|---------|------|---------|
| Gemini Flash | 0 EUR | ⭐⭐⭐⭐⭐ | 400ms | ⚠️ US | ✅ RETENU |
| Ollama Qwen 2.5 | 0 EUR | ⭐⭐⭐⭐⭐ | 500ms | ✅ Local | Alternative |
| Groq Llama 3.1 | 0 EUR | ⭐⭐⭐⭐ | 100ms | ⚠️ US | Fallback |
| GPT-4o-mini | 0.13 EUR | ⭐⭐⭐⭐⭐ | 500ms | ⚠️ US | Payant |
| Mistral Large | 3 EUR | ⭐⭐⭐⭐⭐ | 500ms | ✅ EU | Payant |

**Architecture Backend** :

```python
# requirements.txt
google-generativeai>=0.4.0

# .env
GEMINI_API_KEY=your_key_here  # Gratuit sur https://ai.google.dev/
GEMINI_ENABLED=true
```

**Provider Gemini** :
```python
# backend/modules/financier/application/intelligence/providers/gemini_provider.py

import google.generativeai as genai
import json

class GeminiProvider:
    SYSTEM_PROMPT = """Tu es un expert en gestion financière de chantiers BTP.
Analyse les données budgétaires et propose 2-3 actions concrètes pour optimiser la rentabilité.

Règles :
- Sois concis (2-3 phrases max par suggestion)
- Propose uniquement des actions réalisables
- Quantifie l'impact financier
- Priorise par urgence (CRITICAL > WARNING > INFO)

Format JSON strict :
{
  "suggestions": [
    {
      "type": "CREATE_AVENANT|IMPUTE_ACHATS|OPTIMIZE_COSTS|CREATE_SITUATION|REDUCE_BURN_RATE",
      "severity": "CRITICAL|WARNING|INFO",
      "titre": "Titre court",
      "description": "Description actionable",
      "impact_estime_eur": 12345
    }
  ]
}"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 800,
                "response_mime_type": "application/json"
            }
        )

    async def generate_suggestions(self, chantier_data: dict) -> dict:
        user_prompt = f"""Chantier "{chantier_data['nom']}"

Budget révisé : {chantier_data['montant_revise_ht']:,.0f} EUR HT
Engagé : {chantier_data['total_engage']:,.0f} EUR ({chantier_data['pct_engage']:.1f}%)
Réalisé : {chantier_data['total_realise']:,.0f} EUR ({chantier_data['pct_realise']:.1f}%)
Reste à dépenser : {chantier_data['reste_a_depenser']:,.0f} EUR
Marge estimée : {chantier_data['marge_estimee_pct']:.1f}%"""

        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{user_prompt}"
        response = await self.model.generate_content_async(full_prompt)

        return json.loads(response.text)
```

**Use Case** :
```python
class GetSuggestionsFinancieresUseCase:
    def __init__(
        self,
        budget_repo,
        gemini_provider: GeminiProvider,
        fallback_provider  # Règles algorithmiques
    ):
        self.budget_repo = budget_repo
        self.gemini = gemini_provider
        self.fallback = fallback_provider

    async def execute(self, chantier_id: int) -> SuggestionsOutput:
        # Récupérer données
        dashboard = self.budget_repo.get_dashboard_kpi(chantier_id)

        # Calculer indicateurs prédictifs (FIN-22)
        indicateurs = self._calcul_indicateurs_predictifs(dashboard)

        # Générer suggestions via IA (avec fallback)
        try:
            suggestions = await self.gemini.generate_suggestions(dashboard)
        except Exception as e:
            logger.warning(f"Gemini failed, using fallback: {e}")
            suggestions = self.fallback.generate_suggestions(dashboard)

        return SuggestionsOutput(
            suggestions=suggestions['suggestions'][:3],  # Max 3
            indicateurs_predictifs=indicateurs
        )
```

**Frontend - SuggestionsPanel** :
```tsx
// frontend/src/components/financier/SuggestionsPanel.tsx

export default function SuggestionsPanel({ chantierId }: Props) {
  const { suggestions, loading } = useSuggestions(chantierId)

  if (loading) return <Skeleton />
  if (suggestions.length === 0) return null

  return (
    <div className="space-y-3 mb-6">
      {suggestions.map(suggestion => (
        <SuggestionCard key={suggestion.id} suggestion={suggestion} />
      ))}
    </div>
  )
}

function SuggestionCard({ suggestion }: { suggestion: Suggestion }) {
  const severityConfig = {
    CRITICAL: { color: 'red', icon: AlertTriangle },
    WARNING: { color: 'orange', icon: AlertCircle },
    INFO: { color: 'blue', icon: Info }
  }

  const config = severityConfig[suggestion.severity]
  const Icon = config.icon

  return (
    <div className={`border-l-4 border-${config.color}-500 bg-${config.color}-50 p-4 rounded-lg`}>
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 text-${config.color}-600 flex-shrink-0`} />
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-1">
            {suggestion.titre}
          </h4>
          <p className="text-sm text-gray-700 mb-3">
            {suggestion.description}
          </p>
          {suggestion.impact_estime_eur && (
            <p className="text-xs text-gray-500 mb-2">
              Impact estimé : {formatEUR(suggestion.impact_estime_eur)}
            </p>
          )}
          <div className="flex gap-2">
            {suggestion.actions.map(action => (
              <button
                key={action.label}
                onClick={() => handleAction(action)}
                className={action.primary ? 'btn-primary' : 'btn-secondary'}
              >
                {action.label}
              </button>
            ))}
            <button onClick={() => dismiss(suggestion.id)} className="btn-ghost">
              Ignorer
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
```

**Effort** : 2 jours
- Jour 1 : Backend (Provider Gemini + Use Case + Route API + Tests)
- Jour 2 : Frontend (SuggestionsPanel + intégration + fallback UI)

#### FIN-22 : Indicateurs Prédictifs

**Implémenté dans FIN-21** (même use case)

**3 indicateurs** :

1. **Burn Rate** (Rythme de dépense)
```python
duree_ecoulee_mois = (date.today() - chantier.date_debut).days / 30
burn_rate_mensuel = total_realise / duree_ecoulee_mois if duree_ecoulee_mois > 0 else 0
budget_moyen_mensuel = montant_revise_ht / chantier.duree_prevue_mois
ecart_burn_rate_pct = ((burn_rate_mensuel - budget_moyen_mensuel) / budget_moyen_mensuel) * 100
```

2. **Projection Fin Chantier**
```python
if burn_rate_mensuel > 0:
    mois_restants = reste_a_depenser / burn_rate_mensuel
    date_epuisement_budget = date.today() + timedelta(days=mois_restants * 30)

    if date_epuisement_budget < chantier.date_fin_prevue:
        deficit_prevu = (chantier.date_fin_prevue - date_epuisement_budget).days / 30 * burn_rate_mensuel
```

3. **Avancement Physique vs Financier**
```python
avancement_physique_pct = (nb_taches_terminees / nb_taches_total) * 100
avancement_financier_pct = (total_realise / montant_revise_ht) * 100
ecart_pct = avancement_financier_pct - avancement_physique_pct
```

---

## 📦 Plan d'Implémentation Détaillé

### Semaine 1 - Quick Wins (Jours 1-2)

**Jour 1 - Matin** :
- ✅ Backend : Ajouter `reste_a_depenser` dans DashboardKPI
- ✅ Frontend : Nouvelle carte KPI "Reste à dépenser"
- ✅ Tests unitaires backend + frontend

**Jour 1 - Après-midi** :
- ✅ Frontend : Bannière alertes en haut de BudgetTab
- ✅ Frontend : Jauges circulaires SVG (remplacer barres horizontales)
- ✅ Tests manuels avec vraies données

**Jour 2** : Buffer + polish

---

### Semaine 2 - Graphiques (Jours 3-5)

**Jour 3 - Graphique Évolution** :
- ✅ Backend : Use case GetEvolutionFinanciereUseCase
- ✅ Backend : Route GET /api/financier/chantiers/{id}/evolution
- ✅ Frontend : Composant EvolutionChart avec Recharts
- ✅ Tests

**Jour 4 - Graphiques Lots** :
- ✅ Frontend : Composant CamembertLots
- ✅ Frontend : Composant BarresComparativesLots
- ✅ Intégration dans BudgetDashboard
- ✅ Tests

**Jour 5** : Buffer + polish responsive

---

### Semaine 3 - Refonte UX (Jours 6-8)

**Jour 6 - Dashboard Unique** :
- ✅ Frontend : Refactor BudgetTab (sections 1-2)
- ✅ Frontend : Nouvelle structure 7 sections
- ✅ Responsive mobile/tablette

**Jour 7 - Dashboard Unique (suite)** :
- ✅ Frontend : Sections 3-4 (graphiques intégrés)
- ✅ Frontend : Sections 5-7 (Top 5, opérations, actions)
- ✅ Tests manuels

**Jour 8** : Polish + navigation secondaire (onglets existants)

---

### Semaine 4 - Vue Consolidée + IA (Jours 9-10)

**Jour 9 - Vue Consolidée** :
- ✅ Backend : Use case GetVueConsolideeFinancesUseCase
- ✅ Backend : Route GET /api/finances/consolidation
- ✅ Frontend : Page FinancesPage + composants
- ✅ Frontend : Navigation (ajouter lien menu)
- ✅ Tests

**Jour 10 - Suggestions IA** :
- ✅ Backend : Provider Gemini + Use case + Route
- ✅ Frontend : SuggestionsPanel + intégration
- ✅ Configuration : GEMINI_API_KEY (clé gratuite)
- ✅ Tests + fallback

---

## ✅ Checklist de Validation

### Phase 1 - Quick Wins
- [ ] Backend : `reste_a_depenser` dans API
- [ ] Frontend : 5ème carte KPI affichée
- [ ] Frontend : Bannière alertes visible en haut
- [ ] Frontend : Jauges circulaires fonctionnelles
- [ ] Tests : 10+ tests unitaires passent
- [ ] Tests manuels : 3 chantiers testés

### Phase 2 - Graphiques
- [ ] Backend : Route `/evolution` retourne données mensuelles
- [ ] Frontend : Graphique évolution affiché et interactif
- [ ] Frontend : Camembert lots affiché
- [ ] Frontend : Barres comparatives affichées
- [ ] Recharts : 3 graphiques fonctionnels
- [ ] Responsive : Graphiques lisibles mobile
- [ ] Tests : 15+ tests unitaires passent

### Phase 3 - Refonte UX
- [ ] Frontend : Dashboard 7 sections visible sans scroll
- [ ] Frontend : 0 clic pour voir infos essentielles
- [ ] Frontend : Actions rapides cliquables
- [ ] Responsive : Mobile/tablette OK
- [ ] Tests : 20+ tests unitaires passent

### Phase 4 - Vue Consolidée
- [ ] Backend : Route `/finances/consolidation` opérationnelle
- [ ] Frontend : Page `/finances` accessible depuis menu
- [ ] Frontend : Tableau multi-chantiers avec tri/filtres
- [ ] Frontend : Top 3 rentables + Top 3 dérives affichés
- [ ] Permissions : Admin voit tout, Conducteur ses chantiers
- [ ] Tests : 15+ tests unitaires passent

### Phase 5 - Suggestions IA
- [ ] Backend : Gemini provider configuré
- [ ] Backend : Route `/suggestions` retourne JSON
- [ ] Frontend : SuggestionsPanel affiché si suggestions
- [ ] Gemini : Clé API gratuite configurée
- [ ] Fallback : Règles algo fonctionnent si Gemini down
- [ ] Anonymisation : Noms chantiers remplacés par codes
- [ ] Tests : 10+ tests unitaires passent
- [ ] Tests manuels : 5 types de suggestions générées

---

## 📊 Matrice Effort/Impact/ROI

| Feature | Effort | Impact Business | ROI | Phase |
|---------|--------|-----------------|-----|-------|
| Reste à dépenser | 1h | ⭐⭐⭐⭐⭐ | 100x | 1 |
| Alertes visibles | 2h | ⭐⭐⭐⭐ | 40x | 1 |
| Jauges améliorées | 3h | ⭐⭐⭐ | 20x | 1 |
| Graphique évolution | 1j | ⭐⭐⭐⭐⭐ | 10x | 2 |
| Camembert lots | 4h | ⭐⭐⭐⭐ | 20x | 2 |
| Barres comparatives | 4h | ⭐⭐⭐⭐ | 15x | 2 |
| Dashboard unique | 3j | ⭐⭐⭐⭐⭐ | 5x | 3 |
| Vue consolidée | 2j | ⭐⭐⭐⭐⭐ | 6x | 3 |
| Suggestions IA | 2j | ⭐⭐⭐⭐⭐ | 6x | 3 |

---

## 🔗 Références Techniques

### Documentation
- [Gemini API (gratuit)](https://ai.google.dev/)
- [Recharts Documentation](https://recharts.org/)
- [SPECIFICATIONS.md Section 17](../SPECIFICATIONS.md#17-gestion-financiere-et-budgetaire)

### Analyse Concurrence
- [Graneet](https://www.graneet.com/fr) - Leader marché (150-300 EUR/user/mois)
- [Kalitics](https://www.kalitics-btp.com/) - Meilleure UX (80-150 EUR/user/mois)
- [Obat](https://www.obat.fr/) - TPE Focus (0-50 EUR/user/mois)

### Code Examples
- Provider Gemini : Voir section FIN-21
- Graphiques Recharts : Voir sections FIN-17, FIN-18, FIN-19
- Use Cases : Voir SPECIFICATIONS.md section 17.12

---

## 📈 Métriques de Succès

### Avant Phase 3
- Backend : 9/10 ✅
- Frontend : 5/10 ⚠️
- **Score global : 5/10**

### Après Phase 3
- Backend : 9/10 ✅
- Frontend : 9/10 ✅
- **Score global : 9/10** (niveau Graneet)

### KPIs à Mesurer

**Adoption** :
- Nombre de visites `/chantiers/:id/budget` par jour
- Temps moyen passé sur le dashboard
- Nombre d'actions effectuées (créer avenant, achat, etc.)

**Impact Business** :
- Délai moyen de détection d'un dépassement budgétaire
- Nombre d'avenants créés suite à une suggestion IA
- Taux d'utilisation de la vue consolidée (admin/conducteurs)

**Objectifs chiffrés** :
- +150% visites dashboard financier
- x3 temps moyen sur la page
- -80% délai de détection problèmes
- 70% des suggestions IA suivies d'une action

---

## 💰 Coûts & ROI

### Coûts d'Implémentation

**Développement** :
- 10 jours dev fullstack (phases 1-3)
- Pas de dépendance externe payante (Recharts gratuit, Gemini gratuit)

**Infrastructure** :
- 0 EUR/mois (Gemini tier gratuit 1500 req/jour)
- 0 EUR/mois (Recharts open-source)

### ROI Estimé

**Scénario Greg Construction** (20 employés, 20 chantiers actifs) :

**Avant** :
- Logiciel actuel : Fait maison basique
- Alternative : Graneet 150 EUR/user/mois = **3000 EUR/mois**

**Après Phase 3** :
- Hub-Chantier = même niveau Graneet
- Coût = 0 EUR/mois (déjà développé)
- **Économie : 36 000 EUR/an**

**ROI dev** :
- Coût dev : 10 jours x 500 EUR/jour = 5000 EUR
- Économie annuelle : 36 000 EUR
- **ROI : 7.2x sur 1 an**

---

## 🚀 Prochaines Étapes

### Immédiat (Après Validation Specs)

1. **Obtenir clé API Gemini** (2 min)
   - Aller sur https://ai.google.dev/
   - Créer clé gratuite
   - Ajouter dans `.env` : `GEMINI_API_KEY=xxx`

2. **Installer Recharts** (1 min)
   ```bash
   cd frontend && npm install recharts
   ```

3. **Créer branche dev**
   ```bash
   git checkout -b feature/financier-phase3-ux
   ```

### Semaine 1 - Démarrage

**Lundi matin** : Lancer Phase 1 (Quick Wins)
- [ ] FIN-16 Backend (reste à dépenser)
- [ ] FIN-16 Frontend (5ème carte KPI)

**Lundi après-midi** : Finir Phase 1
- [ ] Alertes en haut
- [ ] Jauges circulaires

**Mardi** : Buffer + tests + demo client

---

**Document créé le** : 1er février 2026
**Dernière mise à jour** : 1er février 2026
**Statut** : Prêt pour implémentation
**Prochaine review** : Après implémentation Phase 1

---

*Ce document fusionne et synthétise :*
- *ANALYSE_CONCURRENCE_FINANCIER.md (analyse 5 concurrents)*
- *INTELLIGENCE_FINANCIERE_OPTIONS.md (3 approches IA)*
- *MODELES_IA_GRATUITS.md (10 modèles évalués)*
- *SPECIFICATIONS.md Section 17 (specs techniques)*
