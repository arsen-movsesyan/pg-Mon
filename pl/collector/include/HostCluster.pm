package HostCluster;

require Exporter;

use Pg;
use strict;

use include::Param;

our @ISA =qw(Exporter);

our @EXPORT_OK = qw( );
our @EXPORT = @EXPORT_OK;

our $ver;
our %self;

sub new {
    my $class=shift;
    my $iam = { };
    $self{table}='host_cluster';
    $self{pk}='id';
    $self{id}=$_[0];
    $self{database_fields}={ };
    $self{modified_fields}={ };

    $self{sql}=Pg::connectdb(Param::get_conn_string('local_conn'));
    if ($self{sql}->status != PGRES_CONNECTION_OK) {
	print "HostCluster Connect Error: ".$self{sql}->errorMessage."\n";
	exit;
    }
    my $res=$self{sql}->exec("SELECT * FROM ".$self{table}." WHERE ".$self{pk}."=".$self{id});
    if ($res->resultStatus != PGRES_TUPLES_OK) {
	print $self{sql}->errorMessage;
	exit;
    }
    my @obj=$res->fetchrow;
    for (my $f=0;$f < $res->nfields;$f++) {
	$self{database_fields}{$res->fname($f)}=$obj[$f];
	$self{modified_fields}{$res->fname($f)}=0;
    }
    $ver=$self{database_fields}{pg_version};
    $ver=~s/\.//g;

    bless($iam,$class);
    return $iam;
}

###############################################

sub set_prod_conn {
    my $res=$self{sql}->exec("SELECT get_conn_string(".$self{id}.") AS prod_conn_string");
    my ($conn_string)=$res->fetchrow;
    $self{prod_sql}=Pg::connectdb($conn_string);
    if ($self{prod_sql}->status != PGRES_CONNECTION_OK) {
	print "HostCluster Prod Connect Error: ".$self{prod_sql}->errorMessage."\n";
	exit;
    }
}


###############################################

sub get_field {
    shift;
    foreach my $field (keys %{$self{database_fields}}) {
	if ($field eq $_[0]) {
	    return $self{database_fields}{$field};
	}
    }
    return undef;
}

sub get_all_fields {
    shift;
    return $self{database_fields};
}

sub get_id {
    shift;
    return $self{id};
}

sub get_version {
    shift;
    return $ver;
}

sub get_databases {
    my $db_res=$self{sql}->exec("SELECT * FROM database_name WHERE hc_id=".$self{id}." AND observable AND alive");
    my @ret;
    while (my @dbs=$db_res->fetchrow) {
	my %struct;
	for (my $f=0; $f < $db_res->nfields; $f++) {
	    $struct{$db_res->fname($f)}=$dbs[$f];
	}
	push(@ret,\%struct);
    }
    return @ret;
}

sub get_database_ids {
    shift;
    my $db_res=$self{sql}->exec("SELECT id FROM database_name WHERE hc_id=".$self{id}." AND observable AND alive");
    my @ret;
    while (my ($id)=$db_res->fetchrow) {
	push(@ret,$id);
    }
    return @ret;
}


sub write_db_stat {
    shift;
    if ($self{database_fields}{track_counts} eq 't') {
	if (!$self{prod_sql}) {
	    set_prod_conn();
	}
	foreach my $db (get_databases()) {
	    my %database=%{$db};
	    my $stat_q="SELECT
pg_database_size(oid) AS db_size,
pg_stat_get_db_xact_commit(oid) AS xact_commit,
pg_stat_get_db_xact_rollback(oid) AS xact_rollback,
pg_stat_get_db_blocks_fetched(oid) AS blks_fetch,
pg_stat_get_db_blocks_hit(oid) AS blks_hit,
pg_stat_get_db_tuples_returned(oid) AS tup_returned,
pg_stat_get_db_tuples_fetched(oid) AS tup_fetched,
pg_stat_get_db_tuples_inserted(oid) AS tup_inserted,
pg_stat_get_db_tuples_updated(oid) AS tup_updated,
pg_stat_get_db_tuples_deleted(oid) AS tup_deleted
FROM pg_database
WHERE oid =".$database{obj_oid};
	    my $stat_res=$self{prod_sql}->exec($stat_q);
	    if ($stat_res->resultStatus != PGRES_TUPLES_OK) {
		print "Error Getting database statistic for database ".$database{db_name}." host ".$self{database_fields}{hostname}."\n";
		exit;
	    }
	    my @dbs=$stat_res->fetchrow;
	    my %db_stat;
	    for (my $f=0;$f < $stat_res->nfields;$f++) {
		$db_stat{$stat_res->fname($f)}=$dbs[$f];
	    }
	    my $ins_q="INSERT INTO database_stat VALUES (".$database{id}.",".$_[0].",
".$db_stat{db_size}.",
".$db_stat{xact_commit}.",
".$db_stat{xact_rollback}.",
".$db_stat{blks_fetch}.",
".$db_stat{blks_hit}.",
".$db_stat{tup_returned}.",
".$db_stat{tup_fetched}.",
".$db_stat{tup_inserted}.",
".$db_stat{tup_updated}.",
".$db_stat{tup_deleted}.")";
	    my $ins_res=$self{sql}->exec($ins_q);
	    if ($ins_res->resultStatus != PGRES_COMMAND_OK) {
		print "Error Inserting database stat for database ".$database{db_name}." host ".$self{database_fields}{hostname}."\n";
		exit;
	    }
	}
    }
}

sub write_bg_stat {
    shift;
    if ($self{database_fields}{track_counts} eq 't') {
	if (!$self{prod_sql}) {
	    set_prod_conn();
	}
	my $stat_res=$self{prod_sql}->exec("SELECT
pg_stat_get_bgwriter_timed_checkpoints() AS checkpoints_timed,
pg_stat_get_bgwriter_requested_checkpoints() AS checkpoints_req,
pg_stat_get_bgwriter_buf_written_checkpoints() AS buffers_checkpoint,
pg_stat_get_bgwriter_buf_written_clean() AS buffers_clean,
pg_stat_get_bgwriter_maxwritten_clean() AS maxwritten_clean,
pg_stat_get_buf_written_backend() AS buffers_backend,
pg_stat_get_buf_alloc() AS buffers_alloc");
	if ($stat_res->resultStatus != PGRES_TUPLES_OK) {
	    print "Error Getting bgwriter stat for host ".$self{database_fields}{hostname}."\n";
	    exit;
	}
	my @bg_stat=$stat_res->fetchrow;
	my %bgw;
	for (my $f=0;$f < $stat_res->nfields;$f++) {
	    $bgw{$stat_res->fname($f)}=$bg_stat[$f];
	}
	my $bg_stat_q="INSERT INTO bgwriter_stat VALUES (
".$self{id}.",".$_[0].",
".$bgw{checkpoints_timed}.",
".$bgw{checkpoints_req}.",
".$bgw{buffers_checkpoint}.",
".$bgw{buffers_clean}.",
".$bgw{maxwritten_clean}.",
".$bgw{buffers_backend}.",
".$bgw{buffers_alloc}.")";
	my $ins_res=$self{sql}->exec($bg_stat_q);


	if ($ins_res->resultStatus != PGRES_COMMAND_OK) {
	    print "Error Inserting bgwriter stat for host ".$self{database_fields}{hostname}."\n";
	    exit;
	}
    }
}

1;


