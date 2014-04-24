from base import InstallationHandler
import socket


class WebfactionHandler(InstallationHandler):

    def __init__(self, sitename, host, webfaction_user,
                 domain, server_email):
        self.host = host
        self.webfaction_user = webfaction_user
        self.domain = domain
        self.server_email = server_email

        super(WebfactionHandler, self).__init__(sitename=sitename)

    def is_current(self):
        if self.host == socket.gethostname():
            # Check if project path matches
            project_path = '/'.join(__file__.split('/')[:-4])
            handler_project_path = '/home/%s/webapps/%s' % \
                                (self.webfaction_user, self.sitename)
            print project_path
            print handler_project_path
            return project_path == handler_project_path
        return False


class DevHandler(WebfactionHandler):
    default_debug = True


class LiveHandler(WebfactionHandler):
    pass
