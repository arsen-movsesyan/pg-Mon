from time import time
from pprint import pprint
from binascii import crc32
from os import remove
from os.path import isfile
from sys import exit

from settings import BUFF_FILE,READY_FILE,TRANS_TEMPLATE,MAX_KEEP_READY_FILES

import cPickle



class Transfer:

    def __init__(self):
	self.local_file=''
	self.container=dict()
	self._load_from_file(BUFF_FILE)

    def _set_time(self):
	self.container['header']['transfer_timestamp']=int(time())


    def _flush(self):
	try:
	    remove(BUFF_FILE)
	except:
	    pass
	self.container.clear()
	self.container.update(TRANS_TEMPLATE)


    def _load_from_file(self,file_name):
	try:
	    buffer_src=open(file_name,'rb')
	except:
	    self.container.update(TRANS_TEMPLATE)
	else:
	    self.container.update(cPickle.load(buffer_src))
	    buffer_src.close()
    def _dump_to_file(self,file_name):
	try:
	    buffer_src=open(file_name,'wb')
	except IOError as e:
	    logger.critical("Canot open {0} for writing. Details: {1}".format(file_name,e))
	    exit(1)
	cPickle.dump(self.container,buffer_src,cPickle.HIGHEST_PROTOCOL)
	buffer_src.close()


    def _ready_file_open(self):
	counter=0
	while counter < MAX_KEEP_READY_FILES:
	    file_path=READY_FILE+'.'+str(counter).zfill(3)
	    if not isfile(file_path):
		return file_path
	    counter=counter+1
	return False



    def pp(self):
	pprint(self.container)


    def set_custom(self,module,field):
	counter=self.container['custom']['counter']
	container_name='append_'+str(counter).zfill(4)
	self.container['custom'][container_name]=dict(module=module,data=field,append_time=int(time()))
	counter=counter+1
	self.container['custom']['counter']=counter
	self._dump_to_file(BUFF_FILE)



    def set_db_data(self,data):
	counter=self.container['stat_content']['db_stat']['counter']
	container_name='append_'+str(counter).zfill(4)
	self.container['stat_content']['db_stat'][container_name]=data
	counter=counter+1
	self.container['stat_content']['db_stat']['counter']=counter
	self._dump_to_file(BUFF_FILE)


    def set_ready(self):
	self._set_time()
	ready_file_name=self._ready_file_open()
	if ready_file_name:
	    self._dump_to_file(ready_file_name)
	    self._flush()
