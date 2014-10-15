Bobsleigh
=========

Helps write less code when deploying Django installations.

(Note this is currently experimental, so you may not want to use it for production yet.)

Overview
--------

Getting a Django project up and running can involve a lot of boilerplate code.  This includes manage.py, wsgi.py, and settings files.  Settings files particularly can get messy and difficult to maintain.  Bobsleigh helps you be more DRY in your projects by providing two key, interlinked utilities:

1. Runners

   Runners provide ways of running your project without having to write much code.  At the moment there are two runners, one for the command line (used in manage.py) and one for wsgi (used in wsgi.py).  These work hand in hand with Installation handlers to get your project working.

2. Installation handlers

   Bobsleigh's `InstallationHandler` class could be thought of as allowing 'class based settings', in the same way as `django.views.generic.base.View` gives us class based views.  They help to encapsulate common patterns of settings so that you can write less code.  For example, you may have a standard way of configuring all your local development sites with Django.  Bobsleigh helps you to write a class that encapsulates this behaviour, which you can then use across different projects.

Conceptually there are the following key aspects of settings in a project:

- Settings common to multiple projects (associated with a developer's individual methodology,
or common hosting patterns).
- Settings common to all installations of a one project
- Settings common to some installations of one project (e.g. stage and production may want similar settings).
- Settings specific to installations, but are convenient to manage using version control within the main code repository.
- Sensitive settings that should not be included in version control (passwords, SECRET_KEY, api keys etc.)

Bobsleigh provides a standard way of handling these different settings requirements.

Quick start
===========

Getting Bobsleigh set up involves:

- Setting up all your standard infrastructure - databases, web server, media folders, virtualenv etc.  Everything that isn't related to the codebase itself.
- Installing bobsleigh: `pip install bobsleigh`
- Adding a file structure to your project as below.

File structure
--------------

The file structure of a Bobsleigh project should be as follows:
   
       myproject
           __init__.py
           manage.py
           wsgi.py
           settings
               __init__.py
               project.py
               installations.py
               secret.py
           (other packages, files etc. as normal)

The project.py file
-------------------

This is a normal settings file, containing all the settings common to all installations of your project.  Typically this will contain INSTALLED_APPS and a few other settings that are project-focused rather than installation-focused.  Try to be as minimal as possible - most of the heavy lifting should be done by the InstallationHandlers.

Usually you will want to import Django's default settings at the top of the file:

    from django.conf.global_settings import *

Though if you have many settings that you use across multiple projects, you can import those instead.

    from mysettingspackage.settings import *

The secret.py file
------------------

This is also a normal settings file, but should be used for anything sensitive that should not be put in version control.  It will be automatically imported.

To set the database password, specify `DB_PASS`, and this will automatically be added to the `DATABASES['default']['PASSWORD']` setting.

The installations.py file
-------------------------

In this file, you specify a list of InstallationHandler instances in a list named INSTALLATIONS.  More about installation handlers below, but it will look something like this:

    from bobsleigh.handlers import InstallationHandler

    INSTALLATIONS = [

        # Local installation
        InstallationHandler(sitename='mysite',
                            domain='mysite.localhost',
                            host='localhost',                            
                            debug=True,
                            db_name='mysite'
                            db_user='mysite',
                            monitor=True),

        # Dev installation
        InstallationHandler(sitename='dev',
                            domain='dev.mysite.com',
                            host='mydevserver',
                            debug=True,
                            db_name='mysite_dev'
                            db_user='mysite_dev'),

        # Live installation
        InstallationHandler(sitename='live',
                            domain='mysite.com',
                            host='myliveserver',
                            db_name='mysite_live'
                            db_user='mysite_live'),
    ]

manage.py
---------

Your manage.py file just needs to contain this:

    #!/usr/bin/env python
    if __name__ == "__main__":
        from bobsleigh.runner import manage_environment
        manage_environment()

wsgi.py
-------

If you're using wsgi, the wsgi.py file is simply:

    from bobsleigh.runner import wsgi_environment
    application = wsgi_environment()


Installation handlers in more detail
====================================

The basic installation handler `bobsleigh.handlers.InstallationHandler` is a pretty naive handler and you will have to tell it a lot about your installation.  Really, it is designed to be extended to fit your deployment patterns, and used across projects, but it's useful to see how it behaves by default.

Required keyword arguments
--------------------------

