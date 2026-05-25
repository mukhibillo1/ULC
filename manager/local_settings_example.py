ALLOWED_HOSTS = ["*"]
DEBUG = True

DATABASES = {
    "default" : {
        "ENGINE" : "django.db.backends.postgresql",
        "NAME" : "db_name",
        "USER" : "username",
        "PASSWORD" : "password",
        "HOST" : "localhost",
        "PORT" : "5432",
        "ATOMIC_REQUEST" : True,
    }
}

HOST = "http://localhost:8000"


