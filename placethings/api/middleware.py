from placethings.settings import TEMPLATE_DIRS
from django.shortcuts import get_object_or_404, render_to_response

class API_ResponseList:
	data = None
	
	def __init__(self, data):
		self.data = data

class API_User:
	data = None
	def __init__(self, data):
		self.data = data

class API_Success:
	data = {}

	def __init__(self, data):
		self.data[ 'message' ] = data

class API_Error:
	data = {}
	def __init__(self, data):
		self.data[ 'message' ] = data

class ResponseFormatter:
	def process_response( self, request, response ):
		response_class = response.__class__.__name__
		filename_lookup = {
			'API_ResponseList': 'response',
			'API_User': 'user',
			'API_Success': 'success',
			'API_Error': 'error',
		}
		if filename_lookup.has_key( response_class ):
			format = request.REQUEST.get( 'format', 'txt' )
			filename = filename_lookup[ response_class ] # if-statement above ensures no KeyError
			template = 'responses/' + filename + '.' + format
			mimetype_lookup = {
				'txt': 'text/plain',
				'xml': 'text/xml',
				'json': 'application/json',
			}
			mimetype = mimetype_lookup[ format ] if format in mimetype_lookup else mimetype_lookup[ 'txt' ]
			response = render_to_response( template, response.data, mimetype=mimetype + '; charset=UTF-8' )
		return response
