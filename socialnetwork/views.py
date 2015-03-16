from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.core.mail import send_mail
# Django transaction system so we can use @transaction.atomic
from django.db import transaction
from django.db.models import Q
from socialnetwork.models import *
from socialnetwork.forms import *
from mimetypes import guess_type
from django.http import Http404,HttpResponse
import datetime
import pytz
from socialnetwork.s3 import s3_upload, s3_delete
from django.contrib.auth.tokens import default_token_generator
# Create your views here.
@login_required
def home(request):
    # Sets up list of just the logged-in user's (request.user's) items
    messageItems = MessageItem.objects.all().order_by('-time')
    print '>>>>>>>>>>>>>>>>>>>>'
    print request.user
    userprofile = UserProfile.objects.get(user=request.user)
    post_lists = []
    for messageItem in messageItems:
        comments = Comment.objects.filter(messageItem=messageItem).order_by('time')
        #comments = {}
        print '[comment NUM]' + str(len(comments))
        post_lists.append((messageItem, comments))
    return render(request, 'index.html', {'posts' : post_lists, 'userprofile' : userprofile, 'username':request.user.username,
                                            'commentform':CommentForm()})

@login_required
@transaction.atomic
def comment(request, item_id):
    print 'enter????????????>>>>>>>>>>>>>>'
    print str(item_id)
    newComment = Comment()
    messageItem = MessageItem.objects.get(id=item_id)
    newComment.messageItem = messageItem
    newComment.user = request.user
    form = CommentForm(request.POST)
    if form.is_valid():
        newComment.commenttext = form.cleaned_data.get('commenttext')
        newComment.save()
        posts = []
        comments = []
        comments.append(newComment)
        
        posts.append((messageItem, comments))
        #get_list_json(request, posts)
        return render(request, 'ajax_comment.html', {'posts': posts})
    else :
        return render(request, 'ajax_comment.html', {'errors' :form.errors['commenttext']})


@login_required
def ajax_update(request):
    #up = UserProfile.objects.get(user=request.user)
    #
    print 'testeeee'
    t = int(request.GET.get('currenttime'))
    ts = datetime.datetime.utcfromtimestamp(t/1000).replace(tzinfo=pytz.UTC)
    print '[username]' + request.user.username
    print '[ajax time]' + str(ts)
    print '[local time]' + str(datetime.datetime.now())
    messageItemsSet = MessageItem.objects.filter(time__gt=ts).exclude(user=request.user)
    print '[MessageItems Time]'
    for item in messageItemsSet:    
        print item.time
    post_lists = []
    for messageItem in messageItemsSet:
        comments = Comment.objects.filter(messageItem=messageItem).order_by('time')
        #print '[comment NUM]' + Comment.objects.filter(messageItem=messageItem).count()
        #comments = {}
        post_lists.append((messageItem, comments))    
    return render(request, 'ajax_update.html', {'posts' : post_lists, 'username':request.user.username, 'commentform':CommentForm()})

@login_required
def edit_portrait(request):
    form=EditPhoto(request.POST,request.FILES)    
    # Creates a new item if it is present as a parameter in the request
    if not form.is_valid():
        print '@@@@'
        messageItems = MessageItem.objects.all().order_by('-time')
        return render(request, 'index.html', {'messageItems' : messageItems,'form' : form, 'username':request.user.username})
    #else : 
    up = UserProfile.objects.get(user=request.user)
    if 'photo' in form.cleaned_data:
        print '=================>>>>>><<<<<<<<<===================='
        up.photo=form.cleaned_data['photo']
    up.save()
    print 111111111111
    messageItems = MessageItem.objects.filter(user=request.user).order_by('-time')
    context = { 'message': 'UP Photo updated.','userProfile': up, 'form': form , 'messageItems' : messageItems}
    return render(request, 'edit_profile.html',context)

@login_required
def get_userportrait(request,id):
    user = get_object_or_404(User, id=id)
    up = UserProfile.objects.get(user=user)
    if not up.photo:
        raise Http404
    content_type = guess_type(up.photo.name)
    return HttpResponse(up.photo, content_type=content_type)


@login_required
def get_portrait(request):
    up = UserProfile.objects.get(user=request.user)
    if not up.photo:
        raise Http404
    content_type = guess_type(up.photo.name)
    return HttpResponse(up.photo, content_type=content_type)

@login_required
def get_photo(request, id):
    
    messageItem = get_object_or_404(MessageItem, id=id)
   
    if not messageItem.picture: 
        raise Http404
    
    content_type = guess_type(messageItem.picture.name)
    #print messageItem.picture
    #print content_type 
    return HttpResponse(messageItem.picture, content_type=content_type)

@login_required
@transaction.atomic
def follow_stream(request):
    messageItems = []
    followed_users = Following.objects.filter(origin_user=request.user)
    for followed_user in followed_users :
        user = UserProfile.objects.filter(username=followed_user.followed_usrname)
        messageItems.extend(MessageItem.objects.filter(user=user).order_by('-time'))

    post_lists = []
    for messageItem in messageItems:
        comments = Comment.objects.filter(messageItem=messageItem).order_by('time')
        #comments = {}
        print '[comment NUM]' + str(len(comments))
        post_lists.append((messageItem, comments))
    #context = {'friendmessageItems' : messageItems}
    context = {'posts':post_lists, 'commentform':CommentForm()}
    return render(request, 'follow_stream.html',context)



