from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth import authenticate, login as login_user, logout as logout_user, get_backends
from django.contrib.sessions.models import Session
from placethings.auth.backends import *
from placethings.api.middleware import *


def convert_request( request ):
	request = dict( request.REQUEST.items() )
	kwargs = {}
	for k,v in request.items():
		kwargs[ str(k) ] = str(v)
	if 'format' in kwargs:
		del kwargs[ 'format' ]
	return kwargs

def login( request, mode='' ):	
	if mode == 'web':
		if request.method == 'POST':
			# Attempt login
			kwargs = convert_request(request)
			user = authenticate( **kwargs )	
			if user:
				login_user( request, user )
				return redirect( '/things/by/%s/' % user.username )
			else:
				return HttpResponse( 'Wrong password, dummy' )
		else:
			# Show login page
			return HttpResponse( '<form method="post">Username: <input type="text" name="username" /><br />Password: <input type="password" name="password" /><br /><button type="submit">Login</button></form>' )
	else:
		kwargs = convert_request(request)
		user = authenticate( **kwargs )	
		if user:
			login_user( request, user )
			return API_Success( 'id=%d' % (user.id) )
		else:
			return API_Error( 'username or password invalid' )

def logout(request, mode=''):
	Session.objects.all().delete()
	logout_user(request)
	if mode == 'web':
		return redirect( '/' )
	else:
		return API_Success( '' )
	
def oauth_login( request ):
	'''Defers authentication to placethings.auth.backends.TwitterBackend'''
	# We may use additional OAuth domains in the future, so check to make sure it's Twitter
	if request.GET.get( 'oauth_domain', None ) == 'twitter':
		request.session[ 'oauth_domain' ] = 'twitter' # Used later on to tell how the user logged in
		backend = TwitterBackend()
		return backend.begin_handshake( request )
	return HttpResponse( 'fail; invalid oauth provider' )

def oauth_callback( request ):
	'''Twitter redirects to this handler after authenticating on their server'''
	if request.session[ 'oauth_domain' ] == 'twitter':
		backend = TwitterBackend()
	else:
		return HttpResponse( 'fail; invalid oauth provider' )
	
	# It's possible that the user didn't authenticate correctly or denied access
	if backend.access_granted( request ):
		# Store Twitter tokens and fetch user info
		request = backend.finalize_handshake( request )
		request.user = backend.get_user( backend.get_user_id( request ) )
	
		if request.user:
			request.user.backend = 'placethings.auth.backends.TwitterBackend' # Required by Django
			login_user( request, request.user )
			
			# Return status message if they authenticated through the API and have already finished registration on our system
			return HttpResponse( 'success; id=%d' % (request.user.id) )
		elif request.META[ 'HTTP_USER_AGENT' ].find( 'iPhone' ):
			# . . . unless they're on an iPhone, then send them the session key so it can do things for us
			return redirect( 'placethings://' + request.session_key )
		else:
			# If they haven't finished registering on Placethings, tell them to do this
			return HttpResponse( 'success; no account on placethings; complete login at /api/register' )
	else:
		request = backend.clear_session_data( request )
		Session.objects.all().delete()
		return HttpResponse( 'fail; access was denied' )