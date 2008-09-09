"""
Debug Toolbar middleware
"""
import re
from django.conf import settings
from django.utils.encoding import smart_str
from debug_toolbar.toolbar.loader import DebugToolbar

_HTML_TYPES = ('text/html', 'application/xhtml+xml')
_END_HEAD_RE = re.compile(r'</head>', re.IGNORECASE)
_END_BODY_RE = re.compile(r'<body[^<]*>', re.IGNORECASE)

class DebugToolbarMiddleware(object):
    """
    Middleware to set up Debug Toolbar on incoming request and render toolbar
    on outgoing response.
    """
    def __init__(self):
        self.debug_toolbar = None

    def show_toolbar(self, request):
        if not settings.DEBUG:
            return False
        if not request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return False
        return True

    def process_request(self, request):
        if self.show_toolbar(request):
            self.debug_toolbar = DebugToolbar(request)
            self.debug_toolbar.load_panels()
            debug = request.GET.get('djDebug')
            # kinda ugly, needs changes to the loader to optimize
            for panel in self.debug_toolbar.panels:
                response = panel.process_request(request)
                if not response:
                    if debug == panel.name:
                        response = panel.process_ajax(request)
                if response:
                    response.skip_debug_response = True
                    return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.show_toolbar(request):
            for panel in self.debug_toolbar.panels:
                cb = panel.process_view(request, callback, callback_args, callback_kwargs)
                if cb:
                    callback = cb
            return callback

    def process_response(self, request, response):
        if self.show_toolbar(request) and not getattr(response, 'skip_debug_response', False):
            if response['Content-Type'].split(';')[0] in _HTML_TYPES and not request.is_ajax():
                # Saving this here in case we ever need to inject into <head>
                #response.content = _END_HEAD_RE.sub(smart_str(self.debug_toolbar.render_styles() + "%s" % match.group()), response.content)
                for panel in self.debug_toolbar.panels:
                    nr = panel.process_response(request, response)
                    # Incase someone forgets `return response`
                    if nr: response = nr
                response.content = _END_BODY_RE.sub(smart_str('<body>' + self.debug_toolbar.render_toolbar()), response.content)
        return response
