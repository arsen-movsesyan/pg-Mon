--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.3
-- Dumped by pg_dump version 9.2.2
-- Started on 2013-09-06 16:24:31 PDT

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

DROP DATABASE pg_mon;
--
-- TOC entry 2159 (class 1262 OID 24981)
-- Name: pg_mon; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE pg_mon WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C';


ALTER DATABASE pg_mon OWNER TO postgres;

\connect pg_mon

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 6 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 2160 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 203 (class 3079 OID 11638)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2162 (class 0 OID 0)
-- Dependencies: 203
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- TOC entry 226 (class 1255 OID 24982)
-- Name: pm_bgwriter_stat_diff(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pm_bgwriter_stat_diff(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(hostname character varying, ip_address inet, is_master boolean, checkpoints_timed bigint, checkpoints_req bigint, buffers_checkpoint bigint, buffers_clean bigint, maxwritten_clean bigint, buffers_backend bigint, buffers_alloc bigint)
    LANGUAGE sql
    AS $_$
SELECT hc.hostname,hc.param_ip_address,hc.is_master,
last.checkpoints_timed - first.checkpoints_timed AS checkpoints_timed,
last.checkpoints_req - first.checkpoints_req AS checkpoints_req,
last.buffers_checkpoint - first.buffers_checkpoint AS buffers_checkpoint,
last.buffers_clean - first.buffers_clean AS buffers_clean,
last.maxwritten_clean - first.maxwritten_clean AS maxwritten_clean,
last.buffers_backend - first.buffers_backend AS buffers_backend,
last.buffers_alloc - first.buffers_alloc AS buffers_alloc
FROM host_cluster hc
JOIN bgwriter_stat first ON hc.id=first.hc_id
JOIN bgwriter_stat last ON hc.id=last.hc_id
JOIN log_time a ON a.id=first.time_id
JOIN log_time b ON b.id=last.time_id
WHERE hc.alive
AND hc.observable
AND a.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $1 * interval '1 hour'))
AND b.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $2 * interval '1 hour'));
$_$;


ALTER FUNCTION public.pm_bgwriter_stat_diff(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 215 (class 1255 OID 24983)
-- Name: pm_database_stat_diff(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pm_database_stat_diff(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(hostname character varying, ip_address inet, is_master boolean, db_name character varying, db_size bigint, xact_commit bigint, xact_rollback bigint, blks_fetch bigint, blks_hit bigint, tup_returned bigint, tup_fetched bigint, tup_inserted bigint, tup_updated bigint, tup_deleted bigint)
    LANGUAGE sql
    AS $_$
SELECT hc.hostname, hc.param_ip_address, hc.is_master, dn.db_name, 
last.db_size - first.db_size AS db_size, 
last.xact_commit - first.xact_commit AS xact_commit, 
last.xact_rollback - first.xact_rollback AS xact_rollback, 
last.blks_fetch - first.blks_fetch AS blks_fetch, 
last.blks_hit - first.blks_hit AS blks_hit, 
last.tup_returned - first.tup_returned AS tup_returned, 
last.tup_fetched - first.tup_fetched AS tup_fetched, 
last.tup_inserted - first.tup_inserted AS tup_inserted, 
last.tup_updated - first.tup_updated AS tup_updated, 
last.tup_deleted - first.tup_deleted AS tup_deleted
FROM host_cluster hc
JOIN database_name dn ON hc.id = dn.hc_id
JOIN database_stat first ON dn.id = first.dn_id
JOIN database_stat last ON dn.id = last.dn_id
JOIN log_time a ON a.id = first.time_id
JOIN log_time b ON b.id = last.time_id
WHERE hc.observable 
AND dn.alive 
AND dn.observable 
AND a.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $1 * interval '1 hour'))
AND b.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $2 * interval '1 hour'));
$_$;


ALTER FUNCTION public.pm_database_stat_diff(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 227 (class 1255 OID 24984)
-- Name: pm_function_stat_diff(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pm_function_stat_diff(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(hostname character varying, ip_address inet, is_master boolean, db_name character varying, sch_name character varying, func_name character varying, func_calls bigint, total_time bigint, self_time bigint)
    LANGUAGE sql
    AS $_$
SELECT hc.hostname,hc.param_ip_address,hc.is_master,dn.db_name,sn.sch_name,fn.func_name,
last.func_calls - first.func_calls AS func_calls,
last.total_time - first.total_time AS total_time,
last.self_time - first.self_time AS self_time
FROM host_cluster hc
JOIN database_name dn ON hc.id=dn.hc_id
JOIN schema_name sn ON dn.id=sn.dn_id
JOIN function_name fn ON sn.id=fn.sn_id
JOIN function_stat first ON fn.id=first.fn_id
JOIN function_stat last ON fn.id=last.fn_id
JOIN log_time a ON a.id=first.time_id
JOIN log_time b ON b.id=last.time_id
WHERE hc.observable
AND dn.observable
AND sn.observable
AND fn.alive
AND a.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $1 * interval '1 hour'))
AND b.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $2 * interval '1 hour'));
$_$;


ALTER FUNCTION public.pm_function_stat_diff(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 230 (class 1255 OID 33221)
-- Name: pm_index_stat_diff(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pm_index_stat_diff(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(index_id integer, idx_size bigint, idx_scan bigint, idx_tup_read bigint, idx_tup_fetch bigint, idx_blks_fetch bigint, idx_blks_hit bigint)
    LANGUAGE sql
    AS $_$
SELECT 
mil.index_id AS index_id --,ind.idx_name,
,last.idx_size - first.idx_size AS idx_size,
last.idx_scan - first.idx_scan AS idx_scan,
last.idx_tup_read - first.idx_tup_read AS idx_tup_read,
last.idx_tup_fetch - first.idx_tup_fetch AS idx_tup_fetch,
last.idx_blks_fetch - first.idx_blks_fetch AS idx_blks_fetch,
last.idx_blks_hit - first.idx_blks_hit AS idx_blks_hit
FROM pm_master_index_lookup_view mil
JOIN index_stat first ON mil.index_id=first.in_id
JOIN index_stat last ON mil.index_id=last.in_id
JOIN log_time a ON a.id=first.time_id
JOIN log_time b ON b.id=last.time_id
WHERE  a.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $1 * interval '1 hour'))
AND b.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $2 * interval '1 hour'));
$_$;


