Perl dependencies:

Pg
http://search.cpan.org/CPAN/authors/id/M/ME/MERGL/pgsql_perl5-1.9.0.tar.gz

Params::Validate
http://search.cpan.org/CPAN/authors/id/D/DR/DROLSKY/Params-Validate-1.00.tar.gz

Log::Handler
http://search.cpan.org/CPAN/authors/id/B/BL/BLOONIX/Log-Handler-0.71.tar.gz



==

Counter's definition and *_stat table mapping:



Cluster wide statistic counters

checkpoints_timed	pg_stat_get_bgwriter_timed_checkpoints()
checkpoints_req		pg_stat_get_bgwriter_requested_checkpoints()
buffers_checkpoint	pg_stat_get_bgwriter_buf_written_checkpoints()
buffers_clean		pg_stat_get_bgwriter_buf_written_clean()
maxwritten_clean	pg_stat_get_bgwriter_maxwritten_clean()
buffers_backend		pg_stat_get_buf_written_backend()
buffers_alloc		pg_stat_get_buf_alloc()



Database counters

db_size			pg_database_size(oid)
xact_commit		pg_stat_get_db_xact_commit(oid)
xact_rollback		pg_stat_get_db_xact_rollback(oid)
blks_fetch		pg_stat_get_db_blocks_fetched(oid)
blks_hit		pg_stat_get_db_blocks_hit(oid)
tup_returned		pg_stat_get_db_tuples_returned(oid)
tup_fetched		pg_stat_get_db_tuples_fetched(oid)
tup_inserted		pg_stat_get_db_tuples_inserted(oid)
tup_updated		pg_stat_get_db_tuples_updated(oid)
tup_deleted		pg_stat_get_db_tuples_deleted(oid)



* Table counters

tbl_size		pg_relation_size(oid)
tbl_total_size		pg_total_relation_size(oid)
tbl_tuples		pg_class.reltuples::bigint
seq_scan		pg_stat_get_numscans(oid)
seq_tup_read		pg_stat_get_tuples_returned(oid)
seq_tup_fetch		pg_stat_get_tuples_fetched(oid)
n_tup_ins		pg_stat_get_tuples_inserted(oid)
n_tup_upd		pg_stat_get_tuples_updated(oid)
n_tup_del		pg_stat_get_tuples_deleted(oid)
n_tup_hot_upd		pg_stat_get_tuples_hot_updated(oid)
n_live_tup		pg_stat_get_live_tuples(oid)
n_dead_tup		pg_stat_get_dead_tuples(oid)
heap_blks_fetch		pg_stat_get_blocks_fetched(oid)
heap_blks_rhit		pg_stat_get_blocks_hit(oid)

last_vacuum		pg_stat_get_last_vacuum_time(oid)
last_autovacuum		pg_stat_get_last_autovacuum_time(oid)
last_analyze		pg_stat_get_last_analyze_time(oid)
last_autoanalyze	pg_stat_get_last_autoanalyze_time(oid)


* Index counters

idx_scan		pg_stat_get_numscans(oid)
idx_tup_read		pg_stat_get_tuples_returned(oid)
idx_tup_fetch		pg_stat_get_tuples_fetched(oid)
idx_blks_fetch		pg_stat_get_blocks_fetched(oid)
idx_blks_hit		pg_stat_get_blocks_hit(oid)


---------------------------------------------
* Including TOAST
