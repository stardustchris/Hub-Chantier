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

## Sauvegarde de la base de donnees

```bash
# Backup
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U hubchantier hub_chantier > backup_$(date +%Y%m%d).sql

# Restore
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T db \
  psql -U hubchantier hub_chantier
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
