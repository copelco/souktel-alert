#!/usr/bin/env python

import os
import sys

from django.core.management import execute_manager
from django.utils.importlib import import_module

PROJECT_NAME = os.path.basename(os.path.abspath(os.path.dirname(__file__)))

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

    project_root = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    rapidsms_root = os.path.join(project_root, PROJECT_NAME, "submodules",
                                 "rapidsms")
    libs = [project_root, os.path.join(rapidsms_root, "lib")]
    libs += os.path.join(rapidsms_root, "submodules", "django-app-settings")
    libs += os.path.join(rapidsms_root, "submodules", "django-tables")
    for lib in libs:
        sys.path.insert(0, lib)

    settings = import_module('%s.settings' % PROJECT_NAME)
    execute_manager(settings)
