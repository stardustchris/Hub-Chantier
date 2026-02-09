# Hub Chantier - Conteneur Backup Automatise avec Cron
FROM alpine:3.19

# Installer dependances
RUN apk add --no-cache \
    bash \
    postgresql16-client \
    docker-cli \
    docker-cli-compose \
    gzip \
    aws-cli \
    tzdata \
    dcron \
    && rm -rf /var/cache/apk/*

# Configuration timezone (Europe/Paris)
ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Creer repertoires
RUN mkdir -p /scripts /var/log /var/backups/hub-chantier

# Copier scripts
COPY scripts/backup.sh /scripts/backup.sh
COPY scripts/docker-backup-cron.sh /scripts/docker-backup-cron.sh

RUN chmod +x /scripts/*.sh

# Configuration cron (tous les jours a 3h00 du matin)
RUN echo "0 3 * * * /scripts/docker-backup-cron.sh" > /etc/crontabs/root

# Healthcheck
HEALTHCHECK --interval=1h --timeout=10s --start-period=10s \
    CMD [ -f /var/log/hub-chantier-backup.log ] || exit 1

# Demarrer cron en foreground
CMD ["crond", "-f", "-l", "2"]
