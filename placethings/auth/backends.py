from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from oauthtwitter import OAuthApi
from placethings.users.models import *
from placethings.settings import TWITTER_KEY, TWITTER_SECRET

class TwitterBackend_Exception( Exception ):
	pass

class TwitterBackend:
	''' Authentication backend used to authenticate with Twitter'''
	session = None
	
	def uses_handshake(self):
		''' I don't think this is used'''
		return True
		
	def authenticate( self, request ):
		if 'twitter_info' in request.session:
			return get_user( request.session[ 'twitter_info' ].screen_name )
		return None
		
	def access_granted( self, request ):
		if 'denied' in request.GET.keys():
			# Uh oh :(
			return False
		else:
			return True
		
	def finalize_handshake( self, request ):
		twitter = OAuthApi( TWITTER_KEY, TWITTER_SECRET, request.session[ 'request_token' ] )
		request.session[ 'access_token' ] = twitter.getAccessToken()
		twitter = OAuthApi( TWITTER_KEY, TWITTER_SECRET, request.session[ 'access_token' ] )
		user_info = twitter.GetUserInfo()
		request.session[ 'twitter_info' ] = user_info
		return request		
		
	def begin_handshake( self, request ):
		twitter = OAuthApi( TWITTER_KEY, TWITTER_SECRET )
		request.session[ 'request_token' ] = twitter.getRequestToken()
		redirect_url = twitter.getAuthorizationURL(request.session[ 'request_token' ] )
		redirect_url = redirect_url[0:redirect_url.find( 'oauth_callback=None' )-2]
		redirect_url = redirect_url.replace( 'http://twitter.com/oauth/authorize', 'http://twitter.com/oauth/authenticate' )
		return HttpResponseRedirect( redirect_url )
		
	def clear_session_data( self, request ):
		del request.session[ 'request_token' ]
		del request.session[ 'access_token' ]
		del request.session[ 'twitter_info' ]
		return request
		
	def get_user_id( self, request ):
		if 'twitter_info' in request.session:
			try:
				profile = Profile.objects.get(twitter_username=request.session[ 'twitter_info' ].screen_name)
				return profile.user
			except Profile.DoesNotExist:
				return None
		
	def get_user( self, user_id ):
		try:
			profile = Profile.objects.get(user=user_id)
		except Profile.DoesNotExist:
			return None
		user = User.objects.get(profile=profile)
		user.backends = 'placethings.auth.backends.TwitterBackend'
		return user
		

class FacebookConnectBackend:
	def uses_handshake():
		return True
		
	def authenticate( self, request ):
		pass

	def get_user( self, user_id ):
		return None
