# -*- coding: utf-8 -*-

from time import mktime

def timestamp(dtime):
    "converts a datetime.datetime object to a timestamp int"
    return int(mktime(dtime.timetuple()))

