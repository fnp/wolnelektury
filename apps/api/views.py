from django.http import HttpResponseRedirect

def oauth_callback(request, data):
    key       = data.key
    secret    = data.secret
    verifier  = data.verifier
    timestamp = data.timestamp
    print data
    return HttpResponseRedirect("wl://")
    #return HttpResponseRedirect("wl://%s/%s/%s/%s/" % (key, secret, verifier, timestamp))
