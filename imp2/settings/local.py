from .base import *

ALLOWED_HOSTS = [
    'imp2-mthomps.c9users.io',
]

DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l0^40gu)c6bq0jpb#crc68mdof@%z6xn1-m7(w^v7(c+&o8ajt'
