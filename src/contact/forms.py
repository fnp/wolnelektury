import json
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import send_mail, mail_managers
from django.core.validators import validate_email
from django import forms
from django.template.loader import render_to_string
from django.template import RequestContext
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


contact_forms = {}
admin_list_width = 0


class ContactFormMeta(forms.Form.__class__):
    def __new__(cls, name, bases, attrs):
        global admin_list_width
        model = super(ContactFormMeta, cls).__new__(cls, name, bases, attrs)
        assert model.form_tag not in contact_forms, 'Duplicate form_tag.'
        if model.admin_list:
            admin_list_width = max(admin_list_width, len(model.admin_list))
        contact_forms[model.form_tag] = model
        return model


class ContactForm(forms.Form):
    """Subclass and define some fields."""
    __metaclass__ = ContactFormMeta

    form_tag = None
    form_title = _('Contact form')
    submit_label = _('Submit')
    admin_list = None
    result_page = False

    required_css_class = 'required'
    # a subclass has to implement this field, but doing it here breaks the order
    contact = NotImplemented

    def save(self, request, formsets=None):
        from .models import Attachment, Contact
        body = {}
        for name, value in self.cleaned_data.items():
            if not isinstance(value, UploadedFile) and name != 'contact':
                body[name] = value

        for formset in formsets or []:
            for f in formset.forms:
                sub_body = {}
                for name, value in f.cleaned_data.items():
                    if not isinstance(value, UploadedFile):
                        sub_body[name] = value
                if sub_body:
                    body.setdefault(f.form_tag, []).append(sub_body)

        contact = Contact.objects.create(
            body=json.dumps(body),
            ip=request.META['REMOTE_ADDR'],
            contact=self.cleaned_data['contact'],
            form_tag=self.form_tag)
        for name, value in self.cleaned_data.items():
            if isinstance(value, UploadedFile):
                attachment = Attachment(contact=contact, tag=name)
                attachment.file.save(value.name, value)
                attachment.save()

        site = Site.objects.get_current()
        dictionary = {
            'form_tag': self.form_tag,
            'site_name': getattr(self, 'site_name', site.name),
            'site_domain': getattr(self, 'site_domain', site.domain),
            'contact': contact,
        }
        context = RequestContext(request)
        mail_managers_subject = render_to_string([
                'contact/%s/mail_managers_subject.txt' % self.form_tag,
                'contact/mail_managers_subject.txt', 
            ], dictionary, context).strip()
        mail_managers_body = render_to_string([
                'contact/%s/mail_managers_body.txt' % self.form_tag,
                'contact/mail_managers_body.txt', 
            ], dictionary, context)
        mail_managers(mail_managers_subject, mail_managers_body, fail_silently=True)

        try:
            validate_email(contact.contact)
        except ValidationError:
            pass
        else:
            mail_subject = render_to_string([
                    'contact/%s/mail_subject.txt' % self.form_tag,
                    'contact/mail_subject.txt', 
                ], dictionary, context).strip()
            if self.result_page:
                mail_body = render_to_string(
                    'contact/%s/results_email.txt' % contact.form_tag,
                    {
                        'contact': contact,
                        'results': self.results(contact),
                    }, context)
            else:
                mail_body = render_to_string([
                        'contact/%s/mail_body.txt' % self.form_tag,
                        'contact/mail_body.txt',
                    ], dictionary, context)
            send_mail(mail_subject, mail_body, 'no-reply@%s' % site.domain, [contact.contact], fail_silently=True)

        return contact
