from django.contrib.auth.models import User
from django.http import HttpResponseRedirect 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from placethings.api.models import *
from placethings.users.models import *
from placethings.users.forms import *
from placethings.analytics.models import *
from placethings.api.middleware import API_ResponseList, API_User, API_Success, API_Error
from django.contrib.auth import authenticate, login as login_user, logout as logout_user, get_backends
from django.db.models import F
from decimal import *
import math
import os

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


def place(request):
	for key in request.POST:
		if request.POST.get( key ) == "":
			request.POST.update( {key: None} )
	
	if request.POST.get('type'):
		media_type = request.POST.get('type')
	else:
		media_type = ''
	
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
			API_Error( 'must be logged in to set privacy') 
			
	if request.POST.get( 'parent' ) is not None:
		thing.parent = Thing.objects.get( pk=request.POST.get( 'parent' ) )
		

	# thing.quantity = request.POST.get( 'quantity', None )
	thing.lattitude = float(request.POST['lattitude'])
	thing.longitude = float(request.POST['longitude'])
	
	thing.duration = request.POST.get( 'duration',None )
	if thing.parent and 0 != thing.parent:
		thing.update_parent()
	thing.save()	
	
	if  media_type == 'webvideo':
		name = "http://www.youtube.com/watch?v=" + request.POST.get('media', None)
		request.session['oauth_domain'] = ''
		thing.save_file (name,'video')
	elif media_type == 'V':
		name = request.POST.get('media', None)
		thing.save_file (name,'video')
	elif request.FILES.get( 'media', None ):
		# Save file
		name = request.FILES['media'].name
		if 0 == name.count( '.' ):
			return API_Error( 'Invalid file type' )
		request.FILES['media'].name = str(thing.id) + name[name.rindex('.'):].lower()
		try:
			thing.save_file( request.FILES['media'], 'other' )
		except Thing_Exception as errorstr:
			thing.delete()
			return API_Error( errorstr )			
	else:
		thing.delete()
		return API_Error( 'No media' )
		

	slat,slng = float('%3.3f' % thing.lattitude), float('%3.3f' % thing.longitude)
	
	# Calculate short lat and short long
	
	region_lat = [None]*9
	region_lng = [None]*9
	wt = [None]*9
	
	#assign the centre lat and lng values of the region
	
	#assigning lat and lng values to the 9 regions created
	for i in range(0, 3):
		region_lat[i] = slat - 0.001
		region_lng[i*3] = slng - 0.001
	
	j = 1
	for i in range(3,6):
		region_lat[i] = slat
		region_lng[j] = slng
		j = j + 3
	
	j = 2
	for i in range(6,9):
		region_lat[i] = slat + 0.001
		region_lng[j] = slng + 0.001
		j = j + 3
	
	#assigning hardcoded weight values to the above created 9 regions
	j = 1
	k = 0
	for i in range(0,4):
		wt[j] = 0.001
		temp = 0.001/1.414
		wt[k] = float('%5.5f' % temp)
		j = j + 2
		if k == 2:
			k = 4
			#assigning maximum weight to the centre of the the region
			wt[k] = 0.002 
		k = k + 2
	
	for i in range(0,9):
		try:
			tw = ThingWeight.objects.get(shortlat = region_lat[i], shortlong  = region_lng[i])
			tw.weight = float('%5.5f' % ((tw.weight or 0.0) + (wt[i] or 0.0)))
			tw.save()
		except ThingWeight.DoesNotExist:
			tw = ThingWeight.objects.create(shortlat = region_lat[i], shortlong = region_lng[i], weight = wt[i])
			tw.save()
	
	return API_Success( 'id=%d' % (thing.id) )

@login_required
@http_parameter_required( 'post', 'id', 'Thing ID' )
def correct(request):
	try:
		thing = Thing.objects.get( id=request.POST.get( 'id' ) )
	except Thing.DoesNotExist:
		return API_Error( 'thing with id %s does not exist' % request.POST.get( 'id' ) )

	if thing.author is None:
		return API_Error( 'thing was placed anonymously and cannot be modified' )
		
	if thing.author != request.user:
		return API_Error( 'only the original author can correct the location of a thing' )

	old = thing.lattitude, thing.longitude
	new = float(request.POST['lattitude']), float(request.POST['longitude'])
	distance = math.sqrt(math.pow(69.1 * (old[0] - new[0]), 2) + math.pow(69.1 * (old[1] - new[1]) * math.cos(old[0]/57.3), 2))
	if distance < 3:
		thing.lattitude, thing.longitude = new
		thing.save()

	return API_Success( 'id=%d' % (thing.id) )


