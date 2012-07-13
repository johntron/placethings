from django.conf.urls.defaults import *
handler500 = 'django.views.defaults.server_error'

urlpatterns = patterns('placethings.api.views',
    ('place/', 'place'),
    ('correct/', 'correct'),
    ('delete/', 'delete'),
    ('take/', 'take'),
    ('view/', 'view'),
    ('list-bundle/', 'list_bundle'),
    ('create-bundle/', 'create_bundle'),
    ('add-to-bundle/', 'add_to_bundle'),
    ('remove-from-bundle/', 'remove_from_bundle'),
    ('reorder-thing-in-bundle/', 'reorder_thing_in_bundle'),
    ('test/', 'test'),
    ('register/', 'register'),
    ('update-profile/', 'update_profile'),
    ('get-profile/', 'get_profile'),    
)

urlpatterns += patterns('placethings.auth.views',
    ('oauth_login/', 'oauth_login'),
    ('oauth_callback/', 'oauth_callback'),
    ('login/', 'login'),
    ('logout/', 'logout'),
)

urlpatterns += patterns('placethings.youtube_auth.views',
    ('youtube_auth/', 'youtube_auth'),
    ('youtube_callback/', 'youtube_callback'),
    ('login/', 'login'),
    ('logout/', 'logout'),
    ('youtube_upload/', 'youtube_upload'),
    ('youtube_callbackForVideo/', 'youtube_callbackForVideo'),
)