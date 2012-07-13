from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from placethings.facebookconnect.models import *
import urllib
import os.path

class FacebookUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    username = forms.RegexField(label=_("facebook username"), max_length=30, regex=r'^\w+$',
        error_message = _("This value must contain only letters, numbers and underscores."))
    email = forms.EmailField(label=_("E-mail"), max_length=75,required=False)

    class Meta:
        model = User
        fields = ("username","email")

    def save(self, commit=True):
        user = super(FacebookUserCreationForm, self).save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user
     
class FacebookForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    username = forms.RegexField(label=_("facebook username"), max_length=30, regex=r'^\w+$',
        error_message = _("This value must contain only letters, numbers and underscores."))
   
    class Meta:
        model = FacebookUser
        exclude = ('user',)

    def save(self, commit=True):
        Facebookuser.save()
        return Facebookuser

'''class FacebookForm(forms.ModelForm):
	username = forms.RegexField(label=_("facebook username"), max_length=30, regex=r'^w+$')

	class Meta:
		model = FacebookUser
		fields = ("username")
		
	def save(self, commit=True):
		Facebookuser = super(FacebookForm, self).save(commit=False)
		Facebookuser.set_unsable_password()
		if commit:
			Facebookuser.save()
		return Facebookuser'''