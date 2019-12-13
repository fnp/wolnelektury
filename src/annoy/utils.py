from functools import wraps


def banner_exempt(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        request.annoy_banner_exempt = True
        return view(request, *args, **kwargs)
    return wrapped
