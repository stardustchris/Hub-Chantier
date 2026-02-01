# Intelligence Financière - Options IA

> Date : 1er février 2026
> Objectif : Choisir la meilleure approche IA pour les suggestions intelligentes (FIN-21)

---

## 🎯 Contexte & Besoins

**Suggestions à implémenter** (définies dans FIN-21) :

1. **Dépassement imminent** → Suggérer création avenant
2. **Achat non imputé** → Détecter + alerter
3. **Marge faible précoce** → Proposer optimisations
4. **Situation en retard** → Rappeler facturation
5. **Burn rate excessif** → Recommander actions

**Contraintes Hub-Chantier** :
- 🔒 Données financières sensibles (RGPD, confidentialité)
- 💰 Budget limité (TPE/PME, 4.3M EUR CA)
- ⚡ Latence < 1s (UX temps réel)
- 🎯 Fiabilité critique (pas de "hallucinations")
- 🔧 Stack Python (FastAPI) + PostgreSQL

---

## 📊 Comparatif 3 Approches

| Critère | 1. Règles Algorithmiques | 2. IA Générative Cloud | 3. ML Prédictif Local |
|---------|-------------------------|------------------------|----------------------|
| **Complexité** | ⭐ Facile | ⭐⭐ Moyenne | ⭐⭐⭐⭐ Complexe |
| **Coût** | Gratuit | 0.50-2 EUR/1000 req | Gratuit (compute) |
| **Confidentialité** | ✅ 100% local | ⚠️ Données en cloud | ✅ 100% local |
| **Fiabilité** | ✅ 100% déterministe | ⚠️ 85-95% | ⚠️ 70-90% |
| **Latence** | < 50ms | 200-800ms | 50-200ms |
| **Maintenance** | ⭐⭐ Règles à ajuster | ⭐ API stable | ⭐⭐⭐⭐ Réentraînement |
| **Valeur ajoutée** | ⭐⭐⭐ Bonne | ⭐⭐⭐⭐⭐ Excellente | ⭐⭐⭐⭐ Très bonne |
| **Temps implémentation** | 2 jours | 3 jours | 10-15 jours |

---

## 🔧 OPTION 1 : Règles Algorithmiques (Recommandé Phase 1)

### Principe

Pas d'IA au sens ML, mais **algorithmes de détection basés sur règles métier**.

**Avantages** :
- ✅ 100% déterministe et explicable
- ✅ Aucune dépendance externe
- ✅ Données restent locales (RGPD)
- ✅ Latence < 50ms
- ✅ Coût = 0 EUR
- ✅ Implémentation rapide (2 jours)

**Inconvénients** :
- ❌ Suggestions textuelles moins "naturelles"
- ❌ Nécessite mise à jour manuelle des règles
- ❌ Pas d'apprentissage automatique

### Architecture

```python
# backend/modules/financier/application/intelligence/
├── suggestion_engine.py          # Moteur principal
├── rules/
│   ├── depassement_rule.py       # Règle dépassement
│   ├── imputation_rule.py        # Règle achats non imputés
│   ├── marge_rule.py             # Règle marge faible
│   ├── situation_rule.py         # Règle situation retard
│   └── burn_rate_rule.py         # Règle burn rate
└── models/
    └── suggestion.py             # Entity Suggestion
```

### Exemple Implémentation

