from django.db.models import Q
from django.contrib import admin
from django import forms
from django.utils.timezone import now
from admin_ordering.admin import OrderableAdmin
from modeltranslation.admin import TranslationAdmin
from wolnelektury.utils import YesNoFilter
from . import models



admin.site.register(models.Campaign)


class IsCurrentFilter(YesNoFilter):
    title = 'Aktualny'
    parameter_name = 'current'

    @property
    def q(self):
        n = now()
        return ~(Q(since__gt=n) | Q(until__lt=n) | Q(campaign__start__gt=n) | Q(campaign__end__lt=n))


class BannerAdmin(TranslationAdmin):
    list_display = [
            'place', 'text',
            'campaign',
            'since', 'until',
            'show_members', 'staff_preview', 'only_authenticated']
    list_filter = [
        'campaign',
        IsCurrentFilter,
    ]
    autocomplete_fields = ['books']


admin.site.register(models.Banner, BannerAdmin)


class DTITForm(forms.ModelForm):
    class Meta:
        model = models.DynamicTextInsertText
        fields = '__all__'
        widgets = {
            'background_color': forms.TextInput(attrs={"type": "color"}),
            'text_color': forms.TextInput(attrs={"type": "color"}),
        }


class DynamicTextInsertTextInline(admin.TabularInline):
    model = models.DynamicTextInsertText
    form = DTITForm
    fields = ['text', 'image', 'own_colors', 'background_color', 'text_color']
    extra = 0
    min_num = 1



class DynamicTextInsertAdmin(admin.ModelAdmin):
    list_display = ['paragraphs']
    inlines = [DynamicTextInsertTextInline]


admin.site.register(models.DynamicTextInsert, DynamicTextInsertAdmin)


class MediaInsertTextInline(OrderableAdmin, admin.TabularInline):
    model = models.MediaInsertText
    extra = 0
    min_num = 1


@admin.register(models.MediaInsertSet)
class MediaInsertSetAdmin(admin.ModelAdmin):
    list_display = ['file_format', 'etag']
    inlines = [MediaInsertTextInline]
    readonly_fields = ['etag']
