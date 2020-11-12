import sqlite3

import config
import psycopg2
from postgres import save_all_data
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from sqlite import Extractor, conn_context


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    data = Extractor(connection).get_data()

    save_all_data(pg_conn, data)


if __name__ == "__main__":
    dsl = {
        "dbname": config.POSTGRES_DB,
        "user": config.POSTGRES_USER,
        "password": config.POSTGRES_PASSWORD,
        "host": config.POSTGRES_HOST,
        "port": config.POSTGRES_PORT,
    }
    with conn_context("db.sqlite") as sqlite_conn, psycopg2.connect(
        **dsl, cursor_factory=DictCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
