# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^$', 'dst.views.factors', name='factors'),
    url(r'^(?P<model>\w+)_help/(?P<id>\d+)/$', 'dst.views.factors', name='grid_help'),  
    url(r'^(?P<model>\w+)_factorhelp/(?P<id>\d+)/$', 'dst.views.factor_help', name='factor_help'),
    
    url(r'^technologies$', 'dst.views.technologies', name='technologies'),
    url(r'^technologies/(?P<id>\d+)/help/$', 'dst.views.technologies_help', name='technologies_help'),
    url(r'^choice/(?P<tech_id>\d+)/$', 'dst.views.tech_choice', name='tech_choice'),

    url(r'^solution$', 'dst.views.solution', name='solution'),
        
    url(r'^help$', direct_to_template, {'template': 'dst/help.html'}, name='help'),
    url(r'^demo$', direct_to_template, {'template': 'dst/demo.html'}, name='demo'),
    url(r'^reset_all$', 'dst.views.reset_all', name='reset_all'),
    url(r'^reset_techs$', 'dst.views.reset_techs', name='reset_techs'),
)
