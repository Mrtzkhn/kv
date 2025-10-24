# Global Key–Value Store API

A lightweight, JWT-protected REST API for storing and retrieving **globally shared key–value pairs**.
Built with **Django**, **Django REST Framework**, **SimpleJWT**, **PostgreSQL**, and **drf-spectacular**. Ships with a Dockerized dev setup.


## Contents

- [Features](#✨-features)
- [Quick Start (Docker)](#🚀-quick-start-docker)
- [Project Structure](#📦-project-structure)
- [Production Tips](#🚢-production-tips)
- [License](#📃-license)


## ✨ Features

* **authenticated read & writes** — reads and writes require a JWT.
* **Idempotent upsert** via `PUT /api/kvstore/{key}/`.
* **OpenAPI docs** with Swagger UI & ReDoc.
* **Postgres 16** via Docker Compose.
* Clean, minimal data model: `KeyValue(key, value)`.


## 🚀 Quick Start (Docker)

```bash
cp .env.example .env
docker compose up --build
```


## OpenAPI docs

* Swagger: `/api/docs/`
* ReDoc: `/api/redoc/`
* JSON: `/api/schema/`


## 📦 Project Structure

```
kv/
├── config/               # Django settings, urls, ASGI/WSGI
├── kvstore/              # Key–Value app (model, serializers, views, routes)
├── users/                # Registration + JWT endpoints wiring
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── manage.py
└── requirements.txt
```


## 🚢 Production Tips

**In `entrypoint.sh`:**

* Remove:

  * `python manage.py makemigrations`
  * `python manage.py runserver 0.0.0.0:8000`
* Use:

  ```bash
  python manage.py migrate --noinput
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
  ```

**In your `.env` file:**

* Update the django secret
* Set `DEBUG=0` and use a strong, secret `SECRET_KEY`.
* Ensure `DJANGO_ALLOWED_HOSTS` includes your domain(s) and any load balancer hostnames.


## 📃 License

This project is licensed under the **GNU General Public License v3.0**.
See the [LICENSE](LICENSE) file for more details.
