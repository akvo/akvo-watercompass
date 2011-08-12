# Django settings for dsp project.
from os.path import dirname, join 
_dir = dirname(__file__)


from settings_base import *

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME   =join(_dir,'data/dsp.sqlite')              # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DOMAIN_NAME = 'waste-dev.akvo.org'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = '/var/dev/waste/waste-dst/dsp/mediaroot/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://%s/media/' % DOMAIN_NAME

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_x4m2#27c2dxz-8+s#4&qpx#15k-4ngulh8^^04-bgv!kcl)ui'

# Makes it possible to override with local settings e.g. DOMAIN_NAME, MEDIA_ROOT, MEDIA_URL
try:
    from settings_local import *
except:
    pass







