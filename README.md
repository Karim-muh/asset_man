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
3. Run `python manage.py migrate`.
4. Start the development server with `python manage.py runserver`.

## Deploy on Render

This repository includes a `render.yaml` blueprint for a Django web service and PostgreSQL database. In Render, create a new Blueprint instance from the GitHub repository and apply the generated plan. Render supplies `DATABASE_URL`, `SECRET_KEY`, and `WEB_CONCURRENCY`; set `ALLOWED_HOSTS` to the service hostname if it is not populated automatically.

The service runs migrations and collects static files during build, then serves Django through Gunicorn. Create a Django superuser with a one-off shell or Render shell after the first deployment.
