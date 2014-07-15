from django.conf import settings
from importlib import import_module
import os


def settings_from_module(module):
    "Returns settings defined in a module as a dictionary."
    return dict([(i, getattr(module, i)) for i in dir(module) \
                                                        if i[0:2] != '__'])


class InstallationHandler(object):

    monitor = False
    default_debug = False

    def __init__(self, sitename, debug=None):
        self.sitename = sitename
        self._settings = None
        if debug is not None:
            self.debug = debug
        else:
            self.debug = self.default_debug

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
        project = import_module('settings.project')
        self._settings = settings_from_module(project)

    def adjust(self):
        "Adjusts the settings"
        # Adjust settings
        self._settings['DEBUG'] = self.debug
        self._settings['TEMPLATE_DEBUG'] = self.debug
        self._settings['THUMBNAIL_DEBUG'] = self.debug

        self._settings['LOGGING']['handlers']['error']['filename'] = \
                                                '%s/error.log' % self.logpath
        self._settings['LOGGING']['handlers']['debug']['filename'] = \
                                                '%s/debug.log' % self.logpath
        self._settings['DATABASES']['default']['NAME'] = self.db_name
        self._settings['DATABASES']['default']['USER'] = self.db_user
        self._settings['ALLOWED_HOSTS'] = [self.domain]

        self._settings['STATIC_ROOT'] = self.static_root
        self._settings['MEDIA_ROOT'] = self.media_root
        self._settings['DOMAIN'] = self.domain
        self._settings['PROJECT_ROOT'] = self.project_root
        self._settings['TEMPLATE_DIRS'] = (os.path.join(self.project_root,
                                                        'templates'),)

        # Secret settings
        secret = settings_from_module(import_module('settings.secret'))
        self._settings['DATABASES']['default']['PASSWORD'] = secret['DB_PASS']
        self._settings.update(secret)

    def is_current(self):
        """Returns whether or not to treat this handler as the correct
        one for the installation."""
        raise NotImplementedError

    def get_virtualenv(self):
        "Returns the path to the virtualenv, if there is one."
        raise NotImplementedError