```python
# backend/modules/financier/application/intelligence/rules/depassement_rule.py

from decimal import Decimal
from datetime import date
from typing import Optional
from ..models.suggestion import Suggestion, SuggestionType, SuggestionSeverity

class DepassementRule:
    """Détecte les dépassements budgétaires imminents"""

    SEUIL_ENGAGE_PCT = Decimal('95')  # 95% engagé
    SEUIL_REALISE_PCT = Decimal('60')  # mais seulement 60% réalisé

    def evaluate(
        self,
        chantier_id: int,
        montant_revise_ht: Decimal,
        total_engage: Decimal,
        total_realise: Decimal,
        pct_engage: Decimal,
        pct_realise: Decimal
    ) -> Optional[Suggestion]:
        """
        Évalue si un avenant est recommandé

        Returns:
            Suggestion si condition remplie, None sinon
        """
        if pct_engage > self.SEUIL_ENGAGE_PCT and pct_realise < self.SEUIL_REALISE_PCT:
            # Calcul montant avenant suggéré
            reste_a_realiser_pct = Decimal('100') - pct_realise
            cout_unitaire_moyen = total_realise / pct_realise if pct_realise > 0 else 0
            montant_avenant_suggere = (reste_a_realiser_pct * cout_unitaire_moyen) - (montant_revise_ht - total_engage)

            return Suggestion(
                type=SuggestionType.CREATE_AVENANT,
                severity=SuggestionSeverity.CRITICAL,
                titre="Dépassement budgétaire imminent",
                description=f"""Vous avez engagé {pct_engage:.1f}% du budget alors que seulement {pct_realise:.1f}% du chantier est réalisé.

À ce rythme, le budget sera insuffisant pour terminer les travaux.

**Action recommandée** : Créer un avenant de +{montant_avenant_suggere:,.0f} EUR pour sécuriser la fin du chantier.""",
                impact_estime_eur=montant_avenant_suggere,
                actions=[
                    {
                        "label": "Créer avenant",
                        "action": f"/chantiers/{chantier_id}/budget/avenants/new",
                        "primary": True
                    },
                    {
                        "label": "Voir détails budget",
                        "action": f"/chantiers/{chantier_id}/budget",
                        "primary": False
                    }
                ],
                metadata={
                    "pct_engage": float(pct_engage),
                    "pct_realise": float(pct_realise),
                    "montant_suggere": float(montant_avenant_suggere)
                }
            )

        return None
```

```python
# backend/modules/financier/application/intelligence/suggestion_engine.py

from typing import List
from .rules.depassement_rule import DepassementRule
from .rules.imputation_rule import ImputationRule
from .rules.marge_rule import MargeRule
from .rules.situation_rule import SituationRule
from .rules.burn_rate_rule import BurnRateRule
from .models.suggestion import Suggestion

class SuggestionEngine:
    """Moteur de suggestions intelligentes basé sur règles"""

    def __init__(self):
        self.rules = [
            DepassementRule(),
            ImputationRule(),
            MargeRule(),
            SituationRule(),
            BurnRateRule()
        ]

    def generate_suggestions(
        self,
        chantier_id: int,
        dashboard_data: dict,
        achats: list,
        situations: list
    ) -> List[Suggestion]:
        """
        Génère toutes les suggestions pour un chantier

        Returns:
            Liste de suggestions triées par severity DESC
        """
        suggestions = []

        # Évaluer chaque règle
        for rule in self.rules:
            suggestion = rule.evaluate(
                chantier_id=chantier_id,
                **dashboard_data,
                achats=achats,
                situations=situations
            )
            if suggestion:
                suggestions.append(suggestion)

        # Trier par severity (CRITICAL > WARNING > INFO)
        suggestions.sort(key=lambda s: s.severity.value, reverse=True)

        # Limiter à 3 suggestions max (UX)
        return suggestions[:3]
```

### Use Case

```python
# backend/modules/financier/application/use_cases/get_suggestions_financieres_use_case.py

from dataclasses import dataclass
from typing import List
from ..intelligence.suggestion_engine import SuggestionEngine
from ..intelligence.models.suggestion import Suggestion

@dataclass
class GetSuggestionsFinancieresInput:
    chantier_id: int

@dataclass
class GetSuggestionsFinancieresOutput:
    suggestions: List[Suggestion]
    indicateurs_predictifs: dict

class GetSuggestionsFinancieresUseCase:
    def __init__(
        self,
        budget_repository,
        achat_repository,
        situation_repository,
        suggestion_engine: SuggestionEngine
    ):
        self.budget_repository = budget_repository
        self.achat_repository = achat_repository
        self.situation_repository = situation_repository
        self.engine = suggestion_engine

    def execute(self, input_dto: GetSuggestionsFinancieresInput) -> GetSuggestionsFinancieresOutput:
        # Récupérer données
        dashboard = self.budget_repository.get_dashboard_kpi(input_dto.chantier_id)
        achats = self.achat_repository.find_by_chantier(input_dto.chantier_id)
        situations = self.situation_repository.find_by_chantier(input_dto.chantier_id)

        # Générer suggestions
        suggestions = self.engine.generate_suggestions(
            chantier_id=input_dto.chantier_id,
            dashboard_data=dashboard,
            achats=achats,
            situations=situations
        )

        # Calculer indicateurs prédictifs
        indicateurs = self._calcul_indicateurs_predictifs(dashboard, achats)

        return GetSuggestionsFinancieresOutput(
            suggestions=suggestions,
            indicateurs_predictifs=indicateurs
        )
```

