# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import get_model
from django.forms import ModelForm 
from django.utils.translation import ugettext, ugettext_lazy as _

from models import Technology, TechGroup

class AnswerAdmin(admin.ModelAdmin):
    model = get_model('dst', 'Answer')

admin.site.register(get_model('dst', 'Answer'), AnswerAdmin)


class CriterionInLine(admin.TabularInline):
    model = get_model('dst', 'Criterion')
    extra = 3

class FactorAdmin(admin.ModelAdmin):
    model = get_model('dst', 'Factor')
    list_display = ('factor', 'order', 'display_criteria',)
    inlines = [CriterionInLine, ]

admin.site.register(get_model('dst', 'Factor'), FactorAdmin)


class RelevancyInLine(admin.TabularInline):
    model = get_model('dst', 'Relevancy')
    extra = 0

class TechnologyAdminForm(ModelForm):
    
    class Meta:
        model = Technology

    def __init__(self, *args, **kwargs):
        super(TechnologyAdminForm, self).__init__(*args, **kwargs)
        try:
            output_groups = TechGroup.objects.filter(order__gt=self.instance.group.order)
        except TechGroup.DoesNotExist:
            output_groups = []
        if len(output_groups):
            self.fields['output'].queryset = Technology.objects.filter(group__order__exact=output_groups[0].order)
        else:
            self.fields['output'].queryset = Technology.objects.filter(pk=0) #Empty QS

class TechnologyAdmin(admin.ModelAdmin):
    model = get_model('dst', 'Technology')
    list_display = ('__unicode__', 'group', 'display_output',  'display_input', )
    ordering = ['group__order']
    inlines = [RelevancyInLine, ]
    form = TechnologyAdminForm

admin.site.register(get_model('dst', 'Technology'), TechnologyAdmin)

class NoteAdmin(admin.ModelAdmin):
    model = get_model('dst', 'Note')

admin.site.register(get_model('dst', 'Note'), NoteAdmin)

class TechGroupAdmin(admin.ModelAdmin):
    model = get_model('dst', 'TechGroup')

admin.site.register(get_model('dst', 'TechGroup'), TechGroupAdmin)


