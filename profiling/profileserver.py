import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'placethings.settings'
sys.path.append( '/www/placethings.com/www' )
from wsgiref.simple_server import make_server
from django.core.handlers.wsgi import WSGIHandler
httpd = make_server('', 8000, WSGIHandler())
httpd.serve_forever()