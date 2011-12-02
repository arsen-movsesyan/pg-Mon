package SchemaName;

require Exporter;

use Pg;
use strict;

our @ISA =qw(Exporter DatabaseName);

use include::Param;
use include::DatabaseName;

our @EXPORT = qw( );
our @EXPORT_OK = @EXPORT;

our %self;
our $prod_conn;

sub new {
    my $class=shift;
    my $iam = { };
    $self{table}='schema_name';
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


sub get_table_ids {
    shift;
    my $res=$self{sql}->exec("SELECT id FROM table_name WHERE alive AND sn_id=".$self{id});
    my @ret;
    while (my ($id)=$res->fetchrow) {
	push(@ret,$id);
    }
    return @ret;
}

sub get_function_ids {
    shift;
    my $res=$self{sql}->exec("SELECT id FROM function_name WHERE alive AND sn_id=".$self{id});
    my @ret;
    while (my ($id)=$res->fetchrow) {
	push(@ret,$id);
    }
    return @ret;
}

sub discover_functions {
    shift;
    my $local_fnc_res=$self{sql}->exec("SELECT * FROM function_name WHERE alive AND sn_id=".$self{database_fields}{id});
    my @exist_functions;
    while (my @fnc=$local_fnc_res->fetchrow) {
	my %l_func;
	for (my $lf=0;$lf < $local_fnc_res->nfields;$lf++) {
	    $l_func{$local_fnc_res->fname($lf)}=$fnc[$lf];
	}
	push(@exist_functions,\%l_func);
    }
    my $prod_fnc_q="SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
FROM pg_proc p
LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_type t ON p.prorettype=t.oid
JOIN pg_language l ON p.prolang=l.oid
WHERE (p.prolang <> (12)::oid)
AND n.oid=".$self{database_fields}{obj_oid};
    my $prod_fnc_res=$prod_conn->exec($prod_fnc_q);
    if ($prod_fnc_res->resultStatus != PGRES_TUPLES_OK) {
	print "Error getting function discovery data for schema ".$self{database_fields}{sch_name}."\n";
	print $prod_conn->errorMessage;
	exit;
    }

    my @prod_functions;
    while (my @prod_fnc=$prod_fnc_res->fetchrow) {
	my %p_fnc;
	for (my $pf=0; $pf < $prod_fnc_res->nfields;$pf++) {
	    $p_fnc{$prod_fnc_res->fname($pf)}=$prod_fnc[$pf];
	}
	push (@prod_functions,\%p_fnc);
	foreach (@exist_functions) {
	    if (${$_}{pro_oid} == $p_fnc{pro_oid}) {
		pop(@prod_functions);
		${$_}{id}=undef;
		last;
	    }
	}
    }
    foreach (@exist_functions) {
	if (defined(${$_}{id})) {
	    $self{sql}->exec("UPDATE function_name SET alive='f' WHERE id=".${$_}{id});
	}
    }
    foreach (@prod_functions) {
	$self{sql}->exec("INSERT INTO function_name (sn_id,pro_oid,proretset,func_name,prorettype,prolang) VALUES (".
	$self{database_fields}{id}.",".${$_}{pro_oid}.",'".${$_}{proretset}."','".${$_}{funcname}."','".${$_}{typname}."','".${$_}{lanname}."')");
    }
}


sub get_existing_tables {
    my $local_tbl_res=$self{sql}->exec("SELECT * FROM table_name WHERE alive AND sn_id=".$self{database_fields}{id});
    my @ret;
    while (my @tbl=$local_tbl_res->fetchrow) {
	my %l_table;
	for (my $t=0;$t < $local_tbl_res->nfields;$t++) {
	    $l_table{$local_tbl_res->fname($t)}=$tbl[$t];
	}
	push(@ret,\%l_table);
    }
    return @ret;
}


sub get_prod_tables {
    my $prod_tbl_q="SELECT r.oid,r.relname,r.reltoastrelid,
CASE WHEN h.inhrelid IS NULL THEN 'f'::boolean ELSE 't'::boolean END AS has_parent,
CASE WHEN i.indexrelid IS NULL THEN 0::int ELSE (SELECT COUNT(1) FROM pg_index WHERE indrelid=r.oid)::int END AS indexes
FROM pg_class r
LEFT JOIN pg_inherits h ON r.oid=h.inhrelid
LEFT JOIN pg_index i ON r.oid=i.indrelid
WHERE r.relkind='r'
AND r.relnamespace=".$self{database_fields}{obj_oid}.
" GROUP BY 1,2,3,4,5
ORDER BY 1,2,3,4,5";
    my $prod_tbl_res=$prod_conn->exec($prod_tbl_q);
    if ($prod_tbl_res->resultStatus != PGRES_TUPLES_OK) {
	print "Error getting table discovery data for schema ".$self{database_fields}{sch_name}."\n";
	print $prod_conn->errorMessage;
	exit;
    }

    my @ret;
    while (my @prod_tbl=$prod_tbl_res->fetchrow) {
	my %p_table;
	for (my $pt=0;$pt < $prod_tbl_res->nfields;$pt++) {
	    $p_table{$prod_tbl_res->fname($pt)}=$prod_tbl[$pt];
	}
	push(@ret,\%p_table);
    }
    return @ret;
}




sub discover_tables {
    shift;
    my @exist_tables=get_existing_tables();
    my @prod_tables=get_prod_tables();
    foreach my $exist_table (@exist_tables) {
	foreach my $prod_table (@prod_tables) {
	    if (${$exist_table}{obj_oid} == ${$prod_table}{oid}) {
# TOAST ##############################################################################
		if (${$prod_table}{reltoastrelid}) {
		    my $toast_res=$self{sql}->exec("SELECT 1 FROM table_toast_name WHERE tn_id=".${$exist_table}{id});
		    if (!$toast_res->fetchrow) {
			my $toast_ti_res=$prod_conn->exec("SELECT t.oid AS t_relid,t.relname AS t_relname,t.reltoastidxid AS t_i_relid,i.relname AS t_i_relname
FROM pg_class t
INNER JOIN pg_class r ON r.reltoastrelid=t.oid
INNER JOIN pg_class i ON t.reltoastidxid=i.oid
WHERE t.oid=".${$prod_table}{reltoastrelid});
			if ($toast_ti_res->resultStatus != PGRES_TUPLES_OK) {
			    print "Error getting index discovery data for schema ".$self{database_fields}{sch_name}."\n";
			    print $prod_conn->errorMessage;
			    exit;
			}
			my ($t_relid,$t_relname,$t_i_relid,$t_i_relname)=$toast_ti_res->fetchrow;
			$self{sql}->exec("INSERT INTO table_toast_name (tn_id,obj_oid,tbl_name) VALUES (".${$exist_table}{id}.",".$t_relid.",'".$t_relname."')");
			$self{sql}->exec("INSERT INTO index_toast_name (tn_id,obj_oid,idx_name) VALUES (".${$exist_table}{id}.",".$t_i_relid.",'".$t_i_relname."')");
		    }
		}

######################################################################################
# INDEXES ############################################################################
		my $index_res=$self{sql}->exec("SELECT * FROM index_name WHERE tn_id=".${$exist_table}{id});
		my @exist_indexes;
		while (my @index_row=$index_res->fetchrow) {
		    my %ind;
		    for (my $if=0;$if < $index_res->nfields; $if++) {
			$ind{$index_res->fname($if)}=$index_row[$if];
		    }
		    push(@exist_indexes,\%ind);
		}
		my @prod_indexes;
		if (${$prod_table}{indexes}) {
		    my $prod_ind_res=$prod_conn->exec("SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
FROM pg_index i
JOIN pg_class c ON i.indexrelid=c.oid
WHERE i.indrelid=".${$prod_table}{oid});
		    if ($prod_ind_res->resultStatus != PGRES_TUPLES_OK) {
			print "Error getting index discovery data for schema ".$self{database_fields}{sch_name}."\n";
			print $prod_conn->errorMessage;
			exit;
		    }
		    while (my @prod_index=$prod_ind_res->fetchrow) {
			my %p_index;
			for (my $pif=0; $pif < $prod_ind_res->nfields; $pif++) {
			    $p_index{$prod_ind_res->fname($pif)}=$prod_index[$pif];
			}
			push(@prod_indexes,\%p_index);
			foreach my $exist_index (@exist_indexes) {
			    if ($p_index{indexrelid} == ${$exist_index}{obj_oid}) {
				${$exist_index}{id}=undef;
				pop(@prod_indexes);
				last;
			    }
			}
		    }
		}
		foreach (@exist_indexes) {
		    if (defined ${$_}{id}) {
			$self{sql}->exec("UPDATE index_name SET alive='f' WHERE id=".${$_}{id});
		    }
		}
		foreach (@prod_indexes) {
		    $self{sql}->exec("INSERT INTO index_name (tn_id,obj_oid,is_unique,is_primary,idx_name) VALUES (".
			${$exist_table}{id}.",".${$_}{indexrelid}.",'".${$_}{indisunique}."','".${$_}{indisprimary}."','".${$_}{relname}."')");
		}
######################################################################################
		${$exist_table}{id}=undef;
		${$prod_table}{relname}=undef;
		last;
	    }
	}
    }
    foreach (@exist_tables) {
	if (defined ${$_}{id}) {
	    $self{sql}->exec("UPDATE table_name SET alive = 'f' WHERE id=".${$_}{id});
	}
    }
    foreach (@prod_tables) {
	if (defined(${$_}{relname})) {
	    my $new_table_res=$self{sql}->exec("INSERT INTO table_name (sn_id,obj_oid,has_parent,tbl_name) VALUES (".$self{database_fields}{id}.",".${$_}{oid}.",'".${$_}{has_parent}."','".${$_}{relname}."') RETURNING id");
	    my ($table_id)=$new_table_res->fetchrow;
	    if (${$_}{reltoastrelid}) {
## TOAST #############################
		my $toast_ti_q="SELECT t.oid AS t_relid,t.relname AS t_relname,t.reltoastidxid AS t_i_relid,i.relname AS t_i_relname
FROM pg_class t
INNER JOIN pg_class r ON r.reltoastrelid=t.oid
INNER JOIN pg_class i ON t.reltoastidxid=i.oid
WHERE t.oid=".${$_}{reltoastrelid};
		my $ext_toast_ti_res=$prod_conn->exec($toast_ti_q);
		if ($ext_toast_ti_res->resultStatus != PGRES_TUPLES_OK) {
		    print "Error getting toast table info for schema ".$self{database_fields}{sch_name}."\n";
		    print $prod_conn->errorMessage;
		    exit;
		}
		my ($t_relid,$t_relname,$t_i_relid,$t_i_relname)=$ext_toast_ti_res->fetchrow;
		$self{sql}->exec("INSERT INTO table_toast_name (tn_id,obj_oid,tbl_name) VALUES (".$table_id.",".$t_relid.",'".$t_relname."')");
		$self{sql}->exec("INSERT INTO index_toast_name (tn_id,obj_oid,idx_name) VALUES (".$table_id.",".$t_i_relid.",'".$t_i_relname."')");
	    }
	    if (${$_}{indexes}) {
## INDEX #############################
		my $new_ind_res=$prod_conn->exec("SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
FROM pg_index i
JOIN pg_class c ON i.indexrelid=c.oid
WHERE i.indrelid=".${$_}{oid});
		if ($new_ind_res->resultStatus != PGRES_TUPLES_OK) {
		    print "Error getting index info for schema ".$self{database_fields}{sch_name}."\n";
		    print $prod_conn->errorMessage;
		    exit;
		}
		while (my ($indexrelid,$relname,$indisunique,$indisprimary)=$new_ind_res->fetchrow) {
		    $self{sql}->exec("INSERT INTO index_name (tn_id,obj_oid,is_unique,is_primary,idx_name) VALUES (".
			$table_id.",".$indexrelid.",'".$indisunique."','".$indisprimary."','".$relname."')");
		}
	    }
	}
    }
}



1;


