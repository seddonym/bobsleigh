"""Base settings shared by all environments.
This is a reusable basic settings file.
"""
from django.conf.global_settings import *
import os
import sys
import re

#==============================================================================
# Generic Django project settings
#==============================================================================

SITE_ID = 1
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'GB'
USE_TZ = True
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en-GB'
LANGUAGES = (
    ('en-GB', 'British English'),
)

INSTALLED_APPS = (
    'south',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)


LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'

STATICFILES_DIRS = (
)

ADMINS = (
    ('David Seddon', 'david@seddonym.me'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'error': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            # 'filename': LOG_PATH, - filled in by handler
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers':['error'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins', 'error'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

# During tests, disable migrations and use syncdb instead
SOUTH_TESTS_MIGRATE = False

ROOT_URLCONF = 'urls'
TEMPLATE_DIRS = ('templates',)