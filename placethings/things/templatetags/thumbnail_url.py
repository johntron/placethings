from placethings.settings import MEDIA_URL
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def thumbnail_url( value, arg ):
	width,height = arg.split( 'x' )
	url,ext = value.rsplit( '.', 1 )
	return url + '-' + arg + '.' + ext