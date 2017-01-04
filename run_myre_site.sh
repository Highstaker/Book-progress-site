#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# get socket name from file
read -r SOCKET_NAME < socket_name

echo SCRIPT_DIR $SCRIPT_DIR
echo SOCKET_NAME $SOCKET_NAME
cd $SCRIPT_DIR

source env/bin/activate
uwsgi --ini myre_wsgi.ini --socket=/tmp/$SOCKET_NAME.sock

exit 0;
