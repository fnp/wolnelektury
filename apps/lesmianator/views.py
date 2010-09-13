# Create your views here.

import pickle
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
    _dictionary = pickle.load(f)
except:
    _dictionary = {}


def poem(request):
    letters = []
    word = u''
    empty = -10
    left = 1000
    if not _dictionary:
        left = 0
    while empty != 3 and left:
        letter = _choose_word(word)
        letters.append(letter)
        word = word[-2:] + letter
        if letter == u'\n':
            empty += 1
        else:
            empty = 0
        left -= 1

    poem = ''.join(letters).strip()

    return render_to_response('lesmianator/poem.html', 
                {"object": poem},
                context_instance=RequestContext(request))