@login_required
@transaction.atomic
def follow(request, id):
    followee_profile = UserProfile.objects.get(id=id)
    messageItems = MessageItem.objects.filter(user=request.user).order_by('-time')

    if Following.objects.filter(origin_user__exact=request.user, followed_usrname__exact=followee_profile.username).count() == 0:
        Following(origin_user=request.user, followed_usrname=followee_profile.username).save()
        
    flag = True
    followee_profile.follower += 1
    followee_profile.save()
    own_profile = UserProfile.objects.get(user=request.user)
    own_profile.following += 1
    own_profile.save()

    form = EditForm(instance=followee_profile)
    context = { 'userprofile' : followee_profile , 'form': form , 'messageItems' : messageItems, 'flag': flag}
    return render(request,'otherprofile.html',context)

@login_required
@transaction.atomic
def unfollow(request, id):
    followee_profile = UserProfile.objects.get(id=id)
    messageItems = MessageItem.objects.filter(user=request.user).order_by('-time')

    if Following.objects.filter(origin_user__exact=request.user, followed_usrname__exact=followee_profile.username).count() != 0:
        Following.objects.get(origin_user=request.user, followed_usrname=followee_profile.username).delete()
    flag = False
    followee_profile.follower -= 1
    followee_profile.save()
    own_profile = UserProfile.objects.get(user=request.user)
    own_profile.following -= 1
    own_profile.save()
    form = EditForm(instance=followee_profile)
    context = { 'userprofile' : followee_profile , 'form': form , 'messageItems' : messageItems, 'flag':flag}
    return render(request,'otherprofile.html',context)


@login_required
def post_message(request):
    form=PostForm(request.POST,request.FILES)    
    # Creates a new item if it is present as a parameter in the request
    if not form.is_valid():
        print '@@@@'
        messageItems = MessageItem.objects.all().order_by('-time')
        return render(request, 'index.html', {'messageItems' : messageItems,'form' : form, 'username':request.user.username})
    #else : 
    text=form.cleaned_data['text']
    new_messageItem = MessageItem(user=request.user,text=text)
    if 'image' in form.cleaned_data:
        new_messageItem.picture=form.cleaned_data['image']
    new_messageItem.text = request.POST.get('text')
    new_messageItem.save()
    print 111111111111
    messageItems = MessageItem.objects.all().order_by('-time')
    post_lists = []
    for messageItem in messageItems:
        comments = Comment.objects.filter(messageItem=messageItem).order_by('time')
        #comments ={}
        print '[comment NUM]' + str(len(comments))
        post_lists.append((messageItem, comments))
    return render(request, 'index.html', {'posts' : post_lists, 'username':request.user.username, 'commentform':CommentForm()})

#show user's profile
@login_required
def view_profile(request, id):
    userprofile = UserProfile.objects.get(id=id)
    messageItems = MessageItem.objects.filter(user=request.user).order_by('-time')
    form = EditForm(instance=userprofile)
    context = { 'userprofile' : userprofile, 'form': form , 'messageItems' : messageItems}
    return render(request, 'otherprofile.html',context)

#Edit and update user's profile
@login_required
@transaction.atomic
def edit_profile(request):
    try:
        if request.method == 'GET':
            userprofile = UserProfile.objects.get(user=request.user)
            print userprofile
            form = EditForm(instance=userprofile)
            messageItems = MessageItem.objects.filter(user=request.user).order_by('-time')
            context = { 'userprofile' : userprofile, 'form': form , 'messageItems' : messageItems}
            return render(request, 'edit_profile.html', context)

        up = UserProfile.objects.select_for_update().get(user=request.user)    
        form = EditForm(request.POST,instance=up)
        messageItems = MessageItem.objects.filter(user=request.user).order_by('-time')
        if not form.is_valid():
            context = { 'userProfile': up, 'form': form , 'messageItems' : messageItems}
            return render(request, 'edit_profile.html', context)      
        form.save()
        context = { 'message': 'UP updated.','userProfile': up, 'form': form , 'messageItems' : messageItems}
        return render(request, 'edit_profile.html',context)

    except UserProfile.DoesNotExist:
        context = { 'message': 'Record does not exist'}
        return render(request, 'edit_profile.html', context)    


#show user's profile
@login_required
def display_profile(request):
    userprofile = UserProfile.objects.get(user=request.user)
    messageItems = MessageItem.objects.filter(user=request.user).order_by('-time')
    form = EditForm(instance=userprofile)
    context = { 'userprofile' : userprofile, 'form': form , 'messageItems' : messageItems}
    return render(request, 'profile.html',context)

@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'register.html', context)

    errors = []
    context['errors'] = errors

    form = RegistrationForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'register.html', context)

    # Creates the new user from the valid form data
    new_user = User.objects.create_user(username=form.cleaned_data['username'], \
                                        password=form.cleaned_data['password1'], \
                                        first_name=form.cleaned_data['first_name'], \
                                        last_name=form.cleaned_data['last_name'], \
                                        email=form.cleaned_data['email'])
    new_user.is_active = False
    new_user.save()

    token = default_token_generator.make_token(new_user)
    email_body = """
Welcome to the Simple Address Book.  Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="yachenw@andrew.cmu.edu",
              recipient_list=[new_user.email])
    context['email'] = form.cleaned_data['email']

    return render(request, 'needs-confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    print '====='
    print username
    print '====='
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, token):
        raise Http404
    user.is_active = True
    user.save()
    try:
        userprofile = UserProfile()
        userprofile.user = user
        userprofile.username = user.username
        userprofile.first_name = user.first_name
        userprofile.last_name = user.last_name
        userprofile.email = user.email
        userprofile.save()
    except Exception as e:
        print e

    return render(request, 'confirmed.html', {})
