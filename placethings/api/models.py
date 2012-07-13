from django.db import models
from django.contrib.auth.models import User
from placethings.settings import MEDIA_ROOT
from placethings.settings import MEDIA_URL
import Image
import StringIO
import os

PRIVACY_CHOICES = (
	('R', 'Private'),
	('F', 'Friends only'),
	('U', 'Public'),
)

class Thing_Exception( Exception ):
	pass

class Thing( models.Model ):	
	TYPE_CHOICES = (
		('T', 'Text'),
		('I', 'Image'),
		('A', 'Audio'),
		('V', 'Video'),
	)
	title = models.CharField(max_length=255, null=True, blank=True)
	description = models.CharField(max_length=255, null=True, blank=True)
	tags = models.CharField(max_length=255, null=True, blank=True)
	author = models.ForeignKey( User, null=True, blank=True )
	media = models.CharField(max_length=255)
	type = models.CharField(max_length=1, choices=TYPE_CHOICES )
	parent = models.ForeignKey( 'self', null=True, blank=True )
	replies = models.IntegerField(default=0)
	quantity = models.IntegerField( null=True, blank=True )
	timestamp = models.DateTimeField(auto_now_add=True)
	privacy = models.CharField(max_length=1, choices=PRIVACY_CHOICES, default='U')
	lattitude = models.FloatField()
	longitude = models.FloatField()
	duration = models.IntegerField(null=True, blank=True)
	
	class Meta:
		ordering = ( '-timestamp', )

	def save_file( self, uploadedfile, type ):
		from time import strftime
		from os import makedirs
		from os.path import exists
		from cgi import escape
		
		path = strftime( '%Y/%m/%d/')
		typeLookup = {'.jpg': 'I', '.jpeg': 'I', '.png': 'I', '.gif': 'I', '.caf': 'A', '.txt': 'T', 'video': 'V' }

		if type == 'video':
			self.media = uploadedfile
			self.type = typeLookup[type]
			self.save()
		else:
			extension = uploadedfile.name[uploadedfile.name.rfind( '.' ):]
			if extension.lower() not in typeLookup:
				raise Thing_Exception( 'Invalid data type' )

			if not exists( MEDIA_ROOT + path ):
				makedirs( MEDIA_ROOT + path, 0777 )
			destination = file( MEDIA_ROOT + path + str(self.id) + extension, 'wb' )
			if extension.lower() == '.txt':
				for chunk in uploadedfile.chunks():
					destination.write( escape( chunk ) )
			else:
				for chunk in uploadedfile.chunks():
					destination.write( chunk )
			destination.close()
			self.media = MEDIA_URL + path + str(self.id) + extension
		
			self.type = typeLookup[extension.lower()]
			self.save()
	
	def update_parent( self ):
		if self.parent.replies:
			self.parent.replies = self.parent.replies + 1
		else:
			self.parent.replies = 1
		self.parent.save()
		
	def make_thumbnail( self, uploadedfile, outputpath ):
		im = Image.open( uploadedfile )
		size = 128, 128
		im.thumbnail( size )
		im.save( outputpath )


class ThingWeight( models.Model ):
    shortlat = models.FloatField()
    shortlong = models.FloatField()
    weight = models.FloatField(null=True)


class Bundle( models.Model ):
	title = models.CharField(max_length=255, null=True)
	things = models.ManyToManyField( Thing, through='BundleRelationship' )
	author = models.ForeignKey( User, null=True )
	privacy = models.CharField(max_length=1, choices=PRIVACY_CHOICES, default='U')
	timestamp = models.DateTimeField(auto_now_add=True)
	description = models.CharField(max_length=250, null=True)

class BundleRelationship( models.Model ):
	thing = models.ForeignKey( Thing )
	bundle = models.ForeignKey( Bundle )
	order = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)
