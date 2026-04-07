# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All Django commands use `uv run manage.py`:

```bash
# Development server
uv run manage.py runserver

# Database migrations
uv run manage.py makemigrations <app_name>
uv run manage.py migrate

# Seed initial data (run in order on fresh setup)
uv run manage.py seed_roles
uv run manage.py seed_titles
uv run manage.py seed_subscription

# Docker (PostgreSQL + pgAdmin)
docker-compose up
```

Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Architecture

**Stack**: Django 6 + Django Ninja (FastAPI-style REST), PostgreSQL, JWT auth, AWS S3, Stripe.

### Module Layout

- `core/` — Django project config: `settings.py`, `urls.py`, `api.py` (central Ninja API instance + router registration)
- `accounts/` — Users, roles, auth, email flows
- `property/` — Properties and units
- `forms/` — Form templates keyed to State + UnitType
- `stripe_integration/` — Payment processing and webhook handling

### API Routing

All endpoints live under `/api/`. Routers are registered in `core/api.py`:

| Prefix | Module |
|---|---|
| `/api/accounts/` | User registration, login, admin user management |
| `/api/config/` | Read-only config (roles, titles, states, subscriptions, unit types/classes) |
| `/api/property/` | Property + unit CRUD |
| `/api/forms/` | Form template CRUD |
| `/api/stripe/` | Checkout, subscriptions, webhook |

### Authentication

- Custom `AuthBearer` in `core/api.py` validates JWT on all endpoints (use `auth=None` to make an endpoint public)
- Token creation: `accounts/jwt.py` — access (3000 min) and refresh (7 days) tokens
- Token validation: `accounts/auth.py` — extracts `User` from payload
- Role enforcement: `accounts/auth_roles_middleware.py` — roles are `Super admin`, `Property Manager`, `Operator`

JWT payload includes: `id`, `email`, `first_name`, `last_name`, `is_subscribed`, `subscription`, `role`, `type`, `exp`, `invited_by`.

### Data Model Highlights

- **User** model (custom, email-based auth): role, title, subscription, Stripe IDs, approval/verification flags, company info
- **PropertyManagement**: property details linked to a manager User
- **Unit**: belongs to PropertyManagement; has type, class, expiration; related Images and UnitForms stored in S3
- **Forms**: templates tied to State + UnitType (not per-unit instances)
- **RefreshToken**: stored in DB for token rotation

### Service Layer

Each app has a `services.py` for business logic, keeping `api.py` thin. `accounts/services.py` handles all email dispatch using templates in `accounts/templates/emails/`.

### File Storage

Media files (unit images, forms) → AWS S3 bucket `akors-files`. Static files → local. Configured via `django-storages` in `settings.py`.

## Environment Variables

Requires a `.env` file with:
- `SECRET_KEY`, `DEBUG`
- `POSTGRES_*` (DB connection)
- `EMAIL_*` (Gmail SMTP)
- `AWS_*` (S3 storage)
- `STRIPE_*` (API keys + webhook secret)
- `SITE_NAME` (used in email links)
- `ADMIN_EMAIL`, `PASSWORD` (seeded superuser)
