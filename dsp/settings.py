# -*- coding: utf-8 -*-
# Django settings for dsp project.

import os.path
from os.path import dirname, join
_dir = dirname(__file__)
# MTW added logging
import logging
BASE_PATH = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG, filename=BASE_PATH+'/mediaroot/logging/debug.log',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
# end MTW
PDF_PATH=BASE_PATH+'/mediaroot/pdf_tmp/'

PROFILE_LOG_BASE=BASE_PATH+'/profile/'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SERVER_EMAIL = 'm.t.westra@akvo.org'

ADMINS = (
    ('Gabriel von Heijne', 'gabriel@akvo.org'),
    (u'Mark Tiele Westra', 'm.t.westra@akvo.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(_dir,'data/dsp.sqlite') ,
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

STATIC_DOC_ROOT= BASE_PATH+'/mediaroot/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = BASE_PATH+'/mediaroot'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm6539&amp;i(t3*94+r7j9c18onc98$#5p1v+e0_8=^^ds)jj(0(bb'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
#    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'dsp.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_PATH+'/templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'dst',
)

# Override the server-derived value of SCRIPT_NAME 
# See http://code.djangoproject.com/wiki/BackwardsIncompatibleChanges#lighttpdfastcgiandothers
FORCE_SCRIPT_NAME = ''
