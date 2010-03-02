# -*- coding: utf-8 -*-

from django.db.models import get_model
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Factor, TechGroup, Technology

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    From: http://www.djangosnippets.org/snippets/821/
    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer


@render_to('dst/start.html')
def start(request):
    return {
    }

@render_to('dst/factors.html')
def factors(request, model=None, id=None):
    factors = Factor.objects.all()
    if model:
        help_item = get_model('dst', model).objects.get(id=id)
    else:
        help_item = None
    colspan = max([len(f.answers.all()) for f in factors])
    return {'factors': factors, 'help_item': help_item, 'colspan': colspan}
    
@render_to('dst/factor_help.html')
def factor_help(request, model=None, id=None):
    factors = Factor.objects.all()
    if model:
        help_item = get_model('dst', model).objects.get(id=id)
    else:
        help_item = None
    return {'help_item': help_item}

@render_to('dst/technologies.html')
def technologies(request):
    techgroups = TechGroup.objects.all()
    user_interface_technologies = Technology.objects.all().filter(group__id__exact=3)
    collection_technologies = Technology.objects.all().filter(group__id__exact=2)
    conveyance_technologies = Technology.objects.all().filter(group__id__exact=1)
    centralized_technologies = Technology.objects.all().filter(group__id__exact=4)
    disposal_technologies = Technology.objects.all().filter(group__id__exact=5)
    
    return {
        'techgroups': techgroups,
        'user_interface_technologies': user_interface_technologies, 
        'collection_technologies': collection_technologies,
        'conveyance_technologies': conveyance_technologies,
        'centralized_technologies': centralized_technologies,
        'disposal_technologies': disposal_technologies,
        }

@render_to('dst/solution.html')
def solution(request):

    return {}