@login_required
@http_parameter_required( 'post', 'id', 'Thing ID' )
def delete(request):
	try:
		thing = Thing.objects.get( id=request.POST.get( 'id' ) )
	except Thing.DoesNotExist:
		return API_Error( 'thing with id %s does not exist' % request.POST.get( 'id' ) )


	if thing.author is None:
		return API_Error( 'thing was placed anonymously and cannot be deleted' )
		
	if thing.author != request.user:
		return API_Error( 'only the original author can delete this thing' )

	id = thing.id
	thing.delete()
	return API_Success( 'thing with id=%d has been removed' % (id) )
	
	
def view(request, template='map.html'):
	
	# region based retrieval of things
	y1 = request.GET.get( 'lat1' , None )
	x1 = request.GET.get( 'lng1' , None )
	y2 = request.GET.get( 'lat2' , None )
	x2 = request.GET.get( 'lng2' , None )
	if x1 and x2 and y1 and y2:
		things = Thing.objects.filter( lattitude__lte = y1, lattitude__gte = y2, longitude__lte = x2, longitude__gte = x1 )
		limit = request.GET.get( 'limit', False )
		limit = limit or 20
		limit = int(limit)
		if limit <= 100:
			things = things[:limit]
		else:
			things = things[:100]
		regions = ThingWeight.objects.filter( shortlat__lte = y1, shortlat__gte = y2, shortlong__lte = x2, shortlong__gte = x1 )
		return API_ResponseList( { 'regions': regions, 'things': things} )
	
	# recent and old things retrieval
	id = request.GET.get( 'id', None )
	pullup_type = request.GET.get( 'pullup_type', None ) 
	if id and not pullup_type:
		try:
			thing = Thing.objects.get(pk=id)
			tc = ThingCount.objects.get( thingid=thing )
			tc.count = tc.count + 1
			tc.save()
		except Thing.DoesNotExist:
			return API_Error( 'thing with id %s does not exist' % id )
		except ThingCount.DoesNotExist:
			tc = ThingCount.objects.create(thingid = thing, count = 1)
			tc.save()			
		return API_ResponseList( { 'things': [thing] } )
	if id and pullup_type == 'old':
		things = Thing.objects.filter(pk__lt=id)
		limit = request.GET.get( 'limit', False )
		limit = limit or 20
		limit = int(limit)
		if limit <= 100:
			things = things[:limit]
		else:
			things = things[:100]
		return API_ResponseList( { 'things': things } )
	if id and pullup_type == 'recent':
		things = Thing.objects.filter(pk__gt=id)
		limit = request.GET.get( 'limit', False )
		limit = limit or 20
		limit = int(limit)
		if limit <= 100:
			things = things[:limit]
		else:
			things = things[:100]
		return API_ResponseList( { 'things': things } )
	

	things = Thing.objects.all()

	parent = request.GET.get( 'parent', None )
	if parent:
		parent = int(parent)
		things = things.filter(parent = parent )
		return API_ResponseList( { 'things': things} )

	things = things.exclude(parent__isnull = False) # don't worry, a limit is applied later . . .
	regions = ThingWeight.objects.all()
	
	uid = request.GET.get( 'uid', None )
	if uid:
		try:
			user = User.objects.get( id=uid )
			things = things.filter( author=user )
		except User.DoesNotExist:
			return API_Error( 'user does not exist with uid %s' % uid )

	username = request.GET.get( 'username', None )
	if username:
		try:
			user = User.objects.get( username=username )
			things.filter( author=user )
		except User.DoesNotExist:
			return API_Error( 'user does not exist with username %s' % username )
	
	lattitude = request.GET.get( 'lattitude', None )
	longitude = request.GET.get( 'longitude', None )
	if lattitude == '':
		lattitude = None

	if longitude == '':
		longitude = None

	if None is not lattitude and None is not longitude:
		lattitude = float( lattitude )
		longitude = float( longitude )
		things = things.extra(select={'distance': 'SQRT(POW(69.1 * (lattitude - %f), 2) + POW(69.1 * (longitude - %f) * COS(lattitude/57.3), 2))' % (lattitude, longitude)})
	else:
		things = things.extra( select={'distance': '""' } )

	maxdist = request.GET.get( 'maxdist', None )
	if maxdist == '':
		maxdist = None

	if maxdist and ( None is lattitude or None is longitude ):
		return API_Error( 'maxdist requires lattitude and longitude to be specified' )

	if None is maxdist and None is not lattitude and None is not longitude:
		maxdist = 10		
	
	if maxdist:
		maxdist = float( maxdist )
		delta_lng = maxdist / math.fabs( math.cos( math.radians( lattitude ) ) * 69 )
		delta_lat = maxdist / 69
		minlng = longitude - delta_lng
		maxlng = longitude + delta_lng
		minlat = lattitude - delta_lat
		maxlat = lattitude + delta_lat
		things = things.filter(longitude__gte=minlng).filter(longitude__lte=maxlng)
		things = things.filter(lattitude__gte=minlat).filter(lattitude__lte=maxlat)
		
	things = filter_access( things, request.user )

	if ( request.GET.get( 'type', False ) ):
		things = things.extra(where=['type = %s' % request.GET[ 'type' ]] )

	parent = request.GET.get( 'parent', None )
	
	if parent:
		parent = int(parent)
		things = things.filter( parent=parent )

	#if ( request.GET.get( 'maxage', False ) ):
	#	pass

	#if ( request.GET.get( 'minage', False ) ):
	#	pass

	if ( request.GET.get( 'order', False ) ):
		things = things.extra(order_by=request.GET[ 'order' ].split( ',' ))
	elif request.GET.get( 'lattitude', None ) and request.GET.get( 'longitude', None ):
		things = things.extra(order_by=['distance'])

	if ( request.GET.get( 'offset', False ) ):
		things = things[int(request.GET[ 'offset' ]):]
	
	limit = request.GET.get( 'limit', False )
	limit = limit or 20
	limit = int(limit)
	if limit <= 100:
		things = things[:limit]
	else:
		things = things[:100]
	
	for t in things:
		try:
			tc = ThingCount.objects.get(thingid = t)
			tc.count = tc.count+1
			tc.save()
		except ThingCount.DoesNotExist:
			tc = ThingCount.objects.create(thingid = t, count = 1)
			tc.save()
			
	#retrieving sets
	records = BundleRelationship.objects.select_related().all().order_by('bundle','timestamp')

	return API_ResponseList( { 'regions': regions, 'things': things, 'records': records } )

