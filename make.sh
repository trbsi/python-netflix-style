#!/usr/bin/env bash
# automationapp.sh - Docker + Django helper script

set -e  # Exit immediately if a command fails

DOCKER_DIR="./docker"
DJANGO_CONTAINER="automationapp-django"
WORKER="automationapp-celery-worker"
BEAT="automationapp-celery-beat"
NGINX="automationapp-nginx-proxy"

# Functions
builddocker() {
    echo "Building and starting Docker containers..."
    cd "$DOCKER_DIR"
    docker compose up -d --build
    cd - >/dev/null
}

migrate() {
    echo "Running Django migrations..."
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py migrate
}

makemigrations() {
    echo "Creating Django migrations..."
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py makemigrations
}

seed() {
    echo "Seeding..."
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py seed_database_command local --truncate
}

test() {
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py test
}

collectstatic() {
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py collectstatic
}

createsuperuser() {
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py createsuperuser
}

copy_category_images() {
    cp -R static/images/ media-asset/
}

restartall() {
  docker restart $DJANGO_CONTAINER
  docker restart $WORKER
  docker restart $BEAT
  docker restart $NGINX
}

cleardockerlogs() {
  sudo find /var/lib/docker/containers/ -name "*.log" -type f -exec truncate -s 0 {} \;
}

clearcache() {
docker exec -it $DJANGO_CONTAINER python manage.py shell -c "
from django.core.cache import cache
from automationapp import settings

for lang, _ in settings.SUPPORTED_LANGUAGES:
    cache.delete(f'frontpage_html_{lang}')
"
}

# Parse command-line argument
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 {builddocker|migrate|makemigrations}"
    exit 1
fi

case "$1" in
    builddocker)
        builddocker
        ;;
    migrate)
        migrate
        ;;
    makemigrations)
        makemigrations
        ;;
    seed)
        seed
        ;;
    test)
        test
        ;;
    collectstatic)
        collectstatic
        ;;
    createsuperuser)
        createsuperuser
        ;;
    copy_category_images)
        copy_category_images
        ;;
    restartall)
        restartall
        ;;
    cleardockerlogs)
        cleardockerlogs
        ;;
    clearcache)
        clearcache
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: $0 {builddocker|migrate|makemigrations}"
        exit 1
        ;;
esac
