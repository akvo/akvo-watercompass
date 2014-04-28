# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms

import itertools
import logging
from django.forms.forms import pretty_name

# PROFILING  
import hotshot
import os
import time
from django.conf import settings

try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"


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



class Factor(models.Model):
    factor          = models.CharField(_(u'factor'), max_length=50)
    order           = models.IntegerField(_(u'order'),)
    info_heading    = models.CharField(_(u'info heading'), max_length=50)
    info_text       = models.TextField(_(u'info text'),)

    def __unicode__(self):
        return self.factor
    
    class Meta:
        ordering = ['order']

    def display_criteria(self):
        return "<br/>".join([a.criterion for a in Criterion.objects.filter(factor=self)])
    display_criteria.allow_tags = True


class Criterion(models.Model):
    factor          = models.ForeignKey(Factor, verbose_name=_(u'factor'), related_name='criteria')
    criterion       = models.CharField(_(u'criterion'), max_length=50)
    order           = models.IntegerField(_(u'order'),)
    info_heading    = models.CharField(_(u'info heading'), max_length=50)
    info_text       = models.TextField(_(u'info text'),)

    def __unicode__(self):
        return self.criterion
    
    class Meta:
        ordering = ['order']
        verbose_name = _(u'criterion')
        verbose_name_plural = _(u'criteria')


class Answer(models.Model):
    session     = models.ForeignKey(Session, verbose_name=_('session'))
    criterion   = models.ForeignKey(Criterion, verbose_name=_('criterion'))
    applicable  = models.BooleanField(verbose_name=_('applicable'))

    def __unicode__(self):
        return "%s: %s" % (str(self.criterion), str(self.applicable))

    class Meta:
        verbose_name = _(u'answer')
        verbose_name_plural = _(u'answers')
        
class PDF_prefs(forms.Form):
    incl_selected= forms.BooleanField(required=False,initial=True)
    incl_short_expl=forms.BooleanField(required=False, initial=True)
    incl_akvopedia_1=forms.BooleanField(required=False, initial=False)
    incl_akvopedia_2=forms.BooleanField(required=False, initial=False)
    incl_akvopedia_3=forms.BooleanField(required=False, initial=False)
    incl_akvopedia_4=forms.BooleanField(required=False, initial=False)
    incl_akvopedia_5=forms.BooleanField(required=False, initial=False)
    incl_akvopedia_6=forms.BooleanField(required=False, initial=False)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'PDF preferences')
        verbose_name_plural = _(u'PDF preferences')
        
class TechGroup(models.Model):
    name        = models.CharField(_(u'name'), max_length=50)
    order       = models.IntegerField(_(u'order'),)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['order']
        verbose_name = _(u'technology group')
        verbose_name_plural = _(u'technology groups')

