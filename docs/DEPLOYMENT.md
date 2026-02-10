# Hub Chantier - Guide de Deploiement

> Deploiement sur Scaleway (ou tout VPS Linux) avec Docker, HTTPS et PWA installable.

## Architecture de production

```
Internet
   |
   v
[Scaleway DEV1-S]
   |
   +-- Nginx (port 80/443)
   |     |-- Static files (React build)
   |     |-- SSL (Let's Encrypt)
   |     +-- Proxy /api -> FastAPI
   |
   +-- FastAPI (port 8000 interne)
   |     +-- PostgreSQL (port 5432 interne)
   |
   +-- Certbot (renouvellement SSL auto)
```

## Etape 1 : Creer une instance Scaleway

1. Aller sur https://console.scaleway.com
2. Creer un compte (CB requise)
3. **Instances** > **Creer une instance**
   - Type : **DEV1-S** (2 vCPU, 2 Go RAM, 20 Go SSD) ~4 EUR/mois
   - Image : **Ubuntu 22.04**
   - Region : **Paris** (fr-par-1)
   - Ajouter votre cle SSH publique
4. Noter l'**IP publique** de l'instance

## Etape 2 : Acheter un domaine

Options recommandees :
- **OVH** (~8 EUR/an pour un .fr)
- **Gandi** (~12 EUR/an)
- **Scaleway Domains** (si disponible)

Configurer le DNS :
```
Type A    hub.votredomaine.fr    -> IP_SCALEWAY
```

Attendre la propagation DNS (quelques minutes a quelques heures).

## Etape 3 : Initialiser le serveur

```bash
# Depuis votre machine locale
ssh root@IP_SCALEWAY 'bash -s' < scripts/init-server.sh
```

Ce script installe Docker, configure le firewall (SSH/HTTP/HTTPS), cree un swap de 2 Go et un utilisateur `deploy`.

## Etape 4 : Deployer l'application

```bash
# Se connecter au serveur
ssh deploy@IP_SCALEWAY

# Cloner le projet
git clone https://github.com/stardustchris/Hub-Chantier.git ~/hub-chantier
cd ~/hub-chantier

# Configurer l'environnement
cp .env.production.example .env.production
nano .env.production
```

### Variables a configurer dans `.env.production`

| Variable | Comment generer |
|----------|-----------------|
| `DOMAIN` | Votre domaine (ex: hub.gregconstruction.fr) |
| `POSTGRES_PASSWORD` | `python3 -c "import secrets; print(secrets.token_urlsafe(24))"` |
| `SECRET_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ENCRYPTION_KEY` | `python3 -c "import secrets; print(secrets.token_hex(16))"` (32 chars exactement) |
| `CERTBOT_EMAIL` | Votre email (notifications expiration SSL) |

### Lancer le deploiement

```bash
bash scripts/deploy.sh
```

Le script :
1. Verifie les prerequis et variables
2. Build les images Docker
3. Obtient le certificat SSL via Let's Encrypt
4. Lance tous les services
5. Verifie la sante de chaque service

## Etape 5 : Verifier

- **Site web** : https://hub.votredomaine.fr
- **API health** : https://hub.votredomaine.fr/api/health
- **PWA installable** : Sur mobile, le navigateur propose "Ajouter a l'ecran d'accueil"

## Commandes utiles

```bash
# Voir les logs
docker compose -f docker-compose.prod.yml logs -f

# Logs d'un service
docker compose -f docker-compose.prod.yml logs -f api

# Redemarrer
docker compose -f docker-compose.prod.yml restart

# Arreter
docker compose -f docker-compose.prod.yml down

# Acceder a la base de donnees
docker compose -f docker-compose.prod.yml exec db psql -U hubchantier hub_chantier

# Mettre a jour (apres git pull)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

## Sauvegarde et restauration de la base de donnees

Hub Chantier inclut un systeme complet de backup automatise avec rotation et support S3.

### Option A : Backups automatiques avec Docker (recommande)

Active le service de backup automatise via Docker Compose profile:

```bash
# Activer le service backup-cron (backup quotidien a 3h00)
docker compose -f docker-compose.prod.yml --profile backup up -d backup-cron

# Verifier les logs
docker logs hub-chantier-backup

# Voir tous les backups
ls -lh /var/backups/hub-chantier/
```

Le service backup-cron execute automatiquement:
- Backup quotidien a 3h00 du matin
- Compression gzip
- Rotation automatique (conservation 7 jours par defaut)
- Upload S3 optionnel

### Option B : Crontab sur l'hote

Alternative si vous preferez un cron sur l'hote plutot qu'un conteneur:

```bash
# Installer le crontab
crontab -e

