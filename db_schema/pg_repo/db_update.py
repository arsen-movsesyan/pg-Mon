#!/usr/bin/env python

import argparse
import sys
import re
import settings
import psycopg2

########################################################################################

class UpdSource():

    def __init__(self,in_source,last_update):
	self.upd_dict=dict()
	self.source=in_source
	self.src_handler=None
	self.last_update=last_update
	if self.source=='file':
	    self._parse_file()


    def _parse_file(self):
	try:
	    src=open(settings.repo_file_name,'r')
	except IOError as e:
	    print "ERROR! Cannot open file"
	    sys.exit(1)
	lines=[]
	for line in src:
	    if re.match('^upd_\d',line):
		lines.append(line.strip())
	    elif len(line.strip()) == 0:
		continue
	    else:
		lines[-1] += ' '+line.strip()

	for upd in lines:
	    a=upd.split('=',1)
	    if re.match('^upd_\d$',a[0]) and int(a[0][4:]) > self.last_update:
		self.upd_dict[int(a[0][4:])]=a[1][1:-1]


    def get_upd_dict(self):
	return self.upd_dict

    def get_total_updates(self):
	return len(self.upd_dict)


class DbState():

    def __init__(self,in_db_conn):
	self.db_conn=in_db_conn
	self.last_applied=None
	self.installed=-1
#	self.check_installed()

    def __del__(self):
	if not self.db_conn.closed:
	    self.db_conn.close()

    def get_last_applied(self):
	if not self.last_applied:
	    cur=self.db_conn.cursor()
	    try:
		cur.execute(settings.get_last_applied_stmt)
	    except Exception as e:
		print "Error! Cannot get last applied update! {0}".format(e.pgerror)
		return -1
	    self.last_applied=cur.fetchone()[0]
	    cur.close()
	return self.last_applied



    def _check_installed(self):
	cur=self.db_conn.cursor()
	try:
	    cur.execute(settings.get_install_check_stmt)
	except Exception as e:
	    print "ERROR! Cannot determine installed! {0}".format(e.pgerror)
	    return False
	self.installed=cur.fetchone()[0]
	return True

    def install(self):
	cur=self.db_conn.cursor()
	try:
	    cur.execute(settings.install_stmt)
	except Exception as e:
	    print "ERROR! Cannot create db_update table!{0}".format(e.pgerror)
	    return False
	else:
	    self.db_conn.commit()
	    print "Application successfully installed"
	    return True

    def get_installed(self):
	if self.installed == -1:
	    self._check_installed()
	return self.installed


class Apply():

    def __init__(self,in_db_conn):
	self.db_conn=in_db_conn
	self.num_applied=0

    def __del__(self):
	if not self.db_conn.closed:
	    self.db_conn.close()

    def _apply_one_update(self,number,stmt,dry_run):
	cur=self.db_conn.cursor()
	try:
	    cur.mogrify(stmt)
	except Exception as e:
	    print "ERROR! Mistake in update {0}{1}".format(number,e.pgerror)
	    return False
	if dry_run:
	    print "upd_{0} => {1}".format(number,stmt)
	else:
	    try:
		cur.execute(stmt)
		cur.execute(settings.confirm_stmt,(number,stmt))
	    except Exception as e:
		print "ERROR! Cannot run update {0}\n{1}".format(number,e.pgerror)
#		print "\n"+stmt+"\n"
		return False

	return True


    def iterate_over(self,in_upd_dict,dry_run):
	for num,stmt in sorted(us.get_upd_dict().iteritems()):
	    res=self._apply_one_update(num,stmt,dry_run)
	    if res and not dry_run:
		self.db_conn.commit()
		self.num_applied += 1
		if args.verbose:
		    print "Update number {0} applied successfully"
	    elif not res:
		break

    def get_num_applied(self):
	return self.num_applied


#########################################################################


parser = argparse.ArgumentParser(description='Database changes and updates tracking system')

parser.add_argument('-r',action='store_true',dest='dry_run',default=False,help="Show updates and exit")
parser.add_argument('-i','--install',action='store_true',default=False,help="Install application and go to dry_run mode")
parser.add_argument('-s',nargs=1,choices=['file','SQLite'],default='file',dest='source',
    help="Source for updates. SQLite is not supported currently")
parser.add_argument('-v','--verbose',action='store_true',default=False,help="Show additional info on terminal")
parser.add_argument('-l','--last',dest='last_applied',action='store_true',default=False,
    help="Show last applied update number and exit")

args=parser.parse_args()




if args.install:
    args.dry_run=True

try:
    conn=psycopg2.connect(settings.custom_dsn('db_handler_1'))
except Exception as e:
    print "ERROR! Cannot connect to database {0}".format(e)
    sys.exit(1)


db_st=DbState(conn)

installed=db_st.get_installed()
#last_applied=db_st.get_last_applied()

#if last_applied == -1:
#    conn.close()
#    sys.exit()


if installed == 0:
    install=db_st.install()
    if not install:
	conn.close()
	sys.exit(1)
elif installed == 1:
    if args.install:
	print "Application already installed"
elif installed == -1:
    conn.close()
    sys.exit(1)

if args.install:
    conn.close()
    sys.exit(1)


last_applied=db_st.get_last_applied()

if args.last_applied:
    if last_applied == 0:
	print "No updates applied"
    else:
	print "Last applied update: upd_{0}".format(last_applied)
    conn.close()
    sys.exit()

us=UpdSource(args.source,last_applied)

upd_dict=us.get_upd_dict()

ap=Apply(conn)

ap.iterate_over(upd_dict,args.dry_run)

if not args.dry_run:
    print "Applied {0} updates out of {1}".format(ap.get_num_applied(),us.get_total_updates())
