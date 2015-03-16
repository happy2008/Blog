from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
from django.contrib.auth.models import User

class MessageItem(models.Model):
    text = models.CharField(max_length=160)
    user = models.ForeignKey(User)
    time = models.DateTimeField('OriginTime', auto_now=True, default=datetime.now())
    picture = models.ImageField(upload_to="pictures", blank=True)
    def __unicode__(self):
        return self.text

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    age  = models.IntegerField(blank=True,null=True)
    bio  = models.CharField(blank=True, max_length=430,null=True)
    follower = models.IntegerField(default=0)
    following = models.IntegerField(default=0) 
    photo = models.ImageField(upload_to="photos", default='photos/dog.jpg')
    def __unicode__(self):
        return self.user.username

class Following(models.Model):
    origin_user = models.ForeignKey(User)
    followed_usrname = models.CharField(max_length=30)

class Comment(models.Model):
    messageItem = models.ForeignKey(MessageItem)
    user = models.ForeignKey(User)
    time = models.DateTimeField('CommentTime', auto_now=True, default=datetime.now())
    commenttext = models.CharField(max_length=50)
    