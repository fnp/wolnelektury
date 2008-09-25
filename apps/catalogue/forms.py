# -*- coding: utf-8 -*-
from django import forms
from slughifi import slughifi

from catalogue.models import Tag
from catalogue.fields import JQueryAutoCompleteField
from catalogue import utils


class SearchForm(forms.Form):
    q = JQueryAutoCompleteField('/katalog/tags/', {'minChars': 2, 'selectFirst': True, 'cacheLength': 50})
    tags = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, *args, **kwargs):
        tags = kwargs.pop('tags', [])
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['title'] = u'tytuł, autor, motyw/temat, epoka, rodzaj, gatunek'
        self.fields['tags'].initial = '/'.join(tag.slug for tag in Tag.get_tag_list(tags))


class UserSetsForm(forms.Form):
    def __init__(self, book, user, *args, **kwargs):
        super(UserSetsForm, self).__init__(*args, **kwargs)
        self.fields['set_ids'] = forms.ChoiceField(
            choices=[(tag.id, tag.name) for tag in Tag.objects.filter(category='set', user=user)],
        )


class ObjectSetsForm(forms.Form):
    def __init__(self, obj, user, *args, **kwargs):        
        super(ObjectSetsForm, self).__init__(*args, **kwargs)
        self.fields['set_ids'] = forms.MultipleChoiceField(
            label=u'Półki',
            required=False,
            choices=[(tag.id, "%s (%s)" % (tag.name, tag.book_count)) for tag in Tag.objects.filter(category='set', user=user)],
            initial=[tag.id for tag in obj.tags.filter(category='set', user=user)],
            widget=forms.CheckboxSelectMultiple
        )
        

class NewSetForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    
    def __init__(self, *args, **kwargs):
        super(NewSetForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['title'] = u'nazwa nowej półki'
        
    def save(self, user, commit=True):
        name = self.cleaned_data['name']
        new_set = Tag(name=name, slug=utils.get_random_hash(name), sort_key=slughifi(name),
            category='set', user=user)
        
        new_set.save()
        return new_set

