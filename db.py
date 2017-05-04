#!/usr/bin/env python
import os
import sshtunnel
import itertools
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import numpy as np
import credentials
from copy import deepcopy

db_schema_file = os.path.join('ops', 'db_schema.txt')
sshtunnel.DAEMON = True  # Prevent hanging process due to forward thread


def flatten(x):
    return list(itertools.chain(*x))


class db(object):
    def __init__(self, config):
        # Pass config -> this class
        for k, v in config.items():
            setattr(self, k, v)

    def __enter__(self):
        forward = sshtunnel.SSHTunnelForwarder(
            credentials.x7_credentials()['ssh_address'],
            ssh_username=self.username,
            ssh_password=self.password,
            remote_bind_address=('127.0.0.1', 5432))
        forward.start()
        pgsql_port = forward.local_bind_port
        pgsql_string = credentials.postgresql_connection(str(pgsql_port))
        self.forward = forward
        self.pgsql_port = pgsql_port
        self.pgsql_string = pgsql_string
        self.conn = psycopg2.connect(**pgsql_string)
        self.conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.forward.close()
        if exc_type is not None:
            print exc_type, exc_value, traceback
        return self

    def close_db(self):
        self.cur.close()
        self.conn.close()

    def init_db(self):
        db_schema = open(db_schema_file).read().splitlines()
        for s in db_schema:
            t = s.strip()
            if len(t):
                self.cur.execute(t)
        self.conn.commit()


def initialize_database():
    creds = credentials.results_postgresql_credentials()
    with db(creds) as db_conn:
        db_conn.init_db()
    print 'Initialized database tables and combos'


def main():
    initialize_database()


if __name__ == '__main__':
    main()
