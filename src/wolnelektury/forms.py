# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from allauth.socialaccount.forms import SignupForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from newsletter.forms import NewsletterForm


# has to be this order, because otherwise the form is lacking fields
class RegistrationForm(UserCreationForm, NewsletterForm):
    data_processing_part2 = '''\
Dane są przetwarzane w zakresie niezbędnym do prowadzenia serwisu, a także w celach prowadzenia statystyk, \
ewaluacji i sprawozdawczości. W przypadku wyrażenia dodatkowej zgody adres e-mail zostanie wykorzystany \
także w celu przesyłania newslettera Wolnych Lektur.'''

    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        super(RegistrationForm, self).save(commit=commit)
        NewsletterForm.save(self)


class SocialSignupForm(SignupForm, NewsletterForm):
    data_processing_part2 = '''\
Dane są przetwarzane w zakresie niezbędnym do prowadzenia serwisu, a także w celach prowadzenia statystyk, \
ewaluacji i sprawozdawczości. W przypadku wyrażenia dodatkowej zgody adres e-mail zostanie wykorzystany \
także w celu przesyłania newslettera Wolnych Lektur.'''

    def save(self, *args, **kwargs):
        super(SocialSignupForm, self).save(*args, **kwargs)
        NewsletterForm.save(self)
