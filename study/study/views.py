from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from account.models import LoginAttempt, UserProfile, EmailVerification, Feedback
from account.forms import RankingNameForm
from account.utils import get_user_profile_for_user, get_ranking


def ranking(request):
    ranking = get_ranking()
    args = {}
    # User is not logged in
    if not request.user.is_authenticated():
        user_profile = None
    # User is logged in
    else:
        user_profile = get_user_profile_for_user(user=request.user)

        if request.method == 'POST':
            form = RankingNameForm(request.POST)  # create form object
            if form.is_valid():
                pseudonym = request.POST.get('pseudonym', None)
                user_profile.pseudonym = pseudonym
                user_profile.save()
                return render(request, 'ranking.html',
                              {'user_profile': user_profile, 'ranking': ranking,
                               'password': user_profile, 'form': RankingNameForm()})

    args['form'] = RankingNameForm()
    args['ranking'] = ranking
    args['user_profile'] = user_profile
    return render(request, 'ranking.html', args)
