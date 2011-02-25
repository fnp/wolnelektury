# -*- coding: utf-8 -*-

from time import mktime

def timestamp(dtime):
    "converts a datetime.datetime object to a timestamp with fractional part"
    return mktime(dtime.timetuple()) + dtime.microsecond / 1000000.0

