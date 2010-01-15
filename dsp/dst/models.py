# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

class Factor(models.Model):
    factor          = models.CharField(_(u'factor'), max_length=50)
    order           = models.IntegerField(_(u'order'),)
    info_heading    = models.CharField(_(u'info_heading'), max_length=50)
    info_text       = models.TextField(_(u'info_text'),)

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

    class Meta:
        ordering = ['order']