@login_required
@http_parameter_required( 'post', 'id', 'Thing ID' )
def take(request):
	from placethings.users.models import Inventory

	try:
		thing = Thing.objects.get( id=request.POST.get( 'id' ) )
	except Thing.DoesNotExist:
		return API_Error( 'thing with id %s does not exist' % request.POST.get( 'id' ) )
	if not has_access( thing, request.user ):
		return API_Error( 'you cannot access that Thing' )
	
	if thing.quantity > 0:
		thing.quantity -= 1
		inventory = Inventory( user=request.user, thing=thing )
		thing.save()
		inventory.save()

		return API_Success( 'id=%d' % (thing.id) )
	else:
		return API_Error( 'all Things have been taken' )


@http_parameter_required( 'get', 'id', 'bundle ID' )
def list_bundle( request ):
	try:
		bundle = Bundle.objects.get( pk=request.GET.get('id') )
		bc = BundleCount.objects.get( bundleid=bundle ) 
		bc.count = bc.count + 1
		bc.save()	
	except Bundle.DoesNotExist:
		return API_Error( 'bundle with id %s does not exist' % request.POST.get( 'id' ) )
	except BundleCount.DoesNotExist:
		bc = BundleCount.objects.create(bundleid=bundle, count=1)
		bc.save()
	
	if not has_access( bundle, request.user ):
		return API_Error( 'you cannot view that bundle' )

	things = Thing.objects.filter( bundle__id=request.GET.get( 'id' ) ).order_by('bundlerelationship__order')
	things = filter_access( things, request.user )

	return API_ResponseList( { 'things': things,} )

