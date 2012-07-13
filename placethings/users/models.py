from django.db import models
from django.contrib.auth.models import User
from placethings.api.models import Thing
from django.db.models.signals import post_save
from placethings.settings import MEDIA_URL

def has_access( object, user ):
	if object.privacy == 'U':
		return True
		
	if object.privacy == 'F':
		return False
		
	if object.privacy == 'R' and user == object.author:
		return True
		
	return False
	
def filter_access( objects, user ):
	from django.contrib.auth.models import AnonymousUser
	from django.db.models import Q

	# TODO: Filter based on friendship once a friend system is created
	if type(user) is AnonymousUser:
		return objects.exclude( privacy='R' )
		
	return objects.exclude( Q(privacy='R'), ~Q(author=user) )


def get_avatar_path(instance, filename):
	from time import strftime
	path = strftime( 'avatars/%Y/%m/%d')
	id = instance.user.id
	extension = filename[filename.rfind( '.' ) + 1:]
	path = '%s/%d.%s' % (path, id, extension )
	return path

class Profile( models.Model ):
	user = models.ForeignKey( User, unique=True )
	avatar = models.ImageField(upload_to=get_avatar_path, null=True, blank=True)
	website = models.URLField(verify_exists=True, null=True, blank=True)
	twitter_username = models.CharField( max_length=255, unique=True, blank=True, null=True )
	youtube_username = models.CharField( max_length=255, unique=True, blank=True, null=True )
	
class Inventory( models.Model ):
	user = models.ForeignKey( User )
	thing = models.ForeignKey( Thing )
	timestamp = models.DateTimeField(auto_now_add=True)