-*- restructuredtext -*-

souktel-alert
=============

Development Environment Setup
-----------------------------

Clone project and setup git submodules::

    ~$ git clone git@github.com:copelco/souktel-alert.git
    ~$ cd souktel-alert/
    ~/souktel-alert$ git submodule init
    ~/souktel-alert$ git submodule update
    ~/souktel-alert$ cd souktel_alert/submodule/rapidsms
    ~/souktel-alert/souktel_alert/submodule/rapidsms$ git submodule init
    ~/souktel-alert/souktel_alert/submodule/rapidsms$ git submodule update

Create local_settings.py file, syncdb, and runserver::

    ~/souktel-alert/souktel_alert$ cp local_settings.py.example local_settings.py
    ~/souktel-alert/souktel_alert$ ./manage.py syncdb
    ~/souktel-alert/souktel_alert$ ./manage.py runserver

Visit http://localhost:8000/ in your browser.
