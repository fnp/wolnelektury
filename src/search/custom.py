# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
from urllib.parse import urlencode
import warnings
from httplib2 import socket
from lxml import etree
from scorched import connection, exc, search


class CustomSolrConnection(connection.SolrConnection):
    def __init__(self, *args, **kw):
        super(CustomSolrConnection, self).__init__(*args, **kw)
        self.analysis_url = self.url + "analysis/field/"

    def analyze(self, params):
        qs = urlencode(params)
        url = "%s?%s" % (self.analysis_url, qs)
        if len(url) > self.max_length_get_url:
            warnings.warn("Long query URL encountered - POSTing instead of GETting. "
                          "This query will not be cached at the HTTP layer")
            url = self.analysis_url
            kwargs = dict(
                method="POST",
                body=qs,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        else:
            kwargs = dict(method="GET")
        response = self.request(url=url, **kwargs)
        if response.status_code != 200:
            raise exc.SolrError(response)
        return response.content


class CustomSolrInterface(connection.SolrInterface):
    # just copied from parent and SolrConnection -> CustomSolrConnection
    def __init__(self, url, http_connection=None, mode='',
                 retry_timeout=-1, max_length_get_url=connection.MAX_LENGTH_GET_URL,
                 search_timeout=()):
        """
        :param url: url to Solr
        :type url: str
        :param http_connection: optional -- already existing connection
        :type http_connection: requests connection
        :param mode: optional -- mode (readable, writable) Solr
        :type mode: str
        :param retry_timeout: optional -- timeout until retry
        :type retry_timeout: int
        :param max_length_get_url: optional -- max length until switch to post
        :type max_length_get_url: int
        :param search_timeout: (optional) How long to wait for the server to
                               send data before giving up, as a float, or a
                               (connect timeout, read timeout) tuple.
        :type search_timeout: float or tuple
        """

        self.conn = CustomSolrConnection(
            url, http_connection, mode, retry_timeout, max_length_get_url)
        self.schema = self.init_schema()
        self._datefields = self._extract_datefields(self.schema)


    def _analyze(self, **kwargs):
        if not self.conn.readable:
            raise TypeError("This Solr instance is only for writing")
        args = {
            'analysis_showmatch': True
            }
        if 'field' in kwargs:
            args['analysis_fieldname'] = kwargs['field']
        if 'text' in kwargs:
            args['analysis_fieldvalue'] = kwargs['text']
        if 'q' in kwargs:
            args['q'] = kwargs['q']
        if 'query' in kwargs:
            args['q'] = kwargs['q']

        params = [
            (k.replace('_', '.'), v)
            for (k, v) in search.params_from_dict(**args)
        ]

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
            return self.substring(
                kwargs['text'], matches, margins=kwargs.get('margins', 30), mark=kwargs.get('mark', ("<b>", "</b>")))
        else:
            return None

    def analyze(self, **kwargs):
        doc = self._analyze(**kwargs)
        terms = doc.xpath("//lst[@name='index']/arr[last()]/lst/str[1]")
        terms = map(lambda n: str(n.text), terms)
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

        return start, end

    def substring(self, text, matches, margins=30, mark=("<b>", "</b>")):
        totlen = len(text)
        matches_margins = [
            ((s, e), self.expand_margins(text, max(0, s - margins), min(totlen, e + margins))) for s, e in matches]

        # lets start with first match
        (start, end) = matches_margins[0][1]
        new_matches = [matches_margins[0][0]]

        for (m, (s, e)) in matches_margins[1:]:
            if end < s or start > e:
                continue
            start = min(start, s)
            end = max(end, e)
            new_matches.append(m)

        snip = text[start:end]
        new_matches.sort(key=lambda a: -a[0])

        for (s, e) in new_matches:
            off = -start
            snip = snip[:e + off] + mark[1] + snip[e + off:]
            snip = snip[:s + off] + mark[0] + snip[s + off:]
        snip = re.sub('%s[ \t\n]+%s' % (mark[1], mark[0]), " ", snip)

        return snip
