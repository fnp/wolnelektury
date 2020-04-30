from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from . import models


class WLRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, slug):
        redirect = get_object_or_404(models.Redirect, slug=slug)
        redirect.update_counter()
        return redirect.url
