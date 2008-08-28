# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class FilteredSelectMultiple(forms.SelectMultiple):
    """
    A SelectMultiple with a JavaScript filter interface.

    Note that the resulting JavaScript assumes that the SelectFilter2.js
    library and its dependencies have been loaded in the HTML page.
    """
    def _media(self):
        from django.conf import settings
        js = ['js/SelectBox.js' , 'js/SelectFilter2.js']
        return forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) for url in js])
    media = property(_media)
    
    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        self.verbose_name = verbose_name
        self.is_stacked = is_stacked
        super(FilteredSelectMultiple, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        from django.conf import settings
        output = [super(FilteredSelectMultiple, self).render(name, value, attrs, choices)]
        output.append(u'<script type="text/javascript">addEvent(window, "load", function(e) {')
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append(u'SelectFilter.init("id_%s", "%s", %s, "%s"); });</script>\n' % \
            (name, self.verbose_name.replace('"', '\\"'), int(self.is_stacked), settings.ADMIN_MEDIA_PREFIX))
        return mark_safe(u''.join(output))


class TaggableModelForm(forms.ModelForm):
    tags = forms.MultipleChoiceField(label=_('tags').capitalize(), required=True, widget=FilteredSelectMultiple(_('tags'), False))

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial']['tags'] = [tag.id for tag in self.tag_model.objects.get_for_object(kwargs['instance'])]
        super(TaggableModelForm, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = [(tag.id, tag.name) for tag in self.tag_model.objects.all()]
    
    def save(self, commit):
        obj = super(TaggableModelForm, self).save()
        tag_ids = self.cleaned_data['tags']
        tags = self.tag_model.objects.filter(pk__in=tag_ids)
        self.tag_model.objects.update_tags(obj, tags)
        return obj

    def save_m2m(self):
        # TODO: Shouldn't be needed
        pass


class TaggableModelAdmin(admin.ModelAdmin):
    form = TaggableModelForm
    
    def get_form(self, request, obj=None):
        form = super(TaggableModelAdmin, self).get_form(request, obj)
        form.tag_model = self.tag_model
        return form

