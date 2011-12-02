package DatabaseName;

require Exporter;

use Pg;
use strict;

use include::Param;

our @ISA =qw(Exporter);

our @EXPORT = qw($prod_conn);
our @EXPORT_OK = @EXPORT;

our %self;
our $prod_conn;

sub new {
    my $class=shift;
    my $iam = { };
    $self{table}='database_name';
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
    bless($iam,$class);
    return $iam;
}

###############################################

sub set_prod_conn {
    shift;
    my $res=$self{sql}->exec("SELECT get_conn_string(".$self{database_fields}{hc_id}.",".$self{id}.") AS prod_conn_string");
    my ($conn_string)=$res->fetchrow;
    $self{prod_sql}=Pg::connectdb($conn_string);
    $prod_conn=$self{prod_sql};
    if ($self{prod_sql}->status != PGRES_CONNECTION_OK) {
	print "HostCluster Prod Connect Error: ".$self{prod_sql}->errorMessage."\n";
	exit;
    }
}

sub get_prod_conn {
    shift;
    return $prod_conn;
}

sub get_schema_ids {
    shift;
    my $res=$self{sql}->exec("SELECT id FROM schema_name WHERE alive AND observable AND dn_id=".$self{id});
    my @ret;
    while (my ($id)=$res->fetchrow) {
	push(@ret,$id);
    }
    return @ret;

}

1;


