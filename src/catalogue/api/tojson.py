import json
import re
from sys import argv
from lxml import etree

tags = {
    'utwor': ('_pass', False, None, None, None),
    '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF': ('_ignore', False, None, None, None),
    'abstrakt': ('_ignore', False, None, None, None),
    'uwaga': ('_ignore', False, None, None, None),
    'extra': ('_ignore', False, None, None, None),
    'nota_red': ('_ignore', False, None, None, None),
    'numeracja': ('_ignore', False, None, None, None),

    'powiesc': ('master', False, None, None, None),
    'opowiadanie': ('master', False, None, None, None),
    'liryka_lp': ('master', False, None, None, None),
    'liryka_l': ('master', False, None, None, None),
    'dramat_wspolczesny': ('master', False, None, None, None),
    'dramat_wierszowany_lp': ('master', False, None, None, None),
    'dramat_wierszowany_l': ('master', False, None, None, None),

    'dlugi_cytat': ('blockquote', False, None, None, None),
    'poezja_cyt': ('blockquote', False, None, None, None),
    'dlugi_cyt': ('blockquote', False, None, None, None),
    'ramka': ('blockquote', False, {'class': 'ramka'}, None, None),
    
    'blok': ('div', False, None, None, None),

    'strofa': ('div', True, {'class': 'stanza'}, None, None),
    'wers': ('div', True, {'class': 'verse'}, None, None),
    'wers_wciety': ('div', True, {'class': 'wers_wciety'}, None, None),
    'wers_cd': ('div', True, {'class': 'wers_cd'}, None, None),
    'wers_akap': ('div', True, {'class': 'wers_akap'}, None, None),
    'zastepnik_wersu': ('div', True, {'class': 'zastepnik_wersu'}, None, None),
    'wers_do_prawej': ('div', True, {'class': 'wers_do_prawej'}, None, None),
    'wers_srodek': ('div', True, {'class': 'wers_srodek'}, None, None),
    
    'autor_utworu': ('div', True, {'class': 'author'}, None, None),
    'dzielo_nadrzedne': ('div', True, {'class': 'dzielo_nadrzedne'}, None, None),
    'nazwa_utworu': ('div', True, {'class': 'title'}, None, None),
    'podtytul': ('div', True, {'class': 'podtytul'}, None, None),

    'motto': ('div', False, {'class': 'motto'}, None, None),
    'motto_podpis': ('div', True, {'class': 'motto_podpis'}, None, None),
    'dedykacja': ('div', True, {'class': 'dedykacja'}, None, None),
    'miejsce_czas': ('div', True, {'class': 'miejsce_czas'}, None, None),
    
    'lista_osob': ('div', False, {'class': 'lista_osob'}, None, None),
    'naglowek_listy': ('div', True, {'class': 'naglowek_listy'}, None, None),
    'lista_osoba': ('div', True, {'class': 'lista_osoba'}, None, None),
    'naglowek_osoba': ('div', True, {'class': 'naglowek_osoba'}, None, None),
    'osoba': ('em', True, {'class': 'osoba'}, None, None),
    'didaskalia': ('div', True, {'class': 'didaskalia'}, None, None),
    'kwestia': ('div', False, {'class': 'kwestia'}, None, None),
    'didask_tekst': ('em', False, {'class': 'didask_tekst'}, None, None),
    
    'naglowek_czesc': ('h2', True, None, None, None),
    'naglowek_akt': ('h2', True, None, None, None),
    'naglowek_scena': ('h3', True, None, None, None),
    'naglowek_rozdzial': ('h3', True, None, None, None),
    'naglowek_podrozdzial': ('h4', True, None, None, None),
    'srodtytul': ('h5', True, None, None, None),

    'nota': ('div', True, {'class': 'note'}, None, False),

    'akap': ('p', True, {'class': 'paragraph'}, None, True),
    'akap_dialog': ('p', True, {'class': 'paragraph'}, None, True),
    'akap_cd': ('p', True, {'class': 'paragraph'}, None, True),

    'sekcja_asterysk': ('p', True, {'class': 'spacer-asterisk'}, None, True),
    'sekcja_swiatlo': ('p', True, {'class': 'sekcja_swiatlo'}, None, True),
    'separator_linia': ('p', True, {'class': 'separator_linia'}, None, True),

    'tytul_dziela': ('em', True, {'class': 'book-title'}, None, False),
    'slowo_obce': ('em', True, {'class': 'foreign-word'}, None, False),
    'wyroznienie': ('em', True, {'class': 'author-emphasis'}, None, False),
    'wieksze_odstepy': ('em', True, {'class': 'wieksze_odstepy'}, None, False),

    'ref': ('a', True, {'class': 'reference'}, {'data-uri': 'href'}, False),

    'begin': ('_ignore', True, {'class': 'reference'}, {'data-uri': 'href'}, False),
    'end': ('_ignore', True, {'class': 'reference'}, {'data-uri': 'href'}, False),
    'motyw': ('a', True, {'class': 'theme'}, None, False),

    'pa': ('a', True, {'class': 'footnote footnote-pa'}, None, False),
    'pe': ('a', True, {'class': 'footnote footnote-pe'}, None, False),
    'pr': ('a', True, {'class': 'footnote footnote-pr'}, None, False),
    'pt': ('a', True, {'class': 'footnote footnote-pt'}, None, False),
    'ptrad': ('a', True, {'class': 'footnote footnote-ptrad'}, None, False),
}


