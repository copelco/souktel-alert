-*- restructuredtext -*-

rapidsms-example-project
========================

This is an example of a RapidSMS project, as it might be deployed
in-country. When development settles down a bit, the rapidsms package
can be bundled into a deb, rpm, .tar.gz (or whatever), and installed
into site-packages. For now, it is a submodule.

Install
-------

Clone and rename project::

    ~$ git clone git://github.com/caktus/rapidsms-example-project.git rapidsms-project
    ~$ cd rapidsms-project
    ~/rapidsms-project$ rm -rf ./.git*
    ~/rapidsms-project$ mv example_project/ myproj
    ~/rapidsms-project$ git add --all
    ~/rapidsms-project$ git commit -m "initial project layout"

Add rapidsms-core-dev as git submodule::

    ~/rapidsms-project$ git submodule add git://github.com/rapidsms/rapidsms-core-dev.git myproj/submodules/rapidsms
    ~/rapidsms-project$ git commit -m "add rapidsms submodule"

rapidsms-core-dev also contains submodules of its own, so init and update those as well::

    ~/rapidsms-project$ cd myproj/submodule/rapidsms
    ~/rapidsms-project/myproj/submodule/rapidsms$ git submodule init
    ~/rapidsms-project/myproj/submodule/rapidsms$ git submodule update

Now just syncdb and start the server::
    
    ~/rapidsms-project$ ./manage.py syncdb
    ~/rapidsms-project$ ./manage.py runserver

Visit http://localhost:8000/ in your browser.
