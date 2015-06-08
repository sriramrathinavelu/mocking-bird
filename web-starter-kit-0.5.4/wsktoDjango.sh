DJANGO_STATIC='/space/mockingbird/mockingsite/static/mocktest'
DJANGO_TEMPLATE='/space/mockingbird/mocktest/templates/mocktest'
DJANGO_HISTORY='/space/template_hist'


WSK_PATH='dist/static/mocktest'

# Clearing previous static files
echo "Clearing Django Static Files"
(cd $DJANGO_STATIC; rm -rf; cd -)

# Build the Web Starter Toolkit
echo "Building Web Starter Kit"
gulp

# Copy Images, CSS and JS to static folder of Django

echo "Copying Fonts"
cp -r dist/fonts $DJANGO_STATIC/

echo "Copying Images"
cp -r $WSK_PATH/images $DJANGO_STATIC/

echo "Copying Scripts"
cp -r $WSK_PATH/scripts $DJANGO_STATIC/
cp -r dist/scripts $DJANGO_STATIC/

echo "Copying Styles" #minified
cp -r dist/styles $DJANGO_STATIC/

# Take Back up of Current templates
FOLDERNAME='Template_'`date +''%d-%m-%y-%H-%M-%S''`
mkdir $DJANGO_HISTORY/$FOLDERNAME
cp -r $DJANGO_TEMPLATE $DJANGO_HISTORY/$FOLDERNAME

# Copy html files to template folder
echo "Copying html files"
cp dist/*.html $DJANGO_TEMPLATE/
