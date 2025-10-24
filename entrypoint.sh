#!/usr/bin/env bash
set -e

python manage.py makemigrations users kvstore --noinput
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
