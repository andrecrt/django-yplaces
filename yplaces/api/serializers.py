import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from yapi.serializers import BaseSerializer

# Instantiate logger.
logger = logging.getLogger(__name__)


class PlaceSerializer(BaseSerializer):
    """
    Adds methods required for instance serialization.
    """
        
    def to_simple(self, obj, user=None):
        """
        Please refer to the interface documentation.
        """
        # Build response.
        simple = {
            'id': obj.pk,
            'url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:id', args=[obj.pk]),
            'name': obj.name,
            'address': obj.address,
            'postal_code': obj.postal_code,
            'city': obj.city,
            'state': obj.state,
            'country': obj.country,
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'email': obj.email,
            'phone_number': obj.phone_number,
            'website': obj.website,
            'rating': obj.get_rating()
        }
        
        # If user is staff, add aditional info.
        if user and user.is_staff:
            simple.update({
                'created_at': obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'created_by': {
                    'email': obj.created_by.email
                },
                'active': obj.active
            })
        
        # Return.
        return simple