#!/bin/sh
cd .. & pwd & ls & gunicorn --reload -c app/gunicorn_config.py -w 4 "app:create_app()"