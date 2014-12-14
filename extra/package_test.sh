#!/bin/bash

set -x

# Config
REPO_PATH=/opt/apt
DIST=wheezy
PACKAGES_PATH=${PACKAGES_PATH:-"/opt/packages"}

# Force --go just in case :p
if ! [ "$1" == "--go" ];then
    echo "This script take .deb package and validate full numeter install with nginx and apache and validate config in docs example"
    echo "usage $0 --go"
    exit 1
fi

setup_local_repo(){
    mkdir -p $REPO_PATH/{conf,incoming}
    cat > $REPO_PATH/conf/distributions <<EOF
Origin: Numeter
Label: eNovance
Suite: oldstable
Codename: numeter-squeeze
Version: 6.0
Architectures: i386 amd64 source
Components: main contrib non-free
Description: Numeter package test
SignWith: 1753A840

Origin: Numeter
Label: eNovance
Suite: stable
Codename: numeter-wheezy
Version: 7.0
Architectures: i386 amd64 source
Components: main contrib non-free
Description: Numeter package test
SignWith: 1753A840
EOF
    cat > $REPO_PATH/conf/incoming <<EOF
Name: default
IncomingDir: incoming
TempDir: /tmp
Allow: numeter-squeeze numeter-wheezy stable>numeter-wheezy oldstable>numeter-squeeze unstable>numeter-wheezy
Cleanup: on_deny on_error
EOF
}

setup_gpg_key(){
    # Extra
    REPO_KEY_PUB="-----BEGIN PGP PUBLIC KEY BLOCK-----
    Version: GnuPG v1.4.14 (GNU/Linux)

    mQENBFJtHqkBCACyFUkv9PKNScVJ/iye4hKabidmEo72JUxG1j5ntewATfqydd96
    IY+9EfJrqYsiuoxQ/iG4chFKrVWqdaR3VHk1GoyyMNEWa2u/7ZillDqchSeQbFrh
    6RWqUT3mwMflsvlJMQ1x6xgIMoEif7sY5+udInqVfm5R1OF4rLPcehmrsYnkHg5F
    JAK/2nb/KiSxYVzQ0dmo+LTyVISjaT3TySSchaVQhIvHNUN1xhAJNZ1l3wJThNr8
    WCKziy1EA9RXKHRr8QtDNQHaVDARYmr+3E4cOY8nHX0x9iMxJIOz6uJX2AU7lHaa
    Nn6S2UZt1UChAQ54GCAVHIVH3zibZNWcXkh1ABEBAAG0FE51bWV0ZXIgdGVzdCBw
    YWNrYWdliQE4BBMBAgAiBQJSbR6pAhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIX
    gAAKCRCV6X01F1OoQNZPB/9jbWSj4d8tAnG4ycc8DiIR4Gch2rXAdQ27TzUwbpCf
    lNTfSZrYaN35zaLkLqxpxhSV0TyWO6xfe8ms7Cz88bJXp5Cuu/Mg02qp4Z3XhUZL
    EoQDweG/SlioLlKk68SDPC3XDKG/JF0RJLGqKYllEGRtS6+aveFlCNRkKVobruQw
    +FY1UCv6tqIPy2SHpYORsy5qwykxEQxDygD0sNnkxOFaeM3kOfABcxbgeSaYtznZ
    2qlDu5EIkJjPHQ50HUrP0hX61QXsc8+Bm/F0wraRj5vmsLcgOUH8rtljiqTIQtrW
    R0sLfBeRooO0H8f1s+dqTIrVqezqQuUtIBzFsqUfyUVJuQENBFJtHqkBCACwiD/M
    Q1FqkVbzFpw+oEqJdlqWWwuDGVJ+JuBuMKki18EEvXixwCKP6nUWKm38Lr5612GQ
    fq4q5v5tZlZTjv/URhNQjsHXMe4EOiQKcgXKqIjsg5y7gNxz987LYC9/I+yoNrBl
    oeo7oMBeSB1FHpzStcRzUhj/GMYasscQ7SNmJ8s2YzUA9cS6iEw2/eX664n507sr
    qYxJtMMB+46oeFn1bT+gaDNiJkMVRjfe4KCzS2kNnR0Id8LSIe6NVomvb28QeEXp
    FdZkRmKyedB+qXH2mYxoeGCfJKirh8IdqB3cKE7q6SkB7NcjB6YpYe5PK1iX2zOT
    nRS76wKxHfp+OyHPABEBAAGJAR8EGAECAAkFAlJtHqkCGwwACgkQlel9NRdTqECj
    JQgAlzq1DBhteqoj9g6d7+g8XLHIr/yuo5yZAilzEo6dJZJoGNgOXrWSnxwcBLlO
    sPDPGhfJ/zpzOkFWwp0mLr+gtNL17bLm6z/Jwsc4CJYpxLhHjcU/KMpgPZZhi8tE
    EWuw188YZJ/93aAJJlEJVQ8LuU37kpfPgsedPtbDPgzKcVJF63AK+ovEFqvHopGf
    EmhIb5GnSiVVKLtfki25/UD/3V5h8ujjDud8/KI+4wWBqNsb4TudypUERC1Y/5+b
    rYt6kd+3m55Y36TGXlhESXkTzWVg/h1c2V4aMVTascFsADujsNuQVSmcfAzNBLPt
    wwo1QIoH6xq5CeGe4Drqtp+muQ==
    =M2Cu
    -----END PGP PUBLIC KEY BLOCK-----"

    REPO_KEY_PRV="-----BEGIN PGP PRIVATE KEY BLOCK-----
    Version: GnuPG v1.4.14 (GNU/Linux)

    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
    fAzNBLPtwwo1QIoH6xq5CeGe4Drqtp+muQ==
    =Rxj6
    -----END PGP PRIVATE KEY BLOCK-----"
    cat <<EOF | gpg --import
$REPO_KEY_PRV
$REPO_KEY_PUB
EOF
}

