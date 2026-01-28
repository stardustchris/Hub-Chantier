# Corrections de Sécurité à Implémenter
**Date** : 28 janvier 2026
**Priorité** : FINDING M-01 bloquant pour production

---

## 🔴 FINDING M-01 : Timestamp Consentements RGPD (OBLIGATOIRE)

### Frontend : Modifier consent.ts

**Fichier** : `/Users/aptsdae/Hub-Chantier/frontend/src/services/consent.ts`

```typescript
// AVANT
export interface ConsentPreferences {
  geolocation: boolean
  notifications: boolean
  analytics: boolean
}

// APRÈS
export interface ConsentPreferences {
  geolocation: boolean
  notifications: boolean
  analytics: boolean
  timestamp?: string // Date ISO du consentement
  ipAddress?: string // IP (optionnel, backend peut la capturer)
  userAgent?: string // User agent (optionnel)
}
```

**Modification de setConsents()** :
```typescript
async function setConsents(consents: Partial<ConsentPreferences>): Promise<void> {
  try {
    // ✅ Ajouter le timestamp avant envoi
    const consentWithMetadata = {
      ...consents,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    }

    await api.post('/api/auth/consents', consentWithMetadata)

    // Mettre à jour le cache
    if (consentCache) {
      consentCache = { ...consentCache, ...consentWithMetadata }
    } else {
      consentCache = {
        geolocation: consents.geolocation ?? false,
        notifications: consents.notifications ?? false,
        analytics: consents.analytics ?? false,
        timestamp: consentWithMetadata.timestamp,
        userAgent: consentWithMetadata.userAgent
      }
    }

    logger.info('Consents updated with timestamp', consentWithMetadata)
  } catch (error) {
    logger.error('Error setting consents', error)
    throw error
  }
}
```

### Backend : Modifier modèle UserConsent

**Fichier** : `/Users/aptsdae/Hub-Chantier/backend/modules/auth/domain/entities/user.py`

```python
# AVANT
class UserConsent:
    geolocation: bool = False
    notifications: bool = False
    analytics: bool = False

# APRÈS
from datetime import datetime

class UserConsent:
    geolocation: bool = False
    notifications: bool = False
    analytics: bool = False
    timestamp: Optional[datetime] = None  # ✅ Date du consentement
    ip_address: Optional[str] = None      # ✅ IP de l'utilisateur
    user_agent: Optional[str] = None      # ✅ User agent
```

### Backend : Migration Alembic

**Créer une migration** :
```bash
cd backend
alembic revision -m "add_consent_metadata"
```

**Fichier généré** : `backend/alembic/versions/XXXXX_add_consent_metadata.py`
```python
def upgrade():
    # Ajouter les colonnes dans la table users
    op.add_column('users', sa.Column('consent_timestamp', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('consent_ip_address', sa.String(45), nullable=True))
    op.add_column('users', sa.Column('consent_user_agent', sa.String(500), nullable=True))

def downgrade():
    op.drop_column('users', 'consent_user_agent')
    op.drop_column('users', 'consent_ip_address')
    op.drop_column('users', 'consent_timestamp')
```

### Backend : Modifier l'endpoint /consents

**Fichier** : `/Users/aptsdae/Hub-Chantier/backend/modules/auth/infrastructure/web/auth_routes.py`

```python
from fastapi import Request

@router.post("/consents")
async def update_consents(
    data: dict,
    request: Request,  # ✅ Ajouter request pour capturer IP
    current_user: User = Depends(get_current_user)
):
    # Extraire les consentements
    consents = {
        "geolocation": data.get("geolocation", False),
        "notifications": data.get("notifications", False),
        "analytics": data.get("analytics", False),
    }

    # ✅ Ajouter les métadonnées
    metadata = {
        "timestamp": datetime.utcnow(),
        "ip_address": request.client.host,  # IP du client
        "user_agent": data.get("userAgent") or request.headers.get("User-Agent")
    }

    # Sauvegarder dans la BDD
    # TODO: Adapter selon votre modèle de persistance
    await user_repository.update_consents(
        user_id=current_user.id,
        consents=consents,
        metadata=metadata
    )

    return {"success": True, "consents": consents, "metadata": metadata}
```

### Test de Validation

