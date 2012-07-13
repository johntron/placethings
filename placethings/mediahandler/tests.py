import unittest
from urlparse import parse_qs
from django.test.client import Client
from placethings.api.models import Thing
from placethings.settings import DOMAIN, MEDIA_ROOT

class MediaHandlerTest(unittest.TestCase):
	def testimage_handler(self):
		"""
		Verifies that placing anonymously is working
		"""
		
		things = Thing.objects.all()
		if len( things ):
			thing = things[0]
		else:
			c = Client()
			data = parse_qs( 'title=&tags=&lattitude=32.82248&longitude=-96.762986&duration=&parent=&privacy=U&lifespan=&format=txt' )
			data[ 'media' ] = open( MEDIA_ROOT + 'unittest_image.jpg' )
			c.post( '/api/place/', data )
			
			thing = Thing.objects.all()[0]

		
		uri = thing.media.replace( 'http://' + DOMAIN, '' )
		
		c = Client()
		response = c.get( uri )
		self.failUnlessEqual(response.status_code, 200)