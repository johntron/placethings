from django.contrib import admin
from placethings.api.models import *
from placethings.users.models import *

class ThingAdmin(admin.ModelAdmin):
	def author_username( thing ):
		if thing.author:
			return thing.author.username
		else:
			return ''
			
	def parent_id( thing ):
		if thing.parent:
			return thing.parent.id
		else:
			return ''
			
	list_display = ( 'id', 'title', 'type', author_username, parent_id, 'replies' )
	list_filter = ( 'type', )
	search_fields = ( 'id', 'author__username' )
	
admin.site.register( Thing, ThingAdmin )
admin.site.register( Bundle )
admin.site.register( Profile )