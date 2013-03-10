
from sunburnt import sunburnt
from lxml import etree
import urllib
import warnings
from sunburnt import search
import copy
from httplib2 import socket
import re


class TermVectorOptions(search.Options):
    def __init__(self, schema, original=None):
        self.schema = schema
        if original is None:
            self.fields = set()
            self.positions = False
        else:
            self.fields = copy.copy(original.fields)
            self.positions = copy.copy(original.positions)

    def update(self, positions=False, fields=None):
        if fields is None:
            fields = []
        if isinstance(fields, basestring):
            fields = [fields]
        self.schema.check_fields(fields, {"stored": True})
        self.fields.update(fields)
        self.positions = positions

    def options(self):
        opts = {}
        if self.positions or self.fields:
            opts['tv'] = 'true'
        if self.positions:
            opts['tv.positions'] = 'true'
        if self.fields:
            opts['tv.fl'] = ','.join(sorted(self.fields))
        return opts


class CustomSolrConnection(sunburnt.SolrConnection):
    def __init__(self, *args, **kw):
        super(CustomSolrConnection, self).__init__(*args, **kw)
        self.analysis_url = self.url + "analysis/field/"

    def analyze(self, params):
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


# monkey patching sunburnt SolrSearch
search.SolrSearch.option_modules += ('term_vectorer',)


def __term_vector(self, positions=False, fields=None):
    newself = self.clone()
    newself.term_vectorer.update(positions, fields)
    return newself
setattr(search.SolrSearch, 'term_vector', __term_vector)


def __patched__init_common_modules(self):
    __original__init_common_modules(self)
    self.term_vectorer = TermVectorOptions(self.schema)
__original__init_common_modules = search.SolrSearch._init_common_modules
setattr(search.SolrSearch, '_init_common_modules', __patched__init_common_modules)


class CustomSolrInterface(sunburnt.SolrInterface):
    # just copied from parent and SolrConnection -> CustomSolrConnection
    def __init__(self, url, schemadoc=None, http_connection=None, mode='', retry_timeout=-1, max_length_get_url=sunburnt.MAX_LENGTH_GET_URL):
        self.conn = CustomSolrConnection(url, http_connection, retry_timeout, max_length_get_url)
        self.schemadoc = schemadoc
        if 'w' not in mode:
            self.writeable = False
        elif 'r' not in mode:
            self.readable = False
        try:
            self.init_schema()
        except socket.error, e:
            raise socket.error, "Cannot connect to Solr server, and search indexing is enabled (%s)" % str(e)

    def _analyze(self, **kwargs):
        if not self.readable:
            raise TypeError("This Solr instance is only for writing")
        args = {
            'analysis_showmatch': True
            }
        if 'field' in kwargs: args['analysis_fieldname'] = kwargs['field']
        if 'text' in kwargs: args['analysis_fieldvalue'] = kwargs['text']
        if 'q' in kwargs: args['q'] = kwargs['q']
        if 'query' in kwargs: args['q'] = kwargs['q']

        params = map(lambda (k, v): (k.replace('_', '.'), v), sunburnt.params_from_dict(**args))

        content = self.conn.analyze(params)
        doc = etree.fromstring(content)
        return doc

    def highlight(self, **kwargs):
        doc = self._analyze(**kwargs)
        analyzed = doc.xpath("//lst[@name='index']/arr[last()]/lst[bool/@name='match']")
        matches = set()
        for wrd in analyzed:
            start = int(wrd.xpath("int[@name='start']")[0].text)
            end = int(wrd.xpath("int[@name='end']")[0].text)
            matches.add((start, end))

        if matches:
            return self.substring(kwargs['text'], matches,
                margins=kwargs.get('margins', 30),
                mark=kwargs.get('mark', ("<b>", "</b>")))
        else:
            return None

    def analyze(self, **kwargs):
        doc = self._analyze(**kwargs)
        terms = doc.xpath("//lst[@name='index']/arr[last()]/lst/str[1]")
        terms = map(lambda n: unicode(n.text), terms)
        return terms

    def expand_margins(self, text, start, end):
        totlen = len(text)

        def is_boundary(x):
            ws = re.compile(r"\W", re.UNICODE)
            return bool(ws.match(x))

        while start > 0:
            if is_boundary(text[start - 1]):
                break
            start -= 1

        while end < totlen - 1:
            if is_boundary(text[end + 1]):
                break
            end += 1

        return (start, end)

    def substring(self, text, matches, margins=30, mark=("<b>", "</b>")):
        start = None
        end = None
        totlen = len(text)
        matches_margins = map(lambda (s, e):
                              ((s, e),
                               (max(0, s - margins), min(totlen, e + margins))),
                                  matches)
        matches_margins = map(lambda (m, (s, e)):
                              (m, self.expand_margins(text, s, e)),
            matches_margins)

            # lets start with first match
        (start, end) = matches_margins[0][1]
        matches = [matches_margins[0][0]]

        for (m, (s, e)) in matches_margins[1:]:
            if end < s or start > e:
                continue
            start = min(start, s)
            end = max(end, e)
            matches.append(m)

        snip = text[start:end]
        matches.sort(lambda a, b: cmp(b[0], a[0]))

        for (s, e) in matches:
            off = - start
            snip = snip[:e + off] + mark[1] + snip[e + off:]
            snip = snip[:s + off] + mark[0] + snip[s + off:]

        return snip
