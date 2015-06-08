DJANGO_TEMPLATE='/space/mockingbird/mocktest/templates/mocktest'
WSK_APP='/space/mockingbird/web-starter-kit-0.5.4/app'
DJANGO_HISTORY='/space/template_hist'

# Take Back up of Current templates
FOLDERNAME='WSK_'`date +''%d-%m-%y-%H-%M-%S''`
mkdir $DJANGO_HISTORY/$FOLDERNAME
cp -r $WSK_APP $DJANGO_HISTORY/$FOLDERNAME

echo "COPYING TEMPLATE FILES"
cp -r $DJANGO_TEMPLATE/*.html $WSK_APP
