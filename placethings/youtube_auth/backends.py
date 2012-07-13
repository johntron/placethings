from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.http import HttpResponse
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from placethings.users.models import *
from placethings.settings import DOMAIN
from xml.etree.ElementTree import ElementTree
import xml
import gdata.youtube
import gdata.youtube.service
import cgi,sys

YOUTUBE_UPLOADTOKEN_URI = 'http://gdata.youtube.com/feeds/api/users/default?v=2'
yt_service = gdata.youtube.service.YouTubeService()

class YoutubeBackend_Exception( Exception ):
	pass

def GetAuthSubUrl():
	next = 'http://' + DOMAIN + '/api/youtube_callback'
  	scope = 'http://gdata.youtube.com/'
 	secure = False
 	session = True
	return yt_service.GenerateAuthSubURL(next, scope, secure, session)
	
def GetAuthSubUrlForVideo():
	next = 'http://' + DOMAIN + '/api/youtube_callbackForVideo'
  	scope = 'http://gdata.youtube.com/'
 	secure = False
 	session = True
	return yt_service.GenerateAuthSubURL(next, scope, secure, session)
		
class YoutubeBackend:
	''' Authentication backend used to authenticate with Youtube'''
	session = None
	
	def uses_handshake(self):
		''' I don't think this is used'''
		return True
		
	def authenticate( self, request ):
		if 'youtube_info' in request.session:
			return get_user( request.session[ 'youtube_info' ].username.text )
		return None
		
	def access_granted( self, request ):
		if 'denied' in request.GET.keys():
			# Uh oh :(
			return False
		else:
			return True
		
	def finalize_handshake( self, request ):
		authsub_token = gdata.auth.extract_auth_sub_token_from_url(request.get_full_path())
		yt_service.SetAuthSubToken(authsub_token)
		authsub_token = yt_service.UpgradeToSessionToken()
		request.session[ 'authsub_token' ] = authsub_token
		user_info =  yt_service.AuthSubTokenInfo()
		user_info =  yt_service.GetYouTubeUserEntry(uri=YOUTUBE_UPLOADTOKEN_URI)
		request.session['youtube_info'] = user_info
		return request		

		
	def begin_handshake( self, request ):
		yt_service.developer_key = 'AI39si6x_3f9NAM_NPGpy3ps7LuvIF7Lvxo0aaJ6wv0P2QjoVzJ3QvH6Xk658Q2gALDrLhf2Vztni5NNk8SCOD0SOwgZrvxqTA'
		if request.GET.get( 'oauth_domain', None ) == 'youtube':
			authSubUrl = GetAuthSubUrl()
		elif request.GET.get( 'oauth_domain', None ) == 'video':
			authSubUrl = GetAuthSubUrlForVideo()
		return HttpResponseRedirect( authSubUrl )
		
	def clear_session_data( self, request ):
		del request.session[ 'authsub_token' ]
		del request.session[ 'youtube_info' ]
		return request
		
	def get_user_id( self, request ):
		if 'youtube_info' in request.session:
			try:
				profile = Profile.objects.get(youtube_username=request.session[ 'youtube_info' ].username.text)
				return profile.user
			except Profile.DoesNotExist:
				return None
		
	def get_user( self, user_id ):
		try:
			profile = Profile.objects.get(user=user_id)
		except Profile.DoesNotExist:
			return None
		user = User.objects.get(profile=profile)
		user.backends = 'placethings.youtube_auth.backends.youtubeBackend'
		return user
	
		
	def upload_video( self, request ):
		# prepare a media group object to hold our video's meta-data
		my_media_group = gdata.media.Group(
			title=gdata.media.Title(text=request.session[ 'title' ]),
  			description=gdata.media.Description(description_type='plain',
  			text= request.session[ 'description' ]),
  			keywords=gdata.media.Keywords(text='place, things, placethings'),
  			category=gdata.media.Category(
      		text='Travel',
      		scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
      		label='Travel'),
  			player=None
		)


		# create the gdata.youtube.YouTubeVideoEntry to be uploaded
		video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
		response = yt_service.GetFormUploadToken(video_entry)
		
		post_url = response[0]
		youtube_token = response[1]
		next = 'http://placethings.com/api/youtube_upload/'
		return redirect( '/test/?post_url=%s&youtube_token=%s&next=%s&oauth_domain=youtube' % (post_url, youtube_token, next ) )


		