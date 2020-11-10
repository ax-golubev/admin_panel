import csv
import io
from datetime import datetime
from typing import Tuple

from psycopg2.extensions import connection
from psycopg2.extensions import cursor as pg_cursor

TIMEZONE = "Europe/Moscow"


def save_movies(cursor: pg_cursor, movies: list):
    """ Загружает фильмы в content.movies. """

    output = io.StringIO()
    headers = ["id", "title", "description", "rating", "created", "modified"]
    delimiter = "<"
    writer = csv.DictWriter(output, delimiter=delimiter, fieldnames=headers)

    for movie in movies:
        movie["created"] = movie["modified"] = datetime.now()
        writer.writerow(movie)

    output.seek(0)

    cursor.copy_from(output, "content.film_work", sep=delimiter, columns=headers)

    output.close()


def save_persons(cursor: pg_cursor, persons: list):
    """ Загружает лица в content.persons. """

    output = io.StringIO()

    for id_, full_name in persons:
        created = modified = datetime.now()
        output.write(f"{id_},{full_name},{created},{modified}\n")

    output.seek(0)

    cursor.copy_from(
        output,
        "content.persons",
        sep=",",
        columns=["id", "full_name", "created", "modified"],
    )

    output.close()


def save_genres(cursor: pg_cursor, genres: list):
    """ Загружает жанры в content.genres. """

    output = io.StringIO()

    for id_, title in genres:
        created = modified = datetime.now()
        output.write(f"{id_},{title},{created},{modified}\n")

    output.seek(0)

    cursor.copy_from(
        output,
        "content.genres",
        sep=",",
        columns=["id", "title", "created", "modified"],
    )

    output.close()


def save_movies_persons(cursor: pg_cursor, movies_persons: list):
    """ Загружает данные в таблицу content.movies_persons. """

    output = io.StringIO()

    for id_, movie_id, person_id, role in movies_persons:
        created = modified = datetime.now()
        output.write(f"{id_},{movie_id},{person_id},{role},{created},{modified}\n")

    output.seek(0)

    cursor.copy_from(
        output,
        "content.film_works_persons",
        sep=",",
        columns=["id", "film_work_id", "person_id", "role", "created", "modified"],
    )

    output.close()


def save_movies_genres(cursor: pg_cursor, movies_genres: list):
    """ Загружает данные в таблицу content.movies_genres. """

    output = io.StringIO()

    for id_, movie_id, genre_id in movies_genres:
        created = modified = datetime.now()
        output.write(f"{id_},{movie_id},{genre_id},{created},{modified}\n")

    output.seek(0)

    cursor.copy_from(
        output,
        "content.film_works_genres",
        sep=",",
        columns=["id", "film_work_id", "genre_id", "created", "modified"],
    )

    output.close()


def save_all_data(conn: connection, data: Tuple[list, list, list, list, list]):
    """ Основной метод загрузки данных в Postgres """
    movies, persons, genres, movies_persons, movies_genres = data

    with conn.cursor() as cursor:
        cursor.execute(f"SET TIME ZONE '{TIMEZONE}';")
        save_movies(cursor, movies)
        save_persons(cursor, persons)
        save_genres(cursor, genres)
        save_movies_persons(cursor, movies_persons)
        save_movies_genres(cursor, movies_genres)
