from time import time
from pprint import pprint
#from binascii import crc32
from os import remove
#from os.path import isfile
from sys import exit

from settings import logger,db_handler

import cPickle


class Reciever:

    def __init__(self,in_file):
	self.container=dict()
	self._load_from_file(in_file)



    def _load_from_file(self,file_name):
	try:
	    buffer_src=open(file_name,'rb')
	except:
	    self.container.update(TRANS_TEMPLATE)
	else:
	    self.container.update(cPickle.load(buffer_src))
	    buffer_src.close()


    def _get_time(self):
	return self.container['header']['transfer_timestamp']




    def pp(self):
	pprint(self.container)


    def get_db_data(self):
	return self.container['stat_content']['db_stat']


    def get_custom(self,cust_key=None):
        if not cust_key:
	    return self.container['custom'].keys()
	else:
	    return self.container['custom'][cust_key]

#    def dispoze(self):
#	remove(in_file)
