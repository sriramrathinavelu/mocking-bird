OPENSHIFT_APP_PATH='/space/openshift/preview/preview/wsgi/'
OPENSHIFT_TEMPLATE_PATH='/space/openshift/preview/preview/wsgi/openshift/'
OPENSHIFT_STATIC_PATH='/space/openshift/preview/preview/wsgi/'

# Copy Mocktest
echo "Copying mocktest"
cp -r mocktest $OPENSHIFT_APP_PATH

# Copy Templates
echo "Copying Templates"
cp -r mocktest/templates $OPENSHIFT_TEMPLATE_PATH

echo "Copying Static Files"
cp -r mockingsite/static $OPENSHIFT_STATIC_PATH 
