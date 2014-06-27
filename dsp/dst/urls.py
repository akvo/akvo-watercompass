 # -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
import logging
from datetime import datetime

urlpatterns = patterns('',
    url(r'^$', 'dst.views.index', name='index'),
    url(r'^factors/$', 'dst.views.factors', name='factors'),
    url(r'^(?P<model>\w+)_help/(?P<id>\d+)/$', 'dst.views.factors', name='grid_help'),  
    url(r'^(?P<model>\w+)_factorhelp/(?P<id>\d+)/$', 'dst.views.factor_help', name='factor_help'),
    
    url(r'^technologies/$', 'dst.views.technologies', name='technologies'),
    url(r'^techs_selected/$', 'dst.views.techs_selected', name='techs_selected'),
    url(r'^technologies/(?P<id>\d+)/help/$', 'dst.views.technologies_help', name='technologies_help'),
    url(r'^choice/(?P<tech_id>\d+)/$', 'dst.views.tech_choice', name='tech_choice'),
    url(r'^order_down/(?P<tech_id>\d+)/$', 'dst.views.tech_choice_order_down', name='order_down'),
    url(r'^order_up/(?P<tech_id>\d+)/$', 'dst.views.tech_choice_order_up', name='order_up'),
    
    url(r'^pdf/(?P<filename>[a-z0-9A-Z_\-]*\.pdf)$', 'dst.views.pdf'),
    url(r'^solution/$', 'dst.views.solution', name='solution'),
        
    # url(r'^help/$', direct_to_template, {'template': 'dst/help.html'}, name='help'),
    # url(r'^demo/$', direct_to_template, {'template': 'dst/demo.html'}, name='demo'),
    url(r'^reset_all/$', 'dst.views.reset_all', name='reset_all'),
    url(r'^reset_techs/$', 'dst.views.reset_techs', name='reset_techs'),
    url(r'^toggle_button/(?P<btn_name>\w+)/$', 'dst.views.toggle_button', name='toggle_button'),
    url(r'^init/$', 'dst.views.init', name='init'),
)
