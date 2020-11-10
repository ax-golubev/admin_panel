from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from film_works import models


@admin.register(models.Genre)
class GenresAdmin(admin.ModelAdmin):
    search_fields = ("title",)


class FilmWorksGenresInline(admin.TabularInline):
    model = models.FilmWorksGenres
    extra = 0


class FilmWorksPersonsInline(admin.TabularInline):
    model = models.FilmWorksPersons
    extra = 0
    autocomplete_fields = ("person",)


@admin.register(models.FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_filter = ("type",)
    inlines = (FilmWorksPersonsInline, FilmWorksGenresInline)


class FilmWorkInline(admin.TabularInline):
    model = models.FilmWorksPersons
    extra = 0
    autocomplete_fields = ("film_work",)


@admin.register(models.Person)
class PersonsAdmin(admin.ModelAdmin):
    search_fields = ("full_name",)
    inlines = (FilmWorkInline,)


@admin.register(models.FilmWorksPersons)
class FilmWorksPersonsAdmin(admin.ModelAdmin):
    list_display = ("id", "film_work", "person")
    list_display_links = ("id",)
    search_fields = ("film_work__title", "person__full_name")
    list_filter = ("role",)

    def get_queryset(self, request):
        return models.FilmWorksPersons.objects.all().select_related(
            "film_work", "person"
        )

    def film_work(self, instance):
        return instance.film_work.title

    def person(self, instance):
        return instance.person.full_name

    person.short_description = _("Лицо")
    film_work.short_description = _("Фильм")
