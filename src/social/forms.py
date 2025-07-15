# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django import forms

from catalogue.models import Book
from . import models


class AddSetForm(forms.Form):
    name = forms.CharField(max_length=50)
    book = forms.IntegerField()

    def save(self, user):
        name = self.cleaned_data['name'].strip()
        if not name: return
        ul = models.UserList.get_by_name(user, name, create=True)
        try:
            book = Book.objects.get(id=self.cleaned_data['book'])
        except Book.DoesNotExist:
            return

        try:
            ul.append(book=book)
        except:
            pass

        return book, ul


class RemoveSetForm(forms.Form):
    slug = forms.CharField(max_length=50)
    book = forms.IntegerField()

    def save(self, user):
        slug = self.cleaned_data['slug']
        try:
            ul = models.UserList.objects.get(user=user, slug=slug)
        except models.UserList.DoesNotExist:
            return
        try:
            book = Book.objects.get(id=self.cleaned_data['book'])
        except Book.DoesNotExist:
            return

        try:
            ul.userlistitem_set.filter(book=book).delete()
        except:
            pass

        return book, ul
