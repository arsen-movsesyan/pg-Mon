#!/usr/local/bin/python -B

import cPickle
import os

#from os import listdir,chdir

from os.path import isfile

from settings import db_handler,upload_dir
#from objects import *


import pprint

#onlyfiles = [ f for f in listdir(upload_dir) if isfile(join(upload_dir,f)) ]

#print onlyfiles

os.chdir(upload_dir)

for f in os.listdir(upload_dir):
    if isfile(f):
	src=open(f,'rb')
	stat=cPickle.load(src)
#	for k in stat.keys():
#	    print k
	print stat['hour_truncate']
#	pprint.pprint(stat_slice)
	src.close()
	print 
