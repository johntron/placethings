# Copyright 2008-2009 Brian Boyer, Ryan Mark, Angela Nitzke, Joshua Pollock,
# Stuart Tiffen, Kayla Webley and the Medill School of Journalism, Northwestern
# University.
#
# This file is part of django-facebookconnect.
#
# django-facebookconnect is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-facebookconnect is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with django-facebookconnect.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import logging
import sha, random
from urllib2 import URLError

from facebook.djangofb import Facebook,get_facebook_client
from facebook import FacebookError

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_delete

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

class FacebookBackend:
    def authenticate(self, request=None):
        fb = get_facebook_client()
        fb.check_session(request)
        if fb.uid:
            try:
                logging.debug("Checking for Facebook Profile %s..." % fb.uid)
                fbprofile = FacebookProfile.objects.get(facebook_id=fb.uid)
                return fbprofile.user
            except FacebookProfile.DoesNotExist:
                logging.debug("FB account hasn't been used before...")
                return None
            except User.DoesNotExist:
                logging.error("FB account exists without an account.")
                return None
        else:
            logging.debug("Invalid Facebook login for %s" % fb.__dict__)
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
class BigIntegerField(models.IntegerField):
    empty_strings_allowed=False
    def get_internal_type(self):
        return "BigIntegerField"
    
    def db_type(self):
        if settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        else:
            return "bigint"

class FacebookTemplate(models.Model):
    name = models.SlugField(unique=True)
    template_bundle_id = BigIntegerField()
    
    def __unicode__(self):
        return self.name.capitalize()

class FacebookUser( models.Model ):
	user = models.ForeignKey( User, unique=True )
	facebook_username = models.CharField( max_length=255, unique=True, blank=True, null=True )
		