- domain: Used to set a setting called DOMAIN, which will also be added to ALLOWED_HOSTS.
- host: The hostname of the machine the installation is on.  This is used to detect which InstallationHandler to use.

Optional keyword arguments
--------------------------

- debug: Whether or not to put the site in debug mode.  This also sets TEMPLATE_DEBUG and THUMBNAIL_DEBUG to the same value.  (Default: False).
- monitor: Whether or not the wsgi application should monitor code changes and reload if there are changes.  Only appropriate for local development.  (Default: False)
- virtualenv_path: Path to the virtualenv, if there is one. 
- log_path: Path to the directory to put log files in.
- project_path: Path to where the project is in the filesystem.
- static_path: Path to static files.
- media_path: Path to media files.
- db_name: Database name.
- db_user: Database user.
- python: String of the python version.  (Default: 'python2.7')
- server_email: Used to set the SERVER_EMAIL and DEFAULT_FROM_EMAIL settings.
- email_host_user: Used to set the EMAIL_HOST_USER setting.
- email_host: Used to set the EMAIL_HOST setting.
- extra_settings: dictionary of other settings to set, e.g. {'MY_CUSTOM_SETTING': 'foo'}

Custom installation handlers
============================

Custom installation handlers allow you to cut down dramatically on the amount of code you write.  Typically, you do this by subclassing InstallationHandler
and then overriding one or more of the following methods:

get_required_kwargs()
---------------------

This method returns a tuple of required kwarg names.  These will be enforced by the InstallationHandler, and the values added to the `config` attribute on the installation handler.

For example, this installation handler would require a sitename kwarg.

    class MyInstallationHandler(InstallationHandler):

        def get_required_kwargs(self):
            required_kwargs = super(InstallationHandler, self)\
                                                        .get_required_kwargs()
            required_kwargs += 'sitename'
            return required_kwargs

get_optional_kwargs()
---------------------

This method returns a dictionary of optional kwargs, with their default values.  These will be added to the `config` attribute on the installation handler.

For example, this installation handler would allow a 'host' kwarg, setting it to 'localhost' if it is not provided.

    class MyInstallationHandler(InstallationHandler):

        def get_optional_kwargs(self):
            optional_kwargs = super(InstallationHandler, self)\
                                                        .get_optional_kwargs()
            optional_kwargs.update({
                'host': 'localhost',
            })
            return optional_kwargs

get_config_patterns()
---------------------

This powerful method returns a dictionary of string patterns, keyed with the name of the config attribute that it should be used for.  It allows you to use other config attributes to form new ones.

For example, this installation handler would specify the project_path based on the domain kwarg.

    class MyInstallationHandler(InstallationHandler):

        def get_config_patterns(self):
            patterns = super(InstallationHandler, self)\
                                                        .get_config_patterns()
            patterns.update({
                'project_path': '/opt/sites/%(domain)s',
            })
            return patterns

adjust()
--------

When the combination of get_required_kwargs(), get_optional_kwargs() and get_config_patterns() is not enough,
this method can be used to adjust the settings further, based on the config attribute.  This would usually involve editing a
_settings dictionary on the object.

For example, to add a new setting called MESSAGE_QUEUE_DOMAIN based on the domain, but prefixed with 'queue.':

    class MyInstallationHandler(InstallationHandler):
    
        def adjust(self):
            super(MyInstallationHandler, self).adjust()
            self._settings['MESSAGE_QUEUE_DOMAIN'] = 'queue.%s' % self.config.domain
            

is_current()
------------

This method is how Bobsleigh knows which installation handler to use.  It iterates through the 
INSTALLATIONS list in installations.py, and will run is_current() on each instantiated 
InstallationHandler.  The first one to return True, will be used.

The default way it tests is using the host name, but if there are multiple installations of a project on
a single host, you will need to subclass the method.

For example, this method checks the virtual env path it's running in too, though it's specific
to where the code is running from on this particular host:

    def is_current(self):
        if self.host == socket.gethostname():
            # Check if virtualenv matches
            virtualenv_path = '/'.join(__file__.split('/')[:5])
            return virtualenv_path == self.config.virtualenv_path
        return False

Conclusion
==========

With a little initial setup you can put together a suite of InstallationHandlers that you can drop in easily to multiple
projects, and handle settings in a much simpler way.

A good way to use Bobsleigh would be to write handlers for Local, Development, Stage and Live that match your standard ways
of deploying projects.

Feedback very welcome!