def create_bundle( request ):
	bundle = Bundle.objects.create()
	bundle.title = request.POST.get( 'title', None )
	bundle.description = request.POST.get( 'description', None )
	if request.user.is_authenticated():
		bundle.author = request.user

	if request.POST.get( 'privacy', None ) is not None:
		if type( request.user ) is User:
			bundle.privacy = request.POST.get( 'privacy' )
		else:
			return API_Error( 'must be logged in to set privacy' )

	bundle.save()
	
	if len( request.POST.get( 'ids' ).strip() ):		
		things = Thing.objects.filter( id__in=request.POST.get( 'ids' ).strip().split( ',' ) )
		things = filter_access( things, request.user )
	
		i = 0
		for thing in things:
			BundleRelationship(bundle=bundle,thing=thing, order=i).save()
			i = i + 1

	return API_Success( 'id=%d' % (bundle.id) )


@http_parameter_required( 'post', 'id', 'bundle ID' )
@http_parameter_required( 'post', 'ids', 'Thing IDs' )
def add_to_bundle( request ):
	try:
		bundle = Bundle.objects.get( id=request.POST.get( 'id' ) )
	except Bundle.DoesNotExist:
		return API_Error( 'no bundle with that ID' )

	if bundle.author is not None and type( request.user ) is not User:
		return API_Error( 'only the original creator can modify a bundle' )
	elif bundle.author is not None and request.user != bundle.author:
		return API_Error( 'only the original creator can modify a bundle' )

	bundle_relationships = BundleRelationship.objects.filter(bundle=bundle).order_by('-order')
	if len( bundle_relationships ):
		order = bundle_relationships[0].order + 1
	else:
		order = 0
		
	things = Thing.objects.filter( id__in=request.POST.get( 'ids' ).strip().split( ',' ) )
	things = filter_access( things, request.user )

	for thing in things:
		BundleRelationship(bundle=bundle,thing=thing,order=order).save()
		order = order + 1

	return API_Success( 'id=%d' % (bundle.id) )


@http_parameter_required( 'post', 'id', 'bundle ID' )
@http_parameter_required( 'post', 'ids', 'Thing IDs' )
def remove_from_bundle( request ):
	try:
		bundle = Bundle.objects.get( id=request.POST.get( 'id' ) )
	except Bundle.DoesNotExist:
		return API_Error( 'no bundle with that ID' )

	if bundle.author is not None and type( request.user ) is not User:
		return API_Error( 'only the original creator can modify a bundle' )
	elif bundle.author is not None and request.user != bundle.author:
		return API_Error( 'only the original creator can modify a bundle' )

	things = Thing.objects.in_bulk( request.POST.get( 'ids' ).strip().split( ',' ) )

	for thing in things:
		relationships = BundleRelationship.objects.filter(bundle=bundle)
		relationship = relationships.get(thing=thing)
		order = relationship.order
		relationship.delete()
		relationships.filter(order__gt=order).update(order=F('order')-1)

		for relationship in relationships:
			relationship.save()

	if bundle.things.count() is 0:
		bundle.delete()
		return API_Success( 'bundle deleted' )
	return API_Success( 'id=%d' % (bundle.id) )


