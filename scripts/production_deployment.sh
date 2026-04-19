#!/usr/bin/env bash
set -e

DOCKER_CONTAINER="automationapp-django"
WORKER="automationapp-celery-worker"
BEAT="automationapp-celery-beat"
NGINX="automationapp-nginx-proxy"

BUILD_DOCKER=false
BRANCH="master"  # default

# Parse arguments
for arg in "$@"; do
    case $arg in
        --build)
            BUILD_DOCKER=true
            ;;
        *)
            BRANCH="$arg"
            ;;
    esac
done

echo "🚀 --------------------------- Updating repository ---------------------------"
echo "Using branch: $BRANCH"

git fetch origin
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
git pull --rebase

echo "🚀 --------------------------- Install dependencies ---------------------------"
docker exec -it "$DOCKER_CONTAINER" poetry install

if $BUILD_DOCKER; then
    echo "🛠️ --------------------------- Rebuilding Docker ---------------------------"
    cd docker
    docker compose up -d --build
    cd -
fi

echo "🖼️ --------------------------- Collecting static files ---------------------------"
docker exec -it "$DOCKER_CONTAINER" poetry run python manage.py collectstatic --noinput --clear

echo "🖼️ --------------------------- Compressing  ---------------------------"
docker exec -it "$DOCKER_CONTAINER" poetry run python manage.py compress

echo "📜 --------------------------- Running migrations ---------------------------"
docker exec -it "$DOCKER_CONTAINER" poetry run python manage.py migrate

echo "🧹 --------------------------- Clearing cache ---------------------------"
docker exec -it $DOCKER_CONTAINER python manage.py shell -c "
from django.core.cache import cache
from automationapp import settings

for lang, _ in settings.SUPPORTED_LANGUAGES:
    print('LANG', lang)
    cache.delete(f'frontpage_html_{lang}')
"
echo "🤖 --------------------------- Generate new frontpage ids ---------------------------"
docker exec -it "$DOCKER_CONTAINER" poetry run python manage.py generate_frontpage_command

echo "🔄 --------------------------- Restarting containers ---------------------------"
docker restart "$DOCKER_CONTAINER" "$WORKER" "$BEAT" "$NGINX"

echo "✅ --------------------------- Done ---------------------------"