### Effort

- **Backend** : 2 jours
  - 1j : Moteur + 5 règles + use case
  - 1j : Tests unitaires (1 test par règle)

- **Frontend** : 1 jour
  - Affichage suggestions dans BudgetDashboard
  - Modal détails suggestion
  - Actions cliquables

**Total : 3 jours**

---

## 🤖 OPTION 2 : IA Générative Cloud (Phase 2 optionnelle)

### Principe

Utiliser GPT-4, Claude Sonnet ou Mistral pour **générer des suggestions textuelles naturelles** et **analyser les données financières**.

### Comparatif Providers

| Provider | Modèle | Prix (1M tokens) | Latence | Confidentialité | Recommandation |
|----------|--------|------------------|---------|-----------------|----------------|
| **OpenAI** | GPT-4o | $2.50 in / $10 out | 800ms | ⚠️ US | ⭐⭐⭐⭐ |
| **Anthropic** | Claude 3.5 Sonnet | $3 in / $15 out | 600ms | ⚠️ US | ⭐⭐⭐⭐⭐ |
| **Mistral AI** | Mistral Large | €3 in / €9 out | 500ms | ✅ EU (France) | ⭐⭐⭐⭐⭐ |
| **Google** | Gemini Pro | $1.25 in / $5 out | 700ms | ⚠️ US | ⭐⭐⭐ |
| **Ollama** | Llama 3.1 (local) | Gratuit | 300ms | ✅ 100% local | ⭐⭐⭐ |

**Recommandation** : **Mistral AI** (EU, RGPD-compliant, excellent rapport qualité/prix)

### Architecture

```python
# requirements.txt
mistralai>=0.2.0  # ou anthropic>=0.18.0 ou openai>=1.12.0

# backend/modules/financier/application/intelligence/
├── ai_suggestion_engine.py       # Moteur IA
├── prompts/
│   ├── system_prompt.txt         # Prompt système (rôle expert BTP)
│   └── suggestion_prompt.txt     # Template prompt suggestions
└── providers/
    ├── mistral_provider.py       # Wrapper Mistral
    ├── claude_provider.py        # Wrapper Claude
    └── openai_provider.py        # Wrapper OpenAI
```

### Exemple Implémentation (Mistral)

