Perl dependencies:

Pg
http://search.cpan.org/CPAN/authors/id/M/ME/MERGL/pgsql_perl5-1.9.0.tar.gz

Params::Validate
http://search.cpan.org/CPAN/authors/id/D/DR/DROLSKY/Params-Validate-1.00.tar.gz

Log::Handler
http://search.cpan.org/CPAN/authors/id/B/BL/BLOONIX/Log-Handler-0.71.tar.gz



==

Counter's definition and *_stat table mapping:

 table_stat

tbl_size	pg_relation_size(oid)
tbl_total_size	pg_total_relation_size(oid)
tbl_tuples	pg_class.reltuples::bigint
seq_scan	pg_stat_get_numscans(oid)
seq_tup_read	pg_stat_get_tuples_returned(oid)
seq_tup_fetch	pg_stat_get_tuples_fetched(oid)
n_tup_ins	pg_stat_get_tuples_inserted(oid)
n_tup_upd	pg_stat_get_tuples_updated(oid)
n_tup_del	pg_stat_get_tuples_deleted(oid)
n_tup_hot_upd	pg_stat_get_tuples_hot_updated(oid)
n_live_tup	pg_stat_get_live_tuples(oid)
n_dead_tup	pg_stat_get_dead_tuples(oid)
heap_blks_fetch	pg_stat_get_blocks_fetched(oid)
heap_blks_rhit	pg_stat_get_blocks_hit(oid)




 index_stat
idx_scan	pg_stat_get_numscans(oid)
idx_tup_read	pg_stat_get_tuples_returned(oid)
idx_tup_fetch	pg_stat_get_tuples_fetched(oid)
idx_blks_fetch	pg_stat_get_blocks_fetched(oid)
idx_blks_hit	pg_stat_get_blocks_hit(oid)
