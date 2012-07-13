import unittest
from urlparse import parse_qs
from django.test.client import Client
from placethings.settings import MEDIA_ROOT

class APITest(unittest.TestCase):
	def testanon_placing(self):
		"""
		Verifies that placing anonymously is working
		"""
		
		c = Client()
		data = parse_qs( 'title=&tags=&lattitude=32.82248&longitude=-96.762986&duration=&parent=&privacy=U&lifespan=&format=txt' )
		data[ 'media' ] = open( MEDIA_ROOT + 'unittest_image.jpg' )
		response = c.post( '/api/place/', data )
		self.failUnlessEqual(response.status_code, 200)
		
		data = parse_qs( 'title=&tags=&lattitude=32.82248&longitude=-96.762986&duration=&parent=&privacy=U&lifespan=&format=txt' )
		data[ 'media' ] = open( MEDIA_ROOT + 'unittest_audio.caf' )
		response = c.post( '/api/place/', data )
		self.failUnlessEqual(response.status_code, 200)
		
		data = parse_qs( 'title=&tags=&lattitude=32.82248&longitude=-96.762986&duration=&parent=&privacy=U&lifespan=&format=txt' )
		data[ 'media' ] = open( MEDIA_ROOT + 'unittest_text.txt' )
		response = c.post( '/api/place/', data )
		self.failUnlessEqual(response.status_code, 200)
		
				
	def testanon_viewing(self):
		"""
		Verifies that viewing anonymously is working
		"""
		
		c = Client()
		response = c.get( '/api/view/?id=&maxdist=&lattitude=32.82248&longitude=-96.762986&maxage=&minage=&limit=&offset=&type=&order=&parent=&format=txt' )		  
		self.failUnlessEqual(response.status_code, 200)
		self.failUnless(len(response.context['things']))
		
		response = c.get( '/api/view/?id=1&maxdist=&lattitude=32.82248&longitude=-96.762986&maxage=&minage=&limit=&offset=&type=&order=&parent=&format=txt' )		  
		self.failUnlessEqual(response.status_code, 200)
		self.failUnless(len(response.context['things']))