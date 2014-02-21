import logging
from django.db import models
from django.conf import settings

# Instantiate logger.
logger = logging.getLogger(__name__)


class Place(models.Model):
    """
    Place.
    """
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return self.name
    
    def get_rating(self):
        """
        Returns the Place's rating.
        """
        if hasattr(self, 'rating'):
            return { 'value': self.rating.value, 'reviews': self.rating.reviews }
        else:
            return { 'value': 0, 'reviews': 0 }
    

class Rating(models.Model):
    """
    Place's rating, based on reviews average.
    """
    place = models.OneToOneField(Place)
    value = models.IntegerField()
    reviews = models.IntegerField()
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return str(self.place)


class Photo(models.Model):
    """
    Place's photos.
    """
    place = models.ForeignKey(Place)
    file = models.ImageField(upload_to='yplaces/photos/')
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    def __unicode__(self):
        """
        String representation of the instance.
        """
        return str(self.place)


class Review(models.Model):
    """
    User review of a place.
    """
    place = models.ForeignKey(Place)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()
    comment = models.TextField()
    photo = models.OneToOneField(Photo, blank=True, null=True)
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return str(self.place)