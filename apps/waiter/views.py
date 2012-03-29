from os.path import join
from waiter.models import WaitedFile
from waiter.settings import WAITER_URL
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

def wait(request, path):
    if WaitedFile.exists(path):
        file_url = join(WAITER_URL, path)
    else:
        file_url = ""
        waiting = get_object_or_404(WaitedFile, path=path)
        if waiting.is_stale():
            waiting = None

    if request.is_ajax():
        return HttpResponse(file_url)
    else:
        return render(request, "waiter/wait.html", locals())
