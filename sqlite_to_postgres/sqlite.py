import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple
from uuid import uuid4


@dataclass
class Movie:
    id: str
    title: str
    description: str
    rating: float
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass
class Person:
    id: str
    full_name: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass
class Genre:
    id: str
    title: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass
class MovieGenre:
    id: str
    movie_id: str
    genre_id: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass
class MoviePerson:
    id: str
    movie_id: str
    person_id: str
    role: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


def _dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """
    Так как в SQLite нет встроенной фабрики для строк в виде dict,
    всё приходится делать самостоятельно
    """
    result = {}
    for idx, col in enumerate(cursor.description):
        result[col[0]] = row[idx]
    return result


@contextmanager
def conn_context(db_path: str):
    """
    В SQLite нет контекстного менеджера для работы с соединениями,
    поэтому добавляем его тут, чтобы грамотно закрывать соединения
    :param db_path: путь до базы данных
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = _dict_factory
    yield conn
    conn.close()


def _get_movies(conn: sqlite3.Connection) -> list:
    """ Получаем все фильмы из SQLite """

    SQL = """
    /* Используем CTE для читаемости. Здесь нет прироста
    производительности, поэтому можно поменять на subquery */
    WITH x as (
        -- Используем group_concat, чтобы собрать id и имена
        -- всех актёров в один список после join'а с таблицей actors
        -- Отметим, что порядок id и имён совпадает
        -- Не стоит забывать про many-to-many связь между
        -- таблицами фильмов и актёров
        SELECT m.id,
               group_concat(a.id)   as actors_ids,
               group_concat(a.name) as actors_names
        FROM movies m
                 LEFT JOIN movie_actors ma on m.id = ma.movie_id
                 LEFT JOIN actors a on ma.actor_id = a.id
        GROUP BY m.id
    )
    -- Получаем список всех фильмов со сценаристами и актёрами
    SELECT m.id,
           genre,
           director,
           title,
           plot    as description,
           imdb_rating,
           x.actors_ids,
           x.actors_names,
    /* Этот CASE решает проблему в дизайне таблицы:
    если сценарист всего один, то он записан простой строкой
    в столбце writer и id. В противном случае данные
    хранятся в столбце writers  и записаны в виде
    списка объектов JSON.
    Для исправления ситуации применяем хак:
    приводим одиночные записи сценаристов к списку
    из одного объекта JSON и кладём всё в поле writers */
    CASE
        WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
        ELSE m.writers
        END AS writers
    FROM movies m
        LEFT JOIN x ON m.id = x.id
    """

    return conn.execute(SQL).fetchall()


def _get_writers(conn: sqlite3.Connection) -> Dict[str, str]:
    """ Получаем всех сценаристов из SQLite """

    SQL = "SELECT DISTINCT id, name FROM writers;"
    result = {}
    for row in conn.execute(SQL):
        result[row["id"]] = row["name"]
    return result


def _get_new_key() -> str:
    """ Получаем новый ключ """
    return str(uuid4())


class Extractor:
    """ Подготоваливает списки для загрузки в таблицы """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self.movies: List[Movie] = []
        self.persons: Dict[str, str] = {}
        self.genres: Dict[str, str] = {}
        self.movies_genres: List[MovieGenre] = []
        self.movies_persons: List[MoviePerson] = []

    def _get_movies(self) -> list:
        """ Получаем все фильмы из SQLite """
        return _get_movies(self._conn)

    def _get_writers(self) -> Dict[str, str]:
        """ Получаем всех сценаристов из SQLite """
        return _get_writers(self._conn)

    def _process_genres(self, raw_movie_data: dict) -> None:
        """ Присваиваем uuid. Добавляем жанры в результирующие списки. """
        for genre in raw_movie_data["genre"].split(","):
            genre_uuid = self.genres.setdefault(genre.strip(), _get_new_key())
            self.movies_genres.append(
                MovieGenre(
                    id=_get_new_key(),
                    movie_id=raw_movie_data["id"],
                    genre_id=genre_uuid,
                )
            )

    def _process_persons(self, raw_movie_data: dict, writers: dict) -> None:
        """ Присваиваем uuid. Добавляем лица в результирующие списки. """

        set_of_actors = set()
        for actor_id, actor_name in zip(
            raw_movie_data["actors_ids"].split(","),
            raw_movie_data["actors_names"].split(","),
        ):
            if actor_name != "N/A" and actor_id not in set_of_actors:
                set_of_actors.add(actor_id)
                person_uuid = self.persons.setdefault(actor_name, _get_new_key())
                self.movies_persons.append(
                    MoviePerson(
                        id=_get_new_key(),
                        movie_id=raw_movie_data["id"],
                        person_id=person_uuid,
                        role="actor",
                    )
                )

        for director in raw_movie_data["director"].split(","):
            if director != "N/A":
                person_uuid = self.persons.setdefault(director, _get_new_key())
                self.movies_persons.append(
                    MoviePerson(
                        id=_get_new_key(),
                        movie_id=raw_movie_data["id"],
                        person_id=person_uuid,
                        role="director",
                    )
                )

        set_of_writers = set()
        for writer in json.loads(raw_movie_data["writers"]):
            writer_name = writers.get(writer["id"])
            if (
                writer_name
                and writer_name != "N/A"
                and writer["id"] not in set_of_writers
            ):
                set_of_writers.add(writer["id"])
                person_uuid = self.persons.setdefault(writer_name, _get_new_key())
                self.movies_persons.append(
                    MoviePerson(
                        id=_get_new_key(),
                        movie_id=raw_movie_data["id"],
                        person_id=person_uuid,
                        role="writer",
                    )
                )

    def _process_movie_data(self, writers: dict, raw_movie_data: dict) -> None:
        """ Очищаем данные, значения N/A заменяем на None. Присваиваем uuid фильму. """

        raw_movie_data["id"] = _get_new_key()

        description = raw_movie_data["description"]
        if description == "N/A":
            description = ""

        try:
            imdb_rating = float(raw_movie_data["imdb_rating"])
        except ValueError:
            imdb_rating = float(0)

        self._process_genres(raw_movie_data)
        self._process_persons(raw_movie_data, writers)

        self.movies.append(
            Movie(
                id=raw_movie_data["id"],
                title=raw_movie_data["title"],
                description=description,
                rating=imdb_rating,
            )
        )

    def get_data(
        self
    ) -> Tuple[
        List[Movie], List[Person], List[Genre], List[MoviePerson], List[MovieGenre]
    ]:
        """ Получаем обобщенные данные для таблиц. """

        raw_movies = self._get_movies()
        writers = self._get_writers()

        for raw_movie_data in raw_movies:
            self._process_movie_data(writers, raw_movie_data)

        persons = [Person(id=v, full_name=k) for k, v in self.persons.items()]
        genres = [Genre(id=v, title=k) for k, v in self.genres.items()]

        return self.movies, persons, genres, self.movies_persons, self.movies_genres


if __name__ == "__main__":
    with conn_context("db.sqlite") as sqlite_conn:
        extractor = Extractor(sqlite_conn)

    data = extractor.get_data()
