#!/bin/bash

#graph_models -a -g -o /mnt/ramtemp/001.png

cd myresite
DJANGO_SETTINGS_MODULE=myresite.test_settings ../env/bin/python3 manage.py "$@"

exit 0