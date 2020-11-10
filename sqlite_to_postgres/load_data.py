import sqlite3

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from postgres import save_all_data
from sqlite import Extractor, conn_context


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    data = Extractor(connection).get_data()

    save_all_data(pg_conn, data)


if __name__ == "__main__":
    dsl = {
        "dbname": "movies",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
    }
    with conn_context("db.sqlite") as sqlite_conn, psycopg2.connect(
        **dsl, cursor_factory=DictCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
