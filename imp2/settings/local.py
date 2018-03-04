from .base import *

ALLOWED_HOSTS = [
    'imp2-mthomps.c9users.io',
]
DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
STATIC_ROOT = '/home/ubuntu/workspace/public/'