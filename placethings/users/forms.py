from django.contrib.auth.models import User
from django.forms import *
from django.core.files.uploadedfile import SimpleUploadedFile
from placethings.users.models import Profile
from placethings.settings import MEDIA_URL, MEDIA_ROOT
import urllib
import os.path

class TwitterForm:
	twitter_info = {}
	
	def get_avatar_url( self, raw_url ):
		url = raw_url.rpartition( '_normal.')
		return url[0] + '.' + url[2]
		
	def convert_info( self, info ):
		first_name = info.name
			
			
		self.twitter_info = {
			'username': info.screen_name,
			'twitter_username': info.screen_name,
			'website': info.url,
			'first_name': first_name,
			'twitter_url': self.get_avatar_url( info.profile_image_url ),
		}
		return self.twitter_info

class YoutubeForm:
	youtube_info = {}
	
	def get_avatar_url( self, raw_url ):
		'''url = raw_url.rpartition( '_normal.')'''
		return raw_url

	def get_website(self, info ):
		for link in info.link:
			if link.rel == 'related':
				return link.href
				
	def convert_info( self, info ):
		if info.first_name:
			first_name = info.first_name.text
		else:
			first_name = ''
		
		if info.last_name:
			last_name = info.last_name.text
		else:
			last_name = ''
			
		self.youtube_info = {
			'username': info.username.text,
			'youtube_username': info.username.text,
			'website': self.get_website(info),
			'first_name': first_name,
			'last_name': last_name,
			'youtube_url': self.get_avatar_url( info.thumbnail.url ),
		}
		return self.youtube_info
		
class UserForm(ModelForm):
	email = CharField( max_length=75, required=True )
	password = CharField( widget=PasswordInput )
	
	class Meta:
		model = User
		fields = ('username', 'password', 'email', 'first_name', 'last_name',)

class TwitterUserForm(ModelForm, TwitterForm):	
	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name',)
		
	message = u'You\'re logging in with Twitter, but we still need a little more info from you'	

class YoutubeUserForm(ModelForm, YoutubeForm):	
	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name',)
		
	message = u'You\'re logging in with Youtube, but we still need a little more info from you'	
	
class PartialUserForm(ModelForm):
	email = CharField( max_length=75, required=True )

	class Meta:
		model = User
		fields = ('email', 'first_name', 'last_name',)

class ProfileForm(ModelForm):
	def clean_twitter_username(self):
		un = self.cleaned_data[ 'twitter_username' ]
		if un == '':
			return None
		return un
	
	def clean_youtube_username(self):
		un = self.cleaned_data[ 'youtube_username' ]
		if un == '':
			return None
		return un

	class Meta:
		model = Profile
		exclude = ('user',)
		
class TwitterProfileForm( ModelForm, TwitterForm ):
	twitter_url = CharField( widget=HiddenInput )
	twitter_username = CharField( widget=HiddenInput )

	def clean_twitter_username(self):
		un = self.cleaned_data[ 'twitter_username' ]
		if un == '':
			return None
		return un
	

	def get_avatar( self, request ):
		if 'avatar' in request.FILES and request.FILES[ 'avatar' ] != '':
			return request

		if 'twitter_info' in request.session:
			url = self.get_avatar_url( request.session[ 'twitter_info' ].profile_image_url )
			f = urllib.urlopen( url ).read()
			f = SimpleUploadedFile(	os.path.basename( request.session[ 'twitter_info' ].profile_image_url ), f
			)
			return {
				'avatar': f, 
			}

	class Meta:
		model = Profile
		exclude = ('user')

class YoutubeProfileForm( ModelForm, YoutubeForm ):
	youtube_url = CharField( widget=HiddenInput )
	youtube_username = CharField( widget=HiddenInput )
	
	def clean_youtube_username(self):
		un = self.cleaned_data[ 'youtube_username' ]
		if un == '':
			return None
		return un
	

	def get_avatar( self, request ):
		if 'avatar' in request.FILES and request.FILES[ 'avatar' ] != '':
			return request
			
		if 'youtube_info' in request.session:
			url = request.session[ 'youtube_info' ].thumbnail.url 
			f = urllib.urlopen( url ).read()
			f = SimpleUploadedFile(	os.path.basename( request.session[ 'youtube_info' ].thumbnail.url ), f
			)
			return {
				'avatar': f, 
			}

	class Meta:
		model = Profile
		exclude = ('user')