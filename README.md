# AI Video Factory (Kandinsky 5.0 via WaveSpeedAI)

Сервис генерирует 5-секундные видео по загруженному изображению и текстовому промпту через `wavespeed.ai` (Kandinsky 5.0).

## Стек

- `FastAPI` + `Celery` + `Redis`
- `PostgreSQL`
- `Next.js` (frontend)
- `Nginx` reverse proxy
- `Docker Compose`

## Что реализовано

- Загрузка изображения (`jpg`, `jpeg`, `png`, `webp`) + ввод промпта + выбор качества `512P`/`1024P`
- Асинхронная генерация видео через очередь Celery
- Retry-логика в воркере (до 3 попыток, exponential backoff)
- Поллинг статуса задачи на фронтенде (каждые 3 секунды)
- Галерея генераций: просмотр, скачивание, удаление

## API

- `POST /api/generate` — создать генерацию (multipart form: `file`, `prompt`, `quality`)
- `GET /api/tasks/{id}` — статус генерации (`PENDING`, `PROCESSING`, `DONE`, `FAILED`)
- `GET /api/videos` — список генераций
- `GET /api/videos/{id}` — получить одну генерацию
- `DELETE /api/videos/{id}` — удалить генерацию
- `GET /api/health` — healthcheck

## Быстрый запуск

1. Скопируйте пример окружения:

```bash
cp .env.example .env
```

2. Заполните в `.env`:

- `WAVESPEED_API_KEY=<ваш_ключ>`
- при необходимости поменяйте `POSTGRES_*`, `BASE_URL`, `NEXT_PUBLIC_API_URL`

3. Поднимите все сервисы:

```bash
make up-all
```

После старта:

- UI: [http://localhost](http://localhost)
- Backend docs: [http://localhost/docs](http://localhost/docs)
- Прямой backend: [http://localhost:8000](http://localhost:8000)

## Docker Compose сервисы

- `postgres`
- `redis`
- `backend`
- `celery_worker`
- `frontend`
- `nginx`

## Проверка (чек-лист)

- `curl http://localhost/api/health` возвращает `{"status":"ok"}`
- из UI форма отправляет `POST /api/generate`
- в UI статус проходит путь `PENDING -> PROCESSING -> DONE`
- в `Gallery` работает скачивание/удаление
- после `make down && make up-all` записи в БД сохраняются

## Полезные команды

```bash
make ps
make logs
make down
make down-v
```

## Примечания по безопасности

- Не коммитьте `.env` в git
- Если API-ключ уже утёк в историю, обязательно отзовите и выпустите новый
