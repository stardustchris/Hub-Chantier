# Hub Chantier - Guide Rapide Backups

Guide pratique pour configurer et utiliser les backups automatises PostgreSQL.

## TL;DR - Demarrage rapide

### Configuration minimale (backup local uniquement)

```bash
# 1. Activer le service backup automatique
docker compose -f docker-compose.prod.yml --profile backup up -d backup-cron

# 2. Verifier
docker logs hub-chantier-backup
ls -lh /var/backups/hub-chantier/

# 3. Tester backup manuel
./scripts/backup.sh
```

**C'est tout!** Backup quotidien a 3h du matin avec rotation 7 jours.

### Avec stockage externe S3 (recommande production)

```bash
# 1. Configurer .env.production
cat >> .env.production <<EOF
S3_BACKUP_BUCKET=hub-chantier-backups
AWS_ACCESS_KEY_ID=votre_key
AWS_SECRET_ACCESS_KEY=votre_secret
AWS_DEFAULT_REGION=fr-par
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
EOF

# 2. Creer bucket Scaleway
scw object bucket create name=hub-chantier-backups region=fr-par

# 3. Activer backup avec S3
docker compose -f docker-compose.prod.yml --profile backup up -d backup-cron

# 4. Tester upload S3
./scripts/backup.sh --upload-s3
```

---

## Scenarios d'utilisation

### Scenario 1 : Backup manuel avant maintenance

```bash
# Backup avant operation risquee
./scripts/backup.sh

# Noter le nom du fichier cree
ls -lt /var/backups/hub-chantier/ | head -2
```

### Scenario 2 : Restaurer apres incident

```bash
# Lister backups disponibles
ls -lth /var/backups/hub-chantier/

# Restaurer le dernier
./scripts/restore.sh --latest

# Ou restaurer un backup specifique
./scripts/restore.sh /var/backups/hub-chantier/hub_chantier_backup_20260208_030000.sql.gz

# Redemarrer application
docker compose -f docker-compose.prod.yml restart api
```

### Scenario 3 : Migrer vers nouveau serveur

```bash
# Sur ancien serveur
./scripts/backup.sh --upload-s3

# Sur nouveau serveur (apres installation)
./scripts/restore.sh --from-s3 hub_chantier_backup_20260208_030000.sql.gz
```

### Scenario 4 : Tester restauration (mensuel recommande)

```bash
# Sur environnement de TEST uniquement
# 1. Backup actuel
./scripts/backup.sh

# 2. Restaurer
./scripts/restore.sh --latest

# 3. Verifier donnees
docker compose exec db psql -U hubchantier hub_chantier -c "SELECT COUNT(*) FROM utilisateurs;"

# 4. Tester connexion application
curl http://localhost:8000/health
```

---

## Configuration S3 detaillee

### Scaleway Object Storage (gratuit < 75 Go)

#### 1. Creer API Key

Console Scaleway > Identity and Access Management > API Keys

- Permissions: Object Storage Read/Write
- Noter: Access Key ID + Secret Key

#### 2. Creer bucket

```bash
# Option A : Scaleway CLI (recommande)
scw object bucket create name=hub-chantier-backups region=fr-par

# Option B : AWS CLI
aws s3 mb s3://hub-chantier-backups --endpoint-url https://s3.fr-par.scw.cloud
```

#### 3. Configurer .env.production

```bash
S3_BACKUP_BUCKET=hub-chantier-backups
AWS_ACCESS_KEY_ID=SCWXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AWS_DEFAULT_REGION=fr-par
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
BACKUP_RETENTION_DAYS=7
```

#### 4. Tester

```bash
# Test backup avec upload
./scripts/backup.sh --upload-s3

# Verifier presence S3
aws s3 ls s3://hub-chantier-backups/backups/ --endpoint-url https://s3.fr-par.scw.cloud
```

### AWS S3 (alternatif)

Configuration similaire, sans `S3_ENDPOINT_URL`:

```bash
S3_BACKUP_BUCKET=hub-chantier-backups
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxx
AWS_DEFAULT_REGION=eu-west-3
# S3_ENDPOINT_URL=  # Laisser vide pour AWS S3 natif
```

---

## Monitoring et alertes

### Verifier etat backups

