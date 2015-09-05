export MOCKINGBIRDPATH="/home/sriram/venv/mocking-bird"
export PYTHONPATH=$PYTHONPATH:/home/sriram/venv/mocking-bird
export DJANGO_SETTINGS_MODULE="mockingsite.settings.production"
alias activate="cd $MOCKINGBIRDPATH/..; source bin/activate; cd -"
export VIRTUALENVPATH="/home/sriram/venv"
