#!/usr/bin/env python

import os
import sys

from django.core.management import execute_manager
from django.utils.importlib import import_module

PROJECT_NAME = os.path.basename(os.path.abspath(os.path.dirname(__file__)))

# use a default settings module if none was specified on the command line
DEFAULT_SETTINGS = '%s.local_settings' % PROJECT_NAME
settings_specified = any([arg.startswith('--settings=') for arg in sys.argv])
if not settings_specified and len(sys.argv) >= 2:
    print "NOTICE: using default settings module '%s'" % DEFAULT_SETTINGS
    sys.argv.append('--settings=%s' % DEFAULT_SETTINGS)

"""
This is basically a clone of the rapidsms runner, but it lives here because
we will do some automatic editing of the python path in order to avoid
sym-linking all the various dependencies that come in as submodules through
this project.
"""

if __name__ == "__main__":
    # remove '.' from sys.path (anything in this package should be referenced
    # with the PROJECT_NAME prefix)
    sys.path.pop(0)

    project = os.path.abspath(os.path.dirname(__file__))
    project_parent = os.path.dirname(project)
    local_apps = os.path.join(project, "apps")
    libs = [project_parent, local_apps]
    submodules = os.path.join(project, "submodules")
    rapidsms = os.path.join(project, "submodules", "rapidsms")
    libs += [os.path.join(rapidsms, 'lib')]
    libs += [os.path.join(rapidsms, "submodules", "django-app-settings")]
    libs += [os.path.join(rapidsms, "submodules", "django-tables", "lib")]
    packages = ['rclickatell', 'rerouter']
    for package in packages:
        sys.path.insert(0, os.path.join(submodules, package))
    for lib in libs:
        sys.path.insert(0, lib)

    settings = import_module('%s.settings' % PROJECT_NAME)
    execute_manager(settings)
