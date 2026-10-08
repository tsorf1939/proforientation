# Диаграмма компонентов системы профориентации
## (UML Component Diagram)

Исходник диаграммы: [architecture.puml](architecture.puml)

### Как открыть

**VSCode** — установите расширение **PlantUML** (jebbs.plantuml),
откройте `architecture.puml` и нажмите **Alt+D** (Preview).

**Онлайн** — вставьте содержимое файла на [plantuml.com/plantuml](https://www.plantuml.com/plantuml/uml/).

---

## Описание уровней

| Уровень | Компоненты | Технологии |
|---------|-----------|-----------|
| Клиентский | Браузер | — |
| Маршрутизации | Nginx :80 | Nginx Alpine |
| Представления | Vue 3 SPA, Static Volume | Vue 3, Vite :5173 |
| Приложения | Gunicorn + Django (users, tests_app, careers, recommendations, reports) | Python 3.12, Django 5, DRF, Gunicorn |
| Данных | PostgreSQL 16 :5432 | PostgreSQL |
| Асинхронной обработки | Redis :6379, Celery Worker | Redis 7, Celery 5 |

## Интерфейсы

| Интерфейс | Описание |
|-----------|---------|
| `HTTP :80` | Входная точка — все запросы браузера |
| `REST API /api/*` | JSON-интерфейс между Nginx и Gunicorn |
| `JWT` | Токены аутентификации (access 24ч, refresh 7д) |
| `WSGI` | Протокол между Gunicorn и Django |
| `SQL / ORM` | Django ORM → PostgreSQL |
| `Redis Protocol` | Django `task.delay()` → Redis брокер |