```python
# backend/modules/financier/application/intelligence/ai_suggestion_engine.py

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from typing import List
import json

class AISuggestionEngine:
    """Moteur de suggestions IA avec Mistral"""

    SYSTEM_PROMPT = """Tu es un expert en gestion financière de chantiers BTP.
Ton rôle est d'analyser les données budgétaires d'un chantier et de proposer des actions concrètes et actionnables pour optimiser la rentabilité.

Règles :
- Sois concis (2-3 phrases max par suggestion)
- Propose uniquement des actions réalisables
- Quantifie l'impact financier quand possible
- Priorise par urgence (CRITICAL > WARNING > INFO)
- Utilise un ton professionnel mais accessible"""

    def __init__(self, api_key: str):
        self.client = MistralClient(api_key=api_key)
        self.model = "mistral-large-latest"

    def generate_suggestions(
        self,
        chantier_nom: str,
        dashboard_data: dict
    ) -> List[dict]:
        """
        Génère suggestions IA à partir des données financières

        Args:
            chantier_nom: Nom du chantier
            dashboard_data: KPI financiers (budget, engagé, réalisé, etc.)

        Returns:
            Liste de suggestions au format JSON
        """
        # Construire prompt
        user_prompt = self._build_prompt(chantier_nom, dashboard_data)

        # Appel API Mistral
        response = self.client.chat(
            model=self.model,
            messages=[
                ChatMessage(role="system", content=self.SYSTEM_PROMPT),
                ChatMessage(role="user", content=user_prompt)
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Peu de créativité (on veut des suggestions fiables)
        )

        # Parser réponse JSON
        suggestions = json.loads(response.choices[0].message.content)
        return suggestions.get("suggestions", [])

    def _build_prompt(self, chantier_nom: str, data: dict) -> str:
        """Construit le prompt utilisateur avec les données financières"""
        return f"""Analyse le chantier "{chantier_nom}" et propose 2-3 suggestions d'optimisation.

**Données financières** :
- Budget révisé : {data['montant_revise_ht']:,.0f} EUR HT
- Engagé : {data['total_engage']:,.0f} EUR ({data['pct_engage']:.1f}%)
- Réalisé : {data['total_realise']:,.0f} EUR ({data['pct_realise']:.1f}%)
- Reste à dépenser : {data['reste_a_depenser']:,.0f} EUR
- Marge estimée : {data['marge_estimee_pct']:.1f}%

**Contexte** :
- Avancement physique : {data.get('avancement_physique_pct', 'N/A')}%
- Burn rate : {data.get('burn_rate_mensuel', 'N/A')} EUR/mois
- Durée écoulée : {data.get('duree_ecoulee_mois', 'N/A')} mois
- Durée totale prévue : {data.get('duree_prevue_mois', 'N/A')} mois

Réponds au format JSON strict :
{{
  "suggestions": [
    {{
      "type": "CREATE_AVENANT|OPTIMIZE_COSTS|REDUCE_BURN_RATE|CREATE_SITUATION|IMPUTE_ACHATS",
      "severity": "CRITICAL|WARNING|INFO",
      "titre": "Titre court (5-8 mots)",
      "description": "Description actionable (2-3 phrases)",
      "impact_estime_eur": 12345.67,
      "actions": [
        {{
          "label": "Créer avenant",
          "primary": true
        }}
      ]
    }}
  ]
}}"""
```

### Coût Estimé

**Exemple chantier** :
- Prompt système : ~100 tokens
- Prompt user : ~300 tokens (données financières)
- Réponse : ~400 tokens (2-3 suggestions JSON)
- **Total : ~800 tokens par génération**

**Tarif Mistral Large** :
- Input : €3/1M tokens
- Output : €9/1M tokens
- **Coût par suggestion : ~0.005 EUR (0.5 centime)**

**Scénario mensuel** :
- 20 chantiers actifs
- 1 génération/jour/chantier
- 20 x 30 = 600 générations/mois
- **Coût mensuel : ~3 EUR**

→ **Négligeable** pour la valeur ajoutée

### Sécurité & RGPD

**Problème** : Données financières sensibles envoyées à un tiers (Mistral US/EU)

**Solutions** :
1. **Anonymisation** : Remplacer noms chantiers/clients par codes
2. **Agrégation** : Envoyer seulement KPI (pas de données brutes)
3. **Opt-in** : Paramètre "Activer suggestions IA" (désactivé par défaut)
4. **Mistral EU** : Serveurs en France (RGPD-compliant)

**Alternative 100% locale** : Ollama + Llama 3.1 (voir Option 3)

### Effort

- **Backend** : 2 jours
  - 1j : Intégration Mistral API + prompts
  - 1j : Tests + gestion erreurs + fallback

- **Frontend** : 1 jour
  - Paramètre activation IA
  - Affichage suggestions enrichies
  - Loader pendant génération

**Total : 3 jours**

---

## 🧠 OPTION 3 : ML Prédictif Local (Phase 3 avancée)

### Principe

Entraîner un modèle ML sur l'historique des chantiers pour **prédire la marge finale** et **détecter anomalies**.

### Cas d'usage

1. **Prédiction marge finale** (régression)
   - Input : KPI actuels (% engagé, % réalisé, burn rate, etc.)
   - Output : Marge finale estimée à ±2%

2. **Détection anomalies** (classification)
   - Input : Séquence temporelle dépenses
   - Output : Probabilité dépassement dans les 30j

3. **Clustering chantiers** (non supervisé)
   - Input : Profil chantier (type, taille, durée, budget)
   - Output : Groupe de chantiers similaires + benchmarks

### Stack Technique