#tree = etree.parse(argv[1])

front1 = set([
    'dzielo_nadrzedne',
    'nazwa_utworu',
    'podtytul',
    ])
front2 = set(['autor_utworu'])


def norm(text):
    text = text.replace('---', '—').replace('--', '–').replace('...', '…').replace(',,', '„').replace('"', '”')
    return text


def toj(elem, S):
    if elem.tag is etree.Comment: return []
    tag, hastext, attrs, attr_map, num = tags[elem.tag]
    contents = []
    if tag == '_pass':
        output = contents
    elif tag == '_ignore':
        return []
    else:
        output = {
            'tag': tag,
        }
        if num:
            S['index'] += 1
            output['paragraphIndex'] = S['index']
            if 'dlugi_cytat' not in S['stack'] and 'poezja_cyt' not in S['stack']:
                S['vindex'] += 1
                output['visibleNumber'] = S['vindex']
        if attrs:
            output['attr'] = attrs.copy()
        if attr_map:
            output.setdefault('attr', {})
            for k, v in attr_map.items():
                output['attr'][k] = elem.attrib[v]
        output['contents'] = contents
        output = [output]
    if elem.tag == 'strofa':
        verses = [etree.Element('wers')]
        if elem.text:
            vparts = re.split(r'/\s+', elem.text)
            for i, v in enumerate(vparts):
                if i:
                    verses.append(etree.Element('wers'))
                verses[-1].text = (verses[-1].text or '') + v
        for child in elem:
            vparts = re.split(r'/\s+', child.tail or '')
            child.tail = vparts[0]
            verses[-1].append(child)
            for v in vparts[1:]:
                verses.append(etree.Element('wers'))
                verses[-1].text = v

        if not(len(verses[-1]) or (verses[-1].text or '').strip()):
            verses.pop()

        elem.clear(keep_tail=True)
        for verse in verses:
            if len(verse) == 1 and (verse[0].tag.startswith('wers') or verse[0].tag == 'zastepnik_wersu') and not (verse[0].tail or '').strip():
                elem.append(verse[0])
            else:
                elem.append(verse)

        #if not len(elem):
        #    for v in re.split(r'/\s+', elem.text):
        #        etree.SubElement(elem, 'wers').text = v
        #    elem.text = None
        
    if hastext and elem.text:
        contents.append(norm(elem.text))
    for c in elem:
        S['stack'].append(elem.tag)
        contents += toj(c, S)
        if hastext and c.tail:
            contents.append(norm(c.tail))
        S['stack'].pop()

    if elem.tag in front1:
        S['front1'] += output
        return []
    if elem.tag in front2:
        S['front2'] += output
        return []
    return output

def conv(tree):
    S = {
        'index': 0,
        'vindex': 0,
        'stack': [],
        'front1': [],
        'front2': [],
    }
    output = toj(tree.getroot(), S)
    if not len(output): return {}
    jt = output[0]
    jt['front1'] = S['front1']
    jt['front2'] = S['front2']
    return jt

#print(json.dumps(jt, indent=2, ensure_ascii=False))
