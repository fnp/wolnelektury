# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.utils.translation import gettext_lazy as _

from catalogue.models import Book, Tag
from catalogue import utils
from social.utils import get_set, set_sets


class UserSetsForm(forms.Form):
    def __init__(self, book, user, *args, **kwargs):
        super(UserSetsForm, self).__init__(*args, **kwargs)
        self.fields['set_ids'] = forms.ChoiceField(
            choices=[(tag.id, tag.name) for tag in Tag.objects.filter(category='set', user=user).iterator()],
        )


class ObjectSetsForm(forms.Form):
    tags = forms.CharField(label=_('Tags (comma-separated)'), required=False,
                           widget=forms.Textarea())

    def __init__(self, obj, user, *args, **kwargs):
        self._obj = obj
        self._user = user
        data = kwargs.setdefault('data', {})
        if 'tags' not in data and user.is_authenticated:
            data['tags'] = ', '.join(
                obj.tags.filter(category='set', user=user).exclude(name__in=(None, '')).values_list('name', flat=True))
        super(ObjectSetsForm, self).__init__(*args, **kwargs)

    def save(self, request):
        tags = [get_set(self._user, tag_name.strip()) for tag_name in self.cleaned_data['tags'].split(',')]
        set_sets(self._user, self._obj, tags)
        return {"like": True}


class NewSetForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)

    def __init__(self, *args, **kwargs):
        super(NewSetForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['title'] = _('Name of the new shelf')

    def save(self, user, commit=True):
        name = self.cleaned_data['name']
        new_set = Tag(name=name, slug=utils.get_random_hash(name), sort_key=name.lower(), category='set', user=user)

        new_set.save()
        return new_set


class AddSetForm(forms.Form):
    name = forms.CharField(max_length=50)
    book = forms.IntegerField()

    def save(self, user):
        name = self.cleaned_data['name'].strip()
        if not name: return
        tag = get_set(user, name)
        try:
            book = Book.objects.get(id=self.cleaned_data['book'])
        except Book.DoesNotExist:
            return

        try:
            book.tag_relations.create(tag=tag)
        except:
            pass

        return book, tag


class RemoveSetForm(forms.Form):
    slug = forms.CharField(max_length=50)
    book = forms.IntegerField()

    def save(self, user):
        slug = self.cleaned_data['slug']
        try:
            tag = Tag.objects.get(user=user, slug=slug)
        except Tag.DoesNotExist:
            return
        try:
            book = Book.objects.get(id=self.cleaned_data['book'])
        except Book.DoesNotExist:
            return

        try:
            book.tag_relations.filter(tag=tag).delete()
        except:
            pass

        return book, tag
