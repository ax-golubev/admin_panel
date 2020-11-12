import environ

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str,),
    ALLOWED_HOSTS=(list, ["*"]),
    POSTGRES_DB=(str, "movies"),
    POSTGRES_HOST=(str, "localhost"),
    POSTGRES_PORT=(int, 5432),
    POSTGRES_USER=(str, "postgres"),
    POSTGRES_PASSWORD=(str, "postgres"),
    POSTGRES_OPTIONS=(dict, {"options": "-c search_path=content"}),
)
