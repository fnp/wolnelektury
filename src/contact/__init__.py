# -*- coding: utf-8 -*-
"""
Generic app for creating contact forms.

0. Add 'contact' to your INSTALLED_APPS and include 'contact.urls' somewhere
in your urls.py, like: 
    url(r'^contact/', 
        include('contact.urls'))

1. Migrate.

2. Create somewhere in your project a module with some subclasses of
contact.forms.ContactForm, specyfing form_tag and some fields in each.

3. Set CONTACT_FORMS_MODULE in your settings to point to the module.

4. Link to the form with {% url 'contact_form' form_tag %}.

5. Optionally override some templates in form-specific template directories
(/contact/<form_tag>/...).

6. Receive submitted forms by email and read them in admin.


Example:
========

settings.py:
    CONTACT_FORMS_MODULE = 'myproject.contact_forms'

myproject/contact_forms.py:
    from django import forms
    from contact.forms import ContactForm
    from django.utils.translation import ugettext_lazy as _

    class RegistrationForm(ContactForm):
        form_tag = 'register'
        name = forms.CharField(label=_('Name'), max_length=128)
        presentation = forms.FileField(label=_('Presentation'))

some_template.html:
    {% url 'contact:form' 'register' %}

"""

from fnpdjango.utils.app import AppSettings


class Settings(AppSettings):
    FORMS_MODULE = "contact_forms"


app_settings = Settings('CONTACT')
