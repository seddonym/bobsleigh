from base import InstallationHandler
import socket


class WebfactionHandler(InstallationHandler):

    def __init__(self, sitename, host, webfaction_user,
                 domain, server_email, prefix=None):
        self.host = host
        self.webfaction_user = webfaction_user
        self.domain = domain
        self.server_email = server_email
        super(WebfactionHandler, self).__init__(sitename=sitename)
        webapps_path = '/home/%s/webapps' % webfaction_user
        self.static_root = '%s/%s_static' % (webapps_path, sitename)
        self.media_root = '%s/%s_uploads' % (webapps_path, sitename)

        self.logpath = '/home/%s/logs/user/%s/django-error.log' \
                            % (self.webfaction_user, self.sitename)

        if prefix:
            prefixed_name = '%s_%s' % (prefix, self.sitename)
        else:
            prefixed_name = self.sitename
        self.db_user = self.db_name = prefixed_name


    def is_current(self):
        if self.host == socket.gethostname():
            # Check if virtualenv matches
            virtualenv_path = '/'.join(__file__.split('/')[:5])
            handler_virtualenv_path = '/home/%s/.virtualenvs/%s' % \
                                (self.webfaction_user, self.sitename)
            return virtualenv_path == handler_virtualenv_path
        return False

    def get_virtualenv(self):
        return '/home/%s/.virtualenvs/%s' % (self.webfaction_user,
                                             self.sitename)


class DevHandler(WebfactionHandler):
    default_debug = True

class LiveHandler(WebfactionHandler):
    pass
