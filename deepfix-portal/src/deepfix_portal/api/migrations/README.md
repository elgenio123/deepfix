# Database Migrations

This directory contains Alembic database migrations.

## Initial Setup

If this is a fresh setup, you may need to initialize Alembic:

```bash
cd deepfix-portal/src/deepfix_portal
alembic init migrations
```

Then update `migrations/env.py` to import your models (already done if using the provided setup).

## Creating Migrations

After making changes to models in `api/models.py`:

```bash
alembic revision --autogenerate -m "Description of changes"
```

## Applying Migrations

```bash
alembic upgrade head
```

## Rolling Back

```bash
alembic downgrade -1  # Roll back one migration
alembic downgrade base  # Roll back all migrations
```
