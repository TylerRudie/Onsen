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

     url(r'^events/packing_pdf/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        packing_pdfView.as_view(),
        name='event_packing_pdf'),

     url(r'^events/srf_pdf/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        srf_pdfView.as_view(),
        name='event_srf_pdf'),

    url(r'^events/checkin/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        checkin_hardware.as_view(),
        name='event_checkin'),

###################

    url(r'^hardware/new/$',
        'atlas.views.new_hardware',
        name='hardware_new'),

    url(r'^hardware/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_hardware',
        name='hardware_edit'),

    url(r'^hardware/list/$',
        list_hardware.as_view(),
        name='hardware_list'),

###################

    url(r'^contact/new/$',
        'atlas.views.new_contact',
        name='contact_new'),

    url(r'^contact/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_contact',
        name='contact_edit'),

    url(r'^contact/list/$',
        list_contact.as_view(),
        name='contact_list'),

###################

    url(r'^airbill/new/$',
        'atlas.views.new_airbill',
        name='airbill_new'),

    url(r'^airbill/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_airbill',
        name='airbill_edit'),

    url(r'^airbill/list/$',
        list_airbill.as_view(),
        name='airbill_list'),

###################

    url(r'^pool/new/$',
        'atlas.views.new_pool',
        name='pool_new'),

    url(r'^pool/edit/(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})/$',
        'atlas.views.edit_pool',
        name='pool_edit'),

    url(r'^pool/list/$',
        list_pool.as_view(),
        name='pool_list'),
###################
    url(r'^accounts/profile/$',  'atlas.views.home_redirect'),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^admin/',
        include(admin.site.urls)),

    # (r'^notifications/', get_nyt_pattern()),
    # (r'^wiki/$', get_wiki_pattern())
    url(r'^pdf/$', HelloPDFView.as_view())
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)