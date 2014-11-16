from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^destination/(?P<code>[\w\-]+)/$', 'flights.views.destination', name='destination'),
    url(r'^$', 'flights.views.home', name='home'),
)
