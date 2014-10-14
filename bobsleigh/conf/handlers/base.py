from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from importlib import import_module
import os


def settings_from_module(module):
    "Returns settings defined in a module as a dictionary."
    return dict([(i, getattr(module, i)) for i in dir(module) \
                                                        if i[0:2] != '__'])


class BaseInstallationHandler(object):
    """An InstallationHandler is a class for configuring common patterns
    of settings.

    A project will declare a number of InstallationHandler instances,
    complete with configuration, and each InstallationHandler in turn
    has the chance to declare whether it is the correct one to use,
    based on the result of is_current().

    If it is, then the InstallationHandler can then be used to set
    the settings via setup()."""

    # The name of the project settings file, for importing
    project_module = ''

    # Required instantiation kwargs.
    # Will be set as attributes on the instance.
    required_kwargs = ()

    # Optional instantiation kwargs.
    # Will be set as attributes on the instance, if present, otherwise
    # the default value will be used.
    optional_kwargs = {}

    # Define a dictionary of patterns that can be used to
    # set config variables based on other config variables.
    #
    # For example, the following line will set self.config.project_root
    # based on self.config.user and self.config.sitename.
    #
    # patterns = {
    #     'project_root': '/home/%(user)s/sites/%(sitename)s'
    # }
    patterns = {}

    def __init__(self, **kwargs):
        # Check the required kwargs are there
        for kwarg in self.required_kwargs:
            if kwarg not in kwargs:
                raise ImproperlyConfigured("Required kwarg '%s' missing from \
                        InstallationHandler." % kwarg)

        # Combine with optional kwargs
        combined_kwargs = kwargs.copy()
        combined_kwargs.update(self.optional_kwargs)

        # Use patterns to fill in any config attributes that
        # depend on a pattern


        # Sets the dict as an object, just
        # so we can access it as attributes instead of keys
        self.config = type('InstallationHandlerConfig', (), combined_kwargs)

    def setup(self):
        "Sets up the settings for Django."
        if not settings.configured:
            settings.configure(**self.get_settings())

    def get_settings(self):
        "Returns dictionary of all the settings."

        if not self._settings:
            self.build_settings()
        return self._settings

    def build_settings(self):
        self.import_initial()
        self.adjust()

    def import_initial(self):
        "Imports the initial settings into self._settings"
        # Import from the project settings file
        project = import_module(self.project_module)
        self._settings = settings_from_module(project)

    def adjust(self):
        "Adjusts the settings"

        # Pull any secret settings from the secret module
        # This file should not be in the main code repository
        secret = settings_from_module(import_module('settings.secret'))
        self._settings.update(secret)

    def is_current(self):
        """Returns whether or not to treat this handler as the correct
        one for the installation."""
        raise NotImplementedError

    def get_virtualenv(self):
        "Returns the path to the virtualenv, if there is one."
        raise NotImplementedError


class InstallationHandler(BaseInstallationHandler):
    "Standard installation handler with likely defaults."

    project_module = 'settings.project'

    required_kwargs = ('sitename',
                       'domain')

    optional_kwargs = {
        'debug': False,
        'email_host': None,
        'email_host_user': None,
        'server_email': None,
        'db_name': None,
        'db_user': None,
    }

    # Specify some patterns - these should be filled in by
    # classes extending this.
    patterns = {
        'static_root': '',
        'media_root': '',
        'project_root': '',
        'logpath': '',
    }

    def adjust(self):
        "Adjusts the settings"
        super(InstallationHandler, self).adjust()
        self.adjust_debug()

        self._settings['ALLOWED_HOSTS'] = [self.config.domain]
        self._settings['DOMAIN'] = self.config.domain
        self._settings['STATIC_ROOT'] = self.config.static_root
        self._settings['MEDIA_ROOT'] = self.config.media_root

        self._settings['PROJECT_ROOT'] = self.config.project_root
        self._settings['TEMPLATE_DIRS'] = (os.path.join(
                                            self.config.project_root,
                                            'templates'),)

    def adjust_debug(self):
        "Adjusts settings based on debug value"
        self._settings['DEBUG'] = self.config.debug
        self._settings['TEMPLATE_DEBUG'] = self.config.debug
        self._settings['THUMBNAIL_DEBUG'] = self.config.debug

    def adjust_logging(self):
        "Adjusts logging settings"
        self._settings['LOGGING']['handlers']['error']['filename'] = \
                                os.path.join(self.config.logpath, 'error.log')
        self._settings['LOGGING']['handlers']['debug']['filename'] = \
                                os.path.join(self.config.logpath, 'debug.log')

    def adjust_databases(self):
        "Adjusts database settings"
        if self.config.db_name and self.config.db_user:
            self._settings['DATABASES']['default']['NAME'] = \
                                                    self.config.db_name
            self._settings['DATABASES']['default']['USER'] = \
                                                    self.config.db_user
            try:
                self._settings['DATABASES']['default']['PASSWORD'] = \
                                                    self._secret['DB_PASS']
            except KeyError:
                raise ImproperlyConfigured('You must define a DB_PASS \
                                            setting in your secret.py.')

    def adjust_email(self):
        "Adjusts email settings"
        self._settings['EMAIL_HOST'] = self.config.email_host
        self._settings['EMAIL_HOST_USER'] = self.config.email_host_user
        self._settings['SERVER_EMAIL'] = self.config.server_email
        self._settings['DEFAULT_FROM_EMAIL'] = self.config.server_email

