# WoodMind — система анализа биорефайнинга

**Заказчик:** НАО «СВЕЗА». Программное обеспечение и репозиторий распространяются на условиях
проприетарной лицензии — см. файл [`LICENSE`](LICENSE).

Веб-приложение на **Streamlit** для просмотра корпуса публикаций по биорефайнингу: таблица «База знаний», интерактивный **граф связей** метод–продукт (PyVis) и **аналитика** по нормализованным тегам. Данные хранятся в **PostgreSQL**; нормализация полей «Метод (AI)» и «Продукт (AI)» выполняется при загрузке из Excel (`ingest_data.py` + `AnalystAgent`).

---

## Возможности

| Раздел | Описание |
|--------|----------|
| **База знаний** | Таблица публикаций с фильтрами (год, TRL, поиск по всем полям). По умолчанию отображаются первые 200 строк для быстрой загрузки; можно развернуть все записи. |
| **Граф связей** | Двудольный граф: методы и продукты из `method_normalized` / `product_normalized`. Режим «Все связи» (ограничение по строкам) и фокус на выбранном узле. |
| **Аналитика** | Топ методов и продуктов по отдельным тегам (разбор строк через запятую). |

Словари совпадений: `replacements/tech_replacements.py`. Очистка «воды» и формулировок «метод не представлен»: `replacements/taxonomy_sanitize.py`.

---

## Структура репозитория

```
.
├── app.py                 # Точка входа Streamlit
├── ingest_data.py         # Чтение Excel → нормализация → INSERT в PostgreSQL
├── reset_db.py            # TRUNCATE таблицы (очистка данных)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example           # Шаблон переменных окружения
├── agents/
│   └── analyst_agent.py   # Нормализация method/product по текстам и словарям
├── core/
│   ├── config.py          # DB_CONFIG из переменных окружения
│   └── orchestrator.py    # Чтение данных из БД для приложения
├── database/
│   ├── connector.py       # SQLAlchemy → pandas
│   └── db_init.py         # Создание таблицы biorefinery_data_clean
├── replacements/
│   ├── tech_replacements.py
│   └── taxonomy_sanitize.py
├── ui/
│   └── graph_visualizer.py
└── data/                  # Положите сюда merged_documents.xlsx (не в Git по умолчанию)
```

Дополнительно: каталог `method_product/` — отдельные скрипты анализа по docx/csv (не обязательны для основного приложения).

---

## Требования

- **Python 3.11+** (рекомендуется)
- **PostgreSQL 14+** (локально или через Docker)
- Файл **`data/merged_documents.xlsx`** с колонками, согласованными с маппингом в `ingest_data.py` (см. `rename_map` в скрипте)

---

## Быстрый старт (локально, без Docker)

### 1. Клонирование и виртуальное окружение

```bash
git clone <URL-вашего-репозитория>.git
cd diploma
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 2. Зависимости

```bash
pip install -r requirements.txt
```

### 3. PostgreSQL

Создайте базу (например, `diploma`) и пользователя. Скопируйте настройки:

```bash
copy .env.example .env    # Windows
# или: cp .env.example .env
```

Отредактируйте `.env`: хост, порт, имя БД, логин и **пароль**. Приложение и скрипты подхватят их через `python-dotenv`.

### 4. Инициализация схемы и загрузка данных

Из **корня проекта** (чтобы работали импорты `core`, `agents`):

```bash
python database/db_init.py
python ingest_data.py
```

При необходимости очистить только строки таблицы:

```bash
python reset_db.py
```

### 5. Запуск интерфейса

```bash
streamlit run app.py
```

Откройте в браузере адрес, который покажет Streamlit (обычно `http://localhost:8501`).

---

## Docker: пошаговая инструкция

Поднимаются два контейнера: **PostgreSQL** и **приложение Streamlit**. Папка `data` на вашем
компьютере подключается к контейнеру только **для чтения** — Excel должен лежать у вас на диске,
внутри образа он не «запекается».

### Что нужно заранее

1. Установлен **Docker** с поддержкой Compose:
   - **Windows / macOS:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux:** пакеты `docker.io` и `docker-compose-plugin` (или аналог)
2. Терминал открыт **в корне проекта** (там, где лежат `docker-compose.yml` и `Dockerfile`).
3. Файл **`data/merged_documents.xlsx`** скопирован в папку `data` проекта (создайте `data`, если её нет).

### Шаг 1 — переменные окружения

Скопируйте шаблон и при необходимости отредактируйте пароль и порты:

```bash
# Windows (PowerShell или cmd)
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

В `.env` можно задать, например:

- `POSTGRES_PASSWORD` — пароль пользователя БД (должен совпадать с тем, что ожидает `docker-compose` для сервиса `db`);
- `POSTGRES_PUBLISH_PORT` — если порт `5432` на ПК уже занят, укажите другой (например `5433`);
- `STREAMLIT_PORT` — порт веб-интерфейса (по умолчанию `8501`).

Сервис `app` в Compose получает доступ к БД по имени хоста **`db`** автоматически; менять `POSTGRES_HOST` в `.env` для контейнера `app` не нужно.

### Шаг 2 — собрать образ приложения

```bash
docker compose build
```

Дождитесь окончания сборки без ошибок.

### Шаг 3 — запустить только базу данных

```bash
docker compose up -d db
```

Проверка, что контейнер с Postgres работает:

```bash
docker compose ps
```

У сервиса `db` в колонке `STATUS` обычно появится `(healthy)` через несколько секунд.

### Шаг 4 — создать таблицы в базе

Однократно (или после `docker compose down -v`, когда том БД удалён):

```bash
docker compose run --rm app python database/db_init.py
```

В логе должно быть сообщение об успешном создании таблицы `biorefinery_data_clean`.

### Шаг 5 — загрузить данные из Excel в PostgreSQL

```bash
docker compose run --rm app python ingest_data.py
```

Скрипт читает **`/app/data/merged_documents.xlsx`** внутри контейнера — это тот же файл, что
`./data/merged_documents.xlsx` на вашем ПК. Если файла нет, шаг завершится ошибкой «Файл не найден».

### Шаг 6 — запустить веб-интерфейс

```bash
docker compose up -d app
```

Откройте в браузере:

- `http://localhost:8501`  
  или, если меняли порт: `http://localhost:<STREAMLIT_PORT>`

Просмотр логов Streamlit при необходимости:

```bash
docker compose logs -f app
```

### Частые действия после первого запуска

| Задача | Команды |
|--------|---------|
| Перезалить данные из того же Excel | `docker compose run --rm app python reset_db.py` затем снова `docker compose run --rm app python ingest_data.py` |
| Остановить всё, **сохранив** базу | `docker compose down` |
| Остановить и **удалить** данные Postgres | `docker compose down -v` (после этого повторите шаги 3–6) |
| Пересобрать образ после правок кода | `docker compose build --no-cache` и снова `docker compose up -d` |

### Если что-то не работает

- **Порт 8501 занят** — задайте в `.env` переменную `STREAMLIT_PORT=8502` и перезапустите `docker compose up -d app`.
- **Порт 5432 занят** — задайте `POSTGRES_PUBLISH_PORT=5433` в `.env`, выполните `docker compose down` и снова `up -d db`.
- **Пустая таблица в приложении** — убедитесь, что шаги 4–5 прошли без ошибок и контейнер `app` запущен после загрузки данных.

---

## Переменные окружения

| Переменная | Назначение | По умолчанию (код) |
|------------|------------|---------------------|
| `POSTGRES_HOST` / `DB_HOST` | Хост PostgreSQL | `127.0.0.1` |
| `POSTGRES_PORT` / `DB_PORT` | Порт | `5432` |
| `POSTGRES_DB` / `DB_NAME` | Имя базы | `diploma` |
| `POSTGRES_USER` / `DB_USER` | Пользователь | `postgres` |
| `POSTGRES_PASSWORD` / `DB_PASSWORD` | Пароль | `postgres` |

В `docker-compose.yml` для сервиса `app` хост БД принудительно **`db`** (имя сервиса в сети Compose).

---

## Публикация на GitHub

1. **Не коммитьте** файл `.env`, пароли, крупные датасеты и виртуальное окружение (см. `.gitignore`).
2. В репозитории оставьте **`.env.example`** без секретов.
3. После клонирования каждый разработчик создаёт свой `.env` и кладёт `data/merged_documents.xlsx` локально.
4. Инициализация:

   ```bash
   git add .
   git commit -m "Initial commit: WoodMind diploma project"
   git branch -M main
   git remote add origin https://github.com/<user>/<repo>.git
   git push -u origin main
   ```

5. В описании репозитория (About) можно указать: Python, Streamlit, PostgreSQL, Docker.

---

## Обновление классификации методов/продуктов

1. Правите словари в `replacements/tech_replacements.py` или логику в `agents/analyst_agent.py` / `replacements/taxonomy_sanitize.py`.
2. Перезапускаете загрузку: `python ingest_data.py` (или через Docker — см. выше).
3. В Streamlit при локальной разработке при необходимости: **Clear cache** в меню или перезапуск `streamlit run`.

---

## Устранение неполадок

| Симптом | Что проверить |
|---------|----------------|
| Ошибка подключения к БД | Запущен ли Postgres, верны ли `.env` и порт, создана ли база. |
| Пустая таблица в приложении | Выполнены ли `db_init.py` и `ingest_data.py`, есть ли строки в `biorefinery_data_clean`. |
| `merged_documents.xlsx` не найден | Путь `data/merged_documents.xlsx` относительно корня проекта. |
| Docker: ingest не видит файл | Том `./data:/app/data` и файл на хосте в `./data/`. |

---

## Лицензия

ПО распространяется на условиях проприетарной лицензии **НАО «СВЕЗА»**. Текст — в файле [`LICENSE`](LICENSE). Размещение на GitHub и любое иное раскрытие кода согласуйте с заказчиком и условиями договора с вузом.

Перед публикацией убедитесь, что в репозитории нет персональных данных, коммерческой тайны и материалов третьих лиц без разрешения.