```python
# requirements.txt
scikit-learn>=1.4.0          # ML classique (régression, clustering)
xgboost>=2.0.0               # Gradient boosting (meilleure précision)
pandas>=2.2.0                # Manipulation données
numpy>=1.26.0                # Calculs numériques
joblib>=1.3.0                # Sérialisation modèles

# Optionnel : Deep Learning
# torch>=2.1.0               # PyTorch (pour séquences temporelles)
# prophet>=1.1.0             # Prévisions séries temporelles (Facebook)
```

### Exemple : Prédiction Marge Finale

```python
# backend/modules/financier/application/intelligence/ml/margin_predictor.py

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from typing import Dict

class MarginPredictor:
    """Prédit la marge finale d'un chantier en cours"""

    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Prédit la marge finale

        Args:
            features: Dictionnaire de features
                - pct_engage: % du budget engagé
                - pct_realise: % du budget réalisé
                - pct_avancement_physique: % tâches terminées
                - burn_rate_ratio: Burn rate / Budget moyen
                - duree_ecoulee_pct: % durée écoulée
                - nb_avenants: Nombre d'avenants
                - nb_alertes: Nombre d'alertes actives

        Returns:
            {
                "marge_finale_estimee_pct": 12.5,
                "intervalle_confiance_min": 10.2,
                "intervalle_confiance_max": 14.8,
                "probabilite_marge_negative": 0.05
            }
        """
        # Convertir dict en array NumPy (ordre des features)
        X = np.array([
            features['pct_engage'],
            features['pct_realise'],
            features['pct_avancement_physique'],
            features['burn_rate_ratio'],
            features['duree_ecoulee_pct'],
            features['nb_avenants'],
            features['nb_alertes']
        ]).reshape(1, -1)

        # Prédiction
        marge_pred = self.model.predict(X)[0]

        # Intervalle de confiance (± 2 écart-types)
        # (nécessite quantile regression ou bootstrap)
        ic_min = marge_pred - 2.0
        ic_max = marge_pred + 2.0

        # Probabilité marge négative (classification binaire)
        proba_negative = 1.0 / (1.0 + np.exp(marge_pred * 2))  # Sigmoid

        return {
            "marge_finale_estimee_pct": round(marge_pred, 1),
            "intervalle_confiance_min": round(ic_min, 1),
            "intervalle_confiance_max": round(ic_max, 1),
            "probabilite_marge_negative": round(proba_negative, 3)
        }
```

### Entraînement du Modèle

```python
# scripts/train_margin_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Charger historique chantiers (export CSV depuis BDD)
df = pd.read_csv('backend/data/chantiers_historique.csv')

# 2. Nettoyer données
df = df.dropna()
df = df[df['statut'] == 'ferme']  # Uniquement chantiers terminés

# 3. Features engineering
features = [
    'pct_engage', 'pct_realise', 'pct_avancement_physique',
    'burn_rate_ratio', 'duree_ecoulee_pct', 'nb_avenants', 'nb_alertes'
]
X = df[features]
y = df['marge_finale_pct']  # Target

# 4. Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. Entraîner modèle
model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=4,
    random_state=42
)
model.fit(X_train, y_train)

# 6. Évaluer
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.2f}% (erreur moyenne)")
print(f"R²: {r2:.3f} (qualité prédiction)")

# 7. Sauvegarder
joblib.dump(model, 'backend/models/margin_predictor.pkl')
```

### Problèmes & Limites

**Besoin de données** :
- Minimum 50-100 chantiers terminés pour entraîner
- Greg Construction : 20 employés → ~10-15 chantiers/an
- **Il faudrait 3-5 ans d'historique** pour avoir assez de données

**Maintenance** :
- Réentraîner tous les 6 mois (dérive du modèle)
- Monitoring précision (alertes si MAE > seuil)
- Complexité DevOps (MLOps)

**Alternative** : **Transfer learning** depuis modèle pré-entraîné sur données BTP publiques (Datainfogreffe, etc.)

### Effort

- **Data collection** : 2 jours (export historique, nettoyage)
- **Training pipeline** : 3 jours (features engineering, modèle, évaluation)
- **Backend intégration** : 2 jours (use case, API)
- **Frontend** : 1 jour (affichage prédictions)
- **Monitoring** : 2 jours (MLOps, alertes dérive)

**Total : 10 jours** (sans compter collecte données initiale)

---

## 🎯 Recommandation Finale