```bash
# Derniers backups locaux
ls -lth /var/backups/hub-chantier/ | head -10

# Taille totale
du -sh /var/backups/hub-chantier/

# Dernier backup
LATEST=$(ls -t /var/backups/hub-chantier/hub_chantier_backup_*.sql.gz | head -1)
echo "Dernier backup: $LATEST"
stat "$LATEST"
```

### Logs

```bash
# Logs service Docker
docker logs hub-chantier-backup --tail 100 -f

# Logs fichier (si cron hote)
tail -f /var/log/hub-chantier-backup.log

# Derniere execution
tail -n 20 /var/log/hub-chantier-backup.log | grep "Backup termine"
```

### Alertes (optionnel)

Script simple pour alertes email si backup echoue:

```bash
#!/bin/bash
# /home/deploy/hub-chantier/scripts/check-backup-alert.sh

BACKUP_DIR="/var/backups/hub-chantier"
LATEST=$(find "$BACKUP_DIR" -name "hub_chantier_backup_*.sql.gz" -mtime -1 | wc -l)

if [ "$LATEST" -eq 0 ]; then
    echo "ALERTE: Aucun backup cree dans les dernieres 24h" | \
    mail -s "Hub Chantier - Backup Failed" admin@votredomaine.fr
fi
```

Ajouter a cron (verification quotidienne 9h):
```bash
0 9 * * * /home/deploy/hub-chantier/scripts/check-backup-alert.sh
```

---

## Troubleshooting

### Probleme 1 : Backup echoue

**Symptome**: Script backup.sh retourne erreur

**Diagnostic**:
```bash
# Verifier conteneur DB up
docker compose -f docker-compose.prod.yml ps db

# Tester connexion
docker compose -f docker-compose.prod.yml exec db pg_isready -U hubchantier

# Tester pg_dump direct
docker compose -f docker-compose.prod.yml exec db pg_dump -U hubchantier hub_chantier | head -20
```

**Solutions**:
- Conteneur arrete: `docker compose -f docker-compose.prod.yml up -d db`
- Mauvais credentials: Verifier `POSTGRES_USER` et `POSTGRES_PASSWORD` dans `.env.production`
- Espace disque plein: `df -h` puis nettoyer ou augmenter volume

### Probleme 2 : Upload S3 echoue

**Symptome**: Backup local OK mais "AVERTISSEMENT: Echec upload S3"

**Diagnostic**:
```bash
# Verifier credentials S3
aws s3 ls s3://hub-chantier-backups --endpoint-url https://s3.fr-par.scw.cloud

# Tester upload manuel
echo "test" > /tmp/test.txt
aws s3 cp /tmp/test.txt s3://hub-chantier-backups/test.txt --endpoint-url https://s3.fr-par.scw.cloud
```

**Solutions**:
- Credentials invalides: Regenerer API Key Scaleway
- Bucket inexistant: Creer avec `scw object bucket create`
- Permissions: Verifier ACL bucket (Read/Write requis)
- Region incorrecte: Verifier `AWS_DEFAULT_REGION` (fr-par pour Scaleway Paris)

### Probleme 3 : Restore echoue

**Symptome**: Script restore.sh retourne erreur pendant restauration

**Diagnostic**:
```bash
# Verifier integrite backup
gunzip -t /var/backups/hub-chantier/hub_chantier_backup_20260208_030000.sql.gz

# Inspecter contenu
gunzip -c /var/backups/hub-chantier/hub_chantier_backup_20260208_030000.sql.gz | head -100
```

**Solutions**:
- Backup corrompu: Utiliser backup anterieur ou backup S3
- Connexion DB perdue: Redemarrer conteneur `docker compose restart db`
- Schema incompatible: Verifier version PostgreSQL source/destination

### Probleme 4 : Espace disque sature

**Symptome**: `/var/backups` plein, backups echouent

**Diagnostic**:
```bash
# Espace disque
df -h /var/backups

# Taille backups
du -sh /var/backups/hub-chantier/*
```

**Solutions**:
```bash
# Reduire retention (ex: 3 jours au lieu de 7)
echo "BACKUP_RETENTION_DAYS=3" >> .env.production
docker compose -f docker-compose.prod.yml --profile backup restart backup-cron

# Nettoyer backups anciens manuellement
find /var/backups/hub-chantier -name "hub_chantier_backup_*.sql.gz" -mtime +3 -delete

# Migrer vers S3 et reduire retention locale
# Garder 2 jours local + 30 jours S3
```

