## 14. INTEGRATIONS

### 14.1 ERP compatibles

| ERP | Import | Export | Donnees synchronisees |
|-----|--------|--------|----------------------|
| Costructor | ✅ | ✅ | Chantiers, heures, documents, taches |
| Graneet | ✅ | ✅ | Chantiers, heures, documents |

### 14.2 Flux de donnees

| Donnees | Direction | Frequence | Mode |
|---------|-----------|-----------|------|
| Chantiers | ERP → App | Temps reel ou quotidien | Automatique |
| Feuilles d'heures | App → ERP | Quotidien/Hebdo/Mensuel | Automatique |
| Documents | ERP ↔ App | A la demande | Automatique |
| Taches | ERP → App | Import initial | Manuel |
| Variables paie | App → ERP | Hebdomadaire | Automatique |

### 14.3 Canaux de notification

| Canal | Utilisation | Delai |
|-------|-------------|-------|
| Push mobile | Affectations, validations, alertes, memos | Temps reel |
| Push meteo | Alertes meteo vigilance (vent, orages, canicule, verglas) | Temps reel |
| SMS | Invitations, urgences critiques | Temps reel |
| Email | Rapports, exports, recapitulatifs hebdo | Differe |

### 14.4 API Publique v1 ✅

**Status**: Implémenté (2026-01-28)

#### API-01: Authentification par clés API ✅

**Description**: Système d'authentification par clés API (hbc_xxx) pour permettre aux systèmes externes d'accéder à l'API Hub Chantier de manière sécurisée et programmatique.

**Fonctionnalités**:
- Génération de clés API cryptographiquement sécurisées (256 bits)
- Authentification via header `Authorization: Bearer hbc_xxx...`
- Gestion de permissions granulaires (scopes: read, write, chantiers:*, planning:*, etc.)
- Expiration configurable (défaut: 90 jours)
- Révocation instantanée
- Audit trail complet (création, dernière utilisation, révocation)
- Rate limiting par clé (1000 req/heure configurables)

**Sécurité**:
- Secrets JAMAIS stockés en clair (hash SHA256)
- Génération via `secrets.token_urlsafe()` (CSPRNG)
- Clés révoquées immédiatement rejetées
- Isolation stricte par utilisateur (un utilisateur ne peut révoquer que ses clés)
- Conformité RGPD (CASCADE DELETE, traçabilité, minimisation données)

**UI de gestion**:
- Page `/api-keys` dans l'application
- Liste des clés actives avec statuts (active, révoquée, expirée, expire bientôt)
- Création de clé avec formulaire (nom, description, scopes, expiration)
- Affichage du secret UNE SEULE FOIS avec copie presse-papier
- Révocation avec confirmation

**Exemple d'utilisation**:
```bash
# Créer une clé via UI → copier le secret

# Utiliser la clé pour accéder à l'API
curl -H "Authorization: Bearer hbc_xxxxxxxxxxxxx" \
     https://api.hub-chantier.fr/api/v1/chantiers
```

**Endpoints**:
- `POST /api/auth/api-keys` - Créer une clé (JWT auth requis)
- `GET /api/auth/api-keys` - Lister mes clés
- `DELETE /api/auth/api-keys/{id}` - Révoquer une clé

**Authentification acceptée**:
- JWT Token (eyJ...) - Utilisateurs de l'application web/mobile
- API Key (hbc_...) - Systèmes externes, scripts, intégrations

**Phase 2 prévue**:
- Rate limiting Redis (protection DoS)
- Limite clés par utilisateur (10 max)
- Logs structurés JSON pour SOC
- Webhooks pour événements

**Tests**: 92 tests unitaires, 97% couverture
**Architecture**: Clean Architecture, séparation Domain/Application/Infrastructure
**Audits**: Security audit PASS (88/100, 0 finding critique), Code review APPROVED (100/100)

---