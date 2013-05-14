
COPY enum_sslmode (id, sslmode, description) FROM stdin;
1	disable	Only try a non-SSL connection
2	allow	First try a non-SSL connection; if that fails, try an SSL connection
3	prefer	First try an SSL connection; if that fails, try a non-SSL connection
4	require	Only try an SSL connection. If a root CA file is present, verify the certificate in the same way as if verify-ca was specified
5	verify-ca	Only try an SSL connection, and verify that the server certificate is issued by a trusted certificate authority (CA)
6	verify-full	Only try an SSL connection, verify that the server certificate is issued by a trusted CA and that the server host name matches that in the certificate
\.


COPY enum_track_functions (id, track_value, description) FROM stdin;
1	none	Functions statistic tracking disabled
2	pl	Track only procedural-language functions
3	all	Track SQL, C and procedural-language functions
\.