class FacebookProfile(models.Model):
    user = models.OneToOneField(User,related_name="facebook_profile")
    facebook_id = BigIntegerField(unique=True)
    
    __facebook_info = None

    FACEBOOK_FIELDS = ['uid,name,first_name,last_name,pic_square_with_logo,affiliations,status,proxied_email']
    DUMMY_FACEBOOK_INFO = {
        'uid':0,
        'name':'(Private)',
        'first_name':'(Private)',
        'last_name':'(Private)',
        'pic_square_with_logo':'http://www.facebook.com/pics/t_silhouette.gif',
        'affiliations':None,
        'status':None,
        'proxied_email':None,
    }
    
    def __init__(self, *args, **kwargs):
        """reset local DUMMY info"""
        super(FacebookProfile,self).__init__(*args,**kwargs)
        try:
            self.DUMMY_FACEBOOK_INFO = settings.DUMMY_FACEBOOK_INFO
        except AttributeError:
            pass
        try:
            self.FACEBOOK_FIELDS = settings.FACEBOOK_FIELDS
        except AttributeError:
            pass
        
        if hasattr(_thread_locals,'fbids'):
            _thread_locals.fbids.append(self.facebook_id)
        else: _thread_locals.fbids = [self.facebook_id]
        
    def __getattr__(self,name):
        self.__configure_me()
        if name in self.__facebook_info:
            return self.__facebook_info[name]
        elif name in self.DUMMY_FACEBOOK_INFO:
            return self.DUMMY_FACEBOOK_INFO[name]
        else:
            raise AttributeError

    def __get_picture_url(self):
        self.__configure_me()
        if self.__facebook_info['pic_square_with_logo']:
            return self.__facebook_info['pic_square_with_logo']
        else:
            return self.DUMMY_FACEBOOK_INFO['pic_square_with_logo']
    picture_url = property(__get_picture_url)
    
    def __get_full_name(self):
        self.__configure_me()
        if self.__facebook_info['name']:
            return u"%s" % self.__facebook_info['name']
        else:
            return self.DUMMY_FACEBOOK_INFO['name']
    full_name = property(__get_full_name)
    
    def __get_networks(self):
        self.__configure_me()
        return self.__facebook_info['affiliations']
    networks = property(__get_networks)

    def __get_email(self):
        self.__configure_me()
        if self.__facebook_info['proxied_email']:
            return self.__facebook_info['proxied_email']
        else:
            return ""
    email = property(__get_email)

    def facebook_only(self):
        """return true if this user uses facebook and only facebook"""
        if self.facebook_id and str(self.facebook_id) == self.user.username:
            return True
        else:
            return False
    
    def is_authenticated(self):
        """Check if this fb user is logged in"""
        _facebook_obj = get_facebook_client()
        if _facebook_obj.session_key and _facebook_obj.uid:
            try:
                fbid = _facebook_obj.users.getLoggedInUser()
                if int(self.facebook_id) == int(fbid):
                    return True
                else:
                    return False
            except FacebookError,ex:
                if ex.code == 102:
                    return False
                else:
                    raise

        else:
            return False

    def get_friends_profiles(self,limit=50):
        '''returns profile objects for this persons facebook friends'''
        friends = []
        friends_info = []
        friends_ids = []
        try:
            friends_ids = self.__get_facebook_friends()
        except (FacebookError,URLError), ex:
            logging.error("FBC: fail getting friends: %s" % ex)
        logging.debug("FBC: Friends of %s %s" % (self.facebook_id,friends_ids))
        if len(friends_ids) > 0:
            #this will cache all the friends in one api call
            self.__get_facebook_info(friends_ids)
        for id in friends_ids:
            try:
                friends.append(FacebookProfile.objects.get(facebook_id=id))
            except (User.DoesNotExist, FacebookProfile.DoesNotExist):
                logging.error("FBC: Can't find friend profile %s" % id)
        return friends

    def __get_facebook_friends(self):
        """returns an array of the user's friends' fb ids"""
        _facebook_obj = get_facebook_client()
        friends = []
        cache_key = 'fb_friends_%s' % (self.facebook_id)
    
        fb_info_cache = cache.get(cache_key)
        if fb_info_cache:
            friends = fb_info_cache
        else:
            if getattr(settings,'RANDOM_FACEBOOK_FAIL',False) and random.randint(1,10) is 8:
                raise FacebookError(102,"RANDOM FACEBOOK FAIL!!!",[])
            elif getattr(settings,'RANDOM_FACEBOOK_FAIL',False) and random.randint(1,10) is 3:
                raise URLError(104)
            logging.debug("FBC: Calling for '%s'" % cache_key)
            friends = _facebook_obj.friends.getAppUsers()
            cache.set(cache_key,friends,getattr(settings,'FACEBOOK_CACHE_TIMEOUT',1800))
        
        return friends        

    def __get_facebook_info(self,fbids):
        """
           Takes an array of facebook ids and caches all the info that comes back.
           Returns a tuple - an array of all facebook info, and info for self's fb id.
        """
        _facebook_obj = get_facebook_client()
        all_info = []
        my_info = self.DUMMY_FACEBOOK_INFO
        ids_to_get = []
        for id in fbids:
            if id is 0:
                ret.append(self.DUMMY_FACEBOOK_INFO)
            
            if _facebook_obj.uid is None:
                cache_key = 'fb_user_info_%s' % id
            else:
                cache_key = 'fb_user_info_%s_%s' % (_facebook_obj.uid,id)
        
            fb_info_cache = cache.get(cache_key)
            if fb_info_cache:
                all_info.append(fb_info_cache)
                if id == self.facebook_id:
                    my_info = fb_info_cache
            else:
                ids_to_get.append(id)
        
        if len(ids_to_get) > 0:
            if getattr(settings,'RANDOM_FACEBOOK_FAIL',False) and random.randint(1,10) is 8:
                raise FacebookError(102,"RANDOM FACEBOOK FAIL!!!",[])
            elif getattr(settings,'RANDOM_FACEBOOK_FAIL',False) and random.randint(1,10) is 3:
                raise URLError(104)
            logging.debug("FBC: Calling for '%s'" % ids_to_get)
            tmp_info = _facebook_obj.users.getInfo(ids_to_get, self.FACEBOOK_FIELDS)
            
            all_info.extend(tmp_info)
            for info in tmp_info:
                if info['uid'] == self.facebook_id:
                    my_info = info
                
                if _facebook_obj.uid is None:
                    cache_key = 'fb_user_info_%s' % id
                else:
                    cache_key = 'fb_user_info_%s_%s' % (_facebook_obj.uid,info['uid'])

                cache.set(cache_key,info,getattr(settings,'FACEBOOK_CACHE_TIMEOUT',1800))
                
        return all_info,my_info

    def __configure_me(self):
        """Calls facebook to populate profile info"""
        try:
            logging.debug("FBID: '%s' profile: '%s' user: '%s'" % (self.facebook_id,self.id,self.user_id))
            if self.__facebook_info == self.DUMMY_FACEBOOK_INFO or not self.__facebook_info:
                ids = getattr(_thread_locals,'fbids',[self.facebook_id])
                all_info,self.__facebook_info = self.__get_facebook_info(ids)
        except (ImproperlyConfigured), ex:
            logging.error('FBC: Facebook not setup')
            self.__facebook_info = self.DUMMY_FACEBOOK_INFO
        except (FacebookError,URLError), ex:
            logging.error('FBC: Fail loading profile: %s' % ex)
            self.__facebook_info = self.DUMMY_FACEBOOK_INFO
        except (IndexError), ex:
            logging.error("FBC: Couldn't retrieve FB info for FBID: '%s' profile: '%s' user: '%s'" % (self.facebook_id,self.id,self.user_id))
            self.__facebook_info = self.DUMMY_FACEBOOK_INFO

    def get_absolute_url(self):
        return "http://www.facebook.com/profile.php?id=%s" % self.facebook_id

    def __unicode__(self):
        return "FacebookProfile for %s" % self.facebook_id

def unregister_fb_profile(sender, **kwargs):
    """call facebook and let them know to unregister the user"""
    fb = get_facebook_client()
    fb.connect.unregisterUser([fb.hash_email(kwargs['instance'].user.email)])

#post_delete.connect(unregister_fb_profile,sender=FacebookProfile)