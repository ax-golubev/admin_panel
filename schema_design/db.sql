CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.genres
(
    id uuid PRIMARY KEY,
    title text NOT NULL,
    description text,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.film_work
(
    id uuid PRIMARY KEY,
    title text NOT NULL,
    description text,
    creation_date date,
    certificate text,
    file_path text,
    rating float,
    type text,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.persons (
    id uuid PRIMARY KEY,
    full_name text NOT NULL,
    birth_date date,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.film_works_genres
(
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work ON DELETE CASCADE,
	genre_id uuid REFERENCES content.genres ON DELETE CASCADE,
	created timestamp with time zone,
	modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.film_works_persons (
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work ON DELETE CASCADE,
    person_id uuid REFERENCES content.persons ON DELETE CASCADE,
    role text NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE UNIQUE INDEX ON content.film_works_genres(film_work_id, genre_id);
CREATE UNIQUE INDEX ON content.film_works_persons(film_work_id, person_id, role);

CREATE INDEX ON content.persons(full_name);
CREATE INDEX ON content.film_work(title);
