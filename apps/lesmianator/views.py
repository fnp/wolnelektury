# Create your views here.

import cPickle
from django.shortcuts import render_to_response
from django.template import RequestContext
from random import randint

import os.path


def _choose_word(word):
    try:
        choices = sum((_dictionary[word][post] for post in _dictionary[word]))
        r = randint(0, choices - 1)

        for post in _dictionary[word]:
            r -= _dictionary[word][post]
            if r < 0:
                return post
    except KeyError:
        return ''

# load dictionary on start, it won't change
try:
    f = open(os.path.join(os.path.dirname(__file__), 'dictionary.p'))
    _dictionary = cPickle.load(f)
except:
    _dictionary = {}


def poem(request):
    letters = []
    word = u''
    empty = -10
    left = 1000
    lines = 0
    if not _dictionary:
        left = 0
    # want at least two lines, but let Lesmianator end his stanzas
    while (empty < 2 or lines < 2) and left:
        letter = _choose_word(word)
        letters.append(letter)
        word = word[-2:] + letter
        if letter == u'\n':
            # count non-empty lines
            if empty == 0:
                lines += 1
            # 
            if lines >= 2:
                empty += 1
            lines += 1
        else:
            empty = 0
        left -= 1

    poem = ''.join(letters).strip()

    return render_to_response('lesmianator/poem.html', 
                {"object": poem},
                context_instance=RequestContext(request))