@http_parameter_required( 'post', 'id', 'bundle ID' )
@http_parameter_required( 'post', 'thing', 'Thing ID' )
@http_parameter_required( 'post', 'index', 'index' )
def reorder_thing_in_bundle( request ):
	try:
		bundle = Bundle.objects.get( id=request.POST.get( 'id' ) )
	except Bundle.DoesNotExist:
		return API_Error( 'no bundle with that ID' )

	if bundle.author is not None and type( request.user ) is not User:
		return API_Error( 'only the original creator can modify a bundle' )
	elif bundle.author is not None and request.user != bundle.author:
		return API_Error( 'only the original creator can modify a bundle' )

	thing = request.POST.get( 'thing' )

	bundle_set = bundle.bundlerelationship_set

	max_order = int(bundle_set.order_by('-order')[0].order + 1)
	index = int(request.POST.get( 'index' ))

	if index > max_order or index < 0:
		return API_Error( 'index out of range' )

	operand = bundle_set.get(thing=thing)
	old_order = operand.order

	if old_order > index:
		# Moving Thing towards beginning
		# Increase order of all items between index and old_order by one
		bundle_set.filter(order__gte=index).filter(order__lt=old_order).update(order=F('order') + 1)
		operand.order = index
		operand.save()

	elif old_order < index:
		# Moving Thing towards end
		# Decrease order of all items between old_order and index by one
		bundle_set.filter(order__gt=old_order).filter(order__lte=index).update(order=F('order') - 1)
		operand.order = index
		operand.save()

	else:
		return API_Error( 'Thing with id %s already at index' % operand.thing.id )

	return API_Success( 'id=%d' % bundle.id)

def test( request ):
	from placethings.users.forms import *
	from placethings.users.models import *
	from django.forms.models import modelformset_factory
	data = {'user': request.user, 'user_form': UserForm() }
	
	if not 'oauth_domain' in request.session:
		request.session[ 'oauth_domain' ] = ''
		
	if not request.user.is_authenticated():
		if 'oauth_domain' in request.session and not request.session[ 'oauth_domain' ] == '':
			if  request.session[ 'oauth_domain' ] == 'twitter':
				initial_values = TwitterUserForm().convert_info( request.session[ 'twitter_info' ] )
				data[ 'twitter_pic' ] = initial_values[ 'twitter_url' ]
				data[ 'user_form' ] = TwitterUserForm( initial=initial_values )
				data[ 'profile_form' ] = TwitterProfileForm( initial=initial_values )
			elif request.session['oauth_domain'] == 'youtube':
				initial_values = YoutubeUserForm().convert_info( request.session[ 'youtube_info' ] )
				data[ 'youtube_pic' ] = initial_values[ 'youtube_url' ]
				data[ 'user_form' ] = YoutubeUserForm( initial=initial_values )
				data[ 'profile_form' ] =YoutubeProfileForm( initial=initial_values )
		else:
			data[ 'user_form' ] = UserForm()
			data[ 'profile_form' ] = ProfileForm()
				
	elif request.GET.get( 'oauth_domain', None ) == 'place_video':
		try:
			profile = request.user.get_profile()
		except Profile.DoesNotExist:
			profile = Profile(user=request.user)
			profile.save()
		data[ 'user_form' ] = PartialUserForm( instance=request.user )
		data[ 'profile_form' ] = ProfileForm( instance=profile )
		data[ 'status' ] = request.GET.get( 'status', '' )
		data[ 'media' ] = request.GET.get( 'media', '' )
		data[ 'type' ] = request.GET.get( 'type', '' )
		
	elif request.session[ 'oauth_domain' ] == 'video':
		try:
			profile = request.user.get_profile()
		except Profile.DoesNotExist:
			profile = Profile(user=request.user)
			profile.save()
		data[ 'user_form' ] = PartialUserForm( instance=request.user )
		data[ 'profile_form' ] = ProfileForm( instance=profile )
		data[ 'next' ] = request.GET.get( 'next', '' )
		data[ 'post_url' ] = request.GET.get( 'post_url', '' )
		data[ 'youtube_token' ] = request.GET.get( 'youtube_token', '' )
		
	else:
		try:
			profile = request.user.get_profile()
		except Profile.DoesNotExist:
			profile = Profile(user=request.user)
			profile.save()
		data[ 'user_form' ] = PartialUserForm( instance=request.user )
		data[ 'profile_form' ] = ProfileForm( instance=profile )
		
	return render_to_response( 'test.htm', data, mimetype='text/html; charset=UTF-8' )

