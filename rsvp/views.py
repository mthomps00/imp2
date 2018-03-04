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
from rsvp.forms import *
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
    '''Main dashboard for camp administrators'''
    
    today = date.today()
    upcoming = Camp.objects.filter(start_date__gte=today)
    past = Camp.objects.filter(start_date__lte=today).order_by('-start_date')
    
    variables = {
        'upcoming' : upcoming,
        'past': past,
    }
    return render(request, 'reboot/reboot.html', variables)

@login_required
def camp(request, camptheme):
    '''Individual camp dashboard for camp administrators'''
    
    camp = get_object_or_404(Camp, theme__iexact=camptheme)
    syncform = GoogleSyncForm()
    invitations = Invitation.objects.filter(camp=camp)
    for invitation in invitations:
        invitation.status = invitation.get_status_display()

    confirmed = invitations.filter(status='Y')
    confirmed_pocs = confirmed.filter(user__sparkprofile__poc=True)
    confirmed_women = confirmed.filter(user__sparkprofile__woman=True)
    confirmed_journos = confirmed.filter(user__sparkprofile__journo=True)
    invitee_pocs = invitations.filter(user__sparkprofile__poc=True)
    invitee_women = invitations.filter(user__sparkprofile__woman=True)
    invitee_journos = invitations.filter(user__sparkprofile__journo=True)
    
    def percent(part, whole):
        denominator = float(len(whole))
        numerator = float(len(part))
        if denominator <= 0:
            denominator = 1
        return int(100 * (numerator/denominator))
        
    percent_poc = percent(confirmed_pocs, confirmed)
    percent_women = percent(confirmed_women, confirmed)
    percent_journos = percent(confirmed_journos, confirmed)
    percent_all_poc = percent(invitee_pocs, invitations)
    percent_all_women = percent(invitee_women, invitations)
    percent_all_journos = percent(invitee_journos, invitations)
    
    variables = {
        'camp': camp,
        'invitations': invitations,
        'confirmed': confirmed,
        'percent_poc': percent_poc,
        'percent_women': percent_women,
        'percent_journos': percent_journos,
        'percent_all_poc': percent_all_poc,
        'percent_all_women': percent_all_women,
        'percent_all_journos': percent_all_journos,
    }
    return render(request, 'reboot/camp.html', variables)

##########
# Invitee views
##########

def route(request, rand_id):
    '''Route an invitation based on its status.'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    
    if invitation.status == 'I':
        return redirect('update', rand_id=rand_id)
    if invitation.status == 'N' or invitation.status == 'C':
        return redirect('restore', rand_id=rand_id)
    if invitation.status == 'Y':
        return redirect('details', rand_id=rand_id)
    if invitation.status == 'W':
        return redirect('waitlist', rand_id=rand_id)
    else:
        return redirect('invite', rand_id=rand_id)

def invite(request, rand_id):
    '''Display the basic original invitation'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    
    # If the invitation has been canceled, declined, or waitlisted, redirect it.
    if invitation.status == 'N' or invitation.status == 'C' or invitation.status == 'W':
        return redirect('route', rand_id=rand_id)
    
    if invitation.camp.paid:
        import stripe
        invitation.key = settings.STRIPE_PUBLIC_KEY
        invitation.stripe_cost = invitation.price() * 100
    
    date_format = '%A, %B %d, %Y'
    welcomedict = {
        'first_name': invitation.user.first_name,
        'last_name': invitation.user.first_name,
        'display_name': invitation.camp.display_name,
        'description': invitation.camp.description,
        'logistics': invitation.camp.logistics,
        'expires': invitation.expires.strftime(date_format),
        'venue': invitation.camp.venue,
        'venue_address': invitation.camp.venue_address,
        'hotel': invitation.camp.hotel,
        'hotel_link': invitation.camp.hotel_link,
        'hotel_code': invitation.camp.hotel_code,
        'invite_link': invitation.get_absolute_url(),
    }
    
    invitation.welcome = invitation.camp.welcome.format(**welcomedict)
    
    variables = {
        'invitation': invitation,
        'camp': invitation.camp,
    }
    return render(request, 'reboot/invite.html', variables)

