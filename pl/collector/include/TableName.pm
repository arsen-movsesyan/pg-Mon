package TableName;

require Exporter;

use Pg;
use strict;

our @ISA =qw(Exporter DatabaseName);

use include::Param;
use include::DatabaseName;

our %self;
our $prod_conn;

our @EXPORT = qw( );
our @EXPORT_OK = @EXPORT;

sub new {
    my $class=shift;
    my $iam = { };
    $self{table}='table_name';
    $self{pk}='id';
    $self{id}=$_[0];
    $self{database_fields}={ };
    $self{modified_fields}={ };

    $self{sql}=Pg::connectdb(Param::get_conn_string('local_conn'));
    if ($self{sql}->status != PGRES_CONNECTION_OK) {
	print "DatabaseName Connect Error: ".$self{sql}->errorMessage."\n";
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
    $prod_conn=DatabaseName::get_prod_conn();
    bless($iam,$class);
    return $iam;
}

###############################################

sub get_index_ids {
    shift;
    my $res=$self{sql}->exec("SELECT id FROM index_name WHERE alive AND tn_id=".$self{id});
    my @ret;
    while (my ($id)=$res->fetchrow) {
	push(@ret,$id);
    }
    return @ret;
}


sub write_va_stat {
    shift;
    my $time_id=$_[0];
    my $va_stat_q="SELECT
pg_stat_get_last_vacuum_time(oid) AS last_vacuum,
pg_stat_get_last_autovacuum_time(oid) AS last_autovacuum,
pg_stat_get_last_analyze_time(oid) AS last_analyze,
pg_stat_get_last_autoanalyze_time(oid) AS last_autoanalyze
FROM pg_class WHERE oid=".$self{database_fields}{obj_oid};
    my $va_stat_res=$prod_conn->exec($va_stat_q);
    if ($va_stat_res->resultStatus != PGRES_TUPLES_OK) {
	print "Error Getting va stat for table ".$self{database_fields}{tbl_name}."\n";
	print $prod_conn->errorMessage;
	exit;
    }
    my @va_stat=$va_stat_res->fetchrow;
    my %va;
    my ($lv,$lav,$la,$laa);
    for (my $tf=0;$tf < $va_stat_res->nfields;$tf++) {
	$va{$va_stat_res->fname($tf)}=$va_stat[$tf];
	$lv=defined($va{last_vacuum}) ? "'".$va{last_vacuum}."'" : 'NULL';
	$lav=defined($va{last_autovacuum}) ? "'".$va{last_autovacuum}."'" : 'NULL';
	$la=defined($va{last_analyze}) ? "'".$va{last_analyze}."'" : 'NULL';
	$laa=defined($va{last_autoanalyze}) ? "'".$va{last_autoanalyze}."'" : 'NULL';
    }
    $self{sql}->exec("INSERT INTO table_va_stat VALUES (".$self{id}.",".$time_id.",".$lv.",".$lav.",".$la.",".$laa.")");
}

sub write_stat {
    shift;
    my $time_id=$_[0];
    my $basic_stat_q="SELECT
pg_relation_size(oid) AS relsize,
pg_total_relation_size(oid) AS totalrelsize,
reltuples::bigint,
pg_stat_get_numscans(oid) AS seq_scan,
pg_stat_get_tuples_returned(oid) AS seq_tup_read,
pg_stat_get_tuples_fetched(oid) AS seq_tup_fetch,
pg_stat_get_tuples_inserted(oid) AS n_tup_ins,
pg_stat_get_tuples_updated(oid) AS n_tup_upd,
pg_stat_get_tuples_deleted(oid) AS n_tup_del,
pg_stat_get_tuples_hot_updated(oid) AS n_tup_hot_upd,
pg_stat_get_live_tuples(oid) AS n_live_tup,
pg_stat_get_dead_tuples(oid) AS n_dead_tup,
pg_stat_get_blocks_fetched(oid) AS heap_blks_fetch,
pg_stat_get_blocks_hit(oid) AS heap_blks_hit
FROM pg_class
WHERE oid=".$self{database_fields}{obj_oid};
    my $stat_res=$prod_conn->exec($basic_stat_q);
    if ($stat_res->resultStatus != PGRES_TUPLES_OK) {
	print "Error Getting basic stat for table ".$self{database_fields}{tbl_name}."\n";
	print $prod_conn->errorMessage;
	exit;
    }
    my @basic_stat=$stat_res->fetchrow;
    my %stat;
    for (my $sf=0;$sf < $stat_res->nfields; $sf++) {
	$stat{$stat_res->fname($sf)}=$basic_stat[$sf];
    }

    $self{sql}->exec("INSERT INTO table_stat VALUES ("
.$self{id}.","
.$time_id.","
.$stat{relsize}.","
.$stat{totalrelsize}.","
.$stat{reltuples}.","
.$stat{seq_scan}.","
.$stat{seq_tup_read}.","
.$stat{seq_tup_fetch}.","
.$stat{n_tup_ins}.","
.$stat{n_tup_upd}.","
.$stat{n_tup_del}.","
.$stat{n_tup_hot_upd}.","
.$stat{n_live_tup}.","
.$stat{n_dead_tup}.","
.$stat{heap_blks_fetch}.","
.$stat{heap_blks_hit}.")");

}

sub write_toast_stat {
    shift;
    my $time_id=$_[0];
    my $toast_check_res=$self{sql}->exec("SELECT t.obj_oid,i.obj_oid FROM table_toast_name t JOIN index_toast_name i ON t.tn_id=i.tn_id WHERE t.tn_id=".$self{id});
    my ($tt_oid,$ti_oid)=$toast_check_res->fetchrow;
    if (defined($tt_oid)) {
	my $toast_table_stat_res=$prod_conn->exec(
"SELECT
pg_stat_get_numscans(oid) AS seq_scan,
pg_stat_get_tuples_returned(oid) AS seq_tup_read,
pg_stat_get_tuples_fetched(oid) AS seq_tup_fetch,
pg_stat_get_tuples_inserted(oid) AS n_tup_ins,
pg_stat_get_tuples_updated(oid) AS n_tup_upd,
pg_stat_get_tuples_deleted(oid) AS n_tup_del,
pg_stat_get_tuples_hot_updated(oid) AS n_tup_hot_upd,
pg_stat_get_live_tuples(oid) AS n_live_tup,
pg_stat_get_dead_tuples(oid) AS n_dead_tup,
pg_stat_get_blocks_fetched(oid) AS heap_blks_fetch,
pg_stat_get_blocks_hit(oid) AS heap_blks_hit
FROM pg_class
WHERE oid=".$tt_oid);
	if ($toast_table_stat_res->resultStatus != PGRES_TUPLES_OK) {
	    print "Error getting toast table stat for table ".$self{database_fields}{tbl_name}."\n";
	    print $prod_conn->errorMessage;
	    exit;
	}
	my @toast_stat=$toast_table_stat_res->fetchrow;
	my %stat;
	for (my $ttf=0; $ttf < $toast_table_stat_res->nfields; $ttf++) {
	    $stat{$toast_table_stat_res->fname($ttf)}=$toast_stat[$ttf];
	}

	$self{sql}->exec("INSERT INTO table_toast_stat VALUES ("
.$self{id}.","
.$time_id.","
.$stat{seq_scan}.","
.$stat{seq_tup_read}.","
.$stat{seq_tup_fetch}.","
.$stat{n_tup_ins}.","
.$stat{n_tup_upd}.","
.$stat{n_tup_del}.","
.$stat{n_tup_hot_upd}.","
.$stat{n_live_tup}.","
.$stat{n_dead_tup}.","
.$stat{heap_blks_fetch}.","
.$stat{heap_blks_hit}.")");

	my $t_i_stat_q="SELECT
pg_relation_size(oid) AS indexsize,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid=".$ti_oid;
	my $t_i_stat_res=$prod_conn->exec($t_i_stat_q);

	if ($t_i_stat_res->resultStatus != PGRES_TUPLES_OK) {
	    print "Error getting toast index stat data for table ".$self{database_fields}{tbl_name}."\n";
	    print $prod_conn->errorMessage;
	    exit;
	}
	my @t_i_stat=$t_i_stat_res->fetchrow;
	my %t_idx_stat;
	for (my $tif=0; $tif < $t_i_stat_res->nfields; $tif++) {
	    $t_idx_stat{$t_i_stat_res->fname($tif)}=$t_i_stat[$tif];
	}
	$self{sql}->exec("INSERT INTO index_toast_stat VALUES ("
.$self{id}.","
.$time_id.","
.$t_idx_stat{idx_scan}.","
.$t_idx_stat{idx_tup_read}.","
.$t_idx_stat{idx_tup_fetch}.","
.$t_idx_stat{idx_blks_fetch}.","
.$t_idx_stat{idx_blks_hit}.")");

    }
}

1;
