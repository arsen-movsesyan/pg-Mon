/*
 * SELECT en.$field - start.$field [AS some_diff] FROM $observe_stat start
 * JOIN $observe_stat en ON start.$name_field_id=en.$name_field_id
 * JOIN $observe_name observe ON observe.id=start.$name_field_id
 * WHERE start.time_id=(SELECT MAX(id) FROM log_time WHERE hour_truncate <= date_trunc('hour',now()-interval '$start_offset hour'))
 * AND en.time_id=(SELECT MAX(id) FROM log_time WHERE hour_truncate <= date_trunc('hour',now()-interval '$end_offset hour'))
 * AND observe.$observe_name_field='$actual_name'
*/

/*
$field				- observation field. Examples: seq_scan, n_tup_ins, idx_tup_read
$observe_stat			- statistical table name. Examples: table_stat, index_stat
$observe_name			- actual abservation unit table. Examples: table_name, index_name
$name_field_id			- foreign key field pointing to observation unit table. Examples: tn_id, in_id
$start_offset, $end_offset	- time intervals in hours from point "now()" in INTEGER. $end_offset usually 0, $start_offset usually 24
$actual_name			- observable unit's actual name. 'events', 'appliances', 'idx_tmp_os_changes_hostid', etc
$observe_name_field		- column name in observable table. tbl_name, idx_name
*/

--
--SQL statement examplpe:
--

SELECT en.seq_scan - start.seq_scan AS seq_scan_diff FROM table_stat start
JOIN table_stat en ON start.tn_id=en.tn_id
JOIN table_name observe ON observe.id=start.tn_id
WHERE start.time_id=(SELECT MAX(id) FROM log_time WHERE hour_truncate <= date_trunc('hour',now()-interval '24 hour'))
AND en.time_id=(SELECT MAX(id) FROM log_time WHERE hour_truncate <= date_trunc('hour',now()-interval '0 hour'))
AND observe.tbl_name='events'
