from django.conf.urls import include, url
from wiki import views


urlpatterns = [

    url(r'^home/$',
        'wiki.views.help_home',
        name='help_home'),

    url(r'^event/$',
        'wiki.views.help_event',
        name='help_event'),

    url(r'^processing/$',
        'wiki.views.help_processing',
        name='help_processing'),

    url(r'^hardware/$',
        'wiki.views.help_hardware',
        name='help_hardware'),

    url(r'^pool/$',
        'wiki.views.help_pool',
        name='help_pool'),

    url(r'^contact/$',
        'wiki.views.help_contact',
        name='help_contact'),
]