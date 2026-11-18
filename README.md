# Asset Management System

A Django web application for managing organizational assets, inventory, assignments, requisitions, disposals, departments, employees, and reports.

## Group members

| Name | Registration number |
| --- | --- |
| LUGEMWA MUHUSIN | 224-063012-29190 |
| MUHEREZA JESUS DIDAS | 224-063012-29054 |
| EKWANG JOSHUA | 224-063012-29670 |

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set a private `SECRET_KEY`.
4. Run `python manage.py migrate`.
5. Start the development server with `python manage.py runserver`.

`config/settings.py` loads `.env` automatically for local development. The file is ignored by Git. On Render, configure the same values in the service's Environment settings; Render-provided variables take precedence over `.env` values.

Generate a secret key with:

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Deploy on Render

This repository includes a `render.yaml` blueprint for a Django web service and PostgreSQL database. In Render, create a new Blueprint instance from the GitHub repository and apply the generated plan. The blueprint supplies `DATABASE_URL`, a generated `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.

The service runs migrations and collects static files during build, then serves Django through Gunicorn. Create a Django superuser with a one-off shell or Render shell after the first deployment.
