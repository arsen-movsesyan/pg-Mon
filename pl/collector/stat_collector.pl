#! /usr/bin/perl -w

use strict;
use Pg;
use Getopt::Long;

use lib qw(/home/arsen/work/pg-mon/collector);

use include::Param;
use include::HostCluster;
use include::DatabaseName;
use include::SchemaName;
use include::TableName;
use include::FunctionName;
use include::IndexName;


use constant BGWRITER_MIN_VERSION => 830;
use constant FUNCTION_STAT_MIN_VERSION => 840;

use vars qw($opt_h $opt_d);

Getopt::Long::Configure('bundling');

GetOptions(
    "h"=>	\$opt_h,"help"=>	\$opt_h,
    "d"=>	\$opt_d,"discover"=>	\$opt_d);

if ($opt_h) {
    print "Help coming soon\n";
    exit(0);
}


my $localSQL=Pg::connectdb(Param::get_conn_string('local_conn'));
if ($localSQL->status != PGRES_CONNECTION_OK) {
    print "Collector Connect Error: ".$localSQL->errorMessage."\n";
    exit;
}

my $time_id;

if (!$opt_d) {
    my $time_res=$localSQL->exec("INSERT INTO log_time (actual_time,hour_truncate) VALUES (LOCALTIMESTAMP,date_trunc('hour',LOCALTIMESTAMP)) RETURNING id");
    unless ($time_res->resultStatus == PGRES_TUPLES_OK) {
	print $localSQL->errorMessage;
	exit;
    }
    ($time_id)=$time_res->fetchrow;
}

my $hc_res=$localSQL->exec("SELECT id FROM host_cluster WHERE alive AND observable AND is_master");
while (my ($hc_id)=$hc_res->fetchrow) {
    my @children;
    my $pid=fork();
    if ($pid) {
	push(@children,$pid);
    } elsif (!$pid) {
	my $hc=new HostCluster($hc_id);
	my $version=$hc->get_version();
	if ($version >= BGWRITER_MIN_VERSION) {
	    if (!$opt_d) {
		$hc->write_bg_stat($time_id);
		$hc->write_db_stat($time_id);
	    }
	    foreach ($hc->get_database_ids()) {
		my $dn=new DatabaseName($_);
		$dn->set_prod_conn();
		foreach ($dn->get_schema_ids()) {
		    my $sn=new SchemaName($_);
		    $sn->discover_functions();
		    $sn->discover_tables();
		    if (!$opt_d) {
			foreach ($sn->get_table_ids()) {
			    my $tn=new TableName($_);
			    if ($hc->get_field('track_counts') eq 't') {
				$tn->write_va_stat($time_id);
				$tn->write_stat($time_id);
				$tn->write_toast_stat($time_id);
				foreach ($tn->get_index_ids()) {
				    my $in=new IndexName($_);
				    $in->write_stat($time_id);
				}
			    }
			}
			foreach ($sn->get_function_ids()) {
			    my $fn=new FunctionName($_);
			    if ($version >= FUNCTION_STAT_MIN_VERSION && $hc->get_field('track_functions') ne 'none') {
				$fn->write_stat($time_id);
			    }
			}
		    }
		}
	    }
	}
################################
	exit(0);
    } elsif (!defined($pid)) {
	print "Error, cannot fork\n";
	exit;
    }
    foreach (@children) {
	waitpid($pid,0);
    }
}
