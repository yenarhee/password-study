# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from .forms import SignupForm, SignupWithoutEmailForm, PasswordRequestForm, LoginForm, FeedbackForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from .models import LoginAttempt, UserProfile, EmailVerification, Feedback
from .utils import send_password_by_email, get_user_profile_for_user, update_best_timing
from django.views.decorators.csrf import csrf_exempt


def profile(request):
    # User is not logged in
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_login'))
    # User is logged in
    else:
        user = request.user
        args = {'user': user, 'user_profile': get_user_profile_for_user(user)}
        return render(request, 'profile.html', args)


def signup(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_profile'))
    else:
        args = {}
        if request.method == 'POST':
            form = SignupForm(request.POST)  # create form object
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('account_verification_sent'))
        else:
            form = SignupForm()
        args['form'] = form

        return render(request, 'signup.html', args)


def signup_without_email(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_profile'))
    else:
        args = {}
        if request.method == 'POST':
            form = SignupWithoutEmailForm(request.POST)  # create form object
            if form.is_valid():
                form.save()
                username = request.POST.get('username', '')
                user = User.objects.get(username=username)
                user_profile = get_user_profile_for_user(user=user)
                return render(request, 'signup_without_email_success.html',
                              {'username': username, 'password': user_profile.password})
        else:
            form = SignupWithoutEmailForm()
        args['form'] = form

        return render(request, 'signup_without_email.html', args)


def password_request(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_profile'))
    else:
        args = {}
        if request.method == 'POST':
            form = PasswordRequestForm(request.POST)  # create form object
            if form.is_valid():
                redirect = form.save()
                return HttpResponseRedirect(reverse(redirect))
        else:
            form = PasswordRequestForm()
        args['form'] = form

        return render(request, 'password_request.html', args)


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_profile'))
    else:
        args = {}
        if request.POST:
            form = LoginForm(request.POST)  # create form object
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            keystroke = request.POST.get('keystroke', '')
            keystroke_intervals = request.POST.get('keystroke_intervals', '')
            user_agent = request.META['HTTP_USER_AGENT']

            user = User.objects.filter(username=username).first()
            login_attempt = LoginAttempt(user=user, username=username, entry=password, keystroke=keystroke,
                                     keystroke_intervals=keystroke_intervals, user_agent=user_agent)
            login_attempt.save()

            if form.is_valid():
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        django_login(request, user)   # Django default login
                        user_profile = UserProfile.objects.filter(user=user).first()
                        user_profile.login()    # save login data in the user profile object
                        update_best_timing(keystroke_intervals, user_profile)
                        return HttpResponseRedirect(reverse('account_profile'))

        else:
            form = LoginForm()
        args['form'] = form

        return render(request, 'login.html', args)


def confirm_email(request, key):
    email_verification = EmailVerification.objects.filter(key=key).first()
    user_profile = email_verification.confirm()
    if user_profile:
        send_password_by_email(user_profile.user.email)
        return HttpResponseRedirect(reverse('account_confirmation'))
    else:
        return HttpResponseRedirect(reverse('index'))


def feedback(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_login'))

    else:
        args = {}
        if request.method == 'POST':
            form = FeedbackForm(request.POST)  # create form object
            if form.is_valid():
                user = request.user
                remembered_password = request.POST.get('remembered_password', '')
                message = request.POST.get('message', '')
                feedback = Feedback(user=user, remembered_password=remembered_password, message=message)
                feedback.save()
                return HttpResponseRedirect(reverse('account_feedback_sent'))
        else:
            form = FeedbackForm()
        args['form'] = form

        return render(request, 'feedback.html', args)
