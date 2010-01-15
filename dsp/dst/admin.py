# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import get_model
from django.utils.translation import ugettext, ugettext_lazy as _

class AnswerInLine(admin.TabularInline):
    model = get_model('dst', 'Answer')
    extra = 3

class FactorAdmin(admin.ModelAdmin):
    model = get_model('dst', 'Factor')
    list_display = ('factor', 'order', 'display_answers',)
    inlines = [AnswerInLine, ]

admin.site.register(get_model('dst', 'Factor'), FactorAdmin)