# Hub Chantier - Scripts de Gestion

Ce repertoire contient les scripts de deploiement, backup et maintenance du projet Hub Chantier.

## Scripts disponibles

### Deploiement

#### `deploy.sh`
Script de deploiement en production.

```bash
bash scripts/deploy.sh
```

**Actions**:
1. Verification prerequis (Docker, .env.production)
2. Build images Docker
3. Configuration SSL (Let's Encrypt)
4. Lancement services
5. Health check

**Prerequis**: `.env.production` configure avec domaine et secrets.

#### `init-server.sh`
Initialisation serveur VPS (Scaleway, etc.).

```bash
ssh root@IP_SERVEUR 'bash -s' < scripts/init-server.sh
```

**Actions**:
1. Mise a jour systeme
2. Installation Docker + Docker Compose
3. Configuration firewall (UFW)
4. Creation swap 2 Go
5. Creation utilisateur `deploy`

**Utilisation**: Une seule fois lors de la premiere configuration serveur.

#### `start-dev.sh`
Demarrage environnement de developpement local.

```bash
bash scripts/start-dev.sh
```

### Backups

#### `backup.sh`
Backup automatise PostgreSQL avec rotation et support S3.

```bash
# Backup local uniquement
./scripts/backup.sh

# Backup avec upload S3
./scripts/backup.sh --upload-s3
```

**Fonctionnalites**:
- pg_dump compresse (gzip)
- Rotation automatique (7 jours par defaut)
- Upload S3 optionnel (AWS, Scaleway Object Storage)
- Logs detailles avec timestamps
- Exit codes appropries pour monitoring

**Configuration**:

Variables dans `.env.production`:
```bash
BACKUP_RETENTION_DAYS=7               # Jours de retention locale
S3_BACKUP_BUCKET=mon-bucket           # Bucket S3 (optionnel)
AWS_ACCESS_KEY_ID=xxx                 # Credentials S3
AWS_SECRET_ACCESS_KEY=xxx
AWS_DEFAULT_REGION=fr-par
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud  # Pour Scaleway
```

**Format fichiers**:
- Nom: `hub_chantier_backup_YYYYMMDD_HHMMSS.sql.gz`
- Emplacement: `/var/backups/hub-chantier/`
- Compression: gzip (~10x)

**Monitoring**:
```bash
# Voir les backups
ls -lth /var/backups/hub-chantier/

# Logs
tail -f /var/log/hub-chantier-backup.log
```

#### `restore.sh`
Restauration base de donnees depuis backup.

```bash
# Restaurer dernier backup
./scripts/restore.sh --latest

# Restaurer fichier specifique
./scripts/restore.sh /path/to/backup.sql.gz

# Restaurer depuis S3
./scripts/restore.sh --from-s3 hub_chantier_backup_20260208_030000.sql.gz
```

**Securites**:
1. Confirmation interactive (taper `OUI` en majuscules)
2. Backup automatique avant restoration
3. Verification integrite post-restore
4. Logs detailles

**ATTENTION**: Ecrase toutes les donnees existantes. Ne pas utiliser a la legere.

#### `docker-backup-cron.sh`
Wrapper pour execution cron dans conteneur Docker.

Ce script est appele automatiquement par le service `backup-cron` du docker-compose.prod.yml.

**Configuration cron**: Tous les jours a 3h00 du matin (Europe/Paris).

### Architecture et Verification

#### `check-architecture.sh`
Verification conformite Clean Architecture.

```bash
bash scripts/check-architecture.sh
```

Verifie:
- Respect des couches (Domain, Application, Infrastructure, Presentation)
- Pas d'imports invalides
- Isolation des modules

#### `generate-module.sh`
Generateur de modules conformes Clean Architecture.

```bash
bash scripts/generate-module.sh nom_module
```

Cree la structure complete avec templates.

## Backups automatises

### Option A : Service Docker (recommande)

Active le service backup-cron dans docker-compose.prod.yml:

```bash
# Activer
docker compose -f docker-compose.prod.yml --profile backup up -d backup-cron

# Logs
docker logs hub-chantier-backup -f

# Stopper
docker compose -f docker-compose.prod.yml --profile backup down
```

**Avantages**:
- Isole dans conteneur
- Logs centralises
- Gestion via Docker Compose
- Timezone Europe/Paris configure

### Option B : Crontab hote

Alternative avec cron sur le serveur hote:

```bash
# Editer crontab
crontab -e

# Ajouter (backup quotidien 3h)
0 3 * * * cd /home/deploy/hub-chantier && /home/deploy/hub-chantier/scripts/backup.sh --upload-s3 >> /var/log/hub-chantier-backup.log 2>&1
```

**Avantages**:
- Pas de conteneur supplementaire
- Controle direct via crontab
- Flexibilite horaires

## Configuration S3 (Scaleway Object Storage)

### 1. Creer bucket

```bash
# Avec Scaleway CLI
scw object bucket create name=hub-chantier-backups region=fr-par

# Ou AWS CLI
aws s3 mb s3://hub-chantier-backups --endpoint-url https://s3.fr-par.scw.cloud
```

### 2. Obtenir credentials

Dans console Scaleway:
1. **Identity and Access Management** > **API Keys**
2. Creer une cle avec acces Object Storage
3. Noter Access Key ID et Secret Key

### 3. Configurer .env.production

```bash
S3_BACKUP_BUCKET=hub-chantier-backups
AWS_ACCESS_KEY_ID=SCWXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AWS_DEFAULT_REGION=fr-par
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
```

### 4. Tester

```bash
./scripts/backup.sh --upload-s3
```

### 5. Verifier

```bash
aws s3 ls s3://hub-chantier-backups/backups/ --endpoint-url https://s3.fr-par.scw.cloud
```

## Maintenance

### Nettoyer vieux backups manuellement

```bash
# Supprimer backups > 30 jours
find /var/backups/hub-chantier -name "hub_chantier_backup_*.sql.gz" -mtime +30 -delete

# S3 (supprimer backups > 30 jours)
aws s3 ls s3://hub-chantier-backups/backups/ --endpoint-url https://s3.fr-par.scw.cloud | \
awk '{if ($1 < "'$(date -d '30 days ago' +%Y-%m-%d)'") print $4}' | \
xargs -I {} aws s3 rm s3://hub-chantier-backups/backups/{} --endpoint-url https://s3.fr-par.scw.cloud
```

### Monitoring espace disque

```bash
# Taille totale backups
du -sh /var/backups/hub-chantier

# Liste par taille
du -h /var/backups/hub-chantier/* | sort -h

# Espace disque disponible
df -h /var/backups
```

### Tester procedure restauration

**IMPORTANT**: A faire regulierement (ex: mensuel) sur environnement de test.

```bash
# 1. Backup actuel
./scripts/backup.sh

# 2. Restore sur base de test
COMPOSE_FILE=docker-compose.yml ./scripts/restore.sh --latest

# 3. Verifier integrite donnees
docker compose exec db psql -U hubchantier hub_chantier -c "SELECT COUNT(*) FROM utilisateurs;"
```

## Couts S3 (Scaleway)

### Object Storage Scaleway

| Volume | Prix/mois | 75 Go backups |
|--------|-----------|---------------|
| Premiers 75 Go | Gratuit | 0 EUR |
| Au-dela | 0.01 EUR/Go | ~0.01 EUR/Go |

**Estimation Hub Chantier** (base ~500 Mo, backups 7 jours):
- Backups comprimes: ~50 Mo x 7 jours = 350 Mo
- Cout mensuel: **0 EUR** (sous quota gratuit)

Meme avec 30 jours retention: ~1.5 Go = **0 EUR**.

### AWS S3 (alternatif)

| Region | Prix/mois (premier To) |
|--------|------------------------|
| eu-west-3 (Paris) | 0.024 USD/Go |

**Estimation**: ~1.5 Go x 0.024 = **0.04 USD/mois** (~0.03 EUR)

**Recommandation**: Scaleway Object Storage (gratuit sous 75 Go).

## Support et Troubleshooting

### Backup echoue

```bash
# Verifier conteneur DB
docker compose -f docker-compose.prod.yml ps db

# Verifier connexion
docker compose -f docker-compose.prod.yml exec db pg_isready -U hubchantier

# Logs
docker compose -f docker-compose.prod.yml logs db

# Tester pg_dump manuellement
docker compose -f docker-compose.prod.yml exec db pg_dump -U hubchantier hub_chantier | head -20
```

### Upload S3 echoue

```bash
# Verifier credentials
aws s3 ls s3://hub-chantier-backups --endpoint-url https://s3.fr-par.scw.cloud

# Tester upload manuel
echo "test" > /tmp/test.txt
aws s3 cp /tmp/test.txt s3://hub-chantier-backups/test.txt --endpoint-url https://s3.fr-par.scw.cloud

# Verifier permissions bucket
aws s3api get-bucket-acl --bucket hub-chantier-backups --endpoint-url https://s3.fr-par.scw.cloud
```

### Restore echoue

```bash
# Verifier integrite backup
gunzip -t /var/backups/hub-chantier/backup.sql.gz

# Verifier contenu
gunzip -c /var/backups/hub-chantier/backup.sql.gz | head -50

# Restore manuel (debug)
gunzip -c backup.sql.gz | docker compose -f docker-compose.prod.yml exec -T db psql -U hubchantier hub_chantier
```

## References

- **Documentation deploiement**: `docs/DEPLOYMENT.md`
- **Architecture**: `docs/architecture/CLEAN_ARCHITECTURE.md`
- **Docker Compose prod**: `docker-compose.prod.yml`
- **Configuration**: `.env.production.example`
