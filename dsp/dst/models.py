# -*- coding: utf-8 -*-

from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext, ugettext_lazy as _

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
    session     = models.ForeignKey(Session)
    criterion   = models.ForeignKey(Criterion, verbose_name=_('criterion'))
    applicable  = models.BooleanField(verbose_name=_('applicable'))

    def __unicode__(self):
        return "%s: %s" % (str(self.criterion), str(self.applicable))

    class Meta:
        verbose_name = _(u'answer')
        verbose_name_plural = _(u'answers')
        

class TechGroup(models.Model):
    name        = models.CharField(_(u'name'), max_length=50)
    order       = models.IntegerField(_(u'order'),)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['order']
        verbose_name = _(u'technology group')
        verbose_name_plural = _(u'technology groups')


class Technology(models.Model):
    group       = models.ForeignKey(TechGroup)
    factors     = models.ManyToManyField(Factor, blank=True)
    name        = models.CharField(_(u'name'), max_length=50)
    descripton  = models.TextField(_(u'descripton'),)
    #input       = models.ManyToManyField('self', blank=True, related_name='output', symmetrical=False, )
    output      = models.ManyToManyField('self', blank=True, related_name='input', symmetrical=False, )
    image       = models.ImageField(upload_to='technologies')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _(u'technology')
        verbose_name_plural = _(u'technologies')


class Note(models.Model):
    note    = models.CharField(_(u'note'), max_length=100)

    def __unicode__(self):
        return self.note[:24]
    

class Relevancy(models.Model):
    CHOICES_APPLICABILITY = (
        ('A', _('Not applicable')),    
        ('Y', _('Yes')),
        ('N', _('No')),
        ('M', _('Maybe')),    
    )        
    technology      = models.ForeignKey(Technology, verbose_name=_(u'technology'),)
    criterion       = models.ForeignKey(Criterion, verbose_name=_(u'criterion'),)
    applicability   = models.CharField(_('applicability'), max_length=1, choices=CHOICES_APPLICABILITY, default='A',)
    note            = models.ForeignKey(Note, verbose_name=_(u'note'), blank=True, null=True)

    def __unicode__(self):
        return self.criterion.factor.factor

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