def update(request, rand_id):
    '''Allow users to update their invitation status'''

    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    user = invitation.user
    profile = SparkProfile.objects.get(user=user)
    
    # Redirect users who've said they can't attend to put them on the waitlist.
    if invitation.status == 'N' or invitation.status == 'C':
        return redirect('restore', rand_id=rand_id)    

    # If the user has submitted a profile form ...
    if request.method == 'POST':
        profileform = SparkProfileForm(request.POST, request.FILES, instance=profile)

        # ... and that form is valid ...
        if profileform.is_valid():
            profile.bio = profileform.cleaned_data['bio']
            profile.job_title = profileform.cleaned_data['job_title']
            profile.employer = profileform.cleaned_data['employer']
            profile.url = profileform.cleaned_data['url']
            profile.twitter = profileform.cleaned_data['twitter']
            profile.phone = profileform.cleaned_data['phone']
            profile.email = profileform.cleaned_data['email']
            profile.dietary = profileform.cleaned_data['dietary']
            profile.headshot = profileform.cleaned_data['headshot']
            user.email = profileform.cleaned_data['email']
            profile.save()
            user.save()

            # ... AND that form has a bio and headshot ...
            if profile.bio != '' and bool(profile.headshot) == True:

                # If the user is on the waitlist, merely update their information. Send no email.
                if invitation.status == 'W':
                    messages.success(request, 'Thank you for updating your information! We\'ll let you know as soon as possible if we can accommodate you at %s' % (invitation.camp.display_name))
                    return redirect('waitlist', rand_id=rand_id)
                
                # And if they're not on the waitlist, then ...
                else: 
                    
                    # If they're already confirmed, also just update; no email.
                    if invitation.status == 'Y':
                        messages.success(request, '%s, thank you for updating your information!' % (user.first_name))
                    
                    # Otherwise, set them as confirmed, and send a confirmation email.
                    else:
                        messages.success(request, '%s, you\'re now registered for %s.' % (user.first_name, invitation.camp.display_name))
                        invitation.status = 'Y'
                        
                        # Confirmation email
                        date_format = '%A, %B %d, %Y'
                        confirmdict = {
                            'first_name': user.first_name,
                            'last_name': user.first_name,
                            'display_name': invitation.camp.display_name,
                            'description': invitation.camp.description,
                            'logistics': invitation.camp.logistics,
                            # 'cancel_by': invitation.camp.cancel_by.strftime(date_format),
                            'venue': invitation.camp.venue,
                            'venue_address': invitation.camp.venue_address,
                            'hotel': invitation.camp.hotel,
                            'hotel_link': invitation.camp.hotel_link,
                            'hotel_code': invitation.camp.hotel_code,
                            'invite_link': invitation.get_absolute_url(),
                        }
                        body = invitation.camp.confirmation_email.format(**confirmdict)
                        subject = 'Confirming your registration for %s' % invitation.camp.display_name
                        if settings.DEBUG == False:
                            email = user.email
                        else:
                            email = settings.TEST_EMAIL
                        send_mail(subject, body, 'rsvp@sparkcamp.com', ['rsvp@sparkcamp.com', email], fail_silently=True)
                        
                    invitation.save()
                    return redirect('details', rand_id=rand_id)
            else:
                invitation.status = 'I'
                messages.warning(request, 'We\'re still missing some key pieces of info to finalize your registration.')
                invitation.save()
        
        else:
            messages.warning(request, 'Sorry, there was an error with your form. Please correct the fields that are highlighted below.')
        
    else:
        profileform = SparkProfileForm(instance=profile)
    
    variables = {
        'invitation': invitation,
        'camp': invitation.camp,
        'profile': profile,
        'headshot': bool(profile.headshot),
        'profileform': profileform,
    }
    return render(request, 'reboot/update.html', variables)

def restore(request, rand_id):
    '''Restore a canceled or declined invitation'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    
    variables = {
        'invitation': invitation,
        'camp': invitation.camp,
    }
    return render(request, 'reboot/restore.html', variables)

def confirm_restore(request, rand_id):
    '''Confirm the restoration of an invitation'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    invitation.status = 'W'
    invitation.save()
    messages.success(request, 'Thanks for letting us know you can make it! We have you on the waitlist, and we\'ll let you know as soon as possible whether we can still accommodate you.')
    return redirect('route', rand_id=rand_id)

def pay(request, rand_id):
    '''Process ticket payments'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    profile = invitation.user.sparkprofile
    profileform = SparkProfileForm(instance=profile)
    
    # If the user has submitted a form
    if request.method == 'POST':
        # If the invitation isn't a comp ticket
        if invitation.comp_ticket != True:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY    
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            error = False

            invitation.cost = invitation.price()
            invitation.stripe_cost = invitation.price() * 100;
            invitation.key = settings.STRIPE_PUBLIC_KEY

            # Create the charge on Stripe's servers - this will charge the user's card
            try:
                charge = stripe.Charge.create(
                  amount=invitation.stripe_cost, # amount in cents, again
                  currency="usd",
                  card=token,
                  description=invitation.user.username,
                  receipt_email=email
                )
            except stripe.error.CardError as e:
            # The card has been declined
                body = e.json_body
                error  = body.get('error', {})
                pass

            if error:
                invitation.has_paid = False
            else:
                invitation.has_paid = True
                invitation.status = 'I'
                invitation.save()
        # If this is actually a comp ticket, just process it as paid
        else:
            invitation.has_paid = True
            if (invitation.has_paid == True) and (invitation.user.sparkprofile.bio != '') and (bool(invitation.user.sparkprofile.headshot) == True):
                invitation.status = 'Y'
            else:
                invitation.status = 'I'
        
        invitation.save()
        
    variables = {
        'invitation': invitation,
        'headshot': bool(invitation.user.sparkprofile.headshot),
        'camp': invitation.camp,
        'cost': invitation.cost,
        'token': token,
        'email': email,
        'error': error,
        'profileform': profileform,
    }
    return render(request, 'reboot/pay.html', variables)

def cancel(request, rand_id):
    '''Cancel a previously accepted invitation'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    today = datetime.date.today()
    cancel_by = invitation.camp.cancel_by.date()
    
    if today > cancel_by:
        invitation.partial_refund = True
    else:
        invitation.partial_refund = False
    
    variables = {
        'invitation': invitation,
        'camp': invitation.camp,
    }
    return render(request, 'reboot/cancel.html', variables)

