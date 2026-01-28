# Webhooks - Hub Chantier

Système de webhooks pour intégrations temps réel (ERP, Slack, automation).

## 🚀 Quick Start

### Activer le Nettoyage Automatique (GDPR)

Dans `backend/main.py`, ajouter au démarrage:

```python
from shared.infrastructure.webhooks import start_cleanup_scheduler, stop_cleanup_scheduler

@app.on_event("startup")
async def startup_event():
    # Démarre le nettoyage automatique (tous les jours à 3h)
    start_cleanup_scheduler()
    logger.info("✅ Webhook cleanup scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    # Arrête proprement le scheduler
    stop_cleanup_scheduler()
```

### Nettoyage Manuel (Cron)

Alternative si vous préférez utiliser cron:

```bash
# Crontab: tous les jours à 3h du matin
0 3 * * * cd /app/backend && python scripts/cleanup_webhook_deliveries.py >> /var/log/webhook_cleanup.log 2>&1
```

Options du script:
```bash
# Dry run (affiche seulement le nombre)
python scripts/cleanup_webhook_deliveries.py --dry-run

# Personnaliser la rétention (défaut: 90 jours)
python scripts/cleanup_webhook_deliveries.py --retention-days 30
```

## 📊 Configuration

### Rate Limiting

Les routes webhooks ont les limites suivantes (par IP):
- `POST /webhooks` - **10/minute** (création)
- `GET /webhooks` - **30/minute** (listing)
- `GET /webhooks/{id}` - **30/minute** (détails)
- `GET /webhooks/{id}/deliveries` - **30/minute** (historique)
- `DELETE /webhooks/{id}` - **20/minute** (suppression)
- `POST /webhooks/{id}/test` - **5/minute** (test)

### Limites Par Utilisateur

- **Maximum 20 webhooks actifs** par utilisateur
- Quota vérifié lors de la création

### Retention Policy (GDPR)

- **90 jours** de rétention des webhook_deliveries
- Nettoyage automatique quotidien (3h du matin)
- Conforme Article 5(1)(e) GDPR (Storage Limitation)

## 🔐 Sécurité

### Protection SSRF

Webhooks bloquent automatiquement les IPs privées:
- `127.0.0.0/8` (localhost)
- `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC1918)
- `169.254.0.0/16` (AWS metadata)
- IPv6 privées

### HTTPS Enforced

Seules les URLs HTTPS sont acceptées (HTTP rejeté).

### HMAC-SHA256

Chaque requête webhook inclut une signature:
```
X-Hub-Chantier-Signature: sha256=<hex_digest>
```

Documentation complète: `docs/WEBHOOK_SIGNATURE_VERIFICATION.md`

### DoS Protection

- Rate limiting (slowapi)
- Timeout 10s par delivery
- Max 50 webhooks concurrents (semaphore)
- Redirect limits (max 3)
- Auto-disable après 10 échecs

## 📈 Monitoring

### Logs

```python
import logging
logger = logging.getLogger('shared.infrastructure.webhooks')
logger.setLevel(logging.INFO)
```

Logs importants:
- `[Cleanup Job] ✅ Nettoyage terminé: X deliveries supprimées`
- `Webhook {id} livré avec succès pour {event_type}`
- `Webhook {id} désactivé après X échecs consécutifs`

### Métriques à Monitorer

- Nombre de deliveries échouées
- Taux de succès par webhook
- Webhooks auto-désactivés
- Temps de réponse moyen
- Quota utilisateurs atteint

## 🧪 Testing

### Test Manuel

```python
from shared.infrastructure.webhooks import run_cleanup_now

# Exécuter le nettoyage immédiatement
run_cleanup_now()
```

### Test Webhook Endpoint

```bash
curl -X POST https://api.hub-chantier.com/api/v1/webhooks/{id}/test \
  -H "Authorization: Bearer <token>"
```

## 📚 Documentation

- **HMAC Verification**: `backend/docs/WEBHOOK_SIGNATURE_VERIFICATION.md`
- **Security Fixes**: `backend/docs/SECURITY_FIXES_PHASE2.md`
- **Migration Guide**: `backend/MIGRATION_GUIDE.md` (refactoring endpoints)

## 🔧 Troubleshooting

### Le nettoyage ne s'exécute pas

1. Vérifier que le scheduler est démarré (logs au startup)
2. Vérifier APScheduler installé: `pip show apscheduler`
3. Forcer l'exécution: `run_cleanup_now()`

### Rate Limit dépassé

Augmenter les limites dans `routes.py`:
```python
@limiter.limit("20/minute")  # Au lieu de 10/minute
```

### Quota webhooks atteint

Modifier `MAX_WEBHOOKS_PER_USER` dans `routes.py`:
```python
MAX_WEBHOOKS_PER_USER = 50  # Au lieu de 20
```

## 🚀 Next Steps (Optional)

### Métriques Avancées

Intégrer Prometheus pour monitoring:
```python
from prometheus_client import Counter, Histogram

webhook_deliveries_total = Counter('webhook_deliveries_total', 'Total deliveries')
webhook_delivery_duration = Histogram('webhook_delivery_duration_seconds', 'Delivery time')
```

### Dashboard

Créer un dashboard admin pour:
- Voir tous les webhooks actifs
- Statistiques de delivery
- Webhooks auto-désactivés
- Alertes sur échecs répétés

### Batch Processing

Pour haute volumétrie:
```python
# Utiliser Celery pour delivery asynchrone
from celery import Celery

@celery.task
def deliver_webhook_task(webhook_id, event_data):
    # Delivery en background
    pass
```

---

**Auteur**: Phase 2 Implementation Team
**Date**: 2026-01-28
**Version**: 1.0
