# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.models import User
from registration.forms import RegistrationForm

from .models import UserProfile, PasswordRequest, Feedback
from .utils import (generate_password, send_password_by_email,
                    send_verification_email, get_user_profile_for_email)


class SignupForm(RegistrationForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'Email-Adresse'}))

    email_exists = False

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        del self.fields['password1']
        del self.fields['password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_profile = get_user_profile_for_email(email)
        if user_profile:
            if user_profile.verified:
                raise forms.ValidationError(
                    "Diese Email-Adresse ist bereits registriert.")
            else:
                self.email_exists = True
        return email

    def save(self, **kwargs):
        password = str(generate_password())
        email = self.cleaned_data["email"]
        if not self.email_exists:
            user = User(username=email, email=email)
            user.set_password(password)
            user.save()
            user_profile = UserProfile(user=user, password=password)
            user_profile.save()
        self.send_verification()

    def send_verification(self):
        email = self.cleaned_data["email"]
        send_verification_email(email)


class SignupWithoutEmailForm(RegistrationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(
            attrs={'placeholder': 'Benutzername'}))

    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super(SignupWithoutEmailForm, self).__init__(*args, **kwargs)
        del self.fields['password1']
        del self.fields['password2']
        del self.fields['email']

    def clean_email(self):
        username = self.cleaned_data.get('username')
        user_profile = User.objects.get(username=username)
        if user_profile:
            raise forms.ValidationError(
                    "Diese Benutzername ist bereits vergeben.")
        return username

    def save(self, **kwargs):
        password = str(generate_password())
        username = self.cleaned_data["username"]
        user = User(username=username, email='')
        user.set_password(password)
        user.save()
        user_profile = UserProfile(user=user, password=password, verified=True)
        user_profile.save()


class PasswordRequestForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'Email-Adresse'}))

    class Meta:
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).count():
            raise forms.ValidationError("Diese Email-Adresse ist nicht registriert.")
        return email

    def save(self):
        email = self.cleaned_data.get('email')
        user = User.objects.filter(email=email)[0]
        password_request = PasswordRequest(user=user)
        password_request.save()

        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile.verified:
            send_password_by_email(email)
            return 'account_password_sent'
        else:
            send_verification_email(email)
            return 'account_verification_sent'

class RankingNameForm(forms.Form):
    pseudonym = forms.CharField(required=False, max_length=15, widget=forms.TextInput(
            attrs={'placeholder': 'Ihr Name auf der Rangliste'}))

    def clean_pseudonym(self):
        pseudonym = self.cleaned_data.get('pseudonym')
        if len(pseudonym) > 15:
            raise forms.ValidationError("Der Name kann maximal 15 Zeichen lang sein.")
        if pseudonym == '':
            pseudonym = None
        return pseudonym

class LoginForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(
            attrs={'placeholder': 'Email-Adresse / Benutzername'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
            attrs={'placeholder': 'Passwort'}))
    keystroke = forms.CharField(required=False, widget=forms.HiddenInput(
            attrs={'type': 'text'}))
    keystroke_intervals = forms.CharField(required=False, widget=forms.HiddenInput(
            attrs={'type': 'text'}))

    class Meta:
        fields = ('username', 'password')

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        password_entry = cleaned_data.get('password')
        username = cleaned_data.get('username')
        keystroke = cleaned_data.get('keystroke') or ''

        if User.objects.filter(username=username).count():
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.password != password_entry:
                raise forms.ValidationError("Bitte überprüfen Sie Ihre Login-Daten.")
            for char in list(password_entry):
                if char not in list(keystroke):
                    raise forms.ValidationError("Bitte geben Sie Ihr Passwort per Hand ein.")
        else:
            raise forms.ValidationError("Diese Email-Adresse oder Benutzername ist nicht registriert.")
        cleaned_data['username'] = username
        cleaned_data['password'] = password_entry
        cleaned_data['keystroke'] = keystroke

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.attrs = {'autocomplete': 'off'}


class FeedbackForm(forms.Form):
    remembered_password = forms.ChoiceField(label="Konnten Sie Ihr Passwort merken?",
                                            widget=forms.RadioSelect,
                                            choices=((False, 'Nein'), (True, 'Ja')))
    message = forms.CharField(required=False,
                              label='Nachricht',
                              max_length=500,
                              help_text='<br />Max. 500 Zeichen',
                              widget=forms.Textarea(
              attrs={'placeholder': 'Z.B. Was Ihnen gefallen oder nicht gefallen haben, Verbesserungsbedarf, ...',
                     'rows':8}))

    class Meta:
        fields = ('remembered_password', 'message',)
