#!/bin/bash
# startup in local mode when using docker-compose
export ONI_DEBUG=1

python /open-oni/manage.py setup_index
python /open-oni/manage.py migrate
python /open-oni/manage.py runserver 0.0.0.0:8080

