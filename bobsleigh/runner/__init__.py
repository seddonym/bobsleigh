from ..conf import handler


def manage_environment():
    "Sets up the command-line environment."
    handler.setup()
    from django.core.management import execute_from_command_line
    import sys
    execute_from_command_line(sys.argv)


def wsgi_environment():
    "Sets up the wsgi environment."
    handler.setup()

    virtualenv_path = handler.config.virtualenv_path
    if virtualenv_path:
        # This makes sure the virtualenv is activated
        # for any virtualenv environments
        import os
        import site
        site.addsitedir(os.path.join(virtualenv_path, 'lib/%s/site-packages'
                                                    % handler.config.python))
        activate_this = os.path.join(virtualenv_path, 'bin/activate_this.py')
        execfile(activate_this, dict(__file__=activate_this))

    if handler.config.monitor:
        import monitor
        monitor.start(interval=1.0)

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    return application
