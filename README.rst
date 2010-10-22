-*- restructuredtext -*-

souktel-alert
=============

Development Environment Setup
-----------------------------

Clone project and bootstrap virtual environment::

    ~$ git clone git@github.com:copelco/souktel-alert.git
    ~$ cd souktel-alert/souktel_alert/
    ~/souktel-alert/souktel_alert$ mkvirtualenv --distribute souktel
    (souktel)~/souktel-alert/souktel_alert$ ./bootstrap.py

Create local_settings.py file, syncdb, and runserver::

    (souktel)~/souktel-alert/souktel_alert$ cp local_settings.py.example local_settings.py
    (souktel)~/souktel-alert/souktel_alert$ ./manage.py syncdb
    (souktel)~/souktel-alert/souktel_alert$ ./manage.py runserver

Visit http://localhost:8000/ in your browser.

**Test Suite**

To run the project test suite, rename `local_test_settings.py.example` to
`local_test_settings.py` and use the following command::

    (souktel)~/souktel-alert/souktel_alert$ ./manage.py test --settings=souktel_alert.local_test_settings decisiontree group_messaging require_registration goals

Deployment
----------

Deployment uses `fabric <http://docs.fabfile.org/>`_. To see a list of the
available fab commands, run ``fab --list``::

    Available commands:

        bootstrap            bootstrap environment on remote machine
        clone                clone github repository on remote machine
        create_virtualenv    create virtual environment on remote host
        production           run commands on the remote production environment
        pull                 pull latest code to remote environment
        restart              restart apache and route
        staging              run commands on the remote staging environment
        update               pull and restart apache and route
        update_requirements  update remote Python environment

Production Environment Setup
----------------------------

To bootstrap a remote environment, modify the fabfile to include the
appropriate configuration for your server. The "staging" environment can be
used as an example for deployment setup.

**Settings**

Once deployed, create a local_settings.py file on the server that includes all
account credentials. For example::

    from souktel_alert.settings_staging import *
    
    DATABASES['default']['PASSWORD'] = '******'
    
    INSTALLED_BACKENDS['clickatell'].update({
        'user': '******',
        'password': '******',
        'api_id': '******',
        'callback': 3,
    })

**Router**

The RapidSMS route process can be initiated using a script similar to
``services/staging.sh``. In order to use start the router as a service, create
a symbolic link to the bash script in ``/etc/init.d``::

    /etc/init.d# ls -l | grep route
    lrwxrwxrwx 1 root root    59 2010-08-11 20:56 staging-route -> /home/souktel2010/staging/souktel_alert/services/staging.sh 

Now the route process can be managed via the service command (see the restat
fab command as an example)::

    $ service staging-route restart


Tagging
-------

Tags input (borrowed from django-taggit) is parsed as follows:

* If the input doesn't contain any commas or double quotes, it is simply
  treated as a space-delimited list of tag names.

* If the input does contain either of these characters:

  * Groups of characters which appear between double quotes take
    precedence as multi-word tags (so double quoted tag names may
    contain commas). An unclosed double quote will be ignored.

  * Otherwise, if there are any unquoted commas in the input, it will
    be treated as comma-delimited. If not, it will be treated as
    space-delimited.

Examples:

====================== ================================= ================================================
Tag input string       Resulting tags                    Notes
====================== ================================= ================================================
apple ball cat         ``["apple", "ball", "cat"]``      No commas, so space delimited
apple, ball cat        ``["apple", "ball cat"]``         Comma present, so comma delimited
"apple, ball" cat dog  ``["apple, ball", "cat", "dog"]`` All commas are quoted, so space delimited
"apple, ball", cat dog ``["apple, ball", "cat dog"]``    Contains an unquoted comma, so comma delimited
apple "ball cat" dog   ``["apple", "ball cat", "dog"]``  No commas, so space delimited
"apple" "ball dog      ``["apple", "ball", "dog"]``      Unclosed double quote is ignored
====================== ================================= ================================================
