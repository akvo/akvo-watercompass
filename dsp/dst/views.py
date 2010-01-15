# -*- coding: utf-8 -*-

from django.db.models import get_model
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Factor

def grid(request, model=None, id=None):
    factors = Factor.objects.all()
    if model:
        help_item = get_model('dst', model).objects.get(id=id)
    else:
        help_item = None
    colspan = max([len(f.answers.all()) for f in factors])
    return render_to_response(
        'dst/grid.html',
        {'factors': factors, 'help_item': help_item, 'colspan': colspan},
        context_instance=RequestContext(request)
    )