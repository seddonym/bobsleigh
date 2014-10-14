from .base import InstallationHandler
import socket


class LocalHandlerMixin(object):
    "Mixin for installation handlers geared up to local development."

    optional_kwargs = {
        'debug': True,
        'email_host': None,
        'email_host_user': None,
        'server_email': None,
        'db_name': None,
        'db_user': None,
        'monitor': True,
    }


class DevHandlerMixin(object):
    "Mixin for installation handlers geared up to development installations."
    optional_kwargs = {
        'debug': True,
        'email_host': None,
        'email_host_user': None,
        'server_email': None,
        'db_name': None,
        'db_user': None,
        'monitor': False,
    }
