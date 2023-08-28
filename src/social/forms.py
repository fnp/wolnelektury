# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms

from catalogue.models import Book, Tag
from social.utils import get_set


class UserSetsForm(forms.Form):
    def __init__(self, book, user, *args, **kwargs):
        super(UserSetsForm, self).__init__(*args, **kwargs)
        self.fields['set_ids'] = forms.ChoiceField(
            choices=[(tag.id, tag.name) for tag in Tag.objects.filter(category='set', user=user).iterator()],
        )


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
