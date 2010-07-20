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
    ~/souktel-alert$ cd souktel_alert/submodules/rapidsms/
    ~/souktel-alert/souktel_alert/submodule/rapidsms$ git submodule init
    ~/souktel-alert/souktel_alert/submodule/rapidsms$ git submodule update

Create a virtual environment::

    ~$ mkvirtualenv --distribute alert
    ~$ pip install django==1.1.2
    ~$ pip install -e git+http://github.com/akaihola/django-nose.git#egg=django-nose

Create local_settings.py file, syncdb, and runserver::

    ~/souktel-alert/souktel_alert$ cp local_settings.py.example local_settings.py
    ~/souktel-alert/souktel_alert$ ./manage.py syncdb
    ~/souktel-alert/souktel_alert$ ./manage.py runserver

Visit http://localhost:8000/ in your browser.
