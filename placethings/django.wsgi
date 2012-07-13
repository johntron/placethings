import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'placethings.settings'
sys.path.append( '/www/placethings.com/www' )
import django.core.handlers.wsgi


application = django.core.handlers.wsgi.WSGIHandler()
