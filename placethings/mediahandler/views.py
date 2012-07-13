from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from placethings.settings import MEDIA_ROOT
from placethings.api.models import *
from placethings.api.views import *
import Image
import os

ext2conttype = {"jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "png": "image/png",
                "gif": "image/gif"}

def content_type(filename):
    return ext2conttype[filename[filename.rfind(".")+1:].lower()]
    
def image_data( out_file ):
	return HttpResponse( file( out_file, 'rb' ).read(), content_type=content_type(out_file))

def imagehandler(request, path, id, width, height, extension):
	in_file = MEDIA_ROOT + path + id + '.' + extension
	out_file = MEDIA_ROOT + path + id + '-' + width + 'x' + height + '.' + extension
	
	if path.lower() == '':
		try:
			t = Thing.objects.get(pk = id)
			if not has_access( t, request.user ):
				return HttpResponse( 'fail; you cannot access that Thing;' )
		except Thing.DoesNotExist:
			return HttpResponse( 'fail; there is no thing with the specified id;' )

	if os.path.exists( out_file ):
		# File already exists, so return it
		return image_data(out_file)
	else:
		size = (int(width), int(height) )
		im = Image.open( in_file )
		im.thumbnail( size, Image.ANTIALIAS )
		im.save( out_file )
 
	return image_data(out_file)