setup_sourcelist(){
    echo "deb file:$REPO_PATH numeter-$DIST main" > /etc/apt/sources.list.d/numeter.list
    echo "deb http://cloud.pkgs.enovance.com/$DIST-havana havana main" > /etc/apt/sources.list.d/havana.list
    apt-key adv --recv-keys --keyserver keyserver.ubuntu.com E52660B15D964F0B
    gpg -a --export 95E97D351753A840 | apt-key add -
    if [ "$DIST" == "wheezy" ]; then
        echo "deb http://ftp.fr.debian.org/debian wheezy-backports main" > /etc/apt/sources.list.d/debian-backports.list
    fi
}

setup_deb_in_repo(){
    cp $PACKAGES_PATH/* $REPO_PATH/incoming
    debsign -m'Numeter test package' $REPO_PATH/incoming/*.changes && reprepro --ignore=wrongdistribution --ignore=undefinedtarget -Vb $REPO_PATH processincoming default
}

setup_numeter(){
    # Force django backports
    if [ "$DIST" == "wheezy" ]; then
        apt-get install --force-yes -q -y -t wheezy-backports python-django python-mimeparse
    fi

    pip install djangorestframework
    pip install django-filter

    for package in {numeter-poller,numeter-storage,numeter-webapp}; do
        echo "# Setup $package"

        apt-get install --force-yes -q -y $package

        if [ "$?" -ne "0" ]; then
          echo "ERROR : Unable to setup package $package"
          exit 2
        fi
    done
}

config_poller(){
    sed -i 's/enable = false/enable = true/' /etc/numeter/numeter_poller.cfg
    sed -i 's/host_id =.*/host_id = poller/' /etc/numeter/numeter_poller.cfg
    sed -i 's/plugins_enable =.*/plugins_enable = ^load$/' /etc/numeter/numeter_poller.cfg
}

config_storage(){
    sed -i 's/enable = false/enable = true/' /etc/numeter/numeter_storage.cfg
    echo poller > /etc/numeter/host-list
    # Nginx
    cp /usr/share/doc/numeter-storage/numeter-storage-web.nginx.example /etc/nginx/sites-available/numeter-storage-web
    ln -s /etc/nginx/sites-available/numeter-storage-web /etc/nginx/sites-enabled/
    /etc/init.d/nginx restart
    # uwsgi
    cp /usr/share/doc/numeter-storage/numeter-storage-uwsgi.ini.example /etc/uwsgi/apps-available/numeter-storage-uwsgi.ini
    ln -s /etc/uwsgi/apps-available/numeter-storage-uwsgi.ini /etc/uwsgi/apps-enabled/
    /etc/init.d/uwsgi restart
}

