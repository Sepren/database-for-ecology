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
3. Set environment variables in the service:
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

Notes:
- `ingest_data.py` expects `data/merged_documents.xlsx`.
- If the file is not in the deployed filesystem, upload/provide it first (or adapt ingestion source).

## 5) Verify app

- Open the Render URL.
- If you see "База данных пуста", re-run data initialization commands and check logs.

## Common issues

- **Deploy loop / crash:** check service logs and DB credentials.
- **Connection refused:** verify `POSTGRES_HOST` and `POSTGRES_PORT`.
- **Empty dataset:** run `db_init.py` + `ingest_data.py` in Render Shell.
