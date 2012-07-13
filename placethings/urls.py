from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	 (r'^api/', include('placethings.api.urls')),
	 (r'^login/', 'placethings.auth.views.login', {'mode': 'web'} ),
     (r'^logout/', 'placethings.auth.views.logout', {'mode': 'web'} ),
	 (r'^things/', include('placethings.things.urls')),
     (r'^test/', 'placethings.api.views.test'),
     (r'^media/(?P<path>(avatars/)?\d{4}/\d{2}/\d{2}/)(?P<id>\d+)-(?P<width>\d+)x(?P<height>\d+).(?P<extension>(png|jpe?g|gif))$', 'placethings.mediahandler.views.imagehandler'),
	 (r'^admin/', admin.site.urls),
	 (r'^min/f=(?P<url>.+)$', 'placethings.min.views.minify'),
	 #(r'^(?P<username>[\da-zA-Z\d_-]\w+)/', 'placethings.things.views.things_by_user'),    

)
