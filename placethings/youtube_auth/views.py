from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth import authenticate, login as login_user, logout as logout_user, get_backends
from django.contrib.sessions.models import Session
from placethings.youtube_auth.backends import *
from placethings.api.middleware import *
import gdata.youtube
import gdata.youtube.service
import cgi,sys

def convert_request( request ):
	request = dict( request.REQUEST.items() )
	kwargs = {}
	for k,v in request.items():
		kwargs[ str(k) ] = str(v)
	if 'format' in kwargs:
		del kwargs[ 'format' ]
	return kwargs
	
def login( request ):
	kwargs = convert_request(request)
	user = authenticate( **kwargs )	
	
	if user:
		login_user( request, user )
		return API_Success( 'id=%d' % (user.id) )
	else:
		return API_Error( 'username or password invalid' )

def logout(request):
	Session.objects.all().delete()
	logout_user(request)
	return API_Success( '' )
	
def youtube_auth( request ):
	# We may use additional OAuth domains in the future, so check to make sure it's Twitter
	if request.GET.get( 'oauth_domain', None ) == 'youtube':
		request.session[ 'oauth_domain' ] = 'youtube' # Used later on to tell how the user logged in
		backend = YoutubeBackend()
		return backend.begin_handshake( request )
	elif request.GET.get('oauth_domain', None ) == 'video':
		request.session[ 'oauth_domain' ] = 'video' # Used later on to tell how the user logged in
		request.session[ 'title' ] = request.POST.get( 'title', None )
		request.session[ 'description' ] = request.POST.get( 'description', None )
		backend = YoutubeBackend()
		return backend.begin_handshake( request )
	return HttpResponse( 'fail; invalid oauth provider' )


def youtube_callback( request ):
	if request.session[ 'oauth_domain' ] == 'youtube':
		backend = YoutubeBackend()
	else:
		return HttpResponse( 'fail; invalid oauth provider' )
	
	# It's possible that the user didn't authenticate correctly or denied access
	if backend.access_granted( request ):
		# Store Twitter tokens and fetch user info
		request = backend.finalize_handshake( request )
		request.user = backend.get_user( backend.get_user_id( request ) )
		if request.user:
			request.user.backend = 'placethings.youtube_auth.backends.YoutubeBackend' # Required by Django
			login_user( request, request.user )
			
			# Return status message if they authenticated through the API and have already finished registration on our system
			return HttpResponse( 'success; id=%d' % (request.user.id) )
		else:
			# If they haven't finished registering on Placethings, tell them to do this
			return HttpResponse( 'success; no account on placethings; complete login at /api/register' )
	else:
		request = backend.clear_session_data( request )
		Session.objects.all().delete()
		return HttpResponse( 'fail; access was denied' )

def youtube_callbackForVideo( request ):
	if request.session[ 'oauth_domain' ] == 'video':
		backend = YoutubeBackend()
	else:
		return HttpResponse( 'fail; invalid redirect url' )
	
	# It's possible that the user didn't authenticate correctly or denied access
	if backend.access_granted( request ):
		# Store Twitter tokens and fetch user info
		request = backend.finalize_handshake( request )
		return backend.upload_video( request )

def youtube_upload( request ):
	request.session['oauth_domain'] = 'place_video'
	status = request.GET.get( 'status', None )
	video_id = request.GET.get( 'id', None )
	return HttpResponseRedirect( '/test/?oauth_domain=place_video&status=%s&media=%s&type=webvideo' % (status, video_id ) )
