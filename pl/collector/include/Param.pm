package Param;

use Exporter();
use strict;

if (eval "require Config::IniFiles" ) {
    use Config::IniFiles;
} else {
    print "Unable to load Config::IniFiles\n";
    exit;
}


our @ISA = qw(Exporter);
our @EXPORT_OK = qw(get_parameters);
our @EXPORT = @EXPORT_OK;

#my @ds = ("a","b","c","d","e","f","g","h","i","j","k","l");

###############################################################################
#  Get all parameters from the ini file
###############################################################################
sub get_parameters {
    my $params_file=$_[0];
    unless (-e $params_file) {
	die "Unknown conf file:: $params_file :: $!\n";
    }
    my %params;
    tie %params, 'Config::IniFiles', ( -file => $params_file );
    return %params;
}

sub get_conn_string {
    my %params=get_parameters("/home/arsen/work/pg-mon/params.conf");
    my $string='';
    my %conn=%{$params{$_[0]}};
    foreach my $key (keys %conn) {
	$string.=$key."=".$conn{$key}." ";
    }
    chop $string;
    return $string;
}



1;
