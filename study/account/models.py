from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.core.validators import validate_comma_separated_integer_list


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name='profile')
    password = models.CharField(max_length=30)
    last_login = models.DateTimeField(default=datetime(2017, 1, 1), verbose_name='last_login')
    login_days = models.PositiveIntegerField(default=0)
    best_timing = models.DecimalField(null=True, default=None, max_digits=8, decimal_places=3)
    last_timing = models.DecimalField(null=True, default=None, max_digits=8, decimal_places=3)
    verified = models.BooleanField(verbose_name='verified', default=False)
    pseudonym = models.CharField(null=True, max_length=15)
    USERNAME_FIELD = 'username'

    def __str__(self):
        return "user profile for %s" % self.user

    def login(self):
        now = timezone.localtime(timezone.now())
        last_login_local = timezone.localtime(self.last_login)
        if last_login_local.date() < now.date() and last_login_local + timedelta(hours=1) <= now:
            self.login_days += 1
            self.last_login = now
            self.save()


# create userprofile if it does not exist
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'password', 'last_login', 'login_days', 'best_timing', 'last_timing', 'verified', "pseudonym")


class LoginAttempt(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    entry = models.CharField(max_length=30)
    keystroke = models.CharField(max_length=50)
    keystroke_intervals = models.CharField(max_length=200, validators=[validate_comma_separated_integer_list])
    user_agent = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)


class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'entry', 'user_agent', 'keystroke', 'keystroke_intervals', 'timestamp')


class PasswordRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class PasswordRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp')


class EmailVerification(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='created',
                                   default=timezone.now)
    sent = models.DateTimeField(verbose_name='sent', null=True)
    key = models.CharField(verbose_name='key', max_length=64, unique=True)

    class Meta:
        verbose_name = "email confirmation"
        verbose_name_plural = "email confirmations"

    def __str__(self):
        return "confirmation for %s" % self.user_profile

    @classmethod
    def create(cls, user_profile):
        key = get_random_string(64).lower()
        return cls._default_manager.create(user_profile=user_profile,
                                           key=key)

    def key_expired(self):
        expiration_date = self.sent + timedelta(days=7)
        return expiration_date <= timezone.now()

    def confirm(self):
        if not self.key_expired() and not self.user_profile.verified:
            user_profile = self.user_profile
            user_profile.verified = True
            user_profile.save()
            return user_profile


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'created', 'sent', 'key')


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remembered_password = models.BooleanField()
    message = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'remembered_password', 'timestamp')
