from django.shortcuts import get_object_or_404
from . import models
from fnpdjango.utils.views import serve_file


def attachment(request, key, ext):
    att = get_object_or_404(models.Attachment, key=key)
    return serve_file(att.attachment.url)

