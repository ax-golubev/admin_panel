CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.genres
(
    id uuid PRIMARY KEY,
    title text NOT NULL,
    description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
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
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.persons (
    id uuid PRIMARY KEY,
    full_name text NOT NULL,
    birth_date date,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.film_works_genres
(
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work ON DELETE SET NULL,
	genre_id uuid REFERENCES content.genres ON DELETE SET NULL,
	created_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.film_works_persons (
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work ON DELETE SET NULL,
    person_id uuid REFERENCES content.persons ON DELETE SET NULL,
    role text NOT NULL,
    created_at timestamp with time zone
);

CREATE UNIQUE INDEX ON content.film_works_genres(film_work_id, genre_id);
CREATE UNIQUE INDEX ON content.film_works_persons(film_work_id, person_id, role);

CREATE INDEX ON content.persons(full_name);
CREATE INDEX ON content.film_work(title);
