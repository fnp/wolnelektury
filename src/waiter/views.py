# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os.path import join
from waiter.models import WaitedFile
from waiter.settings import WAITER_URL
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from wolnelektury.utils import is_ajax


@never_cache
def wait(request, path):
    if WaitedFile.exists(path):
        file_url = join(WAITER_URL, path)
        waiting = None
    else:
        file_url = None
        waiting = get_object_or_404(WaitedFile, path=path)

    if is_ajax(request):
        return HttpResponse(file_url)
    else:
        return render(request, "waiter/wait.html", {
            'waiting': waiting,
            'file_url': file_url,
        })
