import os
import sys
import site

sp = '/home/souktel2010/staging/staging/lib/python2.6/site-packages'
site.addsitedir(sp)

#Calculate the project path based on the location of the WSGI script.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(PROJECT_ROOT))

SHOW_UPGRADE_MESSAGE = False
ADMIN_IPS = ('127.0.0.1', )
UPGRADE_FILE = os.path.join(PROJECT_ROOT, 'media', 'html', 'upgrade.html')
ERROR_FILE = os.path.join(PROJECT_ROOT, 'media', 'html', 'server_error.html')

os.environ['DJANGO_SETTINGS_MODULE'] = 'chicago_hopes.local_settings'


try:
    import django.core.handlers.wsgi
    django_app = django.core.handlers.wsgi.WSGIHandler()
except:
    import traceback
    traceback.print_exc(file=sys.stderr)
    django_app = None


def static_response(environ, start_response, status, file, default_message=''):
    response_headers = [('Retry-After', '120')] # Retry-After: <seconds>
    if os.path.exists(file):
        response_headers.append(('Content-type', 'text/html'))
        response = open(file).read()
    else:
        response_headers.append(('Content-type', 'text/plain'))
        response = default_message
    start_response(status, response_headers)
    return [response]


def server_error(environ, start_response):
    status = '500 Internal Server Error'
    msg = 'Internal Server Error...please retry in a few minutes.'
    return static_response(environ, start_response, status, ERROR_FILE, msg)


def upgrade_in_progress(environ, start_response):
    if environ['REMOTE_ADDR'] in ADMIN_IPS and django_app:
        return django_app(environ, start_response)

    if environ['REQUEST_METHOD'] == 'GET':
        status = '503 Service Unavailable'
    else:
        status = '405 Method Not Allowed'

    msg = 'Upgrade in progress...please retry in a few minutes.'
    return static_response(environ, start_response, status, UPGRADE_FILE, msg)


class LoggingMiddleware(object):

    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        try:
            return self.__application(environ, start_response)
        except:
            import traceback
            traceback.print_exc(file=sys.stderr)
            return server_error(environ, start_response)


if SHOW_UPGRADE_MESSAGE:
    application = upgrade_in_progress
elif not django_app:
    application = server_error
else:
    application = LoggingMiddleware(django_app)
