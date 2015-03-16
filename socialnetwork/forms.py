from django import forms

from django.contrib.auth.models import User
from django.core.validators import validate_email, RegexValidator
from models import *
from django.forms import FileInput, TextInput, Textarea
MAX_UPLOAD_SIZE = 2500000


class EditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name','email','age','bio']

class EditPhoto(forms.Form):
    photo = forms.ImageField(required=False)

class PostForm(forms.Form):
    text = forms.CharField(max_length=160)
    image= forms.ImageField(required=False)

class CommentForm(forms.Form):
    commenttext = forms.CharField(max_length=50, required=True, widget=Textarea(attrs={'class': "form-control",
                                                                    'placeholder': "Comments Here",
                                                                    'maxlength': 50,
                                                                    'rows': 2}))
    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        commenttext = cleaned_data.get('commenttext')
        if commenttext and len(commenttext) > 50:
            raise forms.ValidationError("The length of comment exceed the maximum 50 requirement")
        return self.cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.CharField(max_length=50,validators = [validate_email])
    password1 = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2 = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2 :
            raise forms.ValidationError("Password Fail to match.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return username
