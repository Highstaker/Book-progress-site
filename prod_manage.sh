#!/bin/bash

cd myresite
DJANGO_SETTINGS_MODULE=myresite.prod_settings ../env/bin/python3 manage.py "$@"

exit 0;