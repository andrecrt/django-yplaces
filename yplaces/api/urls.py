from django.conf.urls import patterns, url

from handlers import PlacesHandler, PlaceIdHandler

urlpatterns = patterns('',
                       
    # Places.
    url(r'^/?$', PlacesHandler.as_view(), name='index'),
    url(r'^/(?P<pk>[0-9]+)/?$', PlaceIdHandler.as_view(), name='id')
)