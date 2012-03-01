#!/usr/bin/env python

import json
import sys
import os
import shutil

fname = sys.argv[1]
try:
    lang = sys.argv[2]
except IndexError:
    lang = None

def mkdir(n):
    if not os.path.exists(n): os.mkdir(n)

dst = os.path.dirname(fname)
name = os.path.basename(fname).split('.')[0]

dst2 = os.path.join(dst, name) 

data = json.load(open(fname))
for ip in data:
    dst3 = os.path.join(dst2, ip['fields']['slug'])
    for fld in ip['fields'].keys():
        if filter(lambda x: fld.startswith(x),
                  ['title', 'left_column', 'right_column']):
            if lang and not fld.endswith("_"+lang):
                continue
            try:
                o = open(os.path.join(dst3, fld+".txt"), 'r')
                try:
                    print dst3,fld
                    txt = o.read()
                    try:
                        txt = txt.decode('utf-8')
                    except UnicodeError:
                        txt = txt.decode('utf-16')
                        
                    ip['fields'][fld] = txt

                finally:
                    o.close()
            except IOError:
                print "no infopages file for field %s" % fld


out = open(fname, 'w')
try:
    out.write(json.dumps(data,indent=4))
finally:
    out.close()
