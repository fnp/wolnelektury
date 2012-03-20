from os.path import join
from waiter.models import WaitedFile
from waiter.settings import WAITER_URL
from django.shortcuts import get_object_or_404, render, redirect

def wait(request, path):
    if WaitedFile.exists(path):
        file_url = join(WAITER_URL, path)
    else:
        waiting_for = get_object_or_404(WaitedFile, path=path)
        # TODO: check if not stale, inform the user and send some mail if so.
    return render(request, "waiter/wait.html", locals())
