from defaults import *

DEBUG=True

COMPRESS_ENABLED=True

ALLOWED_HOSTS=['127.0.0.1', 'localhost', 'crackit.com']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'mocktest', 'templates_prod')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],  
        },  
    },  
]

STATIC_ROOT = os.path.join(PROJECT_ROOT, '../static_prod')
