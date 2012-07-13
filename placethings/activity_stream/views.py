#from django.contrib.auth.models import User
from django.http import HttpResponseRedirect 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from placethings.api.models import *
#from placethings.users.models import *
#from placethings.users.forms import *
#from placethings.analytics.models import *
from placethings.api.middleware import API_ResponseList, API_User, API_Success, API_Error
from django.contrib.auth import authenticate, login as login_user, logout as logout_user, get_backends
import math

''' Decorators'''

def login_required( fn ):
	def check_login( request ):
		if not request.user.is_authenticated():
		    return API_Error( 'not logged in' )
		return fn( request )
	return check_login
					
class http_parameter_required(object):
	def __init__(self, request_method, parameter_name, human_readable_name ):
		self.request_method = request_method
		self.parameter_name = parameter_name
		self.human_readable_name = human_readable_name
				
	def __call__(self, fn ):
		def handle_request( request ):
			method = self.request_method.lower()
			lookup = {
				'post': request.POST,
				'get': request.GET,
				'files': request.FILES,
			}
			
			if 0 == len( lookup[ method ].get( self.parameter_name, '' ) ):
			    return API_Error( '%s not specified' % self.human_readable_name )
			return fn( request )
		return handle_request


''' Request handlers'''

@http_parameter_required( 'files', 'media', 'media' )
def place(request):
	for key in request.POST:
		if request.POST.get( key ) == "":
			request.POST.update( {key: None} )

	thing = Thing()
	thing.title = request.POST.get( 'title', None )
	thing.description = request.POST.get( 'description', None )
	thing.tags = request.POST.get( 'tags', None )

	if type( request.user ) is User:
		thing.author = request.user

	if request.POST.get( 'privacy', None ) is not None:
		if type( request.user ) is User:
			thing.privacy = request.POST.get( 'privacy' )
		else:
			API_Error( 'must be logged in to set privacy' )
			
	if request.POST.get( 'parent' ) is not None:
		thing.parent = Thing.objects.get( pk=request.POST.get( 'parent' ) )
		

	# thing.quantity = request.POST.get( 'quantity', None )
	thing.lattitude = float(request.POST['lattitude'])
	thing.longitude = float(request.POST['longitude'])
	
	thing.duration = request.POST.get( 'duration',None )
	if thing.parent and 0 != thing.parent:
		thing.update_parent()
	thing.save()	

	# Save file
	name = request.FILES['media'].name
	if 0 == name.count( '.' ):
		return API_Error( 'Invalid file type' )
		
	request.FILES['media'].name = str(thing.id) + name[name.rindex('.'):].lower()
	try:
		thing.save_file( request.FILES['media'] )
	except Thing_Exception as errorstr:
		return API_Error( errorstr )
		thing.delete()
		
	return API_Success( 'id=%d' % (thing.id) )