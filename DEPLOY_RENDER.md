# Deploy on Render (stable public URL)

This guide publishes the existing Streamlit app so any user can open it by URL.

## 1) Prepare repository

- Ensure these files are in the repo root: `Dockerfile`, `requirements.txt`, `app.py`.
- Keep secrets out of Git (`.env` must stay local).
- Push code to GitHub.

## 2) Create PostgreSQL on Render

1. Open Render Dashboard -> **New** -> **PostgreSQL**.
2. Create DB (for example `woodmind-db`).
3. After creation, copy values from Render:
   - `Host`
   - `Port`
   - `Database`
   - `User`
   - `Password`

## 3) Create Web Service from this repo

1. **New** -> **Web Service** -> connect your GitHub repo.
2. Render should detect Docker automatically (`Dockerfile`).
3. Connect Postgres to the Web Service (recommended):
   - In the Web Service settings, under **Environment**, use **Link database** / add the Postgres instance.
   - Render will inject **`DATABASE_URL`**. The app reads it automatically — do **not** leave the DB host as `127.0.0.1` (that is only for local dev and causes `Connection refused` on Render).

   **Or** set variables manually (values from the Postgres dashboard — host looks like `dpg-xxxxx-a.<region>.postgres.render.com`, never `localhost` / `127.0.0.1`):
   - `POSTGRES_HOST` = Host from Render DB
   - `POSTGRES_PORT` = Port from Render DB
   - `POSTGRES_DB` = Database name from Render DB
   - `POSTGRES_USER` = User from Render DB
   - `POSTGRES_PASSWORD` = Password from Render DB
4. Deploy.

Your app URL will look like:
- `https://<service-name>.onrender.com`

## 4) Initialize schema and load data (one-time)

Open **Shell** in the web service and run:

```bash
python database/db_init.py
python ingest_data.py
```

### Alternative: seed Render DB from your local machine

If you prefer loading data directly from your local project into Render Postgres:

1. Copy External Database URL from Render Postgres.
2. In local terminal set it as env var:

```bash
# PowerShell
$env:RENDER_DATABASE_URL="postgres://user:pass@host:5432/dbname"
python scripts/seed_render_db.py
```

`seed_render_db.py` will:
- parse `RENDER_DATABASE_URL`,
- run `database/db_init.py` against Render DB,
- run `ingest_data.py` against Render DB.

Notes:
- `ingest_data.py` expects `data/merged_documents.xlsx`.
- If the file is not in the deployed filesystem, upload/provide it first (or adapt ingestion source).

## 5) Verify app

- Open the Render URL.
- If you see "База данных пуста", re-run data initialization commands and check logs.

## Common issues

- **Deploy loop / crash:** check service logs and DB credentials.
- **Connection refused to `127.0.0.1:5432`:** the Web Service is using the default local host. Link the database so `DATABASE_URL` is set, or set `POSTGRES_HOST` to Render’s Postgres hostname (see step 3).
- **Empty dataset:** run `db_init.py` + `ingest_data.py` in Render Shell (or `scripts/seed_render_db.py` from your PC).
