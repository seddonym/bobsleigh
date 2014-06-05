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
        var_root = '/home/david/var/www/%s' % self.sitename
        self.static_root = '%s/static' % var_root
        self.media_root = '%s/uploads' % var_root

    def is_current(self):
        return self.host == socket.gethostname()

    def get_virtualenv(self):
        return '/home/david/.virtualenvs/%s' % self.sitename


class VagrantHandler(InstallationHandler):

    monitor = True
    default_debug = True
    host = 'precise32'

    def __init__(self, *args, **kwargs):
        super(VagrantHandler, self).__init__(*args, **kwargs)
        self.domain = "%s.vagrant" % self.sitename
        self.logpath = '/var/log/django/debug.log'
        self.db_user = self.db_name = self.sitename
        self.static_root = '/opt/site/static'
        self.media_root = '/opt/site/uploads'

    def is_current(self):
        return self.host == socket.gethostname()

    def get_virtualenv(self):
        return '/opt/site/.virtualenvs/site'