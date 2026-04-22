# AI Video Factory (WaveSpeedAI WAN 2.2 Spicy)

Веб-сервис для генерации 5-секундных видео из изображения и текстового промпта через `WaveSpeedAI`.

## Стек

- `FastAPI` + `Celery` + `Redis`
- `PostgreSQL`
- `Next.js` (App Router, frontend)
- `Nginx` reverse proxy
- `Docker Compose`

## Что реализовано

- Загрузка изображения (`jpg`, `jpeg`, `png`, `webp`) + ввод промпта
- Выбор качества `480P` / `720P` (под модель `WAN 2.2 Spicy`)
- Асинхронная генерация через очередь Celery
- Retry-логика (до 3 повторов, exponential backoff)
- Поллинг статуса на фронте каждые 3 секунды
- Встроенный видеоплеер в статусе и в галерее (без открытия по ссылке)
- Галерея генераций: предпросмотр, скачивание, удаление
- Обработка ошибок валидации и ошибок внешнего API

## Модель и API

- Провайдер: `WaveSpeedAI`
- Модель по умолчанию: `wavespeed-ai/wan-2.2-spicy/image-to-video`
- Поддерживаемые разрешения модели: `480p`, `720p`

## API backend

- `POST /api/generate` — создать генерацию (`multipart/form-data`: `file`, `prompt`, `quality`)
- `GET /api/tasks/{id}` — получить статус (`PENDING`, `PROCESSING`, `DONE`, `FAILED`)
- `GET /api/videos` — список генераций
- `GET /api/videos/{id}` — получить одну генерацию
- `DELETE /api/videos/{id}` — удалить генерацию
- `GET /api/health` — healthcheck

## Быстрый запуск

1. Скопируйте окружение:

```bash
cp .env.example .env
```

2. Откройте `.env` и **обязательно** заполните:

- `WAVESPEED_API_KEY=<ваш_ключ>` (иначе генерации будут падать с `FAILED`)

Рекомендуемые настройки:

- `BASE_URL=` оставить пустым (по умолчанию берётся хост из входящего запроса, удобно для VM/IP/домена)

Опционально (если надо):

- `DATABASE_URL`, `REDIS_URL` — если хотите подключаться к внешним БД/Redis
- `WAVESPEED_MODEL_ID`, `WAVESPEED_*` — если меняете модель/таймауты
- `UPLOAD_DIR`, `STATIC_UPLOADS_URL_PREFIX`, `MAX_UPLOAD_MB` — если меняете хранение/лимиты
- `NEXT_PUBLIC_API_URL` — обычно оставляем `/api`
- `NEXT_INTERNAL_API_URL` — URL бэкенда для проксирования `/api` при открытии фронта напрямую на `:3000`

3. Поднимите проект:

```bash
make up-all
```

Если `make` не установлен (часто на Windows), используйте:

```bash
docker compose up -d --build
```

## Адреса после запуска

- Основной вход (через nginx): `http://<host>` (порт 80)
- Backend docs: `http://<host>/docs`
- Прямой backend (без nginx): `http://<host>:8000`
- Фронт напрямую (без nginx): `http://<host>:3000` (API всё равно работает, т.к. `/api/*` проксируется в backend)

## Сервисы Docker Compose

- `postgres`
- `redis`
- `backend`
- `celery_worker`
- `frontend`
- `nginx`

## Предсдачный чек-лист

- `docker compose up` поднимает все сервисы
- Можно загрузить картинку и получить видео
- Статусы в UI меняются корректно: `PENDING -> PROCESSING -> DONE`
- Готовые видео отображаются в галерее
- Ошибки обрабатываются (например, пустой prompt -> `422`)
- API ключи не закоммичены (`.env` не должен трекаться git)

## Полезные команды

```bash
make ps
make logs
make down
make down-v
```

Эквиваленты без `make`:

```bash
docker compose ps
docker compose logs -f backend celery_worker
docker compose down
docker compose down -v
```

## Безопасность

- Никогда не коммитьте `.env` и реальные API ключи
- Если ключ засветился, отзовите его и выпустите новый
