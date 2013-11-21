# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import logging
from datetime import datetime
from pyPdf import PdfFileWriter, PdfFileReader

from models import Factor, TechGroup, Technology, Relevancy, Answer, Criterion, TechChoice, PDF_prefs
from utils import pretty_name
from pdf_utils import *

# PROFILING  
import hotshot
import os
import time
import settings
import re
import markdown2

try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"

# turns markdown to html. changes html links to target _blank
def markdownToHtml(mdString):
    result = markdown2.markdown(mdString) 
    # we should add a target="_blank" to the links, so they open in a new window.
    return result 

def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
    where the time stamp is in UTC. This makes it easy to run and compare 
    multiple trials.     
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer

# END PROFILING 
class HttpResponseNoContent(HttpResponse):
    status_code = 204
    
def get_session(request):
    session, created = Session.objects.get_or_create(pk=request.session.session_key)
    #session = Session.objects.get(pk=request.session.session_key)
    return session
    
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


@render_to('dst/index.html')
def index(request):
    request.session.set_test_cookie()
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

# currently not used: may be needed for cookie detection
def init(request):
    request.session['init'] = init
    HttpResponseRedirect(reverse('factors'))

def initialize_linked_techs():
    techs = Technology.objects.all()
    for tech in techs:
        linked_all=tech.all_linked_techs()
        for linked in linked_all:
            tech.linked_techs.add(linked)
            
    #for tech in techs:
    #    linked_all=tech.linked_techs.all()
    #    for linked in linked_all:
    #        logging.debug('tech %s links to %s' % (tech, linked))
    
def init_session(session):
    uses = 'TECH_USE_NO', 'TECH_USE_MAYBE', 'TECH_USE_YES', 'TECH_USE_NOT_ALLOWED'
 #  initializing linked technologies is only necessary to build up the lookup table in the database
 #  initialize_linked_techs()
    btns = [getattr(Technology, use) for use in uses]
    buttons = ["%s_ishidden" % btn for btn in btns ]
    for button in buttons:
        if button not in session.keys():
            session[button] = False
        
def initialize_Akvopedia_articles():
    techs = Technology.objects.all()
    for tech in techs:
        if tech.url!='':
            create_PDF_akvopedia(tech.url)
    
@render_to('dst/factors.html')
def factors(request, model=None, id=None):
    init_session(request.session)
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
            return HttpResponseRedirect(reverse('factors'))
    else:
        #get answers. If they don't exist yet for this session, create them and make the False by default
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
    return {
        'formset'           : formset,
        'zipped_formlist'   : zipped_formlist,
        'help_item'         : help_item,
        'session'           : request.session,
    }


@render_to('dst/factor_help.html')
def factor_help(request, model=None, id=None):
    factors = Factor.objects.all()
    if model:
        help_item = get_model('dst', model).objects.get(id=id)
        help_item.info_text = markdownToHtml(help_item.info_text)
    else:
        help_item = None
    return {'help_item': help_item}

#@profile("technologies.prof")
@render_to('dst/technologies.html')
def technologies(request, model=None, id=None):
    if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

    #forms part 
    init_session(request.session)
    AnswerFormSet = modelformset_factory(
        Answer,
        form = AnswerForm,
        extra = 0,
    )
    
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()   
    
    #if there are no valid answers, we just default to false
    qs = get_or_create_answers(get_session(request))
    
    formset = AnswerFormSet(queryset=qs)
    form_list = [form for form in formset.forms]
    change_list = []
    factor_list = []
    old_factor = ''
    
    # the 'change' variable is used to detect when we need to display a new factor. The form list is just a list of all criteria.
    for form in formset.forms:
        new_factor = form.instance.criterion.factor
        factor_list.append(new_factor)
        change_list.append(new_factor != old_factor)
        form.fields['applicable'].label = pretty_name(str(form.instance.criterion))
        old_factor = new_factor
    
    # create zipped list of forms, factors and change. Each form is one criterium.
    zipped_formlist = zip(form_list, factor_list, change_list)
    
    if model:
        help_item = get_model('dst', model).objects.get(id=id)
    else:
        help_item = None 
    #end forms part 
    
    #technology part
    groups = TechGroup.objects.all()
    choices = TechChoice.objects.filter(session=get_session(request)).order_by('order')
    group_techs = []
    one_chosen = False;
    for group in groups:
        techs = Technology.objects.filter(group=group).order_by('order')
        for tech in techs:
            tech.usable = tech.usability(get_session(request))
            if (tech.usable == 'chosen'):
                one_chosen = True
       #     tech.available = tech.availability(get_session(request))
        group_techs.append(techs)
    # if we want to transpose the data:
    #all_techs = map(None, *group_techs)
    all_techs = zip(groups, group_techs)
    return {
        'techgroups'    : groups,
        'all_techs'     : all_techs,
        'session'       : request.session,
        'formset'           : formset,
        'zipped_formlist'   : zipped_formlist,
        'help_item'         : help_item,
        'one_chosen'        : one_chosen,
        'chosen_techs' : choices,
    }

