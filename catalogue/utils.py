# -*- coding: utf-8 -*-


def split_tags(tags):
    result = {}
    for tag in tags:
        result.setdefault(tag.category, []).append(tag)
    return result

