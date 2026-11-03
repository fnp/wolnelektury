#!/usr/bin/env python3
"""
Tworzy wersję słownika hunspell bez polskich znaków dla PostgreSQL (szablon ispell).

Użycie:
    fold_hunspell.py polish.dict polish.affix polish_ascii.dict polish_ascii.affix

Pliki wejściowe muszą być w UTF-8 (po iconv z ISO-8859-2).

Samo usunięcie znaków psuje warunki reguł z klasami negowanymi: np.
`SFX H ć ło [^ąeśź]ć` (wszystko poza ą, e, ś, ź przed ć) po zamianie
stałoby się `[^aesz]c` i przestało pasować do czasowników na -ać.
Dlatego litera zostaje w klasie negowanej tylko wtedy, gdy oryginał
wykluczał wszystkie litery, które się na nią składają; w przeciwnym
razie jest usuwana, a pusta klasa zamienia się w `.`. Reguły stają się
przez to nieco zbyt liberalne (nadmiarowe formy), ale żadna forma nie ginie.
"""
import re
import sys
import unicodedata


def fold(text):
    text = text.replace('ł', 'l').replace('Ł', 'L')
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )


LETTERS = 'aąbcćdeęfghijklłmnńoóprsśtuvwxyzźż'
GROUPS = {}
for letter in LETTERS:
    GROUPS.setdefault(fold(letter), set()).add(letter)


def fold_negated_class(match):
    excluded = set(match.group(1))
    keep = []
    for c in match.group(1):
        folded = fold(c)
        if GROUPS.get(folded, {c}) <= excluded and folded not in keep:
            keep.append(folded)
    return '[^' + ''.join(keep) + ']' if keep else '.'


def fold_affix_line(line):
    parts = line.split()
    if len(parts) >= 5 and parts[0] in ('SFX', 'PFX') and '[^' in parts[4]:
        condition = re.sub(r'\[\^([^\]]*)\]', fold_negated_class, parts[4])
        line = line.replace(parts[4], condition, 1)
    if line.startswith('SET '):
        return 'SET UTF-8\n'
    return fold(line)


def main(dict_in, affix_in, dict_out, affix_out):
    with open(dict_in, encoding='utf-8') as src, open(dict_out, 'w', encoding='utf-8') as dst:
        dst.write(fold(src.read()))
    with open(affix_in, encoding='utf-8') as src, open(affix_out, 'w', encoding='utf-8') as dst:
        for line in src:
            dst.write(fold_affix_line(line))


if __name__ == '__main__':
    main(*sys.argv[1:5])
