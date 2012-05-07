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

--
-- Name: test_log_time(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION test_log_time() RETURNS boolean
    LANGUAGE plpgsql
    AS $$BEGIN
	PERFORM 1 FROM log_time WHERE hour_truncate=(SELECT date_trunc('hour',now())::timestamp without time zone);
	IF FOUND THEN
		RETURN FALSE;
	END IF;
	RETURN TRUE;
END
	$$;


ALTER FUNCTION public.test_log_time() OWNER TO postgres;

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
    tn_id integer NOT NULL,
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
-- Name: table_toast_stat; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE table_toast_stat (
    id bigint NOT NULL,
    tn_id integer NOT NULL,
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
    ADD CONSTRAINT index_toast_stat_tn_id_time_id_key UNIQUE (tn_id, time_id);


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
    ADD CONSTRAINT table_toast_stat_tn_id_time_id_key UNIQUE (tn_id, time_id);


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
    ADD CONSTRAINT index_toast_stat_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES index_toast_name(id);


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
    ADD CONSTRAINT table_toast_stat_tn_id_fkey FOREIGN KEY (tn_id) REFERENCES table_toast_name(id);


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

