## 15. SECURITE ET CONFORMITE

### 15.1 Authentification

La connexion s'effectue de maniere securisee par SMS (code OTP) ou par identifiants classiques (email + mot de passe). La revocation des acces est instantanee et n'affecte pas les donnees historiques.

### 15.2 Protection des donnees

| Mesure | Description | Status |
|--------|-------------|--------|
| Chiffrement en transit | HTTPS/TLS 1.3 pour toutes les communications | ✅ |
| Chiffrement au repos | Donnees chiffrees AES-256 sur les serveurs | ✅ |
| Sauvegarde | Backup quotidien avec retention 30 jours minimum | ✅ |
| RGPD | Conformite totale, droit d'acces et droit a l'oubli | ✅ |
| Hebergement | Serveurs en Europe (France) certifies ISO 27001 | ✅ |
| Journalisation | Logs d'audit de toutes les actions sensibles | ✅ |
| Protection CSRF | Token CSRF pour requetes mutables (POST/PUT/DELETE) | ✅ |
| Consentement RGPD | Banniere de consentement pour geolocalisation, notifications, analytics | ✅ |
| API Consentements | Endpoints GET/POST /api/auth/consents pour gestion consentements | ✅ |
| Consentement avant login | Possibilite de donner/retirer consentement meme sans authentification | ✅ |

### 15.3 Mode Offline

L'application mobile permet de consulter le planning, saisir les heures, remplir les formulaires et consulter les plans meme sans connexion internet. La synchronisation s'effectue automatiquement au retour de la connectivite, avec gestion des conflits.

### 15.4 Niveaux de confidentialite

| Niveau | Acces | Exemples de donnees |
|--------|-------|---------------------|
| Public chantier | Tous les affectes au chantier | Plans, consignes, planning |
| Restreint chef | Chefs + Conducteurs + Admin | Documents techniques |
| Confidentiel | Conducteurs + Admin | Budgets, contrats, situations |
| Secret | Admin uniquement | Documents RH, donnees sensibles |

### 15.5 Validation qualite (29 janvier 2026)

Audit complet du backend realise avec 7 agents de validation (4 rounds iteratifs).

| Metrique | Resultat |
|----------|----------|
| Tests unitaires backend | 2932 pass, 0 fail, 0 xfail |
| Couverture backend | 85% |
| Findings CRITICAL | 0 |
| Findings HIGH | 0 |
| architect-reviewer | 8/10 PASS |
| code-reviewer | 8/10 APPROVED |
| security-auditor | 8/10 PASS (RGPD PASS, OWASP PASS) |

Corrections appliquees :
- Escalade de privileges via register endpoint (champ role supprime)
- Path traversal incomplet (exists/move/copy proteges)
- IDOR sur GET /users/{id} (controle d'acces ajoute)
- Rate limiting bypassable via X-Forwarded-For (TRUSTED_PROXIES externalise)
- SessionLocal() dans routes (toutes migrees vers Depends(get_db))
- EventBus reecrit en API statique class-level
- N+1 query elimine dans chantier_provider
- 12 fichiers de tests ajoutes pour atteindre 85% couverture

---