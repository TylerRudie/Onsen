"""Onsen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from atlas.views import *

urlpatterns = [
    url(r'^$', 'atlas.views.home', name='home'),


###################

    url(r'^events/calendar/all_events/',
        'atlas.views.all_events',
        name='all_events'),

    url(r'^events/calendar/$',
        'atlas.views.calendar',
        name='calendar'),



    url(r'^events/new/$',
        'atlas.views.new_event',
        name='event_new'),

    url(r'^events/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_event',
        name='event_edit'),

###################

    url(r'^hardware/new/$',
        'atlas.views.new_hardware',
        name='hardware_new'),

    url(r'^hardware/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_hardware',
        name='hardware_edit'),

    url(r'^hardware/list/$',
        list_hardware,
        name='hardware_list'),

###################

    url(r'^contact/new/$',
        'atlas.views.new_contact',
        name='contact_new'),

    url(r'^contact/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_contact',
        name='contact_edit'),

###################

    url(r'^airbill/new/$',
        'atlas.views.new_airbill',
        name='airbill_new'),

    url(r'^airbill/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_airbill',
        name='airbill_edit'),

###################

    url(r'^pool/new/$',
        'atlas.views.new_pool',
        name='pool_new'),

    url(r'^pool/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_pool',
        name='pool_edit'),

###################

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^admin/',
        include(admin.site.urls)),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)