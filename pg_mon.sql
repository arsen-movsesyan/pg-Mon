--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: pg_mon; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE pg_mon WITH TEMPLATE = template0 ENCODING = 'SQL_ASCII' LC_COLLATE = 'C' LC_CTYPE = 'C';


ALTER DATABASE pg_mon OWNER TO postgres;

\connect pg_mon

SET statement_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: track_functions_state; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE track_functions_state AS ENUM (
    'none',
    'pl',
    'all'
);


ALTER TYPE public.track_functions_state OWNER TO postgres;

--
-- Name: get_conn_string(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION get_conn_string(hc_id integer) RETURNS character varying
    LANGUAGE plpgsql
    AS $$DECLARE
	conn_string VARCHAR:='';
	single_param VARCHAR;
BEGIN
	FOR single_param IN SELECT unnest(conn_param) FROM host_cluster WHERE id=hc_id LOOP
		conn_string:=conn_string||single_param||' ';
	END LOOP;
	RETURN trim(conn_string);
END$$;


ALTER FUNCTION public.get_conn_string(hc_id integer) OWNER TO postgres;

--
-- Name: get_conn_string(integer, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION get_conn_string(hc_id integer, db_name character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $$DECLARE
	conn_string VARCHAR:='';
	single_param VARCHAR;
BEGIN
	FOR single_param IN SELECT unnest(conn_param) FROM host_cluster WHERE id=hc_id LOOP
		IF single_param = 'dbname=postgres' THEN
			conn_string:=conn_string||'dbname='||db_name||' ';
		ELSE
			conn_string:=conn_string||single_param||' ';
		END IF;
	END LOOP;
	RETURN trim(conn_string);
END$$;


ALTER FUNCTION public.get_conn_string(hc_id integer, db_name character varying) OWNER TO postgres;

--
-- Name: get_conn_string(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION get_conn_string(hc_id integer, dn_id integer) RETURNS character varying
    LANGUAGE plpgsql
    AS $$DECLARE
	conn_string VARCHAR:='';
	single_param VARCHAR;
	d_n VARCHAR;
BEGIN
	FOR single_param IN SELECT unnest(conn_param) FROM host_cluster WHERE id=hc_id LOOP
		IF single_param = 'dbname=postgres' THEN
			SELECT INTO d_n db_name FROM database_name WHERE id=dn_id;
			conn_string:=conn_string||'dbname='||d_n||' ';
		ELSE
			conn_string:=conn_string||single_param||' ';
		END IF;
	END LOOP;
	RETURN trim(conn_string);
END$$;


ALTER FUNCTION public.get_conn_string(hc_id integer, dn_id integer) OWNER TO postgres;

--
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
-- Name: remove_toas_indexes(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION remove_toas_indexes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE index_toast_name SET alive='f' WHERE NEW.alive='f' AND tn_id=OLD.tn_id AND alive='t';
	RETURN NEW;
END$$;


ALTER FUNCTION public.remove_toas_indexes() OWNER TO postgres;

--
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

SET default_tablespace = '';

SET default_with_oids = false;

--
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
-- Name: bgwriter_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE bgwriter_stat_id_seq OWNED BY bgwriter_stat.id;


--
-- Name: database_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE database_name (
    id integer NOT NULL,
    hc_id integer NOT NULL,
    obj_oid integer NOT NULL,
    observable boolean NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    db_name character varying NOT NULL,
    description text
);


ALTER TABLE public.database_name OWNER TO postgres;

--
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
-- Name: database_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE database_name_id_seq OWNED BY database_name.id;


--
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
-- Name: database_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE database_stat_id_seq OWNED BY database_stat.id;


--
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
-- Name: function_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE function_name_id_seq OWNED BY function_name.id;


--
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
-- Name: function_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE function_stat_id_seq OWNED BY function_stat.id;


--
-- Name: host_cluster; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE host_cluster (
    id integer NOT NULL,
    ip_address inet NOT NULL,
    hostname character varying NOT NULL,
    is_master boolean NOT NULL,
    observable boolean DEFAULT true NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    track_counts boolean,
    track_functions track_functions_state,
    pg_version character varying,
    pg_data_path character varying,
    fqdn character varying,
    spec_comments character varying,
    conn_param character varying[]
);


ALTER TABLE public.host_cluster OWNER TO postgres;

--
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
-- Name: host_cluster_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE host_cluster_id_seq OWNED BY host_cluster.id;


--
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
-- Name: index_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_name_id_seq OWNED BY index_name.id;


--
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
-- Name: index_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_stat_id_seq OWNED BY index_stat.id;


--
-- Name: index_toast_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE index_toast_name (
    id integer NOT NULL,
    tn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    idx_name character varying NOT NULL
);


ALTER TABLE public.index_toast_name OWNER TO postgres;

--
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
-- Name: index_toast_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_toast_name_id_seq OWNED BY index_toast_name.id;


--
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
-- Name: index_toast_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE index_toast_stat_id_seq OWNED BY index_toast_stat.id;


--
-- Name: log_time; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE log_time (
    id integer NOT NULL,
    actual_time timestamp without time zone DEFAULT ('now'::text)::timestamp without time zone NOT NULL,
    hour_truncate timestamp without time zone DEFAULT date_trunc('hour'::text, ('now'::text)::timestamp without time zone) NOT NULL
);


ALTER TABLE public.log_time OWNER TO postgres;

--
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
-- Name: log_time_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE log_time_id_seq OWNED BY log_time.id;


--
-- Name: pm_last_hour_bgwriter_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_hour_bgwriter_stat AS
    SELECT hc.hostname, hc.ip_address, hc.is_master,
    (last.checkpoints_timed - first.checkpoints_timed) AS checkpoints_timed,
    (last.checkpoints_req - first.checkpoints_req) AS checkpoints_req,
    (last.buffers_checkpoint - first.buffers_checkpoint) AS buffers_checkpoint,
    (last.buffers_clean - first.buffers_clean) AS buffers_clean,
    (last.maxwritten_clean - first.maxwritten_clean) AS maxwritten_clean,
    (last.buffers_backend - first.buffers_backend) AS buffers_backend,
    (last.buffers_alloc - first.buffers_alloc) AS buffers_alloc
    FROM ((((host_cluster hc
    JOIN bgwriter_stat first ON ((hc.id = first.hc_id)))
    JOIN bgwriter_stat last ON ((hc.id = last.hc_id)))
    JOIN log_time a ON ((a.id = first.time_id)))
    JOIN log_time b ON ((b.id = last.time_id)))
    WHERE (((hc.alive
    AND hc.observable)
    AND (a.hour_truncate = (date_trunc('hour'::text, (now() - '01:00:00'::interval)))::timestamp without time zone))
    AND (b.hour_truncate = (date_trunc('hour'::text, now()))::timestamp without time zone));


ALTER TABLE public.pm_last_hour_bgwriter_stat OWNER TO postgres;

--
-- Name: pm_last_hour_database_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_hour_database_stat AS
    SELECT hc.hostname, hc.ip_address, hc.is_master, dn.db_name,
    (last.db_size - first.db_size) AS db_size,
    (last.xact_commit - first.xact_commit) AS xact_commit,
    (last.xact_rollback - first.xact_rollback) AS xact_rollback,
    (last.blks_fetch - first.blks_fetch) AS blks_fetch,
    (last.blks_hit - first.blks_hit) AS blks_hit,
    (last.tup_returned - first.tup_returned) AS tup_returned,
    (last.tup_fetched - first.tup_fetched) AS tup_fetched,
    (last.tup_inserted - first.tup_inserted) AS tup_inserted,
    (last.tup_updated - first.tup_updated) AS tup_updated,
    (last.tup_deleted - first.tup_deleted) AS tup_deleted
    FROM (((((host_cluster hc
    JOIN database_name dn ON ((hc.id = dn.hc_id)))
    JOIN database_stat first ON ((dn.id = first.dn_id)))
    JOIN database_stat last ON ((dn.id = last.dn_id)))
    JOIN log_time a ON ((a.id = first.time_id)))
    JOIN log_time b ON ((b.id = last.time_id)))
    WHERE ((((hc.observable
    AND dn.alive)
    AND dn.observable)
    AND (a.hour_truncate = (date_trunc('hour'::text, (now() - '01:00:00'::interval)))::timestamp without time zone))
    AND (b.hour_truncate = (date_trunc('hour'::text, now()))::timestamp without time zone));


ALTER TABLE public.pm_last_hour_database_stat OWNER TO postgres;

--
-- Name: schema_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE schema_name (
    id integer NOT NULL,
    dn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    observable boolean NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    sch_name character varying NOT NULL,
    description text
);


ALTER TABLE public.schema_name OWNER TO postgres;

--
-- Name: pm_last_hour_function_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_hour_function_stat AS
    SELECT hc.hostname, hc.ip_address, hc.is_master, dn.db_name, sn.sch_name, fn.func_name,
    (last.func_calls - first.func_calls) AS func_calls,
    (last.total_time - first.total_time) AS total_time,
    (last.self_time - first.self_time) AS self_time
    FROM (((((((host_cluster hc
    JOIN database_name dn ON ((hc.id = dn.hc_id)))
    JOIN schema_name sn ON ((dn.id = sn.dn_id)))
    JOIN function_name fn ON ((sn.id = fn.sn_id)))
    JOIN function_stat first ON ((fn.id = first.fn_id)))
    JOIN function_stat last ON ((fn.id = last.fn_id)))
    JOIN log_time a ON ((a.id = first.time_id)))
    JOIN log_time b ON ((b.id = last.time_id)))
    WHERE (((((hc.observable
    AND dn.observable)
    AND sn.observable)
    AND fn.alive)
    AND (a.hour_truncate = (date_trunc('hour'::text, (now() - '01:00:00'::interval)))::timestamp without time zone))
    AND (b.hour_truncate = (date_trunc('hour'::text, now()))::timestamp without time zone));


ALTER TABLE public.pm_last_hour_function_stat OWNER TO postgres;

--
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
-- Name: pm_last_hour_index_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_hour_index_stat AS
    SELECT hc.hostname, hc.ip_address, hc.is_master, dn.db_name, sn.sch_name, tn.tbl_name, ind.idx_name,
    (last.idx_size - first.idx_size) AS idx_size,
    (last.idx_scan - first.idx_scan) AS idx_scan,
    (last.idx_tup_read - first.idx_tup_read) AS idx_tup_read,
    (last.idx_tup_fetch - first.idx_tup_fetch) AS idx_tup_fetch,
    (last.idx_blks_fetch - first.idx_blks_fetch) AS idx_blks_fetch,
    (last.idx_blks_hit - first.idx_blks_hit) AS idx_blks_hit
    FROM ((((((((host_cluster hc
    JOIN database_name dn ON ((hc.id = dn.hc_id)))
    JOIN schema_name sn ON ((dn.id = sn.dn_id)))
    JOIN table_name tn ON ((sn.id = tn.sn_id)))
    JOIN index_name ind ON ((tn.id = ind.tn_id)))
    JOIN index_stat first ON ((ind.id = first.in_id)))
    JOIN index_stat last ON ((ind.id = last.in_id)))
    JOIN log_time a ON ((a.id = first.time_id)))
    JOIN log_time b ON ((b.id = last.time_id)))
    WHERE (((((hc.observable
    AND dn.observable)
    AND sn.observable)
    AND ind.alive)
    AND (a.hour_truncate = (date_trunc('hour'::text, (now() - '01:00:00'::interval)))::timestamp without time zone))
    AND (b.hour_truncate = (date_trunc('hour'::text, now()))::timestamp without time zone));


ALTER TABLE public.pm_last_hour_index_stat OWNER TO postgres;

--
-- Name: table_toast_name; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE table_toast_name (
    id integer NOT NULL,
    tn_id integer NOT NULL,
    obj_oid integer NOT NULL,
    alive boolean DEFAULT true NOT NULL,
    tbl_name character varying NOT NULL
);


ALTER TABLE public.table_toast_name OWNER TO postgres;

--
-- Name: pm_last_hour_index_toast_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_hour_index_toast_stat AS
    SELECT hc.hostname, hc.ip_address, hc.is_master, dn.db_name, sn.sch_name, tn.tbl_name, ttn.tbl_name AS toast_tbl_name, tind.idx_name AS toast_idx_name,
    (last.tidx_size - first.tidx_size) AS tidx_size,
    (last.tidx_scan - first.tidx_scan) AS tidx_scan,
    (last.tidx_tup_read - first.tidx_tup_read) AS tidx_tup_read,
    (last.tidx_tup_fetch - first.tidx_tup_fetch) AS tidx_tup_fetch,
    (last.tidx_blks_fetch - first.tidx_blks_fetch) AS tidx_blks_fetch,
    (last.tidx_blks_hit - first.tidx_blks_hit) AS tidx_blks_hit
    FROM (((((((((host_cluster hc
    JOIN database_name dn ON ((hc.id = dn.hc_id)))
    JOIN schema_name sn ON ((dn.id = sn.dn_id)))
    JOIN table_name tn ON ((sn.id = tn.sn_id)))
    JOIN table_toast_name ttn ON ((tn.id = ttn.tn_id)))
    JOIN index_toast_name tind ON ((ttn.id = tind.tn_id)))
    JOIN index_toast_stat first ON ((tind.id = first.tin_id)))
    JOIN index_toast_stat last ON ((tind.id = last.tin_id)))
    JOIN log_time a ON ((a.id = first.time_id)))
    JOIN log_time b ON ((b.id = last.time_id)))
    WHERE (((((hc.observable
    AND dn.observable)
    AND sn.observable)
    AND tind.alive)
    AND (a.hour_truncate = (date_trunc('hour'::text, (now() - '01:00:00'::interval)))::timestamp without time zone))
    AND (b.hour_truncate = (date_trunc('hour'::text, now()))::timestamp without time zone));


ALTER TABLE public.pm_last_hour_index_toast_stat OWNER TO postgres;

--
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
-- Name: pm_last_hour_table_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_hour_table_stat AS
    SELECT hc.hostname, hc.ip_address, hc.is_master, dn.db_name, sn.sch_name, tn.tbl_name,
    (last.tbl_size - first.tbl_size) AS tbl_size,
    (last.tbl_tuples - first.tbl_tuples) AS tbl_tuples,
    (last.seq_scan - first.seq_scan) AS seq_scan,
    (last.seq_tup_read - first.seq_tup_read) AS seq_tup_read,
    (last.seq_tup_fetch - first.seq_tup_fetch) AS seq_tup_fetch,
    (last.n_tup_ins - first.n_tup_ins) AS n_tup_ins,
    (last.n_tup_upd - first.n_tup_upd) AS n_tup_upd,
    (last.n_tup_del - first.n_tup_del) AS n_tup_del,
    (last.n_tup_hot_upd - first.n_tup_hot_upd) AS n_tup_hot_upd,
    (last.n_live_tup - first.n_live_tup) AS n_live_tup,
    (last.n_dead_tup - first.n_dead_tup) AS n_dead_tup,
    (last.heap_blks_fetch - first.heap_blks_fetch) AS heap_blks_fetch,
    (last.heap_blks_hit - first.heap_blks_hit) AS heap_blks_hit
    FROM (((((((host_cluster hc
    JOIN database_name dn ON ((hc.id = dn.hc_id)))
    JOIN schema_name sn ON ((dn.id = sn.dn_id)))
    JOIN table_name tn ON ((sn.id = tn.sn_id)))
    JOIN table_stat first ON ((tn.id = first.tn_id)))
    JOIN table_stat last ON ((tn.id = last.tn_id)))
    JOIN log_time a ON ((a.id = first.time_id)))
    JOIN log_time b ON ((b.id = last.time_id)))
    WHERE (((((hc.observable
    AND dn.observable)
    AND sn.observable)
    AND tn.alive)
    AND (a.hour_truncate = (date_trunc('hour'::text, (now() - '01:00:00'::interval)))::timestamp without time zone))
    AND (b.hour_truncate = (date_trunc('hour'::text, now()))::timestamp without time zone));


ALTER TABLE public.pm_last_hour_table_stat OWNER TO postgres;

--
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
-- Name: pm_last_hour_table_toast_stat; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW pm_last_hour_table_toast_stat AS
    SELECT hc.hostname, hc.ip_address, hc.is_master, dn.db_name, sn.sch_name, tn.tbl_name, ttn.tbl_name AS toast_tbl_name,
    (last.ttbl_size - first.ttbl_size) AS ttbl_size,
    (last.seq_scan - first.seq_scan) AS seq_scan,
    (last.seq_tup_read - first.seq_tup_read) AS seq_tup_read,
    (last.seq_tup_fetch - first.seq_tup_fetch) AS seq_tup_fetch,
    (last.n_tup_ins - first.n_tup_ins) AS n_tup_ins,
    (last.n_tup_upd - first.n_tup_upd) AS n_tup_upd,
    (last.n_tup_del - first.n_tup_del) AS n_tup_del,
    (last.n_tup_hot_upd - first.n_tup_hot_upd) AS n_tup_hot_upd,
    (last.n_live_tup - first.n_live_tup) AS n_live_tup,
    (last.n_dead_tup - first.n_dead_tup) AS n_dead_tup,
    (last.heap_blks_fetch - first.heap_blks_fetch) AS heap_blks_fetch,
    (last.heap_blks_hit - first.heap_blks_hit)
    AS heap_blks_hit
    FROM ((((((((host_cluster hc
    JOIN database_name dn
    ON ((hc.id = dn.hc_id)))
    JOIN schema_name sn ON ((dn.id = sn.dn_id)))
    JOIN table_name tn ON ((sn.id = tn.sn_id)))
    JOIN table_toast_name ttn ON ((tn.id = ttn.tn_id)))
    JOIN table_toast_stat first ON ((ttn.id = first.ttn_id)))
    JOIN table_toast_stat last ON ((ttn.id = last.ttn_id)))
    JOIN log_time a ON ((a.id = first.time_id)))
    JOIN log_time b ON ((b.id = last.time_id)))
    WHERE (((((hc.observable
    AND dn.observable)
    AND sn.observable)
    AND ttn.alive)
    AND (a.hour_truncate = (date_trunc('hour'::text, (now() - '01:00:00'::interval)))::timestamp without time zone))
    AND (b.hour_truncate = (date_trunc('hour'::text, now()))::timestamp without time zone));


ALTER TABLE public.pm_last_hour_table_toast_stat OWNER TO postgres;

--
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
-- Name: schema_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE schema_name_id_seq OWNED BY schema_name.id;


--
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
-- Name: table_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_name_id_seq OWNED BY table_name.id;


--
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
-- Name: table_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_stat_id_seq OWNED BY table_stat.id;


--
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
-- Name: table_toast_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_toast_name_id_seq OWNED BY table_toast_name.id;


--
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
-- Name: table_toast_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_toast_stat_id_seq OWNED BY table_toast_stat.id;


--
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
-- Name: table_va_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE table_va_stat_id_seq OWNED BY table_va_stat.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY bgwriter_stat ALTER COLUMN id SET DEFAULT nextval('bgwriter_stat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_name ALTER COLUMN id SET DEFAULT nextval('database_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_stat ALTER COLUMN id SET DEFAULT nextval('database_stat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_name ALTER COLUMN id SET DEFAULT nextval('function_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_stat ALTER COLUMN id SET DEFAULT nextval('function_stat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY host_cluster ALTER COLUMN id SET DEFAULT nextval('host_cluster_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_name ALTER COLUMN id SET DEFAULT nextval('index_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_stat ALTER COLUMN id SET DEFAULT nextval('index_stat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_name ALTER COLUMN id SET DEFAULT nextval('index_toast_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_stat ALTER COLUMN id SET DEFAULT nextval('index_toast_stat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY log_time ALTER COLUMN id SET DEFAULT nextval('log_time_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schema_name ALTER COLUMN id SET DEFAULT nextval('schema_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_name ALTER COLUMN id SET DEFAULT nextval('table_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_stat ALTER COLUMN id SET DEFAULT nextval('table_stat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_name ALTER COLUMN id SET DEFAULT nextval('table_toast_name_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_stat ALTER COLUMN id SET DEFAULT nextval('table_toast_stat_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_va_stat ALTER COLUMN id SET DEFAULT nextval('table_va_stat_id_seq'::regclass);


--
-- Name: bgwriter_stat_hc_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_hc_id_time_id_key UNIQUE (hc_id, time_id);


--
-- Name: bgwriter_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_pkey PRIMARY KEY (id);


--
-- Name: database_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY database_name
    ADD CONSTRAINT database_name_pkey PRIMARY KEY (id);


--
-- Name: database_stat_dn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_dn_id_time_id_key UNIQUE (dn_id, time_id);


--
-- Name: database_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_pkey PRIMARY KEY (id);


--
-- Name: dbhost_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT dbhost_pkey PRIMARY KEY (id);


--
-- Name: function_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY function_name
    ADD CONSTRAINT function_name_pkey PRIMARY KEY (id);


--
-- Name: function_stat_fn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_fn_id_time_id_key UNIQUE (fn_id, time_id);


--
-- Name: function_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_pkey PRIMARY KEY (id);


--
-- Name: host_cluster_ip_address_pg_data_path_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY host_cluster
    ADD CONSTRAINT host_cluster_ip_address_pg_data_path_key UNIQUE (ip_address, pg_data_path);


--
-- Name: index_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_name
    ADD CONSTRAINT index_name_pkey PRIMARY KEY (id);


--
-- Name: index_stat_in_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_stat_in_id_time_id_key UNIQUE (in_id, time_id);


--
-- Name: index_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_stat_pkey PRIMARY KEY (id);


--
-- Name: index_toast_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_toast_name
    ADD CONSTRAINT index_toast_name_pkey PRIMARY KEY (id);


--
-- Name: index_toast_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_pkey PRIMARY KEY (id);


--
-- Name: index_toast_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_tn_id_time_id_key UNIQUE (tin_id, time_id);


--
-- Name: log_time_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY log_time
    ADD CONSTRAINT log_time_pkey PRIMARY KEY (id);


--
-- Name: schema_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY schema_name
    ADD CONSTRAINT schema_name_pkey PRIMARY KEY (id);


--
-- Name: table_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_name
    ADD CONSTRAINT table_name_pkey PRIMARY KEY (id);


--
-- Name: table_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_stat_pkey PRIMARY KEY (id);


--
-- Name: table_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_stat_tn_id_time_id_key UNIQUE (tn_id, time_id);


--
-- Name: table_toast_name_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_toast_name
    ADD CONSTRAINT table_toast_name_pkey PRIMARY KEY (id);


--
-- Name: table_toast_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_pkey PRIMARY KEY (id);


--
-- Name: table_toast_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_tn_id_time_id_key UNIQUE (ttn_id, time_id);


--
-- Name: table_va_stat_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_pkey PRIMARY KEY (id);


--
-- Name: table_va_stat_tn_id_time_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_tn_id_time_id_key UNIQUE (tn_id, time_id);


--
-- Name: index_name_tn_id_idx_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX index_name_tn_id_idx_name_idx ON index_name USING btree (tn_id, idx_name);


--
-- Name: log_time_hour_truncate_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX log_time_hour_truncate_idx ON log_time USING btree (hour_truncate);


--
-- Name: schema_name_dn_id_sch_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX schema_name_dn_id_sch_name_idx ON schema_name USING btree (dn_id, sch_name);


--
-- Name: remove_databases_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_databases_cascade AFTER UPDATE ON host_cluster FOR EACH ROW EXECUTE PROCEDURE remove_databases();


--
-- Name: remove_functions_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_functions_cascade AFTER UPDATE ON schema_name FOR EACH ROW EXECUTE PROCEDURE remove_functions();


--
-- Name: remove_index_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_index_cascade AFTER UPDATE ON table_toast_name FOR EACH ROW EXECUTE PROCEDURE remove_toas_indexes();


--
-- Name: remove_indexes_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_indexes_cascade AFTER UPDATE ON table_name FOR EACH ROW EXECUTE PROCEDURE remove_indexes();


--
-- Name: remove_schemas_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_schemas_cascade AFTER UPDATE ON database_name FOR EACH ROW EXECUTE PROCEDURE remove_schemas();


--
-- Name: remove_tables_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_tables_cascade AFTER UPDATE ON schema_name FOR EACH ROW EXECUTE PROCEDURE remove_tables();


--
-- Name: remove_toast_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_toast_cascade AFTER UPDATE ON table_name FOR EACH ROW EXECUTE PROCEDURE remove_toast_tables();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON host_cluster FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON database_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON schema_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON table_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON function_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON index_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON index_toast_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: restrict_to_alive; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER restrict_to_alive BEFORE UPDATE ON table_toast_name FOR EACH ROW EXECUTE PROCEDURE terminate_change();


--
-- Name: suspend_schemas_cascade; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER suspend_schemas_cascade AFTER UPDATE ON database_name FOR EACH ROW EXECUTE PROCEDURE suspend_schemas();


--
-- Name: bgwriter_stat_hc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_hc_id_fkey FOREIGN KEY (hc_id) REFERENCES host_cluster(id) ON DELETE CASCADE;


--
-- Name: bgwriter_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY bgwriter_stat
    ADD CONSTRAINT bgwriter_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: database_name_hc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_name
    ADD CONSTRAINT database_name_hc_id_fkey FOREIGN KEY (hc_id) REFERENCES host_cluster(id) ON DELETE CASCADE;


--
-- Name: database_stat_dn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_dn_id_fkey FOREIGN KEY (dn_id) REFERENCES database_name(id) ON DELETE CASCADE;


--
-- Name: database_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY database_stat
    ADD CONSTRAINT database_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: function_name_sn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_name
    ADD CONSTRAINT function_name_sn_id_fkey FOREIGN KEY (sn_id) REFERENCES schema_name(id) ON DELETE CASCADE;


--
-- Name: function_stat_fn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_fn_id_fkey FOREIGN KEY (fn_id) REFERENCES function_name(id) ON DELETE CASCADE;


--
-- Name: function_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY function_stat
    ADD CONSTRAINT function_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: index_basic_stat_in_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_basic_stat_in_id_fkey FOREIGN KEY (in_id) REFERENCES index_name(id) ON DELETE CASCADE;


--
-- Name: index_basic_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_stat
    ADD CONSTRAINT index_basic_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: index_name_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_name
    ADD CONSTRAINT index_name_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- Name: index_toast_name_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_name
    ADD CONSTRAINT index_toast_name_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_toast_name(id);


--
-- Name: index_toast_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: index_toast_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY index_toast_stat
    ADD CONSTRAINT index_toast_stat_tn_id_fkey FOREIGN KEY (tin_id) REFERENCES index_toast_name(id);


--
-- Name: schema_name_dn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY schema_name
    ADD CONSTRAINT schema_name_dn_id_fkey FOREIGN KEY (dn_id) REFERENCES database_name(id) ON DELETE CASCADE;


--
-- Name: table_basic_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_basic_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: table_basic_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_stat
    ADD CONSTRAINT table_basic_stat_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- Name: table_name_sn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_name
    ADD CONSTRAINT table_name_sn_id_fkey FOREIGN KEY (sn_id) REFERENCES schema_name(id) ON DELETE CASCADE;


--
-- Name: table_toast_name_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_name
    ADD CONSTRAINT table_toast_name_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- Name: table_toast_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: table_toast_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_toast_stat
    ADD CONSTRAINT table_toast_stat_tn_id_fkey FOREIGN KEY (ttn_id) REFERENCES table_toast_name(id);


--
-- Name: table_va_stat_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_time_id_fkey FOREIGN KEY (time_id) REFERENCES log_time(id) ON DELETE CASCADE;


--
-- Name: table_va_stat_tn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY table_va_stat
    ADD CONSTRAINT table_va_stat_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_name(id) ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

