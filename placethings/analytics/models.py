from django.db import models
from placethings.api.models import *
from django.contrib.auth.models import User

class ThingCount( models.Model ):
	thingid = models.ForeignKey( Thing )
	count = models.IntegerField()

class BundleCount( models.Model ):
	bundleid = models.ForeignKey( Bundle )
	count = models.IntegerField()
	