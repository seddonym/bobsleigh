from base import InstallationHandler
import socket

class LocalHandler(InstallationHandler):

    monitor = True
    default_debug = True
    host = 'lanky'

    def __init__(self, *args, **kwargs):
        super(LocalHandler, self).__init__(*args, **kwargs)
        self.domain = "%s.localhost" % self.sitename
        self.logpath = '/var/log/django/%s/debug.log' % self.sitename
        self.db_user = self.db_name = self.sitename

    def is_current(self):
        return self.host == socket.gethostname()

    def get_virtualenv(self):
        return '/home/david/.virtualenvs/%s' % self.sitename
