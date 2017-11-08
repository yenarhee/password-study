from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^contact/$', TemplateView.as_view(template_name='contact.html'), name='contact'),
    url(r'^impressum/$', TemplateView.as_view(template_name='impressum.html'), name='impressum'),
    url('^accounts/', include('account.urls')),
    url('^accounts/', include('django.contrib.auth.urls')),
    url(r"^ranking/$", views.ranking, name="ranking"),
    ]