ALTER FUNCTION public.pm_index_stat_diff(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 228 (class 1255 OID 24986)
-- Name: pm_index_toast_stat_diff(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pm_index_toast_stat_diff(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(hostname character varying, ip_address inet, is_master boolean, db_name character varying, sch_name character varying, tbl_name character varying, toast_tbl_name character varying, tidx_name character varying, tidx_size bigint, tidx_scan bigint, tidx_tup_read bigint, tidx_tup_fetch bigint, tidx_blks_fetch bigint, tidx_blks_hit bigint)
    LANGUAGE sql
    AS $_$
SELECT hc.hostname,hc.param_ip_address,hc.is_master,dn.db_name,sn.sch_name,tn.tbl_name,ttn.ttbl_name AS toast_tbl_name,tind.tidx_name AS toast_idx_name,
last.tidx_size - first.tidx_size AS tidx_size,
last.tidx_scan - first.tidx_scan AS tidx_scan,
last.tidx_tup_read - first.tidx_tup_read AS tidx_tup_read,
last.tidx_tup_fetch - first.tidx_tup_fetch AS tidx_tup_fetch,
last.tidx_blks_fetch - first.tidx_blks_fetch AS tidx_blks_fetch,
last.tidx_blks_hit - first.tidx_blks_hit AS tidx_blks_hit
FROM host_cluster hc
JOIN database_name dn ON hc.id=dn.hc_id
JOIN schema_name sn ON dn.id=sn.dn_id
JOIN table_name tn ON sn.id=tn.sn_id
JOIN table_toast_name ttn ON tn.id=ttn.tn_id
JOIN index_toast_name tind ON ttn.id=tind.ttn_id
JOIN index_toast_stat first ON tind.id=first.tin_id
JOIN index_toast_stat last ON tind.id=last.tin_id
JOIN log_time a ON a.id=first.time_id
JOIN log_time b ON b.id=last.time_id
WHERE hc.alive
AND hc.observable
AND dn.observable
AND sn.observable
AND tind.alive
AND a.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $1 * interval '1 hour'))
AND b.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $2 * interval '1 hour'));
$_$;


ALTER FUNCTION public.pm_index_toast_stat_diff(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 229 (class 1255 OID 33219)
-- Name: pm_table_stat_diff(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pm_table_stat_diff(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(table_id integer, tbl_size bigint, tbl_tuples bigint, seq_scan bigint, seq_tup_read bigint, seq_tup_fetch bigint, n_tup_ins bigint, n_tup_upd bigint, n_tup_del bigint, n_tup_hot_upd bigint, n_live_tup bigint, n_dead_tup bigint, heap_blks_fetch bigint, heap_blks_hit bigint)
    LANGUAGE sql
    AS $_$
SELECT 
mtl.table_id,
last.tbl_size - first.tbl_size AS tbl_size,
last.tbl_tuples - first.tbl_tuples AS tbl_tuples,
last.seq_scan - first.seq_scan AS seq_scan,
last.seq_tup_read - first.seq_tup_read AS seq_tup_read,
last.seq_tup_fetch - first.seq_tup_fetch AS seq_tup_fetch,
last.n_tup_ins - first.n_tup_ins AS n_tup_ins,
last.n_tup_upd - first.n_tup_upd AS n_tup_upd,
last.n_tup_del - first.n_tup_del AS n_tup_del,
last.n_tup_hot_upd - first.n_tup_hot_upd AS n_tup_hot_upd,
last.n_live_tup - first.n_live_tup AS n_live_tup,
last.n_dead_tup - first.n_dead_tup AS n_dead_tup,
last.heap_blks_fetch - first.heap_blks_fetch AS heap_blks_fetch,
last.heap_blks_hit - first.heap_blks_hit AS heap_blks_hit
FROM pm_master_table_lookup_view mtl
JOIN table_stat first ON mtl.table_id=first.tn_id
JOIN table_stat last ON mtl.table_id=last.tn_id
JOIN log_time a ON a.id=first.time_id
JOIN log_time b ON b.id=last.time_id
WHERE 
a.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $1 * interval '1 hour'))
AND b.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $2 * interval '1 hour'));
$_$;


