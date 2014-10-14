from django.conf import settings
from importlib import import_module
import os


def settings_from_module(module):
    "Returns settings defined in a module as a dictionary."
    return dict([(i, getattr(module, i)) for i in dir(module) \
                                                        if i[0:2] != '__'])


class InstallationHandler(object):
    """An InstallationHandler is a class for configuring common patterns
    of settings.

    A project will declare a number of InstallationHandler instances,
    complete with configuration, and each InstallationHandler in turn
    has the chance to declare whether it is the correct one to use,
    based on the result of is_current().

    If it is, then the InstallationHandler can then be used to set
    the settings via setup()."""

    # The name of the project settings file, for importing
    project_module = 'settings.project'

    # Required instantiation kwargs.
    # Will be set as attributes on the instance.
    required_kwargs = ('sitename',)

    # Optional instantiation kwargs.
    # Will be set as attributes on the instance, if present, otherwise
    # the default value will be used.
    optional_kwargs = {
        'debug': False,
    }

    def __init__(self, **kwargs):
        # Check the required kwargs are there
        for kwarg in self.required_kwargs:
            if kwarg not in kwargs:
                raise Exception("Required kwarg '%s' missing from \
                        InstallationHandler." % kwarg)

        # Combine with optional kwargs
        combined_kwargs = kwargs.copy()
        combined_kwargs.update(self.optional_kwargs)

        # Set kwargs as attributes on the handler
        for kwarg, value in combined_kwargs.items():
            setattr(self, kwarg, value)

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

        # If it's set, add the database password to the correct setting
        try:
            self._settings['DATABASES']['default']['PASSWORD'] = \
                                                    self._secret['DB_PASS']
        except KeyError:
            pass

    def is_current(self):
        """Returns whether or not to treat this handler as the correct
        one for the installation."""
        raise NotImplementedError

    def get_virtualenv(self):
        "Returns the path to the virtualenv, if there is one."
        raise NotImplementedError
