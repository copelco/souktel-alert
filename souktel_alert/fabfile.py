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
    env.virtualenv_root = os.path.join(env.path, env.environment)


def staging():
    """ run commands on the remote staging environment """
    env.environment = 'staging'
    env.hosts = ['208.109.191.99']
    env.user = 'souktel2010'
    env.root = '/home/souktel2010'
    env.repo = 'git://github.com/copelco/souktel-alert.git'
    _setup_path()


def production():
    """ run commands on the remote production environment """
    utils.abort('Production environment is currently disabled.')


def bootstrap():
    """ bootstrap environment on remote machine """
    clone()
    create_virtualenv()
    update_requirements()


def clone():
    """ clone github repository on remote machine """
    require('root', provided_by=('production', 'staging'))
    with cd(env.root):
        run('git clone %s %s' % (env.repo, env.environment))


def create_virtualenv():
    """ Create virtual environment on remote host """
    require('code_root', provided_by=('production', 'staging'))
    args = '--clear --distribute'
    run('virtualenv %s %s' % (args, env.virtualenv_root))
    run('pip install -E %(virtualenv_root)s -U distribute' % env)


def update_requirements():
    """ Update remote Python environment """
    require('code_root', provided_by=('production', 'staging'))
    requirements = os.path.join(env.code_root, 'requirements')
    with cd(requirements):
        cmd = ['pip install']
        cmd += ['-E %(virtualenv_root)s' % env]
        cmd += ['--requirement %s' % os.path.join(requirements, 'apps.txt')]
        run(' '.join(cmd))


def pull():
    """ pull latest code to remote environment """
    require('code_root', provided_by=('production', 'staging'))
    with cd(env.path):
        run('git pull origin master')
    with cd(env.code_root):
        run('touch services/staging.wsgi')


def restart():
    """ restart apache and route """
    run('sudo -uroot service staging-route restart')
    with cd(env.code_root):
        run('touch services/staging.wsgi')
