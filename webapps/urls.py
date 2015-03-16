from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webapps.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'socialnetwork.views.home', name='home'),
    # Route for built-in authentication with our own custom login page
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'login.html'}, name='login'),
    url(r'^post$', 'socialnetwork.views.post_message', name='post'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register$', 'socialnetwork.views.register',name='register'),
    url(r'^profile$', 'socialnetwork.views.display_profile', name='profile'),
    url(r'^view-profile/(?P<id>\d+)$', 'socialnetwork.views.view_profile', name='view-profile'),
    url(r'^follow/(?P<id>\d+)$', 'socialnetwork.views.follow', name='follow'),
    url(r'^unfollow/(?P<id>\d+)$', 'socialnetwork.views.unfollow', name='unfollow'),
    url(r'^edit-profile$', 'socialnetwork.views.edit_profile', name='edit-profile'),
    url(r'^follow-stream$', 'socialnetwork.views.follow_stream', name='follow-stream'),
    url(r'^photo/(?P<id>\d+)$', 'socialnetwork.views.get_photo', name='photo'),
    url(r'^portrait$', 'socialnetwork.views.get_portrait', name='portrait'),
    url(r'^update_portrait$', 'socialnetwork.views.edit_portrait', name='update_portrait'),
    url(r'^ajax_update$', 'socialnetwork.views.ajax_update',name='ajax_update'),
    url(r'^comment/(?P<item_id>\d+)$', 'socialnetwork.views.comment',name='comment'),
    url(r'^portrait_user/(?P<id>\d+)$', 'socialnetwork.views.get_userportrait', name='portrait_user'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'socialnetwork.views.confirm_registration', name='confirm'),

)
