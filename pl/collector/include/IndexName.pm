package IndexName;

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
    $self{table}='index_name';
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

sub write_stat {
    shift;
    my $time_id=$_[0];
    my $index_stat_res=$prod_conn->exec("SELECT
pg_relation_size(oid) AS indexsize,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid=".$self{database_fields}{obj_oid});
    if ($index_stat_res->resultStatus != PGRES_TUPLES_OK) {
	print "Error getting stat data for index ".$self{database_fields}{idx_name}."\n";
	print $prod_conn->errorMessage;
	exit;
    }
    my @idx_stat=$index_stat_res->fetchrow;
    my %i_stat;
    for (my $if=0; $if < $index_stat_res->nfields; $if++) {
	$i_stat{$index_stat_res->fname($if)}=$idx_stat[$if];
    }
    $self{sql}->exec("INSERT INTO index_stat VALUES (".$self{id}.","
.$time_id.","
.$i_stat{idx_scan}.","
.$i_stat{idx_tup_read}.","
.$i_stat{idx_tup_fetch}.","
.$i_stat{idx_blks_fetch}.","
.$i_stat{idx_blks_hit}.")");

}

1;
