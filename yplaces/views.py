import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.text import slugify

from models import Place

# Instantiate logger.
logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse('places')


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
    try:
        place = Place.objects.get(pk=pk, active=True)
    except ObjectDoesNotExist:
        raise Http404

    # Render page
    return render_to_response('yplaces/place.html',
                              { 'place': place, 'rating': place.get_rating(),
                               'reviews_api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:reviews', args=[place.pk]) },
                              context_instance=RequestContext(request))