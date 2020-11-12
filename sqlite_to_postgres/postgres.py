from typing import List, Tuple

from config import TIMEZONE
from psycopg2.extensions import connection
from psycopg2.extensions import cursor as pg_cursor
from psycopg2.extras import execute_values
from sqlite import Genre, Movie, MovieGenre, MoviePerson, Person


def save_movies(cursor: pg_cursor, movies: List[Movie]) -> None:
    """ Загружает фильмы в content.movies. """

    SQL = "INSERT INTO content.film_work(id, title, description, rating, created, modified) VALUES %s"

    execute_values(
        cursor,
        SQL,
        [
            (m.id, m.title, m.description, m.rating, m.created, m.modified)
            for m in movies
        ],
    )


def save_persons(cursor: pg_cursor, persons: List[Person]) -> None:
    """ Загружает лица в content.persons. """

    SQL = "INSERT INTO content.persons(id, full_name, created, modified) VALUES %s"

    execute_values(
        cursor, SQL, [(p.id, p.full_name, p.created, p.modified) for p in persons]
    )


def save_genres(cursor: pg_cursor, genres: List[Genre]) -> None:
    """ Загружает жанры в content.genres. """

    SQL = "INSERT INTO content.genres(id, title, created, modified) VALUES %s"

    execute_values(
        cursor, SQL, [(g.id, g.title, g.created, g.modified) for g in genres]
    )


def save_movies_persons(cursor: pg_cursor, movies_persons: List[MoviePerson]) -> None:
    """ Загружает данные в таблицу content.movies_persons. """

    SQL = "INSERT INTO content.film_works_persons(id, film_work_id, person_id, role, created, modified) VALUES %s"

    execute_values(
        cursor,
        SQL,
        [
            (mp.id, mp.movie_id, mp.person_id, mp.role, mp.created, mp.modified)
            for mp in movies_persons
        ],
    )


def save_movies_genres(cursor: pg_cursor, movies_genres: List[MovieGenre]) -> None:
    """ Загружает данные в таблицу content.movies_genres. """

    SQL = "INSERT INTO content.film_works_genres(id, film_work_id, genre_id, created, modified) VALUES %s"

    execute_values(
        cursor,
        SQL,
        [
            (mg.id, mg.movie_id, mg.genre_id, mg.created, mg.modified)
            for mg in movies_genres
        ],
    )


def save_all_data(
    conn: connection,
    data: Tuple[
        List[Movie], List[Person], List[Genre], List[MoviePerson], List[MovieGenre]
    ],
) -> None:
    """ Основной метод загрузки данных в Postgres """
    movies, persons, genres, movies_persons, movies_genres = data

    with conn.cursor() as cursor:
        cursor.execute(f"SET TIME ZONE '{TIMEZONE}';")
        save_movies(cursor, movies)
        save_persons(cursor, persons)
        save_genres(cursor, genres)
        save_movies_persons(cursor, movies_persons)
        save_movies_genres(cursor, movies_genres)
