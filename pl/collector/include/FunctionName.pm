package FunctionName;

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
    $self{table}='function_name';
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
    my $stat_q="SELECT
COALESCE(pg_stat_get_function_calls(oid),0) AS func_calls,
COALESCE((pg_stat_get_function_time(oid)),0) AS total_time,
COALESCE((pg_stat_get_function_self_time(oid)),0) AS self_time
FROM pg_proc p
WHERE oid=".$self{database_fields}{pro_oid};

    my $stat_res=$prod_conn->exec($stat_q);
    if ($stat_res->resultStatus != PGRES_TUPLES_OK) {
	print "Error Getting stat for Function ".$self{database_fields}{func_name}."\n";
	print $prod_conn->errorMessage;
	exit;
    }
    my ($func_calls,$total_time,$self_time)=$stat_res->fetchrow;

    $self{sql}->exec("INSERT INTO function_stat VALUES (".$self{id}.",".$time_id.",".$func_calls.",".$total_time.",".$self_time.")");
}

1;
