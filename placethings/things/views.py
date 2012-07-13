from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.models import User
from placethings.api.models import *
from placethings.users.models import *

def things_by_user(request, username):
	vars = {}
	try:
		vars[ 'user' ] = User.objects.get(username=username)
		vars[ 'request' ] = request
		vars[ 'things' ] = Thing.objects.filter( author=vars[ 'user' ] )
		vars[ 'things' ] = filter_access( vars[ 'things' ], vars[ 'user' ] )[:20]
		
		template = 'things_by_user/'	
		return render_to_response( 	template + request.GET.get( 'mode', 'full' ) + '.htm', vars )
	
	except User.DoesNotExist:
		return HttpResponse( 'User does not exist' )

def thing_with_id( request, id ):
	pass
		
def things_in_region( request, region ):
	pass
		
def newest_things(request):
	vars = {}
	vars[ 'things' ] = Thing.objects.order_by( '-timestamp' )[0:100]

	template = 'newest_things/'
	return render_to_response( 	template + request.GET.get( 'mode', 'full' ) + '.htm', vars )