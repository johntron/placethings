import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'placethings.settings'
sys.path.append( '/www/placethings.com/www' )
import django.core.handlers.wsgi

ifdef( `debug', `
class Debugger:

    def __init__(self, object):
        self.__object = object

    def __call__(self, *args, **kwargs):
        import pdb, sys
        debugger = pdb.Pdb()
        debugger.use_rawinput = 0
        debugger.reset()
        sys.settrace(debugger.trace_dispatch)

        try:
            return self.__object(*args, **kwargs)
        finally:
            debugger.quitting = 1
            sys.settrace(None)


application = Debugger( django.core.handlers.wsgi.WSGIHandler() )
', `
application = django.core.handlers.wsgi.WSGIHandler()
')