```bash
# 1. Appliquer la migration
cd backend
alembic upgrade head

# 2. Redémarrer le backend
uvicorn main:app --reload

# 3. Tester depuis le frontend
# Ouvrir http://localhost:5173
# Accepter les consentements dans le banner RGPD
# Vérifier dans les logs backend que timestamp, ip, user_agent sont bien capturés

# 4. Vérifier en BDD
psql -d hub_chantier -c "SELECT id, email, consent_timestamp, consent_ip_address FROM users WHERE consent_timestamp IS NOT NULL;"
```

**Temps estimé** : 2 heures

---

## 🟡 FINDING B-01 : État Pointage en sessionStorage (RECOMMANDÉ)

### Option 1 : Migrer vers sessionStorage (Simple)

**Fichier** : `/Users/aptsdae/Hub-Chantier/frontend/src/hooks/useClockCard.ts`

```typescript
// AVANT
const CLOCK_STORAGE_KEY = 'hub_chantier_clock_state'
localStorage.setItem(CLOCK_STORAGE_KEY, JSON.stringify(state))

// APRÈS
const CLOCK_STORAGE_KEY = 'hub_chantier_clock_state'
sessionStorage.setItem(CLOCK_STORAGE_KEY, JSON.stringify(state))
// ✅ Session uniquement (disparaît à la fermeture)
```

**Avantages** :
- ✅ État nettoyé automatiquement à la fermeture
- ✅ Moins de risque de désynchronisation
- ✅ Changement minimal (1 ligne)

**Inconvénient** :
- ⚠️ Utilisateur perd l'état s'il ferme l'onglet (acceptable pour un pointage)

### Option 2 : Source de vérité côté serveur (Robuste)

**Frontend** : Supprimer complètement le localStorage
```typescript
// useClockCard.ts
const [clockState, setClockState] = useState<ClockState | null>(null)

useEffect(() => {
  // ✅ Récupérer l'état depuis le backend au chargement
  const fetchClockState = async () => {
    try {
      const response = await api.get('/api/pointages/current')
      setClockState(response.data)
    } catch (error) {
      setClockState(null)
    }
  }

  fetchClockState()
}, [])

const handleClockIn = async () => {
  const response = await api.post('/api/pointages/clock-in')
  setClockState(response.data) // ✅ État vient du serveur
}
```

**Backend** : Endpoint `/api/pointages/current`
```python
@router.get("/current")
async def get_current_pointage(
    current_user: User = Depends(get_current_user)
):
    # Récupérer le pointage en cours (non terminé) de l'utilisateur
    pointage = await pointage_repository.find_active_by_user(current_user.id)

    if pointage and not pointage.heure_depart:
        return {
            "isClockedIn": True,
            "clockInTime": pointage.heure_arrivee.strftime("%H:%M"),
            "chantierId": pointage.chantier_id
        }
    else:
        return {
            "isClockedIn": False,
            "clockInTime": None,
            "chantierId": None
        }
```

**Avantages** :
- ✅ Source de vérité unique (backend)
- ✅ Impossible de manipuler l'heure côté client
- ✅ Synchronisation multi-onglets automatique

**Inconvénient** :
- ⚠️ Requiert un appel API au chargement (latence +50ms)

**Temps estimé** : Option 1 = 30min, Option 2 = 2h

---

## 🟢 FINDING B-02 : Nettoyer Code Firebase (OPTIONNEL)

### Option 1 : Supprimer complètement (si non utilisé)

```bash
# Supprimer le fichier
rm frontend/src/services/firebase.ts
rm frontend/src/services/firebase.test.ts

# Supprimer les dépendances dans package.json
cd frontend
npm uninstall firebase

# Supprimer les variables d'environnement dans .env
# Supprimer toutes les lignes VITE_FIREBASE_*
```

**Vérifier** :
```bash
# Rechercher les imports firebase
grep -r "from './firebase'" frontend/src
grep -r "firebase" frontend/src

# Si aucune occurrence, OK pour supprimer
```

### Option 2 : Désactiver proprement (si prévu pour plus tard)

**Fichier** : `/Users/aptsdae/Hub-Chantier/frontend/src/services/firebase.ts`

