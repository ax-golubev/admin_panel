from uuid import uuid4

from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class Genre(TimeStampedModel):
    """ Модель для хранения жанров. """
    id = models.UUIDField(primary_key=True, blank=True, default=uuid4, editable=False)
    title = models.TextField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True, null=True)

    class Meta:
        db_table = "genres"
        verbose_name = _("Жанр")
        verbose_name_plural = _("Жанры")

    def __str__(self):
        return self.title


class FilmWorkType(models.TextChoices):
    """ Класс для выбора типа кинокартины. """
    MOVIE = "movie", _("фильм")
    TV_SERIES = "tv_series", _("сериал")


class Person(TimeStampedModel):
    """ Модель для хранения участников. """
    id = models.UUIDField(primary_key=True, blank=True, default=uuid4, editable=False)
    full_name = models.CharField(_("имя"), db_index=True, max_length=255)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ("id",)
        db_table = "persons"
        verbose_name = _("Участник кинокартины")
        verbose_name_plural = _("Участники кинокартины")

    def __str__(self):
        return self.full_name


class FilmWork(TimeStampedModel):
    """ Модель для хранения кинокартин. """
    id = models.UUIDField(primary_key=True, blank=True, default=uuid4, editable=False)
    title = models.CharField(_("название"), db_index=True, max_length=255)
    description = models.TextField(_("описание"), blank=True)
    creation_date = models.DateField(_("дата выпуска"), null=True, blank=True)
    certificate = models.TextField(_("возрастной ценз"), null=True, blank=True)
    file_path = models.TextField(_("файл"), null=True, blank=True)
    rating = models.FloatField(_("рейтинг"), blank=True, null=True)
    type = models.TextField(
        _("тип"), blank=True, null=True, choices=FilmWorkType.choices
    )
    persons = models.ManyToManyField(Person, through="FilmWorksPersons")
    genres = models.ManyToManyField(Genre, through="FilmWorksGenres")

    class Meta:
        ordering = ("id",)
        db_table = "film_work"
        verbose_name = _("Кинокартина")
        verbose_name_plural = _("Кинокартина")

    def __str__(self):
        return self.title


class FilmWorksGenres(TimeStampedModel):
    """ Модель для хранения сопоставлений кинокартин и жанров. """
    id = models.UUIDField(primary_key=True, blank=True, default=uuid4, editable=False)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)
        db_table = "film_works_genres"
        constraints = [
            UniqueConstraint(
                fields=["film_work", "genre"], name="unique_film_work_genre"
            )
        ]


class RolePerson(models.TextChoices):
    """ Класс для выбора роли. """
    DIRECTOR = "director", _("режиссер")
    ACTOR = "actor", _("актер")
    WRITERS = "writer", _("сценарист")


class FilmWorksPersons(TimeStampedModel):
    """ Модель для хранения сопоставлений кинокартин и участников. """
    id = models.UUIDField(primary_key=True, blank=True, default=uuid4, editable=False)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.TextField(choices=RolePerson.choices)

    class Meta:
        ordering = ("id",)
        db_table = "film_works_persons"
        verbose_name = _("Кинокартины и участники")
        verbose_name_plural = _("Кинокартины и участники")
        constraints = [
            UniqueConstraint(
                fields=["film_work", "person", "role"],
                name="unique_film_work_person_role",
            )
        ]
