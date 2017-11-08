from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^profile/$', views.profile, name='account_profile'),
    url(r"^signup/$", views.signup, name="account_signup"),
    url(r"^signup_without_email/$", views.signup_without_email, name="account_signup_without_email"),
    url(r"^login/$", views.login, name="account_login"),
    url(r"^verification/sent$", TemplateView.as_view(template_name='verification_sent.html'),
        name="account_verification_sent"),
    url(r"^password/request/$", views.password_request, name="account_password_request"),
    url(r"^password/sent/$", TemplateView.as_view(template_name='password_sent.html'), name="account_password_sent"),
    url(r"^confirm-email/(?P<key>[-:\w]+)/$", views.confirm_email,
        name="account_confirm_email"),
    url(r"^confirmation$", TemplateView.as_view(template_name='confirmation.html'), name="account_confirmation"),
    url(r"^feedback/$", views.feedback, name="account_feedback"),
    url(r"^feedback/sent$", TemplateView.as_view(template_name='feedback_sent.html'), name="account_feedback_sent"),
]
