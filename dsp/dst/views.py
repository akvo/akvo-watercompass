# -*- coding: utf-8 -*-

from django.contrib.sessions.models import Session
from django.db.models import get_model
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from models import Factor, TechGroup, Technology, Relevancy, Answer, Criterion

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

def get_or_create_answers(session):
    session = Session.objects.get(pk=session)
    answers = Answer.objects.filter(session=session)
    if not answers.count():
        criteria = Criterion.objects.all()
        for criterion in criteria:
            Answer.objects.create(session=session, criterion=criterion, applicable=False)
    return Answer.objects.filter(session=session).order_by('criterion__factor__order', 'criterion__order')

def pretty_name(name):
    "Converts 'first_name' to 'First name'"
    name = name[0].upper() + name[1:]
    return name.replace('_', ' ')
    
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
    AnswerFormSet = modelformset_factory(
        Answer,
        form = AnswerForm,
        extra = 0,
    )
    
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect('/')
    else:
        qs = get_or_create_answers(request.session.session_key)
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


@render_to('dst/technologies_help.html')
def technologies_help(request,id=None):
    
    technology = get_object_or_404(Technology, pk=id)
    relevancy_objects = Relevancy.objects.all().filter(technology__exact=id).exclude(applicability__exact='A')
    
    #relevancy_objects = Relevancy.objects.all().filter(technology__exact=id).filter(criterion='fetched')
    
    return { 'technology': technology, 'relevancy_objects':relevancy_objects }


@render_to('dst/solution.html')
def solution(request):

    return {}