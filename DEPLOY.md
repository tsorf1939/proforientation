# Деплой на сервер

Продовый стек отличается от локального (`docker-compose.yml`):
фронтенд собирается в статику и отдаётся через nginx, а внешним входом
служит Caddy — он сам получает и продлевает HTTPS-сертификат
(Let's Encrypt), если указан настоящий домен.

## Один раз на сервере

```bash
curl -fsSL https://get.docker.com | sh          # если Docker не установлен
git clone https://github.com/tsorf1939/proforientation.git
cd proforientation
cp .env.prod.example .env
nano .env                                       # заполнить реальные значения
```

В `.env` обязательно поменять:
- `POSTGRES_PASSWORD`, `SECRET_KEY` — на реальные секреты
- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `SITE_ADDRESS` — на домен сервера

Если домена пока нет — поставь `SITE_ADDRESS=http://<IP_сервера>`,
`ALLOWED_HOSTS=<IP_сервера>` (HTTPS в этом случае не включится: у Let's
Encrypt нет сертификатов для голых IP). Как только появится домен,
достаточно поменять эти значения в `.env` и перезапустить — сертификат
Caddy получит сам.

Открыть порты в файрволе:
```bash
sudo ufw allow 80,443/tcp
```

## Запуск

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Проверить:
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

## Обновление после изменений в коде

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Создать суперпользователя Django

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Бэкап базы

```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_$(date +%F).sql
```