### Approche Progressive (3 Phases)

#### ✅ Phase 1 - Quick Win (2-3 jours) : **Règles Algorithmiques**

**Pourquoi** :
- ✅ 0 EUR de coût
- ✅ 100% local (RGPD)
- ✅ Fiable et explicable
- ✅ 80% de la valeur avec 20% de l'effort

**Ce qui manque vs IA** :
- Suggestions textuelles moins naturelles ("Si X alors Y" vs prose fluide)
- Pas d'apprentissage automatique

**Verdict** : **Implémenter immédiatement** (fait partie de FIN-21 specs actuelles)

---

#### 🚀 Phase 2 - Enhancement (3 jours) : **+ IA Générative (Mistral EU)**

**Pourquoi** :
- ✅ Coût négligeable (~3 EUR/mois)
- ✅ Suggestions textuelles naturelles
- ✅ RGPD-compliant (Mistral EU)
- ✅ Valeur perçue énorme (effet "waouh")

**Quand** :
- Après Phase 1 implémentée
- Si feedback utilisateurs positif sur suggestions règles
- Si budget disponible (même si minime)

**Architecture hybride** :
```python
# Règles algorithmiques = détection
# IA générative = formulation texte

if depassement_detected:  # Règle
    suggestion_text = ai.generate_text(context)  # IA pour le wording
```

**Verdict** : **Recommandé** si budget validé

---

#### 🔬 Phase 3 - Advanced (10+ jours) : **ML Prédictif**

**Pourquoi** :
- ⭐ Prédictions précises (±2% marge finale)
- ⭐ Détection précoce anomalies
- ⭐ Différenciation concurrence

**Quand** :
- Après 2-3 ans d'utilisation (50+ chantiers historique)
- Si ressources data science disponibles
- Si ROI justifié (nombre de chantiers suffisant)

**Verdict** : **Futur** (pas prioritaire en 2026 pour Greg Construction)

---

## 🏆 Ma Recommandation Personnelle

### Implémentation Recommandée : **Hybride Phase 1 + Phase 2**

```
┌─────────────────────────────────────────────┐
│  SUGGESTION ENGINE                          │
├─────────────────────────────────────────────┤
│                                             │
│  1. Règles Algorithmiques (détection)      │
│     ✓ 5 règles métier                      │
│     ✓ Calculs prédictifs (burn rate, etc.) │
│     ✓ 100% local, 0 EUR                    │
│                                             │
│  2. IA Générative (formulation) [OPT]      │
│     ✓ Mistral Large (EU)                   │
│     ✓ Prose naturelle + recommandations    │
│     ✓ ~3 EUR/mois                          │
│     ✓ Désactivable (opt-in)                │
│                                             │
└─────────────────────────────────────────────┘
```

**Workflow** :
1. Règles détectent situation (ex: dépassement imminent)
2. Règles calculent KPI (montant avenant suggéré)
3. **Option A** : Template texte fixe (Phase 1 seule)
4. **Option B** : IA génère description naturelle (Phase 1+2)

**Avantages** :
- ✅ Fonctionne sans IA (fallback)
- ✅ UX améliorée avec IA (mais optionnelle)
- ✅ Coût maîtrisé
- ✅ Confidentialité préservée (anonymisation)
- ✅ Évolutif (Phase 3 ML ultérieurement)

**Implémentation** :
- Semaine 1 : Règles algorithmiques (Phase 1)
- Semaine 2 : Intégration Mistral (Phase 2)
- **Total : 5-6 jours**

---

## 📋 Checklist Décision

Pour choisir, réponds à ces questions :

| Question | Réponse |
|----------|---------|
| Budget mensuel acceptable pour IA ? | Oui (3-5 EUR) / Non (0 EUR) |
| Données peuvent sortir EU ? | Oui / Non (Mistral EU OK ?) |
| Priorité : Rapidité ou Perfection ? | Rapidité → Phase 1 / Perfection → Phase 2 |
| Historique chantiers > 50 ? | Oui → Envisager ML / Non → Pas encore |
| Ressources data science dispo ? | Oui → ML possible / Non → IA générative |

---

**Prochaine étape** : Tu me dis quel budget et quelles contraintes confidentialité, je te prépare le plan d'implémentation détaillé !

