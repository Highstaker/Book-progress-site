#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo $SCRIPT_DIR
cd $SCRIPT_DIR

source env/bin/activate
uwsgi --ini myre_wsgi.ini --socket=/tmp/myre_site_beta.sock

exit 0;
