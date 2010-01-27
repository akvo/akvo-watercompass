# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'dst.views.grid', name='grid'),
    url(r'^(?P<model>\w+)_help/(?P<id>\d+)/$', 'dst.views.grid', name='grid_help'),  
    url(r'^(?P<model>\w+)_factorhelp/(?P<id>\d+)/$', 'dst.views.factor_help', name='factor_help'),
    
    url(r'^technologies/$', 'dst.views.technologies', name='technologies'),
    url(r'^solution/$', 'dst.views.solution', name='solution'),
)
