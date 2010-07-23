from __future__ import with_statement

import os
import sys
import tempfile

from fabric.api import *
from fabric.contrib import files, console, project
from fabric import utils


# use this instead of os.path.join since remote OS might differ from local
PATH_SEP = '/'
env.project = 'souktel_alert'
# remove -l from env.shell, "mesg n" in ~/.profile was causing issues
# see Why do I sometimes see ``err: stdin: is not a tty``?
# http://github.com/bitprophet/fabric/blob/master/FAQ
env.shell = '/bin/bash -c'


def _setup_path():
    env.path = PATH_SEP.join((env.root, env.environment))
    env.code_root = PATH_SEP.join((env.path, env.project))


def staging():
    """ Run commands on the remote staging environment """
    env.environment = 'staging'
    env.hosts = ['208.109.191.99']
    env.user = 'souktel2010'
    env.root = '/home/souktel2010'
    env.repo = 'git://github.com/copelco/souktel-alert.git'
    _setup_path()


def production():
    """ Run commands on the remote production environment """
    utils.abort('Production environment is currently disabled.')


def bootstrap():
    """ bootstrap environment on remote machine """
    clone()
    update_submodules()


def clone():
    """ clone github repository on remote machine """
    require('root', provided_by=('production', 'staging'))
    with cd(env.root):
        run('git clone %s %s' % (env.repo, env.environment))


def update_submodules():
    """ update git submodules in remote environment """
    require('code_root', provided_by=('production', 'staging'))
    with cd(env.path):
        run('git submodule init')
        run('git submodule update')
    rapidsms = PATH_SEP.join((env.code_root, 'submodules/rapidsms'))
    with cd(rapidsms):
        run('git submodule init')
        run('git submodule update')


def pull():
    """ pull latest code to remote environment """
    require('code_root', provided_by=('production', 'staging'))
    with cd(env.path):
        run('git pull origin master')
