#!/bin/bash

#Run as root

#Some commands need to be run as root. This is the username to run non-root commands
MY_USERNAME=$(logname)

#Just a dummy command so it could generate a secret key. 
#Sometimes it fails to  perform a command if the secret key isn't there, but generates it nevertheless
sudo -u $MY_USERNAME ./prod_manage.sh check

# installing dependencies
sudo -u $MY_USERNAME virtualenv env
sudo -u $MY_USERNAME env/bin/pip3 install -r requirements.txt

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

echo "Enter path to SSL certificates:"
while [[ -z $CERT_PATH ]]
do
read CERT_PATH
done

echo "Enter filename for key and certificate [$DIR_NAME]: "
read CERT_NAME
if [[ -z $CERT_NAME ]]; then
    # if left empty, set socket name to parent directory's name
	CERT_NAME=$DIR_NAME
fi

# the folder where the project is located
SITE_FOLDER=myresite

# creating IP file for ALLOWED_HOSTS
sudo -u $MY_USERNAME echo "SERVER_IP='$SERVER_IP'" > $SITE_FOLDER/server_ip.py

# creating a file with socket name. Same name will be used for nginx config file name
sudo -u $MY_USERNAME echo "$SOCKET_NAME" > socket_name

# creating a file with path to static files
sudo -u $MY_USERNAME echo "STATIC_ROOT='$STATIC_PATH'" > $SITE_FOLDER/$SITE_FOLDER/static_root.py

# Create certificates may require root or not
if [ ! -f $CERT_PATH/$CERT_NAME.key ] || [ ! -f $CERT_PATH/$CERT_NAME.crt ]; then
sudo -u $MY_USERNAME openssl req -x509 -nodes -newkey rsa:2048 -keyout $CERT_PATH/$CERT_NAME.key -out $CERT_PATH/$CERT_NAME.crt
fi

# creating an nginx configuration
# read -d '' NGINX_CONF_FILE << EOF
NGINX_CONF_FILE=$"server {\n
\tlisten $PORT;\n
\tserver_name $SERVER_IP;\n
\tssl on;\n
\tssl_certificate        $CERT_PATH/$CERT_NAME.crt;\n
\tssl_certificate_key    $CERT_PATH/$CERT_NAME.key;\n
\terror_page  497 https://\$server_name:\$server_port\$request_uri;
\n
\tlocation /static {\n
\t\t alias $STATIC_PATH;\n
\t }\n
\n
\tlocation / {\n
\t\t  include uwsgi_params;\n
\t\t  uwsgi_pass unix:/tmp/$SOCKET_NAME.sock;\n
\t\t  proxy_set_header X-Forwarded-Proto \$scheme;\n
\t }\n
}"
# EOF

# Applying nginx settings. Requires root.
echo -e $NGINX_CONF_FILE > /etc/nginx/sites-available/conf_$SOCKET_NAME
ln -s /etc/nginx/sites-available/conf_$SOCKET_NAME /etc/nginx/sites-enabled
nginx -s reload

# creating static files
sudo -u $MY_USERNAME mkdir -p $STATIC_PATH
sudo -u $MY_USERNAME ./prod_manage.sh collectstatic

# creating database
sudo -u $MY_USERNAME ./prod_manage.sh makemigrations
sudo -u $MY_USERNAME ./prod_manage.sh migrate

