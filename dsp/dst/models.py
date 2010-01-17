# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext, ugettext_lazy as _

class Factor(models.Model):
    factor          = models.CharField(_(u'factor'), max_length=50)
    order           = models.IntegerField(_(u'order'),)
    info_heading    = models.CharField(_(u'info_heading'), max_length=50)
    info_text       = models.TextField(_(u'info_text'),)

    def __unicode__(self):
        return self.factor
    
    class Meta:
        ordering = ['order']

    def display_answers(self):
        return "<br/>".join([a.answer for a in Answer.objects.filter(factor=self)])
    display_answers.allow_tags = True


class Answer(models.Model):
    factor          = models.ForeignKey(Factor, verbose_name=_(u'factor'), related_name='answers')
    answer          = models.CharField(_(u'answer'), max_length=50)
    order           = models.IntegerField(_(u'order'),)
    info_heading    = models.CharField(_(u'info_heading'), max_length=50)
    info_text       = models.TextField(_(u'info_text'),)

    def __unicode__(self):
        return self.answer
    
    class Meta:
        ordering = ['order']

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
    name        = models.CharField(_(u'name'), max_length=50)
    descripton  = models.TextField(_(u'descripton'),)
    input       = models.ManyToManyField('self', blank=True, related_name='input', )
    output      = models.ManyToManyField('self', blank=True, related_name='output', )

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _(u'technology')
        verbose_name_plural = _(u'technologies')

    
class Note(models.Model):
    note        = models.CharField(_(u'note'), max_length=100)

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
    answer          = models.ForeignKey(Answer, verbose_name=_(u'answer'),)
    applicability   = models.CharField(_('applicability'), max_length=1, choices=CHOICES_APPLICABILITY, default='A',)
    note            = models.ForeignKey(Note, verbose_name=_(u'note'), blank=True, null=True)

    def __unicode__(self):
        return self.answer.factor.factor

    class Meta:
        verbose_name = _(u'Appropriatness')
        verbose_name_plural = _(u'Appropriatnesses')

def create_relevancy_objects(sender, **kwargs):
    """
    create the "grid" of appropriateness for a certain Technology
    """
    if kwargs['created']:
        technology = kwargs['instance']
        for factor in Factor.objects.all():
            for answer in factor.answers.all():
                Relevancy.objects.create(technology=technology, answer=answer,)

post_save.connect(create_relevancy_objects, sender=Technology)
