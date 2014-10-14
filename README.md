Bobsleigh
=========

Helps write less code when deploying Django installations.

Note this is not ready for production use yet.

(DOCUMENTATION INCOMPLETE)

Overview
--------

- runners
- setting handlers


Runners
-------

- manage.py
- wsgi.py


Settings handlers
-----------------

These could be called 'Class Based Settings', or 'the Other True Way'.

The principle behind it is to be more DRY when writing settings files.  Conceptually there are
the following key aspects of settings in a project:

- Settings common to multiple projects (associated with a developer's individual methodology,
or common hosting patterns).
- Settings common to all installations of a one project
- Settings common to some installations of one project (e.g. stage and production may want similar settings).
- Settings specific to installations, but are convenient to manage using version control within the main code repository.
- Sensitive settings that should not be included in version control (passwords, SECRET_KEY, api keys etc.)


Project settings
----------------

These should be in settings/project.py.

The settings should generally import from a default settings file.  This can either be Django's default global settings file,
or a settings file that you use across different projects.

from django.conf.global_settings import * 

# Override settings here

Or:

from myconfigpackage.settings import *

# Override settings here


