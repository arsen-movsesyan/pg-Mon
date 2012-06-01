/*
 * src/test/examples/testlibpq.c
 *
 *
 * testlibpq.c
 *
 *		Test the C version of libpq, the PostgreSQL frontend library.
 */
#include <stdio.h>
#include <libpq-fe.h>


int main(int argc, char **argv) {
    const char *conninfo;
    PGPing conn;

/*
 * If the user supplies a parameter on the command line, use it as the
 * conninfo string; otherwise default to setting dbname=postgres and using
 * environment variables or defaults for all other connection parameters.
 */
    if (argc > 1) {
	conninfo = argv[1];
    } else {
	conninfo = "host=172.16.159.17 dbname=postgres port=5432 sslmode=prefer";
    }

/* Make a connection to the database */
    conn = PQping(conninfo);

/* Check to see that the backend connection was successfully made */

    switch (conn) {
	case PQPING_OK:
	    printf("Remote server is alive. Ping status is: PQPING_OK\n");
	    break;
	case PQPING_REJECT:
	    printf("Remote server rejected connection. Ping status is: PQPING_REJECT\n");
	    break;
	case PQPING_NO_RESPONSE:
	    printf("No response from remote server. Ping status is: PQPING_NO_RESPONSE\n");
	    break;
	case PQPING_NO_ATTEMPT:
	    printf("No attempt was made to contact remote server. Ping status is: PQPING_NO_ATTEMPT\n");
	    break;
	}
    return 0;
}
