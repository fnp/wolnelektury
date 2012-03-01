#!/usr/bin/env python

import json
import sys
import os
import shutil

fname = sys.argv[1]
def mkdir(n):
    if not os.path.exists(n): os.mkdir(n)

dst = os.path.dirname(fname)
name = os.path.basename(fname).split('.')[0]

dst2 = os.path.join(dst, name) 
mkdir(dst2)

data = json.load(open(fname))
for ip in data:
    dst3 = os.path.join(dst2, ip['fields']['slug'])
    mkdir(dst3)
    for fld, val in ip['fields'].items():
        if val is None:
            val = ''
        if filter(lambda x: fld.startswith(x),
                  ['title', 'left_column', 'right_column']):
            o = open(os.path.join(dst3, fld+".txt"),'w')
            try:
                o.write(val.encode('utf-8'))
            finally:
                o.close()
            
