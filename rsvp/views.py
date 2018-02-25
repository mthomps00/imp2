# coding: utf-8

from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template import Context, RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from rsvp.models import *
# from rsvp.forms import *
# from rsvp.mailsnake import MailSnake
# import mailchimp, random, csv, datetime, unicodecsv
from datetime import date, timedelta
from urllib.request import urlopen

##########
# Staff views
##########

@login_required
def user_page(request, username):
    user = get_object_or_404(User, username=username)        
    invitations = user.invitation_set.all()
    
    for invitation in invitations:
        invitation.status = invitation.get_status_display()
    
    variables = {
        'username': username,
        'invitations': invitations,
    }
    return render_to_response('users.html', variables, context_instance=RequestContext(request))

@login_required
def dashboard(request):
    today = date.today()
    upcoming = Camp.objects.filter(start_date__gte=today)
    past = Camp.objects.filter(start_date__lte=today).order_by('-start_date')
    
    variables = {
        'upcoming' : upcoming,
        'past': past,
    }
    return render(request, 'reboot/reboot.html', variables)

