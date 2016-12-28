#!/bin/bash

#graph_models -a -g -o /mnt/ramtemp/001.png

cd myresite
../env/bin/python3 manage.py $@

exit 0