
from sunburnt import sunburnt
from lxml import etree
import urllib
import warnings


class HLSolrConnection(sunburnt.SolrConnection):
    def __init__(self, *args, **kw):
        super(HLSolrConnection, self).__init__(*args, **kw)
        self.analysis_url = self.url + "analysis/field/"

    def highlight(self, params):
        qs = urllib.urlencode(params)
        url = "%s?%s" % (self.analysis_url, qs)
        if len(url) > self.max_length_get_url:
            warnings.warn("Long query URL encountered - POSTing instead of "
                "GETting. This query will not be cached at the HTTP layer")
            url = self.analysis_url
            kwargs = dict(
                method="POST",
                body=qs,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        else:
            kwargs = dict(method="GET")
        r, c = self.request(url, **kwargs)
        if r.status != 200:
            raise sunburnt.SolrError(r, c)
        return c


class HLSolrInterface(sunburnt.SolrInterface):
    # just copied from parent and SolrConnection -> HLSolrConnection
    def __init__(self, url, schemadoc=None, http_connection=None, mode='', retry_timeout=-1, max_length_get_url=sunburnt.MAX_LENGTH_GET_URL):
        self.conn = HLSolrConnection(url, http_connection, retry_timeout, max_length_get_url)
        self.schemadoc = schemadoc
        if mode == 'r':
            self.writeable = False
        elif mode == 'w':
            self.readable = False
        self.init_schema()

    def highlight(self, **kwargs):
        if not self.readable:
            raise TypeError("This Solr instance is only for writing")
        args = {
            'analysis_fieldname': kwargs['field'],
            'analysis_showmatch': True,
            'analysis_fieldvalue': kwargs['text'],
            'q': kwargs['q']
            }
        params = map(lambda (k, v): (k.replace('_', '.'), v), sunburnt.params_from_dict(**args))

        content = self.conn.highlight(params)
        doc = etree.fromstring(content)
        analyzed = doc.xpath("//lst[@name='index']/arr[last()]/lst[bool/@name='match']")
        matches = set()
        for wrd in analyzed:
            start = int(wrd.xpath("int[@name='start']")[0].text)
            end = int(wrd.xpath("int[@name='end']")[0].text)
            matches.add((start, end))

        print matches
        return self.substring(kwargs['text'], matches,
                            margins=kwargs.get('margins', 30),
            mark=kwargs.get('mark', ("<b>", "</b>")))

    def substring(self, text, matches, margins=30, mark=("<b>", "</b>")):
        start = None
        end = None
        totlen = len(text)
        matches_margins = map(lambda (s, e): (max(0, s - margins), min(totlen, e + margins)), matches)
        (start, end) = matches_margins[0]

        for (s, e) in matches_margins[1:]:
            if end < s or start > e:
                continue
            start = min(start, s)
            end = max(end, e)

        snip = text[start:end]
        matches = list(matches)
        matches.sort(lambda a, b: cmp(b[0], a[0]))
        for (s, e) in matches:
            off = - start
            snip = text[:e + off] + mark[1] + snip[e + off:]
            snip = text[:s + off] + mark[0] + snip[s + off:]
            # maybe break on word boundaries
        return snip
