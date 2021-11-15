#!/bin/bash
# startup in local mode when using docker-compose
export ONI_DEBUG=1

python manage.py setup_index
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