def register(request):
	if not request.user.is_authenticated():
		if 'oauth_domain' in request.session and not request.session[ 'oauth_domain' ] == '':	
			if request.session[ 'oauth_domain' ] == 'twitter':
				initial_values = TwitterUserForm().convert_info( request.session[ 'twitter_info' ] )
				user_form = TwitterUserForm( 
					request.POST,
					initial=initial_values
				)
			elif request.session['oauth_domain'] == 'youtube':
				initial_values = YoutubeUserForm().convert_info( request.session[ 'youtube_info' ] )
				user_form = YoutubeUserForm( 
					request.POST,
					initial=initial_values
				)
		else:
			user_form = UserForm(request.POST)
			
		if user_form.is_valid():
			user_form.save()
		else:
			return API_Error( 'invalid data: %s' % user_form.errors.as_text() )
			
		user = user_form.instance
		
		if 'oauth_domain' in request.session and not request.session[ 'oauth_domain' ] == '':	
			if request.session[ 'oauth_domain' ] == 'twitter':
				user.backend = 'placethings.auth.backends.TwitterBackend'
			elif request.session[ 'oauth_domain' ] == 'youtube':
				user.backend = 'placethings.youtube_auth.backends.YoutubeBackend'
		else:
			user.backend = 'django.contrib.auth.backends.ModelBackend'
			user.set_password( user_form.cleaned_data[ 'password' ] )
	
		user.save()
		request.user = user
		login_user( request, request.user )
	
	# Create an empty profile for this user
	profile = Profile(user=request.user)
		
	# Add the additional info
	if 'oauth_domain' in request.session and not request.session[ 'oauth_domain' ]== '':
		if request.session[ 'oauth_domain' ] == 'twitter' and not request.session[ 'oauth_domain' ] == '':
			initial_values = TwitterProfileForm().convert_info( request.session[ 'twitter_info' ] )
			profile_form = TwitterProfileForm( 
				request.POST,
				TwitterProfileForm().get_avatar( request ),
				initial=initial_values,
				instance=profile
			)
		elif request.session[ 'oauth_domain' ] == 'youtube' and not request.session[ 'oauth_domain' ] == '':
			initial_values = YoutubeProfileForm().convert_info( request.session[ 'youtube_info' ] )
			profile_form = YoutubeProfileForm( 
				request.POST,
				YoutubeProfileForm().get_avatar( request ),
				initial=initial_values,
				instance=profile
			)
	else:
		if request.FILES:
			# User uploaded a profile pic
			profile_form = ProfileForm( request.POST, request.FILES, instance=profile )
		else:
			# No profile pic
			profile_form = ProfileForm( request.POST, instance=profile )
		
	if profile_form.is_valid():
		profile_form.save()
	else:
		return API_Error( 'invalid data: %s' % profile_form.errors )
		
	return API_Success( 'id=%d' % (request.user.id) )

def login(request):
	user = authenticate(username=request.POST.get( 'username', None ), password=request.POST.get( 'password') )
	if user is not None:
		login_user(request, user)
		return API_Success( 'id=%d' % (user.id) )
	else:
	    return API_Error( 'username and password were incorrect' )

def logout(request):
	logout_user(request)
	return API_Success()

def update_profile( request ):
	if not request.user.is_authenticated():
		return API_Error( 'not logged in' )
		
	if request.method != "POST":
		return API_Error( 'no data' )
		
	user_form = PartialUserForm(request.POST, instance=request.user)

	profile = Profile.objects.get(user=request.user)
	
	if 'avatar' in request.FILES:
		profile_form = ProfileForm( request.POST, request.FILES, instance=profile )
	else:
		profile_form = ProfileForm( request.POST, instance=profile )
	
	if user_form.is_valid():
		user_form.save()
	else:
		return API_Error( '%s' % user_form.errors )
	
	if profile_form.is_valid():
		profile_form.save()
	else:
		return API_Error( '%s' % profile_form.errors )
	
	return API_Success( 'profile updated')

def get_profile( request ):
	if request.GET.get( 'uid' ):
		try:
			return API_User( { 'user': User.objects.get( id=request.GET.get( 'uid' ) ) } )
		except User.DoesNotExist:
			return API_Error( 'user with id %s does not exist' % request.GET.get( 'uid' ) )
	elif request.user.is_authenticated():
		return API_User( {'user': request.user } )
	else:
		return API_Error( 'No UID given and not logged in' )
