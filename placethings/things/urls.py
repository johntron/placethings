from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('placethings.things.views',
    (r'^by/(?P<username>[\da-zA-Z\d_-]+)', 'things_by_user' ),
    (r'^id/(?P<id>\d+)', 'thing_with_id' ),
	(r'^in/(?P<region>[\da-zA-Z\d_-]+)', 'things_in_region' ),
    (r'^newest/', 'newest_things'),
)
