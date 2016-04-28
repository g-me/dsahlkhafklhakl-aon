import os
from django.core.urlresolvers import reverse

import dotenv
from getenv import env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = env('APP_KEY', 'key')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]
EXTERNAL_APPS = [
    'registration',  # django-registration-redux
    'avatar',  # django-avatar
]
INTERNAL_APPS = [
    'app',
]

INSTALLED_APPS += EXTERNAL_APPS
INSTALLED_APPS += INTERNAL_APPS

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aon.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'aon.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Membership Setting

REGISTRATION_OPEN = True
# REGISTRATION_FORM = 'app.forms.AppRegistrationForm'
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = '/accounts/login/'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # todo change email backend on production
EMAIL_HOST = env('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True




# AVATAR SETTING
AVATAR_GRAVATAR_DEFAULT = 'identicon'
AVATAR_DEFAULT_URL = 'avatars/default.jpg'


import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)



PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# todo fix image path issue
# MEDIA SETTINGS
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")
MEDIA_URL = "/media/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)



STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
