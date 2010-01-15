# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'dst.views.grid', name='grid'),
    url(r'^(?P<model>\w+)_help/(?P<id>\d+)/$', 'dst.views.grid', name='grid_help'),    
)
