# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


from models import Factor, TechGroup, Technology, Relevancy, Answer, Criterion, TechChoice
from utils import pretty_name

def get_session(request):
    return Session.objects.get(pk=request.session.session_key)
    
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
    try:
        return HttpResponseRedirect(settings.START_URL)
    except:
        return {}

def get_or_create_answers(session):
    answers = Answer.objects.filter(session=session)
    if not answers.count():
        criteria = Criterion.objects.all()
        for criterion in criteria:
            Answer.objects.create(session=session, criterion=criterion, applicable=False)
    return Answer.objects.filter(session=session).order_by('criterion__factor__order', 'criterion__order')

    
from django.forms.models import modelformset_factory
from django.forms.widgets import HiddenInput, CheckboxInput


class AnswerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # change the widget type:
        self.base_fields['criterion'].widget = HiddenInput()

        super(AnswerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Answer
        fields = ['id', 'criterion', 'applicable',]


@render_to('dst/factors.html')
def factors(request, model=None, id=None):
    request.session['init'] = 'init'
    AnswerFormSet = modelformset_factory(
        Answer,
        form = AnswerForm,
        extra = 0,
    )
    
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('technologies'))
    else:
        qs = get_or_create_answers(get_session(request))
        formset = AnswerFormSet(queryset=qs)
        form_list = [form for form in formset.forms]
        change_list = []
        factor_list = []
        old_factor = ''
        for form in formset.forms:
            new_factor = form.instance.criterion.factor
            factor_list.append(new_factor)
            change_list.append(new_factor != old_factor)
            form.fields['applicable'].label = pretty_name(str(form.instance.criterion))
            old_factor = new_factor
        zipped_formlist = zip(form_list, factor_list, change_list)
    if model:
        help_item = get_model('dst', model).objects.get(id=id)
    else:
        help_item = None
    return { 'formset': formset, 'zipped_formlist': zipped_formlist, 'help_item': help_item, }#'colspan': colspan, }


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
    groups = TechGroup.objects.all()
    group_techs = []
    for group in groups:
        techs = Technology.objects.filter(group=group)
        for tech in techs:
            tech.usable = tech.usability(get_session(request))
            tech.available = tech.availability(get_session(request))
        group_techs.append(techs)
    # if we want to transpose the data:
    #all_techs = map(None, *group_techs)
    all_techs = zip(groups, group_techs)
    return {
        'techgroups'    : groups,
        'all_techs'     : all_techs,
    }


def tech_choice(request, tech_id):
    choice, created = TechChoice.objects.get_or_create(session=get_session(request), technology=Technology.objects.get(pk=tech_id))
    if not created:
        choice.delete()
    return HttpResponseRedirect(reverse('technologies'))


def reset_all(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('start'))


def reset_techs(request):
    TechChoice.objects.filter(session=get_session(request)).delete()
    return HttpResponseRedirect(reverse('technologies'))


@render_to('dst/technologies_help.html')
def technologies_help(request,id=None):
    # Needs to be refined to filter on selection
    #
    
    #user_id = request.session['auth_user_id']
    session = get_session(request)
        
    technology = get_object_or_404(Technology, pk=id)
    applicable = technology.applicable(session)
    relevancy_objects = []
    
    if applicable == technology.TECH_USE_MAYBE:
        relevancy_objects = technology.maybe_relevant(session)

    elif applicable == technology.TECH_USE_NO:
        relevancy_objects = technology.not_relevant(session)
    
    return { 'technology': technology, 'relevancy_objects':relevancy_objects,}


@render_to('dst/solution.html')
def solution(request):
    groups = TechGroup.objects.all()
    group_techs = []
    for group in groups:
        chosen_techs = Technology.objects.filter(group=group).filter(tech_choices__session=get_session(request))
        for tech in chosen_techs:
            tech.usable = tech.usability(get_session(request))
            tech.available = tech.availability(get_session(request))
        group_techs.append(chosen_techs)
    
    # if we want to transpose the data:
    #all_techs = map(None, *group_techs)
    all_techs = zip(groups, group_techs)
    return {
        'techgroups'    : groups,
        'all_techs'     : all_techs,
    }