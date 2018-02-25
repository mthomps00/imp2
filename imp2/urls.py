"""imp2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url, static
from django.contrib.auth.views import login, logout_then_login
from rsvp.views import *
from nod.views import *

# enable admin
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
#    url(r'^$', dashboard, name="dashboard"), # lists upcoming and recent camps
#    url(r'^camp/(?P<camptheme>[a-zA-Z-,& ]+)/$', include([
#        url(r'^$', camp, name="camp"), # camp dashboard
#        url(r'^detail/$', campdetail, name="campdetail"), # camp dashboard
#        url(r'^contacts/$', contacts, name="contacts"), # one-on-one contacts
#        url(r'^mailchimp/setup/$', mailcamp, name="mailcamp"), # setup camp in MailChimp
#        url(r'^mailchimp/sync/$', mailsync, name="mailsync"), # sync invites with MailChimp
#        url(r'^csv/$', camp_table, name="camp_table"), # CSV of all camp invitees
#        ])),
#    url(r'^usercsv/$', user_table, name="user_table"), # CSV of all users
#    url(r'^route/(?P<rand_id>\d{8})/$', include([
#        url(r'^$', route, name="route"), # routes incoming users based on invitation status
#        url(r'^(?P<rand_id>\d{8})/faq/$', faq, name="faq"), #faq
#        ])),
#    url(r'^rsvp/(?P<rand_id>\d{8})/$', include([
#        url(r'^$', invite, name="invite"), # first landing page for invitees
#        url(r'^pay/$', pay, name="pay"), # processes payment for camp registration
#        url(r'^update/$', update, name="update"), # allows invitees to update profile information and complete registration
#        url(r'^details/$', details, name="details"), # landing page for confirmed attendees
#        url(r'^stipend/$', stipend, name="stipend"), # stipend request form
#        url(r'^cancel/$', cancel, name="cancel"), # registration cancellation page
#        url(r'^confirm_cancel/$', confirm_cancel, name="confirm_cancel"), # registration cancellation confirmation
#        url(r'^restore/$', restore, name="restore"), # allows users who've canceled or refused to request waitlisting
#        url(r'^confirm_restore/$', confirm_restore, name="confirm_restore"), # waitlist request confirm
#        url(r'^waitlist/$', waitlist, name="waitlist"), # landing page for waitlisted users
#        url(r'^(?P<main_object>\w+)/signup/$', signup, name="signup"), # allows users to sign up for roommates, ignite talks, etc.
#        url(r'^(?P<main_object>\w+)/signdown/$', signdown, name="signdown"), # allows users to cancel roommate/ignite/etc signups
#        url(r'^(?P<main_object>\w+)/(?P<object_id>\d+)/delete/$', delete_signup, name="delete_signup"), # confirmation of cancellation
#        ])),

    # Nod views
#    url(r'^search/$', search, name="search"), # generic search of all users
#    url(r'^search/nominate/$', search, {'nominate': True}, name="nodsearch"), # search for potential nominees for camp
#    url(r'^(?P<camptheme>[a-zA-Z-,& ]+)/nominate/$', search, {'nominate': True}, name="nodsearch"), # nominate users for a particular camp
#    url(r'^nominate/(?P<camptheme>[a-zA-Z-,& ]+)/$', nominate, name="nominate"), # nominate for camp
#    url(r'^nominate/$', nominate, name="nominate"), # nominate for camp
#    url(r'^nominated/$', nominated, name="nominated"), # nominated users
#    url(r'^vote/(?P<round>\d+)/$', vote, name="vote"), # voting table
#    url(r'^round/(?P<round>\d+)/$', round, name="round"), # voting round breakdown
#    url(r'^invites/(?P<camptheme>[a-zA-Z-,& ]+)/$', invites, name="invites"), # post-vote invite
#    url(r'^process/$', process_emails, name="process_emails"), # voting round breakdown


    # Deprecated views (replace these!)
#    url(r'^camps/(?P<camptheme>[a-zA-Z-,& ]+)/dietary/$', dietary, name="dietary"),
#    url(r'^camps/(?P<camptheme>[a-zA-Z-,& ]+)/stipends/$', stipends, name="stipends"),
#    url(r'^camps/(?P<camptheme>[a-zA-Z-,& ]+)/sessions/$', sessions, name="sessions"),
#    url(r'^camps/(?P<camptheme>[a-zA-Z-,& ]+)/mailsync/$', mailsync, name="mailsync"),
#    url(r'^user/(\w+)/$', user_page, name="user_page"),
                       
    # Django.contrib views                   
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^login/$', login, {'template_name': 'login.html'}),
    url(r'^logout/$', logout_then_login),
    
    # For flatpages to work, this apparently has to come last
#    url(r'^pages/', include('django.contrib.flatpages.urls')),
    ]

# if settings.DEBUG == True:
#    urlpatterns += [
#        url(r'^static/media/(?P<path>.*)$', 'django.views.static.serve', {
#            'document_root': settings.MEDIA_ROOT,
#        }),
#   ]
