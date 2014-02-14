#!/usr/bin/python -B

import psycopg2

import settings


conn=psycopg2.connect(settings.custom_dsn('pg_mon'))
lm_max="SELECT MAX(id) FROM log_time"
lmt_max="SELECT MAX(id) FROM log_time_mt"

cur=conn.cursor()

cur.execute(lm_max)
lm_id=cur.fetchone()[0]

cur.execute(lmt_max)
lmt_id=cur.fetchone()[0]

if lm_id:
    cur.execute("DELETE FROM log_time WHERE id={0}".format(lm_id))

if lmt_id:
    cur.execute("DELETE FROM log_time_mt WHERE id={0}".format(lmt_id))

cur.close()
conn.commit()
conn.close()
