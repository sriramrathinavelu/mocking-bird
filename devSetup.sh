#!/bin/bash

BASHPARTIAL="bashenv.inc"


# Attempting to find the mocking-bird path
MOCKINGBIRDPATH=`dirname \`readlink -f $0\``


touch $MOCKINGBIRDPATH/$BASHPARTIAL
truncate -s 0 $MOCKINGBIRDPATH/$BASHPARTIAL

echo "export MOCKINGBIRDPATH=\"$MOCKINGBIRDPATH\"" >> $MOCKINGBIRDPATH/$BASHPARTIAL
echo "export PYTHONPATH=\$PYTHONPATH:$MOCKINGBIRDPATH" >> $MOCKINGBIRDPATH/$BASHPARTIAL

# Setting the DJANGO_SETTINGS_MODULE
DJANGO_SETTINGS_MODULE="mockingsite.settings.dev"
echo "export DJANGO_SETTINGS_MODULE=\"$DJANGO_SETTINGS_MODULE\"" >> $MOCKINGBIRDPATH/$BASHPARTIAL

ACTIVATE_ALIAS="alias activate=\"cd \$MOCKINGBIRDPATH/..; source bin/activate; cd -\""
echo "$ACTIVATE_ALIAS" >> $MOCKINGBIRDPATH/$BASHPARTIAL

grep --quiet "source $MOCKINGBIRDPATH/$BASHPARTIAL" ~/.bashrc || printf "\n%s\n%s\n" "# Setting up the MockingBird environment" "source $MOCKINGBIRDPATH/$BASHPARTIAL" >> ~/.bashrc

source ~/.bashrc