def confirm_cancel(request, rand_id):
    '''Confirm the cancellation of an invitation'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    messages.warning(request, 'Your registration has been canceled. Again, we\'re sad to hear you can\'t make it. If your circumstances change, please do let us know.')
    
    invitation.status = 'C'
    invitation.save()
    
    return redirect('restore', rand_id=rand_id)
    
def details(request, rand_id):
    '''Find stipend/roommate/ignite requests related to an invite.'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    invitation.pretty_status = invitation.get_status_display()
    confirmed = Invitation.objects.filter(camp=invitation.camp).filter(status='Y').order_by('user__last_name')

    if invitation.status != 'Y':
        return redirect('route', rand_id=rand_id)
    
    # Find roommate requests
    try:
        roommate = invitation.roommate
        
        # Find potential roommate matches
        roommate.potentials = []
        
        for potential in Roommate.objects.exclude(invitation=invitation):
            if (potential.invitation.camp == invitation.camp):
                if (roommate.roommate == 'A') or (potential.sex == roommate.roommate):
                    if (potential.roommate == 'A') or (roommate.sex == potential.roommate):
                        roommate.potentials.append(potential)
        
        roommate.sex = roommate.get_sex_display()
        roommate.roommate = roommate.get_roommate_display()
    except:
        roommate = False
    
    # Find stipend requests
    try:
        stipend = invitation.stipend
        stipend.jobhelp = stipend.get_employer_subsidized_display()
    except:
        stipend = False
        
    # Find Ignite sign-ups
    try:
        ignite = invitation.ignite
        ignite.experience = ignite.get_experience_display()
    except:
        ignite = False
    
    # Find session proposals
    try:
        session = invitation.session
    except:
        session = False
    
    invitation.pretty_status = invitation.get_status_display()

    variables = {
        'invitation': invitation,
        'camp': invitation.camp,
        'confirmed': confirmed,
        'roommate': roommate,
        'stipend': stipend,
        'ignite': ignite,
        'session': session,
        'headshot': bool(invitation.user.sparkprofile.headshot),
    }
    return render(request, 'reboot/details.html', variables)

def signup(request, rand_id, main_object):
    '''Add a roommate, ignite, or session request to an invite.'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    main_object = eval(main_object)
    try:
        object = main_object.objects.get(invitation=invitation)
    except main_object.DoesNotExist:
        object = main_object(invitation=invitation)
    
    properties = {
        'Roommate': ( 'sex', 'roommate', 'more', ),
        'Ignite': ( 'title', 'experience', 'description', ),
        'Session': ( 'title', 'description', ),
    }
    
    local_dict = properties[main_object.__name__]
    
    if request.method == 'POST':
        form = eval('%sForm(request.POST, instance=object)' % main_object.__name__)
        if form.is_valid():
            for item in local_dict:
                key = compile(item, '', 'exec')
                object.key = form.cleaned_data[item]
            object.save()
            messages.success(request, 'You\'ve got it. You\'re on the %s List.' % (main_object.__name__))
            return redirect('route', rand_id=rand_id)
    else:
        form = eval('%sForm(instance=object)' % main_object.__name__)
    
    variables = {
        'invitation': invitation,
        'camp': invitation.camp,
        'form': form,
        'object': object,
        'main_object': main_object.__name__,
        'properties': properties,
        'rand_id': rand_id,
    }
    
    return render(request, 'reboot/signup.html', variables)

def signdown(request, rand_id, main_object):
    '''Delete a roommate, ignite, or session request from an invite.'''
    
    invitation = get_object_or_404(Invitation, rand_id=rand_id)
    main_object = eval(main_object)
    try:
        object = main_object.objects.get(invitation=invitation)
    except main_object.DoesNotExist:
        raise Http404(u'Could not find this %s.' % main_object)
    
    variables = {
        'invitation': invitation,
        'camp': invitation.camp,
        'object': object,
        'main_object': main_object.__name__,
        'rand_id': rand_id,
    }
    
    return render(request, 'reboot/signdown.html', variables)
  
def delete_signup(request, main_object, object_id, rand_id):
    '''Confirm delete of a roommate/ignite/session request.'''
    
    main_object = eval(main_object)
    object = get_object_or_404(main_object, id=object_id)
    object.delete()
    messages.success(request, 'You\'ve got it. You\'re no longer on the %s List.' % (main_object.__name__))
    return redirect('route', rand_id=rand_id)
