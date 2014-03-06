import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.text import slugify

from models import Place, Rating, Review

# Instantiate logger.
logger = logging.getLogger(__name__)


def index(request):
    """
    Index page.
    """
    # Top places.
    top_rating = Rating.objects.all().order_by('-average')[:5]
    
    # Fetch latest reviews.
    reviews = Review.objects.all().order_by('-date')[:5]    
    
    # Render page.
    return render_to_response('yplaces/index.html',
                              { 'title': 'YPLACES',
                               'description': 'Description',
                               'top_rating': top_rating,
                               'reviews': reviews,
                               'places_api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:index') },
                              context_instance=RequestContext(request))


@login_required
def add(request):
    """
    Add new Place.
    """
    return render_to_response('yplaces/edit.html',
                              { 'api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:index'),
                               'action': 'POST' },
                              context_instance=RequestContext(request))


def search(request):
    """
    Place search.
    """
    return render_to_response('yplaces/search.html', context_instance=RequestContext(request))


def place_id(request, pk):
    """
    Checks if the place with given ID exists and, if it does, redirect to the page with respective slug.
    """
    try:
        place = Place.objects.get(pk=pk, active=True)
        return HttpResponseRedirect(reverse('yplaces:slug', args=[place.pk, slugify(place.name)]))
    except ObjectDoesNotExist:
        raise Http404


def place_slug(request, pk, slug):
    """
    Returns page for the place with the given ID.
    """
    # Fetch Place with given ID.
    try:
        place = Place.objects.get(pk=pk, active=True)
    except ObjectDoesNotExist:
        raise Http404
    
    # Highlighted Photos.
    photos = [None, None, None]
    no_photos = True
    for idx, photo in enumerate(place.photo_set.all()):
        if idx < 3:
            photos[idx] = photo
            no_photos = False
        else:
            break

    # Render page
    return render_to_response('yplaces/place.html',
                              { 'place': place,
                               'rating': place.get_rating(),
                               'photos': photos, 'no_photos': no_photos,
                               'reviews_api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:reviews', args=[place.pk]) },
                              context_instance=RequestContext(request))
    

@login_required
def edit(request, pk, slug):
    """
    Edit Place's information.
    """
    # Only staff members.
    if not request.user.is_staff:
        raise Http404
    
    # Fetch Place with given ID.
    try:
        place = Place.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404
    
    # Render page.
    return render_to_response('yplaces/edit.html',
                              { 'place': place,
                               'api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:id', args=[place.pk]),
                               'action': 'PUT' },
                              context_instance=RequestContext(request))

    
def photos(request, pk, slug):
    """
    Renders the Place's photo gallery.
    """
    # Fetch Place with given ID.
    try:
        place = Place.objects.get(pk=pk, active=True)
    except ObjectDoesNotExist:
        raise Http404
    
    # Render page.
    return render_to_response('yplaces/photos.html',
                              { 'place': place,
                               'rating': place.get_rating(),
                               'photos_api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:photos', args=[place.pk]) },
                              context_instance=RequestContext(request))