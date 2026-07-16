# Finance Utility Suite v1.7.0-alpha

## Architecture change

This release introduces PostgreSQL, Alembic, Docker, and environment-based settings.

## 1. Protect the current version

Commit and push v1.6.7 before continuing.

## 2. Install production dependencies

```powershell
cd D:\FinanceUtilitySuite
python -m pip install -r requirements-production.txt
```

## 3. Copy the environment file

```powershell
Copy-Item .env.example .env
```

Change the database password and JWT secret.

## 4. Start PostgreSQL for development

```powershell
docker compose -f docker-compose.dev.yml up -d
```

## 5. Stop automatic schema creation

Remove this from `backend/main.py`:

```python
Base.metadata.create_all(bind=engine)
```

Alembic must control schema creation.

## 6. Generate the initial migration

```powershell
alembic revision --autogenerate -m "initial production schema"
```

Review the generated file, then run:

```powershell
alembic upgrade head
```

## 7. Start FastAPI

```powershell
python -m uvicorn backend.main:app --reload
```

Test:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## 8. Full Docker test

```powershell
docker compose up --build
```

## 9. Existing SQLite data

This alpha package does not automatically copy SQLite records to PostgreSQL.
Keep `finance_utility_suite.db` as a backup until a one-time migration script is
created and verified.

## 10. Remaining persistence work

Portfolio Live and MTF uploads are still kept in memory. Persistent upload
storage should be implemented in v1.7.0-beta.
