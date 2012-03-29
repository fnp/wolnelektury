import djcelery
djcelery.setup_loader()

BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_SEND_TASK_ERROR_EMAILS = True
