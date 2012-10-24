class SetRemoteAddrFromXRealIP(object):
    """Sets REMOTE_ADDR from the X-Real-IP header, as set by Nginx."""
    def process_request(self, request):
        try:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
        except KeyError:
            return None