```typescript
// Début du fichier
const FIREBASE_ENABLED = false // ✅ Flag pour désactiver

export const isFirebaseConfigured = (): boolean => {
  return FIREBASE_ENABLED && Boolean(
    firebaseConfig.apiKey &&
    firebaseConfig.projectId
  )
}

// Retourner des stubs si désactivé
export const requestNotificationPermission = async (): Promise<string | null> => {
  if (!FIREBASE_ENABLED) {
    console.log('[Firebase] Désactivé')
    return null
  }
  // ... code normal
}
```

**Résultat** :
- ✅ Aucun log "Firebase non configuré"
- ✅ Code reste disponible pour activation future
- ✅ Pas d'impact sur l'application

**Temps estimé** : 15 minutes

---

## 📋 CHECKLIST DE VALIDATION

### Après FINDING M-01 (Timestamp RGPD)
- [ ] Migration Alembic appliquée sans erreur
- [ ] Consentements sauvegardés avec timestamp en BDD
- [ ] Frontend envoie bien userAgent et timestamp
- [ ] Backend capture bien l'IP du client
- [ ] Logs backend montrent les métadonnées
- [ ] Tester avec plusieurs utilisateurs
- [ ] Vérifier dans PostgreSQL que les données sont bien persistées

### Après FINDING B-01 (Pointage)
- [ ] État pointage ne persiste plus après fermeture onglet (si sessionStorage)
- [ ] OU État pointage toujours cohérent après rechargement (si source serveur)
- [ ] Tester avec plusieurs onglets ouverts (synchronisation)
- [ ] Vérifier qu'un utilisateur ne peut pas manipuler son heure

### Après FINDING B-02 (Firebase)
- [ ] Aucun log "Firebase non configuré" dans la console
- [ ] Application démarre normalement
- [ ] Aucun import Firebase cassé

---

## 🚀 ORDRE D'EXÉCUTION RECOMMANDÉ

### Jour 1 : FINDING M-01 (Obligatoire - 2h)
1. Modifier interface `ConsentPreferences` (frontend)
2. Modifier fonction `setConsents()` (frontend)
3. Créer migration Alembic (backend)
4. Modifier endpoint `/consents` (backend)
5. Tester bout-en-bout
6. Valider en BDD

### Jour 2 : FINDING B-01 (Recommandé - 30min)
1. Remplacer `localStorage` par `sessionStorage` dans `useClockCard.ts`
2. Tester le pointage (arrivée/départ)
3. Vérifier que l'état disparaît après fermeture

### Jour 3 : FINDING B-02 (Optionnel - 15min)
1. Ajouter flag `FIREBASE_ENABLED = false`
2. Vérifier logs propres
3. Documenter pour activation future

---

## 📞 AIDE & SUPPORT

**Blocage sur FINDING M-01 ?**
Vérifier que :
- La colonne `consent_timestamp` existe bien en BDD
- L'endpoint `/api/auth/consents` accepte les nouveaux champs
- Le frontend envoie bien le payload avec `timestamp` et `userAgent`

**Blocage sur FINDING B-01 ?**
Si Option 2 (source serveur) choisie :
- Créer l'endpoint `/api/pointages/current`
- Tester avec `curl http://localhost:8000/api/pointages/current` (avec cookie auth)
- Vérifier que le pointage actif est bien retourné

**Questions sur l'architecture ?**
Référez-vous à :
- `docs/architecture/CLEAN_ARCHITECTURE.md`
- `SECURITY-AUDIT-FRONTEND-28JAN2026.md` (rapport complet)

---

## ✅ VALIDATION FINALE

**Après toutes les corrections** :
1. Relancer l'audit de sécurité :
   - Vérifier que les 3 findings sont résolus
   - Score devrait passer à 9.5/10 ou 10/10

2. Tests manuels :
   - Tester le banner RGPD (accepter/refuser/personnaliser)
   - Vérifier que les timestamps sont bien enregistrés
   - Tester le pointage (arrivée/départ)
   - Vérifier les logs propres (pas de warning Firebase)

3. Tests automatisés :
   - `cd backend && pytest tests/unit -v`
   - `cd frontend && npm run test`

4. Prêt pour production ✅

---

*Document créé le 28 janvier 2026*
*Référence audit : SECURITY-AUDIT-FRONTEND-28JAN2026.md*