def pdf(request, filename):
    logging.debug('------------------------path -----')
    
    fullpath = os.path.join(settings.PDF_PATH, filename)
    logging.debug('------------------------path -----'+fullpath)
    response = HttpResponse(file(fullpath).read())
    response['Content-Type'] = 'application/pdf'
    response['Content-disposition'] = 'attachment'
    return response

@render_to('dst/techs_selected.html')
def techs_selected(request, model=None, id=None):

    groups = TechGroup.objects.all()

    chosen_techs = Technology.objects.filter(tech_choices__session=get_session(request))    
    chosen_in_group = []
    relevance=[]
    empty=[]

    for group in groups:
        found_tech = False
        found_relevance=False
        techs = Technology.objects.filter(group=group)
        for tech in techs:
            if tech in chosen_techs:
                chosen_in_group.append(tech)
                found_tech = True
               
                applicable = tech.applicable(get_session(request))
              #  relevancy_objects = []
                
                if applicable == tech.TECH_USE_MAYBE:
                    relevancy_objects = list(tech.maybe_relevant(get_session(request)))
                    if len(relevancy_objects)!=0:
                        #for object in relevancy_objects:
                         #   logging.debug(object.note)
                        relevance.append(relevancy_objects)
                        found_relevance=True

        if found_tech == False:
            chosen_in_group.append('')
        if found_relevance == False:
            relevance.append(empty)
        
    all_chosen_techs = zip(groups,chosen_in_group,relevance)
    
    if request.method == 'POST': # If the form has been submitted...
        form = PDF_prefs(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            
            incl_selected=form.cleaned_data['incl_selected']
            incl_short_expl=form.cleaned_data['incl_short_expl']
            
            incl_akvopedia=[]
            incl_akvopedia.append(form.cleaned_data['incl_akvopedia_1'])
            incl_akvopedia.append(form.cleaned_data['incl_akvopedia_2'])
            incl_akvopedia.append(form.cleaned_data['incl_akvopedia_3'])
            incl_akvopedia.append(form.cleaned_data['incl_akvopedia_4'])
            incl_akvopedia.append(form.cleaned_data['incl_akvopedia_5'])
            incl_akvopedia.append(form.cleaned_data['incl_akvopedia_6'])
            
            # create list of Akvopedia articles to be included
            Akvopedia_articles_URL=[]
            for index,incl_akv in enumerate(incl_akvopedia):
                if (incl_akv==True and chosen_in_group[index]!=''):
                    if chosen_in_group[index].url!='':
                        Akvopedia_articles_URL.append(chosen_in_group[index].url)
            
            # create list of factors and criteria
            answers = get_or_create_answers(get_session(request))
        
            criterion_list=[]
            applicable_list=[]
            change_list = []
            factor_list = []
            old_factor = ''
    
            # the 'change' variable is used to detect when we need to display a new factor. The form list is just a list of all criteria.
            for answer in answers:
                criterion_list.append(answer.criterion)
                applicable_list.append(answer.applicable)
                new_factor = answer.criterion.factor
                factor_list.append(new_factor)
                change_list.append(new_factor != old_factor)
                old_factor = new_factor
        
        
            zipped_answerlist = zip(factor_list,change_list,criterion_list,applicable_list)
        
            # This will generate all akvopedia articles in pdf form from the wiki. Needs to be done only once.
            #initialize_Akvopedia_articles()
            
            #create the basic PDF
            today=datetime.datetime.today()
    
            format_temp = "Akvo-DST-%a-%b-%d-%Y_%H-%M-%S.temp.pdf"
            format_final= "Akvo-DST-%a-%b-%d-%Y_%H-%M-%S.pdf"
            
            s_name_temp=today.strftime(format_temp)
            s_name_final=today.strftime(format_final)
            
            #first create first pages
            pdf_path=create_PDF_selected_techs(all_chosen_techs, zipped_answerlist,incl_selected,incl_short_expl,s_name_temp)
            
            # append akvopedia articles if checked.
            THIS_PATH=os.path.dirname(__file__)
            (HOME,HERE)=os.path.split(THIS_PATH)
            akvopedia_pdf_dir=HOME+'/mediaroot/akvopedia_pdf/'
            output_dir=HOME+'/mediaroot/pdf_tmp/'
               
            output = PdfFileWriter()
            outputStream = file(output_dir+s_name_final, "wb")
            
            input = PdfFileReader(file(output_dir+s_name_temp, "rb"))
            num_pages=input.getNumPages()
            for i in range(num_pages):
                output.addPage(input.getPage(i))
            
            for article_url in Akvopedia_articles_URL:    
                # create pdf path
                URL_list=article_url.split("/")
                article_name=URL_list[-1]
                full_path=akvopedia_pdf_dir+article_name+'.pdf'
                
                # append article
                input = PdfFileReader(file(full_path, "rb"))
                num_pages=input.getNumPages()
                for i in range(num_pages):
                    output.addPage(input.getPage(i))
            
            output.write(outputStream)
            outputStream.close()       
            
            
            return {
              'techgroups'    : groups,
                'all_chosen_techs'    : all_chosen_techs,
                'session'       : request.session,
                'form'          : form,
                'pdf_file'      :'/pdf/'+s_name_final,
            }        
                
                #HttpResponseRedirect(reverse('techs_selected_download')) # Redirect after POST
    else:
        form = PDF_prefs() # An unbound form
    
    return {
        'techgroups'    : groups,
        'all_chosen_techs'    : all_chosen_techs,
        'session'       : request.session,
        'form'          : form,
        'pdf_file'      :'',
    }



def tech_choice(request, tech_id):
    numChoices = TechChoice.objects.filter(session=get_session(request)).count()
    choice, created = TechChoice.objects.get_or_create(session=get_session(request), technology=Technology.objects.get(pk=tech_id))
    if not created:
        allChoices = TechChoice.objects.filter(session=get_session(request))
        for ch in allChoices:
            if (ch.order > choice.order):
                ch.order = ch.order - 1
                ch.save()
        choice.delete()
    else:
        choice.order = numChoices + 1
        choice.save()
    return HttpResponseRedirect(reverse('technologies'))


def toggle_button(request, btn_name=''):
    if btn_name:
        if not request.session.setdefault(btn_name, False):
            request.session[btn_name] = True
        else:
            request.session[btn_name] = False
    return HttpResponseNoContent()

def reset_all(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('technologies'))


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
    relevancy_objects = []
    
    # turn links into html links
    technology.description = markdownToHtml(technology.description)
    technology.desc_financial = markdownToHtml(technology.desc_financial)
    technology.desc_institutional = markdownToHtml(technology.desc_institutional)
    technology.desc_environmental = markdownToHtml(technology.desc_environmental)
    technology.desc_technical = markdownToHtml(technology.desc_technical)
    technology.desc_social = markdownToHtml(technology.desc_social)

    relevancy_objects = technology.relevancy_notes(session) 
    return { 'technology': technology, 'relevancy_objects':relevancy_objects, 'settings': settings}


@render_to('dst/solution.html')
def solution(request):
    groups = TechGroup.objects.all()
    group_techs = []
    for group in groups:
        chosen_techs = Technology.objects.filter(group=group).filter(tech_choices__session=get_session(request))
        for tech in chosen_techs:
            tech.usable = tech.usability(get_session(request))
     #       tech.available = tech.availability(get_session(request))
        group_techs.append(chosen_techs)
    
    # if we want to transpose the data:
    #all_techs = map(None, *group_techs)
    all_techs = zip(groups, group_techs)
    return {
        'techgroups'    : groups,
        'all_techs'     : all_techs,
    }