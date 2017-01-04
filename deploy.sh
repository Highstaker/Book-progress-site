#!/bin/bash

# installing dependencies
virtualenv env
env/bin/pip3 install -r requirements.txt

echo "Enter your server IP:"
while [[ -z $SERVER_IP ]]
do
read SERVER_IP
done

DIR_FULL_PATH=$PWD
DIR_NAME=${PWD##*/} # ## deletes the longest matching pattern, which is everything before the actual dir name.
echo "Enter socket name [$DIR_NAME]: "
read SOCKET_NAME
if [[ -z $SOCKET_NAME ]]; then
    # if left empty, set socket name to parent directory's name
	SOCKET_NAME=$DIR_NAME
fi

echo "Enter the location of static files [$DIR_FULL_PATH/static_root]: "
read STATIC_PATH
if [[ -z $STATIC_PATH ]]; then
	STATIC_PATH="$DIR_FULL_PATH/static_root"
fi

echo "Enter port number (for connection to your website):"
while [[ -z $PORT ]]
do
read PORT
done

# the folder where the project is located
SITE_FOLDER=myresite

# creating IP file for ALLOWED_HOSTS
echo "SERVER_IP='$SERVER_IP'" > $SITE_FOLDER/server_ip.py

# creating a file with socket name. Same name will be used for nginx config file name
echo "$SOCKET_NAME" > socket_name

# creating a file with path to static files
echo "STATIC_ROOT='$STATIC_PATH'" > $SITE_FOLDER/$SITE_FOLDER/static_root.py

# creating an nginx configuration
# read -d '' NGINX_CONF_FILE << EOF
NGINX_CONF_FILE=$"server {\n
\tlisten $PORT;\n
\tserver_name $SERVER_IP;\n
\n
\tlocation /static {\n
\t\t alias $STATIC_PATH;\n
\t }\n
\n
\tlocation / {\n
\t\t  include uwsgi_params;\n
\t\t  uwsgi_pass unix:/tmp/$SOCKET_NAME.sock;\n
\t }\n
}"
# EOF

# Applying nginx settings. Requires root.
echo -e $NGINX_CONF_FILE > /etc/nginx/sites-available/$SOCKET_NAME
ln -s /etc/nginx/sites-available/$SOCKET_NAME /etc/nginx/sites-enabled
nginx -s reload

# creating static files
mkdir -p $STATIC_PATH
./prod_manage.sh collectstatic