# Ajouter cette ligne (backup quotidien a 3h00)
0 3 * * * cd /home/deploy/hub-chantier && /home/deploy/hub-chantier/scripts/backup.sh >> /var/log/hub-chantier-backup.log 2>&1
```

### Backup manuel

```bash
# Backup local uniquement
./scripts/backup.sh

# Backup avec upload S3
./scripts/backup.sh --upload-s3
```

Le script cree un fichier compresse:
- Chemin: `/var/backups/hub-chantier/hub_chantier_backup_YYYYMMDD_HHMMSS.sql.gz`
- Rotation automatique: garde les 7 derniers jours
- Compression: gzip (facteur ~10x)
- Logs: timestamps et tailles

### Restauration depuis backup

**ATTENTION**: Cette operation ecrase toutes les donnees existantes.

```bash
# Restaurer depuis le dernier backup local
./scripts/restore.sh --latest

# Restaurer depuis un fichier specifique
./scripts/restore.sh /var/backups/hub-chantier/hub_chantier_backup_20260208_030000.sql.gz

# Restaurer depuis S3
./scripts/restore.sh --from-s3 hub_chantier_backup_20260208_030000.sql.gz
```

Le script de restauration:
1. Demande confirmation (tapez `OUI` en majuscules)
2. Cree un backup de securite automatique
3. Restore la base de donnees
4. Verifie l'integrite post-restauration
5. Affiche un resume avec le chemin du backup de securite

### Configuration S3 (optionnelle)

Pour activer l'upload automatique vers S3 (AWS, Scaleway Object Storage, etc.):

1. Installer AWS CLI dans le conteneur backup (deja inclus) ou sur l'hote:
   ```bash
   pip3 install awscli
   ```

2. Ajouter les variables dans `.env.production`:
   ```bash
   # Scaleway Object Storage (ou AWS S3)
   S3_BACKUP_BUCKET=hub-chantier-backups
   AWS_ACCESS_KEY_ID=votre_access_key
   AWS_SECRET_ACCESS_KEY=votre_secret_key
   AWS_DEFAULT_REGION=fr-par
   S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud

   # Retention (optionnel, defaut: 7 jours)
   BACKUP_RETENTION_DAYS=7
   ```

3. Creer le bucket S3:
   ```bash
   # Avec Scaleway CLI
   scw object bucket create name=hub-chantier-backups region=fr-par

   # Ou via AWS CLI
   aws s3 mb s3://hub-chantier-backups --endpoint-url https://s3.fr-par.scw.cloud
   ```

4. Tester l'upload:
   ```bash
   ./scripts/backup.sh --upload-s3
   ```

La rotation S3 est automatique (meme duree que locale).

### Monitoring des backups

```bash
# Voir les derniers backups locaux
ls -lth /var/backups/hub-chantier/ | head -10

# Voir le dernier log de backup
tail -n 50 /var/log/hub-chantier-backup.log

# Logs du service backup-cron (si Docker)
docker logs hub-chantier-backup --tail 100

# Lister backups S3
aws s3 ls s3://hub-chantier-backups/backups/ --endpoint-url https://s3.fr-par.scw.cloud
```

### Tester la procedure de restauration

Il est recommande de tester regulierement la restauration:

```bash
# 1. Backup actuel
./scripts/backup.sh

# 2. Identifier le dernier backup
LATEST_BACKUP=$(ls -t /var/backups/hub-chantier/hub_chantier_backup_*.sql.gz | head -1)
echo "Dernier backup: $LATEST_BACKUP"

# 3. Tester restore (sur environnement de dev uniquement!)
# NE PAS FAIRE EN PRODUCTION sans raison valable
./scripts/restore.sh "$LATEST_BACKUP"
```

## Renouvellement SSL

Le conteneur Certbot renouvelle automatiquement le certificat toutes les 12h.
Pour forcer un renouvellement :

```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker compose -f docker-compose.prod.yml restart frontend
```

## Cout mensuel estime

| Service | Cout |
|---------|------|
| Instance DEV1-S | ~4 EUR/mois |
| Domaine .fr | ~8 EUR/an (~0.7 EUR/mois) |
| SSL (Let's Encrypt) | Gratuit |
| **Total** | **~5 EUR/mois** |

## Passage a l'echelle

Si besoin de plus de ressources :
- **DEV1-M** (4 Go RAM, 40 Go SSD) : ~8 EUR/mois
- **GP1-XS** (4 vCPU, 16 Go RAM) : ~18 EUR/mois
- Scaleway Managed PostgreSQL si > 50 utilisateurs reguliers
