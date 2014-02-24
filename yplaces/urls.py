from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^/?$', views.index, name='index'),
    url(r'^/(?P<pk>[0-9]+)/?$', views.place_id, name='id'),
    url(r'^/(?P<pk>[0-9]+)/(?P<slug>[a-zA-Z0-9-]+)/?$', views.place_slug, name='slug'),
    url(r'^/(?P<pk>[0-9]+)/(?P<slug>[a-zA-Z0-9-]+)/photos/?$', views.photos, name='photos')
)