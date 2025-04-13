from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$n!76c$@_w%t-1&(eyz_-w26&^%^t^$tua@l6dj8v$l6vzjb2x"

# SECURITY WARNING: define the correct hosts in production!
# ALLOWED_HOSTS = ["172.234.109.80","quirkgeek.co.zw"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