#Custom manager
#based on http://www.djangosnippets.org/snippets/562/ and
#http://simonwillison.net/2008/May/1/orm/
class QuerySetManager(models.Manager):
    def get_query_set(self):
        return self.model.QuerySet(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

class Technology(models.Model):
    TECH_USE_NO, TECH_USE_MAYBE, TECH_USE_YES, TECH_USE_NA, TECH_USE_NOT_ALLOWED, TECH_USE_CHOSEN = (
        'no', 'maybe', 'yes', 'na', 'hide', 'chosen',
    )
    group       = models.ForeignKey(TechGroup, verbose_name=_('technology group'))
    factors     = models.ManyToManyField(Factor, verbose_name=_('factors'), blank=True)
    name        = models.CharField(_(u'name'), max_length=50)
    description  = models.TextField(_(u'description'),)
    desc_financial = models.TextField(_(u'financial'),)
    desc_institutional = models.TextField(_(u'institutional'),)
    desc_environmental = models.TextField(_(u'environmental'),)
    desc_technical = models.TextField(_(u'technical'),)
    desc_social = models.TextField(_(u'social'),)
    output      = models.ManyToManyField('self', blank=True, related_name='input', symmetrical=False, )
    image       = models.CharField(_(u'icon image'), max_length=100, help_text=_('Enter the url of the icon image'))
    url_source1 = models.CharField(_(u'source 1'), blank=True,max_length=100, help_text=_('Enter the source of a webpage'))
    url_title1 = models.CharField(_(u'title 1'), blank=True,max_length=100, help_text=_('Enter the webpage title'))
    url1         = models.URLField(_(u'URL 1'), blank=True, help_text=_('Enter the url to the page, starting with http://'))
    url_source2 = models.CharField(_(u'source 2'), blank=True,max_length=100)
    url_title2 = models.CharField(_(u'title 2'), blank=True,max_length=100)
    url2         = models.URLField(_(u'URL 2'),blank=True)
    url_source3 = models.CharField(_(u'source 3'), blank=True,max_length=100)
    url_title3 = models.CharField(_(u'title 3'), blank=True,max_length=100)
    url3         = models.URLField(_(u'URL 3'),blank=True)

    linked_techs = models.ManyToManyField('self',blank=True, related_name='linked_tech',symmetrical=True)
    order       =  models.IntegerField(null=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _(u'technology')
        verbose_name_plural = _(u'technologies')
        ordering = [ 'name']

    # cutom manager
    objects     = QuerySetManager()
    
    class QuerySet(QuerySet):
        def input(self):
            "find all techs that have self as output"
            return Technology.objects.filter(output__in=self)
    
        def output(self):
            "find all techs that have self as input"
            return Technology.objects.filter(input__in=self)
        
      
        def all_output(self):
            "find all techs that have self as input recursively"
            return (
                self.output() |
                self.output().output() |
                self.output().output().output() |
                self.output().output().output().output() |
                self.output().output().output().output().output()
            ).distinct()
    
        def all_input(self):
            "find all techs that have self as output recursively"
            return (
                self.input() |
                self.input().input() |
                self.input().input().input() |
                self.input().input().input().input() |
                self.input().input().input().input().input()
            ).distinct()

        #def all_linked_techs(self):
        #    """
        #    find all techs linked to self
        #    the reason for itertools is that when I do
        #    (self.all_input() | self.all_output()) the result is not
        #    the expected union of all_input and all_output
        #    """
        #    return itertools.chain(self.all_input(), self.all_output())

        def all_chosen(self, session):
            return self.filter(tech_choices__session=session).order_by('group__order')

    


    #def all_linked_techs(self):
    #    #return Technology.objects.filter(pk=self.pk).all_linked_techs()

        
    def display_output(self):
        return "<table style=''>%s</table>" % "".join(
            ["<tr><td style='text-align: left; border: 0px;'>%s</td><td style='border: 0px;'>%s</td></tr>" % (
                 tech.name, tech.display_image('height: 32px; width: 32px; float: right;'),
            ) for tech in Technology.objects.filter(input=self)])
    display_output.allow_tags = True
            
    def display_input(self):
        return "<table style=''>%s</table>" % "".join(
            ["<tr><td style='text-align: left; border: 0px;'>%s</td><td style='border: 0px;'>%s</td></tr>" % (
                 tech.name, tech.display_image('height: 32px; width: 32px; float: right;'),
            ) for tech in Technology.objects.filter(output=self)])
    display_input.allow_tags = True
            
    def display_image(self, style=''):
        if style:
            return '<img src="%s%s" style="%s"/>' % (settings.MEDIA_URL, self.image, style)
        else:
            return '<img src="%s%s" />' % (settings.MEDIA_URL, self.image)
    display_image.allow_tags = True
    
         
    #def availability(self, session):
    #    """
    #    figure out if I am "available" that is can be used given choices of techs already made
    #    """
    #    chosen_techs = Technology.objects.filter(tech_choices__session=session)
    #    # self is within the chosen techs
    #    if self in chosen_techs:
    #        return self.TECH_USE_CHOSEN
    #    
    #     # self is in a group where a choice has already been made, and because we failed the first test, we are not the one chosen. Hence not available
    #    if self.group in [t.group for t in chosen_techs]:
    #        return self.TECH_USE_NOT_ALLOWED
    #    
    #    # self is within those techs which are linked to the chosen techs, hence available.
    #    if self in chosen_techs.all_linked_techs():
    #        return True
    #    return False
    #
 
    def applicable(self, session):
        """
        figure out if I'm applicable given the current environmental factors
        """
        # find the criteria that apply, i.e. get answers where applicable = True
        answers = Answer.objects.filter(session=session, applicable__exact=True)

        # given the answers, get the corresponding criteria
        criteria = Criterion.objects.filter(answer__in=answers)

        # given the criteria, find the factors that have a criterion which is selected
        factors = Factor.objects.filter(criteria__in=criteria)

        result = 0
        for fac in factors:
            criteria = Criterion.objects.filter(answer__in=answers, factor=fac)
            yes_len = len(self.relevancies.filter(applicability=Relevancy.CHOICE_YES, criterion__in=criteria))
            if yes_len:
                continue
            maybe_len = len(self.relevancies.filter(applicability=Relevancy.CHOICE_MAYBE, criterion__in=criteria))
            if maybe_len:
                result = max(result,1)
                continue
            no_len = len(self.relevancies.filter(applicability=Relevancy.CHOICE_NO, criterion__in=criteria))
            if no_len:
                result = max(result,2)

        if (result == 1):
            return self.TECH_USE_MAYBE
        elif (result == 2):
            return self.TECH_USE_NO
        return self.TECH_USE_YES

       
    def usability(self, session):
        """
        figure out "usability" status based on Answers and TechChoices
        """
        # first figure if self is usable based on choices already made
        chosen_techs = Technology.objects.filter(tech_choices__session=session)
        if chosen_techs:
            # among the chosen; return with the good news
            if self in chosen_techs:
                return self.TECH_USE_CHOSEN

            # self is in a group where the choice is already made and we're not the one
            #if self.group in [t.group for t in chosen_techs]:
            #    return self.TECH_USE_NOT_ALLOWED

            # self
            #linked = [t for t in chosen_techs.all_linked_techs()]
            #if not self in linked:
            #    return self.TECH_USE_NOT_ALLOWED

            # find all techs linked to self
            #my_linked = [t for t in self.linked_techs.all()]
            #my_linked = [t for t in self.all_linked_techs()]
            
            #my_linked  = set(my_linked)
            #chosen = set(chosen_techs)
            # all techs already chosen must be linked to me;
            # otherwise I'm not compatible with the current choices
            #if not chosen.issubset(my_linked):
                #return self.TECH_USE_NOT_ALLOWED
        # self is still eligible for selection, find out the applicability
        return self.applicable(session)

    def maybe_relevant(self, session):
        # find the criteria that apply, i.e. get answers where applicable = True
        answers = Answer.objects.filter(session=session, applicable__exact=True)
        # given the answers, get the corresponding criteria
        criteria = Criterion.objects.filter(answer__in=answers)
        # return the relevancy objects that maybe are applicable
        return Relevancy.objects.filter(technology=self, applicability=Relevancy.CHOICE_MAYBE, criterion__in=criteria)

    def not_relevant(self, session):
        # find the criteria that apply, i.e. get answers where applicable = True
        answers = Answer.objects.filter(session=session, applicable__exact=True)
        # given the answers, get the corresponding criteria
        criteria = Criterion.objects.filter(answer__in=answers)
        # return the relevancy objects that indicate the tech is not applicable
        return Relevancy.objects.filter(technology=self, applicability=Relevancy.CHOICE_NO, criterion__in=criteria) 

    def relevancy_notes(self,session):
        # find the criteria that apply, i.e. get answers where applicable = True
        answers = Answer.objects.filter(session=session, applicable__exact=True)
        # given the answers, get the corresponding criteria
        criteria = Criterion.objects.filter(answer__in=answers)
        # return the relevancy objects that indicate the tech is not applicable or maybe applicable
        return Relevancy.objects.filter(technology=self, applicability=Relevancy.CHOICE_NO, criterion__in=criteria) | Relevancy.objects.filter(technology=self, applicability=Relevancy.CHOICE_MAYBE, criterion__in=criteria)

    def maybe_notes(self, session):
        "return the notes for the maybe relevant techs"
        return [rel.note for rel in self.maybe_relevant(session)]

    def no_notes(self, session):
        "return the notes for the not relevant techs"
        return [rel.note for rel in self.not_relevant(session)]

class TechChoice(models.Model):
    session     = models.ForeignKey(Session, verbose_name=_('session'))
    technology  = models.ForeignKey(Technology, verbose_name=_('technology'), related_name='tech_choices' )
    order = models.IntegerField(null=True)
    
    class Meta:
        verbose_name = _(u'technology choice')
        verbose_name_plural = _(u'technology choices')

    def __unicode__(self):
        return str(self.technology)


class Note(models.Model):
    note    = models.TextField(_(u'note'),)

    def __unicode__(self):
        return self.note[:100]
        
    class Meta:
        ordering = ['note']


class Relevancy(models.Model):
    CHOICE_NA       = 'A'
    CHOICE_YES      = 'Y'
    CHOICE_NO       = 'N'
    CHOICE_MAYBE    = 'M'
    CHOICES_APPLICABILITY = (
        (CHOICE_NA,     _('Not applicable')),
        (CHOICE_YES,    _('Yes')),
        (CHOICE_NO,     _('No')),
        (CHOICE_MAYBE,  _('Maybe')),
    )
    technology      = models.ForeignKey(Technology, related_name='relevancies', verbose_name=_(u'technology'),)
    criterion       = models.ForeignKey(Criterion, related_name='relevancies', verbose_name=_(u'criterion'),)
    applicability   = models.CharField(_('applicability'), max_length=1, choices=CHOICES_APPLICABILITY, default='A',)
    note            = models.ForeignKey(Note, verbose_name=_(u'note'), blank=True, null=True)

    def __unicode__(self):
        return pretty_name(str(self.criterion.factor))
    
    def show_criterion(self):
        return pretty_name(str(self.criterion))

    class Meta:
        verbose_name = _(u'Appropriatness')
        verbose_name_plural = _(u'Appropriatnesses')


def create_relevancy_objects(technology):
    """
    create the "grid" of appropriateness for a certain Technology
    """
    #if kwargs['created']:
    #technology = kwargs['instance']
    for factor in Factor.objects.filter(pk__in=[pk for pk in technology.factors.all().values_list('pk', flat=True)]):
        for criterion in factor.criteria.all():
            try:
                Relevancy.objects.get(technology=technology, criterion=criterion,)
            except Relevancy.DoesNotExist:
                Relevancy.objects.create(technology=technology, criterion=criterion,)

from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
def act_on_log_entry(sender, **kwargs):
    """
    catch the LogEntry post_save to grab newly added Technology instances and create
    relevancy objects for it
    we do this at this time to be able to work with a fully populated Technology
    instance
    """
    CRITERIA = [
        {'app': 'dst', 'model': 'technology', 'action': ADDITION, 'call': create_relevancy_objects},
        {'app': 'dst', 'model': 'technology', 'action': CHANGE,   'call': create_relevancy_objects},
    ]
    if kwargs.get('created', False):
        log_entry = kwargs['instance']
        content_type = ContentType.objects.get(pk=log_entry.content_type_id)
        for criterion in CRITERIA:
            if (
                content_type.app_label == criterion['app']
                and content_type.model == criterion['model']
                and log_entry.action_flag == criterion['action']
            ):
                #user = User.objects.get(pk=log_entry.user_id)
                object = content_type.get_object_for_this_type(pk=log_entry.object_id)
                criterion['call'](object)
       
#post_save.connect(create_relevancy_objects, sender=Technology)
post_save.connect(act_on_log_entry, sender=LogEntry)
