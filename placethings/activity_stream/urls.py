from django.conf.urls.defaults import *
handler500 = 'django.views.defaults.server_error'

urlpatterns = patterns('placethings.activity_stream.views',
    ('^/', 'global'),
)