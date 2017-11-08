# -*- coding: utf-8 -*-
import json
import os
from random import choice, randint, random
from codecs import open as codecs_open

from django.contrib.auth.models import User
from django.template import Context
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone

from .app_settings import *
from .models import UserProfile, EmailVerification

#assert os.path.isfile(WORDLIST_FILE)

def generate_password():
    # list of allowed symbols: ( ) ! @ # $ % & * - + = | \ { } [ ] : ; " ' < > , . ? /
    symbols = ('(', ')', '!', '@', '#', '$', '%', '&', '*', '-', '_', '+', '=', '|', '\\', '{',
               '}', '[', ']', ':', ';', '"', '\'', '<', '>', ',', '.', '?', '/')

    # random password length between 8 and 12
    length = randint(8,12)

    # password form: [l1][d][s][l2]
    l1_length = length//3 if random() > 0.5 else length//3 + 1
    d_length = length//3 - 1 if random() > 0.5 else length//3 - 2
    s_length = 1
    l2_length = length - (l1_length + d_length + s_length)

    l1 = get_random_word(l1_length)
    d = ''.join([str(randint(0,9)) for iterate in range(d_length)])
    s = ''.join([choice(symbols) for iterate in range(s_length)])
    l2 =  get_random_word(l2_length)

    password = '{}{}{}{}'.format(l1, d, s, l2)

    return password


def get_random_word(word_length):
    filename = WORDLIST_FILE
    num_words = WORDLIST_SIZE

    word = ''
    with open(filename, 'r') as word_file:
        # get all words in a list
        lines = word_file.read().split('\n')
        # find a word of the length
        while True:
            index = randint(0, num_words-1)
            word = lines[index]
            if word.isalpha() and len(word) == word_length:
                break
    assert len(word) == word_length
    return word


def send_verification_email(email):
    user = User.objects.filter(email=email).first()
    user_profile = UserProfile.objects.filter(user=user).first()
    email_verification = EmailVerification.create(user_profile=user_profile)
    email_verification.sent = timezone.now()
    email_verification.save()
    activate_url = '{}{}'.format(SITE_DOMAIN, reverse('account_confirm_email', kwargs={'key': email_verification.key}))
    send_email(email, 'email/verification', Context({'activate_url': activate_url}))


def send_password_by_email(email):
    user = User.objects.filter(email=email).first()
    user_profile = UserProfile.objects.filter(user=user).first()
    if user_profile:
        if user_profile.verified:
            send_email(email, 'email/password_request',
                       Context({'email': email, 'password': user_profile.password}))


def send_bulk_reminders():
    now = timezone.now()
    receivers = []
    user_profiles = UserProfile.objects.filter(verified=True)

    # choose who have not logged in today
    for user_profile in user_profiles:
        if user_profile.login_days < 5 and user_profile.last_login.date() < now.date():
            receivers.append(user_profile.user.email)

    # send bulk emails
    for email in receivers:
        send_reminder_email(email)


def send_reminder_email(email):
    login_page = '{}{}{}'.format(SITE_DOMAIN, CGI_PATH, reverse('account_login'))
    user_profile = get_user_profile_for_email(email)
    send_email(email, 'email/reminder',
               Context({'login_days': user_profile.login_days, 'login_page': login_page}))


def get_user_for_email(email):
    user = User.objects.filter(email=email).first()
    return user


def get_user_profile_for_user(user):
    user_profile = UserProfile.objects.filter(user=user).first()
    return user_profile


def get_user_profile_for_email(email):
    user = get_user_for_email(email)
    user_profile = get_user_profile_for_user(user)
    return user_profile


def get_password(user):
    return getattr(UserProfile.objects.filter(user=user).first(), 'password')


def send_email(email, template_prefix, context):
    if not email:
        return

    subject = render_to_string('{0}_subject.txt'.format(template_prefix), context).strip()
    body = render_to_string('{0}_message.txt'.format(template_prefix), context).strip()
    email_data = {'subject': subject, 'body': body, 'to': email}

    # handle if the file does not exist
    if not os.path.isfile(EMAIL_DATA_FILE):
        with codecs_open(EMAIL_DATA_FILE, "w+", encoding='utf-8') as json_file:
            json.dump({'emails': []}, json_file, ensure_ascii=False, encoding='utf-8', indent=4)

    # update email data file
    with codecs_open(EMAIL_DATA_FILE, "r+", encoding='utf-8') as json_file:
        data = json.load(json_file)
        data['emails'].append(email_data)
        json_file.seek(0)  # rewind
        json.dump(data, json_file, ensure_ascii=False, encoding='utf-8', indent=4)
        json_file.truncate()


def update_best_timing(keystroke_intervals, user_profile):
    keystroke_interval_list = [int(item) for item in keystroke_intervals.split(',')]
    timing = sum(keystroke_interval_list[1:])/1000.0
    user_profile.last_timing = timing
    best_timing = user_profile.best_timing
    if best_timing == None or best_timing > timing:
        user_profile.best_timing = timing
        user_profile.save()
        return True
    else:
        user_profile.save()
        return False

def get_ranking():
    objects = UserProfile.objects.all()
    rankings = objects.extra(select={
        'timing_is_null': 'best_timing IS NULL OR best_timing IS 0',},
        order_by=['timing_is_null','best_timing'],)
    return rankings
