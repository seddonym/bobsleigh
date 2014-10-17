from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from importlib import import_module
import os
import socket


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

    def __init__(self, **kwargs):
        # Check the required kwargs are there
        required_kwargs = self.get_required_kwargs()
        for kwarg in required_kwargs:
            if kwarg not in kwargs:
                raise ImproperlyConfigured("Required kwarg '%s' missing from" \
                        " InstallationHandler %s." % (kwarg, self))

        # Combine with optional kwargs
        combined_kwargs = self.get_optional_kwargs().copy()
        combined_kwargs.update(kwargs)

        # Use patterns to fill in/override any config attributes that
        # define a pattern
        for key, pattern in self.get_config_patterns():
            if key not in kwargs:
                # Only override it if they were not passed in as kwargs
                combined_kwargs[key] = pattern % combined_kwargs

        # Sets the dict as an object, just
        # so we can access it as attributes instead of keys
        self.config = type('InstallationHandlerConfig', (), combined_kwargs)

    def get_required_kwargs(self):
        # Returns a tuple of required instantiation kwargs.
        # Will be set as attributes on self.config
        return ()

    def get_optional_kwargs(self):
        # Returns a dict of optional instantiation kwargs, with their defaults.
        # Will be set as attributes on self.config, if present.
        return {
            'extra_settings': {},
        }

    def get_config_patterns(self):
        """Returns a tuple of two-tuples containing patterns
        that can be used to set config variables based on other
        config variables.

        For example, the following line will set self.config.project_path
        based on self.config.user and self.config.sitename.

        patterns = (
             ('project_path', '/home/%(user)s/sites/%(sitename)s'),
        )
        """
        return ()

    def setup(self):
        "Sets up the settings for Django."
        if not settings.configured:
            settings.configure(**self.get_settings())

    def get_settings(self):
        "Returns dictionary of all the settings."
        if not getattr(self, '_settings', None):
            self.build_settings()
        return self._settings

    def build_settings(self):
        """Builds the settings into self._settings,
        and makes any adjustments."""
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

        # Process the extra_settings kwarg
        self._settings.update(self.config.extra_settings)

    def is_current(self):
        """Returns whether or not to treat this handler as the correct
        one for the installation."""
        raise NotImplementedError


class InstallationHandler(BaseInstallationHandler):
    "Standard installation handler with likely defaults."

    project_module = 'settings.project'

    def get_required_kwargs(self):
        required_kwargs = super(InstallationHandler, self)\
                                                    .get_required_kwargs()
        required_kwargs += ('domain', 'host')
        return required_kwargs

    def get_optional_kwargs(self):
        optional_kwargs = super(InstallationHandler, self)\
                                                    .get_optional_kwargs()
        optional_kwargs.update({
            'debug': False,
            'email_host': None,
            'email_host_user': None,
            'server_email': None,
            'db_name': None,
            'db_user': None,
            # Whether or not to monitor the codebase for changes
            'monitor': False,
            # The path to the virtualenv, if there is one.
            'virtualenv_path': None,
            # The name of the python version.  This is used by some runners
            # to locate, for example, the virtualenv's sitepackages
            'python': 'python2.7',
            'static_path': None,
            'media_path': None,
            'project_path': None,
            'log_path': None,
        })
        return optional_kwargs

    def get_config_patterns(self):
        """Specify some patterns - these should be filled in by
        classes extending this."""
        patterns = super(InstallationHandler, self).get_config_patterns()
        patterns += (
            ('static_path', ''),
            ('media_path', ''),
            ('project_path', ''),
            ('log_path', ''),
        )
        return patterns

    def adjust(self):
        "Adjusts the settings"
        super(InstallationHandler, self).adjust()

        self.adjust_debug()
        self.adjust_logging()
        self.adjust_databases()
        self.adjust_email()

        self._settings['ALLOWED_HOSTS'] = [self.config.domain]
        self._settings['DOMAIN'] = self.config.domain
        self._settings['STATIC_ROOT'] = self.config.static_path
        self._settings['MEDIA_ROOT'] = self.config.media_path

        self._settings['PROJECT_ROOT'] = self.config.project_path
        self._settings['TEMPLATE_DIRS'] = (os.path.join(
                                            self.config.project_path,
                                            'templates'),)

    def adjust_debug(self):
        "Adjusts settings based on debug value"
        self._settings['DEBUG'] = self.config.debug
        self._settings['TEMPLATE_DEBUG'] = self.config.debug
        self._settings['THUMBNAIL_DEBUG'] = self.config.debug

    def adjust_logging(self):
        "Adjusts logging settings"
        self._settings['LOGGING']['handlers']['error']['filename'] = \
                                os.path.join(self.config.log_path, 'error.log')
        self._settings['LOGGING']['handlers']['debug']['filename'] = \
                                os.path.join(self.config.log_path, 'debug.log')
        # Make sure we don't bother to mail admins if debug is True
        if self.config.debug:
            try:
                self._settings['LOGGING']['loggers']['django.request']\
                                            ['handlers'].remove('mail_admins')
            except (KeyError, ValueError):
                pass

    def adjust_databases(self):
        "Adjusts database settings"
        if self.config.db_name and self.config.db_user:
            self._settings['DATABASES']['default']['NAME'] = \
                                                    self.config.db_name
            self._settings['DATABASES']['default']['USER'] = \
                                                    self.config.db_user
            try:
                self._settings['DATABASES']['default']['PASSWORD'] = \
                                                    self._settings['DB_PASS']
            except KeyError:
                raise ImproperlyConfigured('You must define a DB_PASS \
                                            setting in your secret.py.')

    def adjust_email(self):
        "Adjusts email settings"
        self._settings['EMAIL_HOST'] = self.config.email_host
        self._settings['EMAIL_HOST_USER'] = self.config.email_host_user
        self._settings['SERVER_EMAIL'] = self.config.server_email
        self._settings['DEFAULT_FROM_EMAIL'] = self.config.server_email

    def is_current(self):
        """Basic way of testing whether or not this is the current
        installationhandler.  This won't work for situations where
        multiple instances run on the same host."""
        return self.config.host == socket.gethostname()
