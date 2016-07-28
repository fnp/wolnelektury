# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from newsletter.forms import NewsletterForm


# has to be this order, because otherwise the form is lacking fields
class RegistrationForm(UserCreationForm, NewsletterForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        super(RegistrationForm, self).save(commit=commit)
        NewsletterForm.save(self)
