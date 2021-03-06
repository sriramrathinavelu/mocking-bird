#!/bin/bash

BASHPARTIAL="bashenv.inc"


# Attempting to find the mocking-bird path
MOCKINGBIRDPATH=`dirname \`readlink -f $0\``


touch $MOCKINGBIRDPATH/$BASHPARTIAL
truncate -s 0 $MOCKINGBIRDPATH/$BASHPARTIAL

echo "export MOCKINGBIRDPATH=\"$MOCKINGBIRDPATH\"" >> $MOCKINGBIRDPATH/$BASHPARTIAL
echo "export PYTHONPATH=\$PYTHONPATH:$MOCKINGBIRDPATH" >> $MOCKINGBIRDPATH/$BASHPARTIAL

# Setting the DJANGO_SETTINGS_MODULE
DJANGO_SETTINGS_MODULE="mockingsite.settings.production"
echo "export DJANGO_SETTINGS_MODULE=\"$DJANGO_SETTINGS_MODULE\"" >> $MOCKINGBIRDPATH/$BASHPARTIAL

ACTIVATE_ALIAS="alias activate=\"cd \$MOCKINGBIRDPATH/..; source bin/activate; cd -\""
echo "$ACTIVATE_ALIAS" >> $MOCKINGBIRDPATH/$BASHPARTIAL

VIRTUALENVPATH=`dirname $MOCKINGBIRDPATH`
echo "export VIRTUALENVPATH=\"$VIRTUALENVPATH\"" >> $MOCKINGBIRDPATH/$BASHPARTIAL

grep --quiet "source $MOCKINGBIRDPATH/$BASHPARTIAL" ~/.bashrc || printf "\n%s\n%s\n" "# Setting up the MockingBird environment" "source $MOCKINGBIRDPATH/$BASHPARTIAL" >> ~/.bashrc

CASSANDRA_HOST=`(ls /etc/cassandra/cassandra.yaml>/dev/null 2>&1 && grep listen_address: /etc/cassandra/cassandra.yaml | cut -f2 -d:) || (ls /etc/dse/cassandra/cassandra.yaml>/dev/null 2>&1 && grep listen_address: /etc/dse/cassandra/cassandra.yaml | cut -f2 -d:)`
CASSANDRA_HOST=$(echo $CASSANDRA_HOST | tr -d ' ')
echo "export CASSANDRA_HOST=$CASSANDRA_HOST" >> $MOCKINGBIRDPATH/$BASHPARTIAL

echo "export DOMAIN_NAME=localhost" >> $MOCKINGBIRDPATH/$BASHPARTIAL
echo "export PORT=8000" >> $MOCKINGBIRDPATH/$BASHPARTIAL


source ~/.bashrc

# Generating uwsgi and nginx templates
python $MOCKINGBIRDPATH/mockingsite/config_gen.py $MOCKINGBIRDPATH/mockingsite/mockingsite_uwsgi.ini.template $MOCKINGBIRDPATH/mockingsite/mockingsite_uwsgi.ini
python $MOCKINGBIRDPATH/mockingsite/config_gen.py $MOCKINGBIRDPATH/mockingsite/websockets_uwsgi.ini.template $MOCKINGBIRDPATH/mockingsite/websockets_uwsgi.ini
python $MOCKINGBIRDPATH/mockingsite/config_gen.py $MOCKINGBIRDPATH/mockingsite/mockingsite_nginx.conf.template $MOCKINGBIRDPATH/mockingsite/mockingsite_nginx.conf
python $MOCKINGBIRDPATH/mockingsite/config_gen.py $MOCKINGBIRDPATH/mockingsite/supervisord.conf.template $MOCKINGBIRDPATH/mockingsite/supervisord.conf