config_webapp(){

    # Create database
    cat <<EOF | mysql --defaults-file=/etc/mysql/debian.cnf
CREATE DATABASE numeter;
GRANT ALL ON numeter.* TO numeter@'localhost' IDENTIFIED BY 'yourpass';
EOF

    # Config webapp
    sed -i /etc/numeter/numeter_webapp.cfg -re '
      s/^engine.*/engine = django.db.backends.mysql/ ;
      s/^name.*/name = numeter/ ;
      s/^user.*/user = numeter/ ;
      s/^password.*/password = yourpass/ ;
      s/^host.*/host = localhost/ ;
      s/^port.*/port = 3306/'

    # Write default json user
    # Generated by : numeter-webapp dumpdata --indent=2 core.user > /tmp/user.json
    cat > /tmp/user.json <<EOF
[
{
  "pk": 1,
  "model": "core.user",
  "fields": {
    "username": "admin",
    "graph_lib": "dygraph",
    "is_active": true,
    "is_superuser": true,
    "is_staff": true,
    "last_login": "2013-10-30T21:15:47Z",
    "groups": [],
    "password": "pbkdf2_sha256\$10000\$cX65C75h7s3t\$z0J3y6808UcsJ0aVpqn4OZ7OJcYMVlEGljbHOWZbnOI=",
    "email": "",
    "date_joined": "2013-10-30T21:15:47Z"
  }
}
]
EOF
    # populate database
    numeter-webapp syncdb --noinput
    # Import default admin user (admin : admin)
    numeter-webapp loaddata /tmp/user.json
    # Add storage
    numeter-webapp storage add --name=local_storage --port=8080 --url_prefix=/numeter-storage --address=127.0.0.1

    # Configure web server
    unlink /etc/nginx/sites-enabled/default
    NUMETER_DIR=$(dirname $(python -c 'import numeter_webapp;print numeter_webapp.__file__'))
    RESTFW_DIR=$(dirname $(python -c 'import rest_framework;print rest_framework.__file__'))

    # Apache
    a2enmod wsgi
    a2dissite default
    cp /usr/share/doc/numeter-webapp/numeter-apache.example /etc/apache2/sites-available/numeter-webapp
    a2ensite numeter-webapp
    sed -i "s#@APP_DIR@#$NUMETER_DIR#g" /etc/apache2/sites-available/numeter-webapp
    sed -i "s#@RESTFW_DIR@#$RESTFW_DIR#g" /etc/apache2/sites-available/numeter-webapp
    sed -i "s/:80/:81/g" /etc/apache2/sites-available/numeter-webapp
    sed -i "s/80/81/g" /etc/apache2/ports.conf
    /etc/init.d/apache2 restart

    #cp /usr/share/doc/numeter-storage/numeter-storage-uwsgi.ini.example /etc/uwsgi/apps-available/numeter-storage-uwsgi.ini
    # Nginx
    cp /usr/share/doc/numeter-webapp/numeter-nginx.example /etc/nginx/sites-available/numeter-webapp
    ln -s /etc/nginx/sites-available/numeter-webapp /etc/nginx/sites-enabled/
    sed -i "s#@APP_DIR@#$NUMETER_DIR#g" /etc/nginx/sites-available/numeter-webapp
    sed -i "s#@RESTFW_DIR@#$RESTFW_DIR#g" /etc/nginx/sites-available/numeter-webapp
    /etc/init.d/nginx restart
    # uwsgi
    cp /usr/share/doc/numeter-webapp/numeter_webapp.ini.example /etc/uwsgi/apps-available/numeter_webapp.ini
    ln -s /etc/uwsgi/apps-available/numeter_webapp.ini /etc/uwsgi/apps-enabled/
    sed -i "s#@APP_DIR@#$NUMETER_DIR#g" /etc/uwsgi/apps-available/numeter_webapp.ini
    /etc/init.d/uwsgi restart

}


launch_numeter(){
    # First launch storage to create rabbitmq queue
    eval "numeter-storage &"
    storage_pid=$!
    sleep 5
    kill $storage_pid

    sleep 1

    # Launch poller
    rm -f /tmp/numeter-poller_last
    numeter-poller

    sleep 1

    # Launch storage to consume datas
    eval "numeter-storage &"
    storage_pid=$!
    sleep 5
    kill $storage_pid

    # Populate webapp db after storage launch one time
    numeter-webapp populate -i all
}

check_wsp_file(){
    if [ -z "$(find /var/lib/numeter/wsps/ -type f -name load.wsp)" ];then
        echo ERROR wsp file not found
        exit 2
    fi
}

check_storage_api(){
    if [ -z "$(curl http://127.0.0.1:8080/numeter-storage/list?host=poller | grep load)" ];then
        echo ERROR storage api datas
        exit 2
    fi
    if [ -z "$(curl 'http://127.0.0.1:8080/numeter-storage/info?host=poller&plugin=load' | grep load)" ];then
        echo ERROR storage api infos
        exit 2
    fi
}

check_webapp(){
    # By Nginx
    if [ -z "$(curl 'http://127.0.0.1/wide-storage/list?host=poller' -u admin:admin | grep load)" ];then
        echo ERROR webapp wild_storage info by Nginx
        exit 2
    fi
    if [ -z "$(curl 'http://127.0.0.1/login' | grep '<title>Numeter - Authentification</title>')" ];then
        echo ERROR webapp login page by Nginx
        exit 2
    fi
    # By Apache
    if [ -z "$(curl 'http://127.0.0.1:81/wide-storage/list?host=poller' -u admin:admin | grep load)" ];then
        echo ERROR webapp wild_storage info by Apache
        exit 2
    fi
    if [ -z "$(curl 'http://127.0.0.1:81/login' | grep '<title>Numeter - Authentification</title>')" ];then
        echo ERROR webapp login page by Apache
        exit 2
    fi
}

#
# main
#

echo "Setup dependencies ..."
# Apt depends
apt-get install --force-yes -q -y devscripts reprepro rabbitmq-server curl munin-node
apt-get install --force-yes -q -y python-mysqldb mysql-client apache2 libapache2-mod-wsgi python-setuptools
easy_install pip

# gpg key depends
setup_gpg_key
# Local reprepro
setup_local_repo
setup_sourcelist

# add incomming packages in repo
setup_deb_in_repo

apt-get update

export DEBIAN_FRONTEND=noninteractive
apt-get --force-yes -q -y install mysql-server
unset DEBIAN_FRONTEND

# Install numeter
setup_numeter

# Configure numeter
config_poller
config_storage
config_webapp

# Launch numeter
launch_numeter

# Check if it's ok
check_wsp_file
check_storage_api
check_webapp

echo "Success"