### Probleme 5 : Service backup-cron ne demarre pas

**Symptome**: `docker compose --profile backup up -d` echoue

**Diagnostic**:
```bash
# Voir erreurs build
docker compose -f docker-compose.prod.yml build backup-cron

# Logs conteneur
docker logs hub-chantier-backup
```

**Solutions**:
- Erreur build Dockerfile: Verifier syntaxe `docker/backup-cron/Dockerfile`
- Socket Docker inaccessible: Verifier volume `/var/run/docker.sock`
- Scripts manquants: Verifier presence `scripts/backup.sh` et permissions execute

---

## Checklist maintenance mensuelle

- [ ] Verifier derniers backups locaux: `ls -lth /var/backups/hub-chantier/ | head -5`
- [ ] Verifier backups S3: `aws s3 ls s3://hub-chantier-backups/backups/ --endpoint-url https://s3.fr-par.scw.cloud`
- [ ] Controler espace disque: `df -h /var/backups`
- [ ] Lire logs backup: `tail -100 /var/log/hub-chantier-backup.log`
- [ ] Tester restauration (environnement test): `./scripts/restore.sh --latest`
- [ ] Verifier integrite base restauree: connexion + requetes test
- [ ] Documenter test restauration: date, duree, resultats

---

## FAQ

### Q: Combien de temps garde-t-on les backups?

**R**: Par defaut:
- **Local**: 7 jours (configurable via `BACKUP_RETENTION_DAYS`)
- **S3**: 7 jours (meme rotation que local)

Recommandations selon usage:
- **Dev/Test**: 3-7 jours local suffit
- **Production PME**: 7 jours local + 30 jours S3
- **Production critique**: 14 jours local + 90 jours S3 + archivage annuel

### Q: Quelle taille font les backups?

**R**: Pour Hub Chantier (base typique 500 Mo):
- **Non compresse**: ~500 Mo
- **Compresse (gzip)**: ~50 Mo (facteur 10x)
- **7 jours**: ~350 Mo total
- **30 jours**: ~1.5 Go total

### Q: Backup impacte-t-il les performances?

**R**: Impact minimal:
- pg_dump utilise une transaction snapshot (pas de lock ecriture)
- Compression CPU-intensive mais sur court instant (~30s pour 500 Mo)
- Backup a 3h du matin = hors heures ouvrees
- Aucun impact utilisateur perceptible

### Q: Peut-on restaurer sur version PostgreSQL differente?

**R**: Oui, avec precautions:
- **Meme majeure** (16.1 -> 16.3): Toujours compatible
- **Mineure superieure** (15 -> 16): Generalement OK (tester en dev)
- **Majeure inferieure** (16 -> 15): Risque, peut echouer

Recommandation: Garder meme version majeure PostgreSQL source/destination.

### Q: Backup fonctionne-t-il avec plusieurs bases?

**R**: Scripts actuels backupent une seule base (`$POSTGRES_DB`).

Pour plusieurs bases:
```bash
# Modifier backup.sh pour lister toutes les bases
docker compose exec db psql -U hubchantier -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;"

# Ou backup complet cluster PostgreSQL
docker compose exec db pg_dumpall -U hubchantier | gzip > cluster_backup.sql.gz
```

### Q: Comment archiver backups long terme (> 90 jours)?

**R**: Strategie 3-2-1:
- **3 copies**: Production + S3 + Archive
- **2 supports**: Disque local + Cloud
- **1 hors-site**: S3 externe

Configuration S3 lifecycle:
```bash
# Scaleway Object Storage - Glacier (archivage pas de glace)
aws s3api put-bucket-lifecycle-configuration \
  --bucket hub-chantier-backups \
  --endpoint-url https://s3.fr-par.scw.cloud \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json
{
  "Rules": [
    {
      "Id": "ArchiveOldBackups",
      "Status": "Enabled",
      "Prefix": "backups/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

**Cout Glacier Scaleway**: ~0.002 EUR/Go/mois (5x moins cher que standard)

---

## Ressources

- **Documentation complete**: `docs/DEPLOYMENT.md` (section backups)
- **Scripts**: `scripts/README.md`
- **Support Scaleway Object Storage**: https://www.scaleway.com/en/docs/storage/object/
- **PostgreSQL pg_dump**: https://www.postgresql.org/docs/16/app-pgdump.html
