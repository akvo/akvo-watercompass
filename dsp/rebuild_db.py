#!/usr/local/bin/python
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

from django.conf import settings

# dump the data to fixtures
#os.system('python manage.py dumpdata collector --indent=2 > collector/models/fixtures/data.json')
# replace with db_dump.py:
os.system('python db_dump.py dump')
# drop and recreate the db (this is for sqlite)
os.system('rm %s' % settings.DATABASE_NAME)
# sync the db
os.system('python manage.py syncdb --noinput')

# create a super user
from django.contrib.auth.models import User
u = User.objects.create(
    username='gabriel',
    first_name='',
    last_name='',
    email='gabriel@akvo.org',
    is_superuser=True,
    is_staff=True,
    is_active=True
)
u.set_password('qedvsb')
u.save()
print "User account created"

# load the fixtures back in
os.system('python db_dump.py load')
# run the server
os.system('python manage.py runserver')