ALTER FUNCTION public.pm_table_stat_diff(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 225 (class 1255 OID 24988)
-- Name: pm_table_toast_stat_diff(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION pm_table_toast_stat_diff(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(hostname character varying, ip_address inet, is_master boolean, db_name character varying, sch_name character varying, tbl_name character varying, toast_tbl_name character varying, ttbl_size bigint, seq_scan bigint, seq_tup_read bigint, eq_tup_fetch bigint, n_tup_ins bigint, n_tup_upd bigint, n_tup_del bigint, n_tup_hot_upd bigint, n_live_tup bigint, n_dead_tup bigint, heap_blks_fetch bigint, heap_blks_hit bigint)
    LANGUAGE sql
    AS $_$
SELECT hc.hostname,hc.param_ip_address,hc.is_master,dn.db_name,sn.sch_name,tn.tbl_name,ttn.ttbl_name AS toast_tbl_name,
last.ttbl_size - first.ttbl_size AS ttbl_size,
last.seq_scan - first.seq_scan AS seq_scan,
last.seq_tup_read - first.seq_tup_read AS seq_tup_read,
last.seq_tup_fetch - first.seq_tup_fetch AS seq_tup_fetch,
last.n_tup_ins - first.n_tup_ins AS n_tup_ins,
last.n_tup_upd - first.n_tup_upd AS n_tup_upd,
last.n_tup_del - first.n_tup_del AS n_tup_del,
last.n_tup_hot_upd - first.n_tup_hot_upd AS n_tup_hot_upd,
last.n_live_tup - first.n_live_tup AS n_live_tup,
last.n_dead_tup - first.n_dead_tup AS n_dead_tup,
last.heap_blks_fetch - first.heap_blks_fetch AS heap_blks_fetch,
last.heap_blks_hit - first.heap_blks_hit AS heap_blks_hit
FROM host_cluster hc
JOIN database_name dn ON hc.id=dn.hc_id
JOIN schema_name sn ON dn.id=sn.dn_id
JOIN table_name tn ON sn.id=tn.sn_id
JOIN table_toast_name ttn ON tn.id=ttn.tn_id
JOIN table_toast_stat first ON ttn.id=first.ttn_id
JOIN table_toast_stat last ON ttn.id=last.ttn_id
JOIN log_time a ON a.id=first.time_id
JOIN log_time b ON b.id=last.time_id
WHERE hc.observable
AND dn.observable
AND sn.observable
AND ttn.alive
AND a.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $1 * interval '1 hour'))
AND b.id=(SELECT MIN(id) FROM log_time WHERE hour_truncate >= date_trunc('hour',now()- $2 * interval '1 hour'));
$_$;


ALTER FUNCTION public.pm_table_toast_stat_diff(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 216 (class 1255 OID 24989)
-- Name: remove_databases(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_databases() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE database_name SET alive='f' WHERE NEW.alive='f' AND hc_id=OLD.id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_databases() OWNER TO postgres;

--
-- TOC entry 217 (class 1255 OID 24990)
-- Name: remove_functions(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_functions() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE function_name SET alive='f' WHERE NEW.alive='f' AND sn_id=OLD.id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_functions() OWNER TO postgres;

--
-- TOC entry 218 (class 1255 OID 24991)
-- Name: remove_indexes(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_indexes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE index_name SET alive='f' WHERE NEW.alive='f' AND tn_id=OLD.id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_indexes() OWNER TO postgres;

--
-- TOC entry 219 (class 1255 OID 24992)
-- Name: remove_schemas(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_schemas() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE schema_name SET alive='f' WHERE NEW.alive='f' AND dn_id=OLD.id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_schemas() OWNER TO postgres;

--
-- TOC entry 220 (class 1255 OID 24993)
-- Name: remove_tables(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_tables() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE table_name SET alive='f' WHERE NEW.alive='f' AND sn_id=OLD.id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_tables() OWNER TO postgres;

--
-- TOC entry 221 (class 1255 OID 24994)
-- Name: remove_toas_indexes(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_toas_indexes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE index_toast_name SET alive='f' WHERE NEW.alive='f' AND ttn_id=OLD.tn_id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_toas_indexes() OWNER TO postgres;

--
-- TOC entry 222 (class 1255 OID 24995)
-- Name: remove_toast_tables(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_toast_tables() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE table_toast_name SET alive='f' WHERE NEW.alive='f' AND tn_id=OLD.id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_toast_tables() OWNER TO postgres;

--
-- TOC entry 223 (class 1255 OID 24996)
-- Name: suspend_schemas(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION suspend_schemas() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE schema_name SET observable=NEW.observable WHERE dn_id=OLD.id;
	RETURN NEW;
END$$;


ALTER FUNCTION public.suspend_schemas() OWNER TO postgres;

--
-- TOC entry 224 (class 1255 OID 24997)
-- Name: terminate_change(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION terminate_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	IF NEW.alive='t' AND OLD.alive='f' THEN
		RETURN OLD;
	END IF;
	RETURN NEW;
END$$;


ALTER FUNCTION public.terminate_change() OWNER TO postgres;

--
-- TOC entry 231 (class 1255 OID 33224)
-- Name: vw_hot_update_pct(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION vw_hot_update_pct(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(table_id integer, n_tup_upd bigint, n_tup_hot_upd bigint, hot_upd_pct numeric)
    LANGUAGE sql
    AS $_$
SELECT
table_id,
n_tup_upd,
n_tup_hot_upd,
CAST(n_tup_hot_upd AS numeric) / n_tup_upd AS hot_upd_pct
FROM pm_table_stat_diff($1,$2)
WHERE n_tup_upd > 0;
$_$;


ALTER FUNCTION public.vw_hot_update_pct(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 233 (class 1255 OID 33223)
-- Name: vw_index_pct(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION vw_index_pct(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(table_id integer, tbl_size bigint, tbl_tuples bigint, seq_scan bigint, seq_tup_read bigint, idx_scan bigint, idx_tup_fetch bigint, idx_scan_pct numeric, idx_tup_pct numeric)
    LANGUAGE sql
    AS $_$
SELECT 
tsv.table_id
,tsv.tbl_size
,tsv.tbl_tuples
,tsd.seq_scan
,tsd.seq_tup_read
,SUM(isd.idx_scan)::bigint AS idx_scan
,SUM(isd.idx_tup_fetch)::bigint AS idx_tup_fetch
,CAST(SUM(isd.idx_scan) AS numeric) / (SUM(isd.idx_scan) + tsd.seq_scan) AS idx_scan_pct
,CAST(SUM(isd.idx_tup_fetch) AS numeric) / (SUM(isd.idx_tup_fetch) + tsd.seq_tup_read) AS idx_tup_pct
FROM pm_table_size_view tsv
JOIN pm_table_stat_diff($1,$2) tsd ON tsv.table_id=tsd.table_id
JOIN pm_master_index_lookup_view mil ON tsv.table_id=mil.table_id
JOIN pm_index_stat_diff($1,$2) isd ON mil.index_id=isd.index_id
GROUP BY 1,2,3,4,5
HAVING (SUM(isd.idx_scan) + tsd.seq_scan) > 0 AND (SUM(isd.idx_tup_fetch) + tsd.seq_tup_read) > 0;
$_$;


ALTER FUNCTION public.vw_index_pct(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 235 (class 1255 OID 33228)
-- Name: vw_table_hip_pct(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION vw_table_hip_pct(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(table_id integer, heap_blks_hit bigint, heap_blks_read bigint, hit_pct numeric)
    LANGUAGE sql
    AS $_$
SELECT table_id
,heap_blks_hit
,heap_blks_fetch-heap_blks_hit AS heap_blks_read
,CAST(heap_blks_hit AS numeric) / heap_blks_fetch AS hit_pct
FROM pm_table_stat_diff($1,$2)
WHERE heap_blks_fetch > 0;
$_$;


ALTER FUNCTION public.vw_table_hip_pct(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 234 (class 1255 OID 33227)
-- Name: vw_table_idx_hip_pct(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION vw_table_idx_hip_pct(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(table_id integer, idx_blks_hit bigint, idx_blks_read bigint, idx_hit_pct numeric)
    LANGUAGE sql
    AS $_$
SELECT mtl.table_id
,SUM(idx_blks_hit)::bigint AS idx_blks_hit
,SUM(idx_blks_fetch-idx_blks_hit)::bigint AS idx_blks_read
,SUM(idx_blks_hit) / SUM(idx_blks_fetch) AS idx_hit_pct
FROM pm_master_table_lookup_view mtl
JOIN pm_master_index_lookup_view mil ON mtl.table_id=mil.table_id
JOIN pm_index_stat_diff($1,$2) isd ON mil.index_id=isd.index_id
GROUP BY 1
HAVING SUM(isd.idx_blks_fetch) > 0;
$_$;


ALTER FUNCTION public.vw_table_idx_hip_pct(first integer, last integer) OWNER TO postgres;

--
-- TOC entry 232 (class 1255 OID 33225)
-- Name: vw_table_modify_pct(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION vw_table_modify_pct(first integer DEFAULT 1, last integer DEFAULT 0) RETURNS TABLE(table_id integer, ins_pct numeric, upd_pct numeric, del_pct numeric)
    LANGUAGE sql
    AS $_$
SELECT
table_id
,CAST(n_tup_ins AS numeric) / (n_tup_ins+n_tup_upd+n_tup_del) AS ins_pct
,CAST(n_tup_upd AS numeric) / (n_tup_ins+n_tup_upd+n_tup_del) AS upd_pct
,CAST(n_tup_del AS numeric) / (n_tup_ins+n_tup_upd+n_tup_del) AS del_pct
FROM pm_table_stat_diff($1,$2)
WHERE (n_tup_ins+n_tup_upd+n_tup_del) > 0;
$_$;


ALTER FUNCTION public.vw_table_modify_pct(first integer, last integer) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 161 (class 1259 OID 24998)
-- Name: bgwriter_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE bgwriter_stat (
    id bigint NOT NULL,
    hc_id integer NOT NULL,
    time_id integer NOT NULL,
    checkpoints_timed bigint,
    checkpoints_req bigint,
    buffers_checkpoint bigint,
    buffers_clean bigint,
    maxwritten_clean bigint,
    buffers_backend bigint,
    buffers_alloc bigint
);


ALTER TABLE public.bgwriter_stat OWNER TO postgres;

--
-- TOC entry 162 (class 1259 OID 25001)
-- Name: bgwriter_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE bgwriter_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bgwriter_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2163 (class 0 OID 0)
-- Dependencies: 162
-- Name: bgwriter_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE bgwriter_stat_id_seq OWNED BY bgwriter_stat.id;


--
-- TOC entry 163 (class 1259 OID 25003)
-- Name: database_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE database_name (
    id integer NOT NULL,
    hc_id integer NOT NULL,
    obj_oid integer NOT NULL,
    observable boolean DEFAULT false NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    db_name character varying NOT NULL,
    description text
);


ALTER TABLE public.database_name OWNER TO postgres;

--
-- TOC entry 164 (class 1259 OID 25011)
-- Name: database_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE database_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_name_id_seq OWNER TO postgres;

--
-- TOC entry 2164 (class 0 OID 0)
-- Dependencies: 164
-- Name: database_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE database_name_id_seq OWNED BY database_name.id;


--
-- TOC entry 165 (class 1259 OID 25013)
-- Name: database_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE database_stat (
    id bigint NOT NULL,
    dn_id integer NOT NULL,
    time_id integer NOT NULL,
    db_size bigint,
    xact_commit bigint,
    xact_rollback bigint,
    blks_fetch bigint,
    blks_hit bigint,
    tup_returned bigint,
    tup_fetched bigint,
    tup_inserted bigint,
    tup_updated bigint,
    tup_deleted bigint
);


ALTER TABLE public.database_stat OWNER TO postgres;

--
-- TOC entry 166 (class 1259 OID 25016)
-- Name: database_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE database_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2165 (class 0 OID 0)
-- Dependencies: 166
-- Name: database_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE database_stat_id_seq OWNED BY database_stat.id;


--
-- TOC entry 167 (class 1259 OID 25018)
-- Name: enum_sslmode; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE enum_sslmode (
    id integer NOT NULL,
    sslmode character varying NOT NULL,
    description text
);


ALTER TABLE public.enum_sslmode OWNER TO postgres;

--
-- TOC entry 168 (class 1259 OID 25024)
-- Name: enum_track_functions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE enum_track_functions (
    id integer NOT NULL,
    track_value character varying NOT NULL,
    description text
);


ALTER TABLE public.enum_track_functions OWNER TO postgres;

--
-- TOC entry 169 (class 1259 OID 25030)
-- Name: function_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE function_name (
    id integer NOT NULL,
    sn_id integer NOT NULL,
    pro_oid integer NOT NULL,
    proretset boolean NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    func_name character varying NOT NULL,
    prorettype character varying NOT NULL,
    prolang character varying NOT NULL,
    description text
);


ALTER TABLE public.function_name OWNER TO postgres;

--
-- TOC entry 170 (class 1259 OID 25037)
-- Name: function_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE function_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.function_name_id_seq OWNER TO postgres;

--
-- TOC entry 2166 (class 0 OID 0)
-- Dependencies: 170
-- Name: function_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE function_name_id_seq OWNED BY function_name.id;


--
-- TOC entry 171 (class 1259 OID 25039)
-- Name: function_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE function_stat (
    id bigint NOT NULL,
    fn_id integer NOT NULL,
    time_id integer NOT NULL,
    func_calls bigint,
    total_time bigint,
    self_time bigint
);


ALTER TABLE public.function_stat OWNER TO postgres;

--
-- TOC entry 172 (class 1259 OID 25042)
-- Name: function_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE function_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.function_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2167 (class 0 OID 0)
-- Dependencies: 172
-- Name: function_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE function_stat_id_seq OWNED BY function_stat.id;


--
-- TOC entry 173 (class 1259 OID 25044)
-- Name: host_cluster; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE host_cluster (
    id integer NOT NULL,
    track_function_id integer DEFAULT 1 NOT NULL,
    param_sslmode_id integer DEFAULT 3 NOT NULL,
    param_port integer DEFAULT 5432 NOT NULL,
    param_ip_address inet NOT NULL,
    is_master boolean DEFAULT true NOT NULL,
    observable boolean DEFAULT true NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    track_counts boolean DEFAULT true,
    param_maintenance_dbname character varying DEFAULT 'postgres'::character varying NOT NULL,
    param_user character varying DEFAULT 'postgres'::character varying NOT NULL,
    hostname character varying NOT NULL,
    pg_version character varying,
    pg_data_path character varying,
    fqdn character varying,
    param_password character varying,
    description text
);


ALTER TABLE public.host_cluster OWNER TO postgres;

--
-- TOC entry 174 (class 1259 OID 25059)
-- Name: host_cluster_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE host_cluster_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.host_cluster_id_seq OWNER TO postgres;

--
-- TOC entry 2168 (class 0 OID 0)
-- Dependencies: 174
-- Name: host_cluster_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE host_cluster_id_seq OWNED BY host_cluster.id;


--
-- TOC entry 175 (class 1259 OID 25061)
-- Name: index_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE index_name (
    id integer NOT NULL,
    tn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    is_unique boolean NOT NULL,
    is_primary boolean NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    idx_name character varying NOT NULL
);


ALTER TABLE public.index_name OWNER TO postgres;

--
-- TOC entry 176 (class 1259 OID 25068)
-- Name: index_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE index_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.index_name_id_seq OWNER TO postgres;

--
-- TOC entry 2169 (class 0 OID 0)
-- Dependencies: 176
-- Name: index_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_name_id_seq OWNED BY index_name.id;


--
-- TOC entry 177 (class 1259 OID 25070)
-- Name: index_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE index_stat (
    id bigint NOT NULL,
    in_id integer NOT NULL,
    time_id integer NOT NULL,
    idx_size bigint,
    idx_scan bigint,
    idx_tup_read bigint,
    idx_tup_fetch bigint,
    idx_blks_fetch bigint,
    idx_blks_hit bigint
);


ALTER TABLE public.index_stat OWNER TO postgres;

--
-- TOC entry 178 (class 1259 OID 25073)
-- Name: index_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE index_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.index_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2170 (class 0 OID 0)
-- Dependencies: 178
-- Name: index_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_stat_id_seq OWNED BY index_stat.id;


--
-- TOC entry 179 (class 1259 OID 25075)
-- Name: index_toast_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE index_toast_name (
    id integer NOT NULL,
    ttn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    tidx_name character varying NOT NULL
);


ALTER TABLE public.index_toast_name OWNER TO postgres;

--
-- TOC entry 180 (class 1259 OID 25082)
-- Name: index_toast_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE index_toast_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.index_toast_name_id_seq OWNER TO postgres;

--
-- TOC entry 2171 (class 0 OID 0)
-- Dependencies: 180
-- Name: index_toast_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_toast_name_id_seq OWNED BY index_toast_name.id;


--
-- TOC entry 181 (class 1259 OID 25084)
-- Name: index_toast_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE index_toast_stat (
    id bigint NOT NULL,
    tin_id integer NOT NULL,
    time_id integer NOT NULL,
    tidx_size bigint,
    tidx_scan bigint,
    tidx_tup_read bigint,
    tidx_tup_fetch bigint,
    tidx_blks_fetch bigint,
    tidx_blks_hit bigint
);


ALTER TABLE public.index_toast_stat OWNER TO postgres;

--
-- TOC entry 182 (class 1259 OID 25087)
-- Name: index_toast_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE index_toast_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.index_toast_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2172 (class 0 OID 0)
-- Dependencies: 182
-- Name: index_toast_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_toast_stat_id_seq OWNED BY index_toast_stat.id;


--
-- TOC entry 183 (class 1259 OID 25089)
-- Name: log_time; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE log_time (
    id integer NOT NULL,
    actual_time timestamp without time zone DEFAULT ('now'::text)::timestamp without time zone NOT NULL,
    hour_truncate timestamp without time zone DEFAULT date_trunc('hour'::text, ('now'::text)::timestamp without time zone) NOT NULL
);


ALTER TABLE public.log_time OWNER TO postgres;

--
-- TOC entry 184 (class 1259 OID 25094)
-- Name: log_time_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE log_time_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.log_time_id_seq OWNER TO postgres;

--
-- TOC entry 2173 (class 0 OID 0)
-- Dependencies: 184
-- Name: log_time_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE log_time_id_seq OWNED BY log_time.id;


--
-- TOC entry 185 (class 1259 OID 25096)
-- Name: schema_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE schema_name (
    id integer NOT NULL,
    dn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    observable boolean DEFAULT false NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    sch_name character varying NOT NULL,
    description text
);


ALTER TABLE public.schema_name OWNER TO postgres;

--
-- TOC entry 186 (class 1259 OID 25104)
-- Name: table_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE table_name (
    id integer NOT NULL,
    sn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    has_parent boolean DEFAULT false NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    tbl_name character varying NOT NULL
);


ALTER TABLE public.table_name OWNER TO postgres;

--
-- TOC entry 198 (class 1259 OID 33190)
-- Name: pm_master_table_lookup_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_master_table_lookup_view AS
    SELECT hc.id AS host_id, hc.hostname, dn.id AS db_id, dn.db_name, sn.id AS schema_id, sn.sch_name, tn.id AS table_id, tn.tbl_name FROM (((host_cluster hc JOIN database_name dn ON ((hc.id = dn.hc_id))) JOIN schema_name sn ON ((dn.id = sn.dn_id))) JOIN table_name tn ON ((sn.id = tn.sn_id))) WHERE ((((hc.is_master AND hc.observable) AND dn.observable) AND sn.observable) AND tn.alive);


ALTER TABLE public.pm_master_table_lookup_view OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 33210)
-- Name: pm_master_index_lookup_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_master_index_lookup_view AS
    SELECT mtl.table_id, idn.id AS index_id, idn.idx_name FROM (pm_master_table_lookup_view mtl JOIN index_name idn ON ((mtl.table_id = idn.tn_id))) WHERE idn.alive;


ALTER TABLE public.pm_master_index_lookup_view OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 33214)
-- Name: pm_index_size_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_index_size_view AS
    SELECT mil.index_id, __tmp_idx.idx_size FROM ((log_time lt JOIN (SELECT idn.id AS index_id, ids.idx_size, ids.time_id FROM (index_name idn JOIN index_stat ids ON ((idn.id = ids.in_id))) WHERE idn.alive) __tmp_idx ON ((lt.id = __tmp_idx.time_id))) JOIN pm_master_index_lookup_view mil ON ((mil.index_id = __tmp_idx.index_id))) WHERE (lt.hour_truncate = date_trunc('hour'::text, now()));


ALTER TABLE public.pm_index_size_view OWNER TO postgres;

--
-- TOC entry 187 (class 1259 OID 25112)
-- Name: table_va_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE table_va_stat (
    id bigint NOT NULL,
    tn_id integer NOT NULL,
    time_id integer NOT NULL,
    last_vacuum timestamp without time zone,
    last_autovacuum timestamp without time zone,
    last_analyze timestamp without time zone,
    last_autoanalyze timestamp without time zone
);


ALTER TABLE public.table_va_stat OWNER TO postgres;

--
-- TOC entry 188 (class 1259 OID 25115)
-- Name: pm_last_va_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_va_stat AS
    SELECT hc.hostname, dn.db_name, sn.sch_name, tn.tbl_name, (now() - (tvas.lv)::timestamp with time zone) AS last_vacuum, (now() - (tvas.lav)::timestamp with time zone) AS last_autovacuum, (now() - (tvas.la)::timestamp with time zone) AS last_analyze, (now() - (tvas.laa)::timestamp with time zone) AS last_autoanalyze FROM ((((host_cluster hc JOIN database_name dn ON ((hc.id = dn.hc_id))) JOIN schema_name sn ON ((dn.id = sn.dn_id))) JOIN table_name tn ON ((sn.id = tn.sn_id))) JOIN (SELECT table_va_stat.tn_id, max(table_va_stat.last_vacuum) AS lv, max(table_va_stat.last_autovacuum) AS lav, max(table_va_stat.last_analyze) AS la, max(table_va_stat.last_autoanalyze) AS laa FROM table_va_stat GROUP BY table_va_stat.tn_id) tvas ON ((tn.id = tvas.tn_id))) WHERE (sn.observable AND tn.alive);


ALTER TABLE public.pm_last_va_stat OWNER TO postgres;

--
-- TOC entry 199 (class 1259 OID 33200)
-- Name: pm_master_function_lookup_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_master_function_lookup_view AS
    SELECT hc.id AS host_id, hc.hostname, dn.id AS db_id, dn.db_name, sn.id AS schema_id, sn.sch_name, fn.id AS func_id, fn.func_name FROM (((host_cluster hc JOIN database_name dn ON ((hc.id = dn.hc_id))) JOIN schema_name sn ON ((dn.id = sn.dn_id))) JOIN function_name fn ON ((sn.id = fn.sn_id))) WHERE ((((hc.is_master AND hc.observable) AND dn.observable) AND sn.observable) AND fn.alive);


ALTER TABLE public.pm_master_function_lookup_view OWNER TO postgres;

--
-- TOC entry 189 (class 1259 OID 25120)
-- Name: table_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE table_stat (
    id bigint NOT NULL,
    tn_id integer NOT NULL,
    time_id integer NOT NULL,
    tbl_size bigint,
    tbl_tuples bigint,
    seq_scan bigint,
    seq_tup_read bigint,
    seq_tup_fetch bigint,
    n_tup_ins bigint,
    n_tup_upd bigint,
    n_tup_del bigint,
    n_tup_hot_upd bigint,
    n_live_tup bigint,
    n_dead_tup bigint,
    heap_blks_fetch bigint,
    heap_blks_hit bigint
);


ALTER TABLE public.table_stat OWNER TO postgres;

--
-- TOC entry 190 (class 1259 OID 25123)
-- Name: table_toast_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE table_toast_name (
    id integer NOT NULL,
    tn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    ttbl_name character varying NOT NULL
);


ALTER TABLE public.table_toast_name OWNER TO postgres;

--
-- TOC entry 191 (class 1259 OID 25130)
-- Name: table_toast_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE table_toast_stat (
    id bigint NOT NULL,
    ttn_id integer NOT NULL,
    time_id integer NOT NULL,
    ttbl_size bigint,
    seq_scan bigint,
    seq_tup_read bigint,
    seq_tup_fetch bigint,
    n_tup_ins bigint,
    n_tup_upd bigint,
    n_tup_del bigint,
    n_tup_hot_upd bigint,
    n_live_tup bigint,
    n_dead_tup bigint,
    heap_blks_fetch bigint,
    heap_blks_hit bigint
);


ALTER TABLE public.table_toast_stat OWNER TO postgres;

--
-- TOC entry 200 (class 1259 OID 33205)
-- Name: pm_table_size_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_table_size_view AS
    SELECT mtl.table_id, __tmp_tn.tbl_tuples, __tmp_tn.tbl_size, count(__tmp_idx.id) AS idx_num, sum(__tmp_idx.idx_size) AS total_idx_size, count(__tmp_ttn.id) AS toast_num, sum(__tmp_ttn.ttbl_size) AS total_toast_tbl_size, sum(__tmp_tidx.tidx_size) AS toast_idx_size FROM (((((log_time lt JOIN (SELECT tn.id, ts.tbl_tuples, ts.tbl_size, ts.time_id FROM (table_name tn JOIN table_stat ts ON ((tn.id = ts.tn_id)))) __tmp_tn ON ((lt.id = __tmp_tn.time_id))) JOIN pm_master_table_lookup_view mtl ON ((mtl.table_id = __tmp_tn.id))) LEFT JOIN (SELECT ttn.id, ttn.tn_id, tts.ttbl_size, tts.time_id FROM (table_toast_name ttn JOIN table_toast_stat tts ON ((ttn.id = tts.ttn_id))) WHERE ttn.alive) __tmp_ttn ON (((mtl.table_id = __tmp_ttn.tn_id) AND (lt.id = __tmp_ttn.time_id)))) LEFT JOIN (SELECT idn.id, idn.tn_id, ids.idx_size, ids.time_id FROM (index_name idn JOIN index_stat ids ON ((idn.id = ids.in_id))) WHERE idn.alive) __tmp_idx ON (((mtl.table_id = __tmp_idx.tn_id) AND (lt.id = __tmp_idx.time_id)))) LEFT JOIN (SELECT idtn.ttn_id, idts.tidx_size, idts.time_id FROM (index_toast_name idtn JOIN index_toast_stat idts ON ((idtn.id = idts.tin_id))) WHERE idtn.alive) __tmp_tidx ON (((__tmp_ttn.id = __tmp_tidx.ttn_id) AND (lt.id = __tmp_tidx.time_id)))) WHERE (lt.id = (SELECT log_time.id FROM log_time WHERE (log_time.hour_truncate = date_trunc('hour'::text, now())))) GROUP BY mtl.table_id, __tmp_tn.tbl_tuples, __tmp_tn.tbl_size;


ALTER TABLE public.pm_table_size_view OWNER TO postgres;

--
-- TOC entry 192 (class 1259 OID 25138)
-- Name: schema_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE schema_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.schema_name_id_seq OWNER TO postgres;

--
-- TOC entry 2174 (class 0 OID 0)
-- Dependencies: 192
-- Name: schema_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schema_name_id_seq OWNED BY schema_name.id;


--
-- TOC entry 193 (class 1259 OID 25140)
-- Name: table_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE table_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_name_id_seq OWNER TO postgres;

--
-- TOC entry 2175 (class 0 OID 0)
-- Dependencies: 193
-- Name: table_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_name_id_seq OWNED BY table_name.id;


--
-- TOC entry 194 (class 1259 OID 25142)
-- Name: table_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE table_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2176 (class 0 OID 0)
-- Dependencies: 194
-- Name: table_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_stat_id_seq OWNED BY table_stat.id;


--
-- TOC entry 195 (class 1259 OID 25144)
-- Name: table_toast_name_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE table_toast_name_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_toast_name_id_seq OWNER TO postgres;

--
-- TOC entry 2177 (class 0 OID 0)
-- Dependencies: 195
-- Name: table_toast_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_toast_name_id_seq OWNED BY table_toast_name.id;


--
-- TOC entry 196 (class 1259 OID 25146)
-- Name: table_toast_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE table_toast_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_toast_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2178 (class 0 OID 0)
-- Dependencies: 196
-- Name: table_toast_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_toast_stat_id_seq OWNED BY table_toast_stat.id;


--
-- TOC entry 197 (class 1259 OID 25148)
-- Name: table_va_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE table_va_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.table_va_stat_id_seq OWNER TO postgres;

--
-- TOC entry 2179 (class 0 OID 0)
-- Dependencies: 197
-- Name: table_va_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_va_stat_id_seq OWNED BY table_va_stat.id;


--
-- TOC entry 2013 (class 2604 OID 25150)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY bgwriter_stat ALTER COLUMN id SET DEFAULT nextval('bgwriter_stat_id_seq'::regclass);


--
-- TOC entry 2016 (class 2604 OID 25151)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_name ALTER COLUMN id SET DEFAULT nextval('database_name_id_seq'::regclass);


--
-- TOC entry 2017 (class 2604 OID 25152)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_stat ALTER COLUMN id SET DEFAULT nextval('database_stat_id_seq'::regclass);


--
-- TOC entry 2019 (class 2604 OID 25153)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_name ALTER COLUMN id SET DEFAULT nextval('function_name_id_seq'::regclass);


--
-- TOC entry 2020 (class 2604 OID 25154)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_stat ALTER COLUMN id SET DEFAULT nextval('function_stat_id_seq'::regclass);


--
-- TOC entry 2030 (class 2604 OID 25155)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY host_cluster ALTER COLUMN id SET DEFAULT nextval('host_cluster_id_seq'::regclass);


--
-- TOC entry 2032 (class 2604 OID 25156)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_name ALTER COLUMN id SET DEFAULT nextval('index_name_id_seq'::regclass);


--
-- TOC entry 2033 (class 2604 OID 25157)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_stat ALTER COLUMN id SET DEFAULT nextval('index_stat_id_seq'::regclass);


--
-- TOC entry 2035 (class 2604 OID 25158)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_name ALTER COLUMN id SET DEFAULT nextval('index_toast_name_id_seq'::regclass);


--
-- TOC entry 2036 (class 2604 OID 25159)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_stat ALTER COLUMN id SET DEFAULT nextval('index_toast_stat_id_seq'::regclass);


--
-- TOC entry 2039 (class 2604 OID 25160)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY log_time ALTER COLUMN id SET DEFAULT nextval('log_time_id_seq'::regclass);


--
-- TOC entry 2042 (class 2604 OID 25161)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schema_name ALTER COLUMN id SET DEFAULT nextval('schema_name_id_seq'::regclass);


--
-- TOC entry 2045 (class 2604 OID 25162)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_name ALTER COLUMN id SET DEFAULT nextval('table_name_id_seq'::regclass);


--
-- TOC entry 2047 (class 2604 OID 25163)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_stat ALTER COLUMN id SET DEFAULT nextval('table_stat_id_seq'::regclass);


--
-- TOC entry 2049 (class 2604 OID 25164)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_name ALTER COLUMN id SET DEFAULT nextval('table_toast_name_id_seq'::regclass);


--
-- TOC entry 2050 (class 2604 OID 25165)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_stat ALTER COLUMN id SET DEFAULT nextval('table_toast_stat_id_seq'::regclass);


--
-- TOC entry 2046 (class 2604 OID 25166)
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_va_stat ALTER COLUMN id SET DEFAULT nextval('table_va_stat_id_seq'::regclass);


--
-- TOC entry 2052 (class 2606 OID 25168)
-- Name: bgwriter_stat_hc_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_hc_id_time_id_key UNIQUE (hc_id, time_id);


--
-- TOC entry 2054 (class 2606 OID 25170)
-- Name: bgwriter_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2056 (class 2606 OID 25172)
-- Name: database_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY database_name
    ADD CONSTRAINT database_name_pkey PRIMARY KEY (id);


--
-- TOC entry 2058 (class 2606 OID 25174)
-- Name: database_stat_dn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_dn_id_time_id_key UNIQUE (dn_id, time_id);


--
-- TOC entry 2060 (class 2606 OID 25176)
-- Name: database_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2072 (class 2606 OID 25178)
-- Name: dbhost_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT dbhost_pkey PRIMARY KEY (id);


--
-- TOC entry 2062 (class 2606 OID 25180)
-- Name: enum_sslmode_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY enum_sslmode
    ADD CONSTRAINT enum_sslmode_pkey PRIMARY KEY (id);


--
-- TOC entry 2064 (class 2606 OID 25182)
-- Name: enum_track_functions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY enum_track_functions
    ADD CONSTRAINT enum_track_functions_pkey PRIMARY KEY (id);


--
-- TOC entry 2066 (class 2606 OID 25184)
-- Name: function_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY function_name
    ADD CONSTRAINT function_name_pkey PRIMARY KEY (id);


--
-- TOC entry 2068 (class 2606 OID 25186)
-- Name: function_stat_fn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_fn_id_time_id_key UNIQUE (fn_id, time_id);


--
-- TOC entry 2070 (class 2606 OID 25188)
-- Name: function_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2074 (class 2606 OID 25190)
-- Name: host_cluster_fqdn_param_port_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT host_cluster_fqdn_param_port_key UNIQUE (fqdn, param_port);


--
-- TOC entry 2076 (class 2606 OID 25192)
-- Name: host_cluster_ip_address_pg_data_path_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT host_cluster_ip_address_pg_data_path_key UNIQUE (param_ip_address, pg_data_path);


--
-- TOC entry 2078 (class 2606 OID 25194)
-- Name: host_cluster_param_ip_address_param_port_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT host_cluster_param_ip_address_param_port_key UNIQUE (param_ip_address, param_port);


--
-- TOC entry 2080 (class 2606 OID 25196)
-- Name: index_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_name
    ADD CONSTRAINT index_name_pkey PRIMARY KEY (id);


--
-- TOC entry 2083 (class 2606 OID 25198)
-- Name: index_stat_in_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_stat_in_id_time_id_key UNIQUE (in_id, time_id);


--
-- TOC entry 2085 (class 2606 OID 25200)
-- Name: index_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2087 (class 2606 OID 25202)
-- Name: index_toast_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_toast_name
    ADD CONSTRAINT index_toast_name_pkey PRIMARY KEY (id);


--
-- TOC entry 2089 (class 2606 OID 25204)
-- Name: index_toast_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2091 (class 2606 OID 25206)
-- Name: index_toast_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_tn_id_time_id_key UNIQUE (tin_id, time_id);


--
-- TOC entry 2094 (class 2606 OID 25208)
-- Name: log_time_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY log_time
    ADD CONSTRAINT log_time_pkey PRIMARY KEY (id);


--
-- TOC entry 2097 (class 2606 OID 25210)
-- Name: schema_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY schema_name
    ADD CONSTRAINT schema_name_pkey PRIMARY KEY (id);


--
-- TOC entry 2099 (class 2606 OID 25212)
-- Name: table_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_name
    ADD CONSTRAINT table_name_pkey PRIMARY KEY (id);


--
-- TOC entry 2105 (class 2606 OID 25214)
-- Name: table_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2107 (class 2606 OID 25216)
-- Name: table_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_stat_tn_id_time_id_key UNIQUE (tn_id, time_id);


--
-- TOC entry 2109 (class 2606 OID 25218)
-- Name: table_toast_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_toast_name
    ADD CONSTRAINT table_toast_name_pkey PRIMARY KEY (id);


--
-- TOC entry 2111 (class 2606 OID 25220)
-- Name: table_toast_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2113 (class 2606 OID 25222)
-- Name: table_toast_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_tn_id_time_id_key UNIQUE (ttn_id, time_id);


--
-- TOC entry 2101 (class 2606 OID 25224)
-- Name: table_va_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_pkey PRIMARY KEY (id);


--
-- TOC entry 2103 (class 2606 OID 25226)
-- Name: table_va_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_tn_id_time_id_key UNIQUE (tn_id, time_id);


--
-- TOC entry 2081 (class 1259 OID 25227)
-- Name: index_name_tn_id_idx_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX index_name_tn_id_idx_name_idx ON index_name USING btree (tn_id, idx_name);


--
-- TOC entry 2092 (class 1259 OID 25228)
-- Name: log_time_hour_truncate_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX log_time_hour_truncate_idx ON log_time USING btree (hour_truncate);


--
-- TOC entry 2095 (class 1259 OID 25229)
-- Name: schema_name_dn_id_sch_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX schema_name_dn_id_sch_name_idx ON schema_name USING btree (dn_id, sch_name);


--
-- TOC entry 2143 (class 2620 OID 25230)
-- Name: remove_databases_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_databases_cascade AFTER UPDATE ON host_cluster FOR EACH ROW EXECUTE PROCEDURE remove_databases();


--
-- TOC entry 2147 (class 2620 OID 25231)
-- Name: remove_functions_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_functions_cascade AFTER UPDATE ON schema_name FOR EACH ROW EXECUTE PROCEDURE remove_functions();


--
-- TOC entry 2153 (class 2620 OID 25232)
-- Name: remove_index_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_index_cascade AFTER UPDATE ON table_toast_name FOR EACH ROW EXECUTE PROCEDURE remove_toas_indexes();


--
-- TOC entry 2150 (class 2620 OID 25233)
-- Name: remove_indexes_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_indexes_cascade AFTER UPDATE ON table_name FOR EACH ROW EXECUTE PROCEDURE remove_indexes();


--
-- TOC entry 2139 (class 2620 OID 25234)
-- Name: remove_schemas_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_schemas_cascade AFTER UPDATE ON database_name FOR EACH ROW EXECUTE PROCEDURE remove_schemas();


--
-- TOC entry 2148 (class 2620 OID 25235)
-- Name: remove_tables_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_tables_cascade AFTER UPDATE ON schema_name FOR EACH ROW EXECUTE PROCEDURE remove_tables();


--
-- TOC entry 2151 (class 2620 OID 25236)
-- Name: remove_toast_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_toast_cascade AFTER UPDATE ON table_name FOR EACH ROW EXECUTE PROCEDURE remove_toast_tables();


--
-- TOC entry 2144 (class 2620 OID 25237)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON host_cluster FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2140 (class 2620 OID 25238)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON database_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2149 (class 2620 OID 25239)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON schema_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2152 (class 2620 OID 25240)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON table_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2142 (class 2620 OID 25241)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON function_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2145 (class 2620 OID 25242)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON index_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2146 (class 2620 OID 25243)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON index_toast_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2154 (class 2620 OID 25244)
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON table_toast_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- TOC entry 2141 (class 2620 OID 25245)
-- Name: suspend_schemas_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER suspend_schemas_cascade AFTER UPDATE ON database_name FOR EACH ROW EXECUTE PROCEDURE suspend_schemas();


--
-- TOC entry 2114 (class 2606 OID 25246)
-- Name: bgwriter_stat_hc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_hc_id_fkey FOREIGN KEY (hc_id) REFERENCES host_cluster(id) ON DELETE CASCADE;


--
-- TOC entry 2115 (class 2606 OID 25251)
-- Name: bgwriter_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2116 (class 2606 OID 25256)
-- Name: database_name_hc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_name
    ADD CONSTRAINT database_name_hc_id_fkey FOREIGN KEY (hc_id) REFERENCES host_cluster(id) ON DELETE CASCADE;


--
-- TOC entry 2117 (class 2606 OID 25261)
-- Name: database_stat_dn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_dn_id_fkey FOREIGN KEY (dn_id) REFERENCES database_name(id) ON DELETE CASCADE;


--
-- TOC entry 2118 (class 2606 OID 25266)
-- Name: database_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2119 (class 2606 OID 25271)
-- Name: function_name_sn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_name
    ADD CONSTRAINT function_name_sn_id_fkey FOREIGN KEY (sn_id) REFERENCES schema_name(id) ON DELETE CASCADE;


--
-- TOC entry 2120 (class 2606 OID 25276)
-- Name: function_stat_fn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_fn_id_fkey FOREIGN KEY (fn_id) REFERENCES function_name(id) ON DELETE CASCADE;


--
-- TOC entry 2121 (class 2606 OID 25281)
-- Name: function_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2122 (class 2606 OID 25286)
-- Name: host_cluster_sslmode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT host_cluster_sslmode_id_fkey FOREIGN KEY (param_sslmode_id) REFERENCES enum_sslmode(id);


--
-- TOC entry 2123 (class 2606 OID 25291)
-- Name: host_cluster_track_function_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT host_cluster_track_function_id_fkey FOREIGN KEY (track_function_id) REFERENCES enum_track_functions(id);


--
-- TOC entry 2125 (class 2606 OID 25296)
-- Name: index_basic_stat_in_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_basic_stat_in_id_fkey FOREIGN KEY (in_id) REFERENCES index_name(id) ON DELETE CASCADE;


--
-- TOC entry 2126 (class 2606 OID 25301)
-- Name: index_basic_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_basic_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2124 (class 2606 OID 25306)
-- Name: index_name_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_name
    ADD CONSTRAINT index_name_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- TOC entry 2127 (class 2606 OID 25311)
-- Name: index_toast_name_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_name
    ADD CONSTRAINT index_toast_name_tn_id_fkey FOREIGN KEY (ttn_id) REFERENCES table_toast_name(id) ON DELETE CASCADE;


--
-- TOC entry 2128 (class 2606 OID 25316)
-- Name: index_toast_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2129 (class 2606 OID 25321)
-- Name: index_toast_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_tn_id_fkey FOREIGN KEY (tin_id) REFERENCES index_toast_name(id) ON DELETE CASCADE;


--
-- TOC entry 2130 (class 2606 OID 25326)
-- Name: schema_name_dn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schema_name
    ADD CONSTRAINT schema_name_dn_id_fkey FOREIGN KEY (dn_id) REFERENCES database_name(id) ON DELETE CASCADE;


--
-- TOC entry 2134 (class 2606 OID 25331)
-- Name: table_basic_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_basic_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2135 (class 2606 OID 25336)
-- Name: table_basic_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_basic_stat_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- TOC entry 2131 (class 2606 OID 25341)
-- Name: table_name_sn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_name
    ADD CONSTRAINT table_name_sn_id_fkey FOREIGN KEY (sn_id) REFERENCES schema_name(id) ON DELETE CASCADE;


--
-- TOC entry 2136 (class 2606 OID 25346)
-- Name: table_toast_name_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_name
    ADD CONSTRAINT table_toast_name_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- TOC entry 2137 (class 2606 OID 25351)
-- Name: table_toast_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2138 (class 2606 OID 25356)
-- Name: table_toast_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_tn_id_fkey FOREIGN KEY (ttn_id) REFERENCES table_toast_name(id) ON DELETE CASCADE;


--
-- TOC entry 2132 (class 2606 OID 25361)
-- Name: table_va_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- TOC entry 2133 (class 2606 OID 25366)
-- Name: table_va_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- TOC entry 2161 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2013-09-06 16:24:32 PDT

--
-- PostgreSQL database dump complete
--

