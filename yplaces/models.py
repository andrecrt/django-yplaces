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
    description = models.TextField(blank=True)
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
            return self.rating
        else:
            return None
        
    def refresh_rating(self):
        """
        Calculates Place's rating.
        """
        # No Place rating details, create.
        if not hasattr(self, 'rating'):
            rating = Rating(place=self)
        # Else, fetch Place's rating.
        else:
            rating = self.rating
            
        # Calculate Place's rating.
        reviews = 0
        total_ratings = 0
        for review in self.review_set.all():
            reviews += 1
            total_ratings += review.rating
        
        # Update Rating.
        if reviews > 0:
            rating.average = float(total_ratings) / reviews
            rating.reviews = reviews
            rating.save()    
        
        # Return rating.
        return self


class Rating(models.Model):
    """
    Place's rating, based on reviews average.
    """
    place = models.OneToOneField(Place)
    average = models.FloatField(default=0)
    reviews = models.IntegerField(default=0)
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return self.place.name
    
    def get_average_percentage(self):
        """
        Returns the Review's rating value in percentage.
        """
        return self.average*100/5


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
        return self.place.name


class Review(models.Model):
    """
    User review of a place.
    """
    # Available rating values.
    RATING_VALUES = (
        (1, '*'),
        (2, '* *'),
        (3, '* * *'),
        (4, '* * * *'),
        (5, '* * * * *')
    )
    
    # Fields.
    place = models.ForeignKey(Place)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(choices=RATING_VALUES)
    comment = models.TextField()
    photo = models.OneToOneField(Photo, blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return self.place.name
    
    def save(self, *args, **kwargs):
        """
        Override method to make sure Place's Rating is refreshed whenever a Review is saved.
        """
        super(Review, self).save(*args, **kwargs)
        self.place.refresh_rating()
    
    def destroy(self):
        """
        Deletes the Review and refreshes the Place's rating.
        """
        self.delete()
        self.place.refresh_rating()
        return self
    
    def get_rating_percentage(self):
        """
        Returns the Review's rating value in percentage.
        """
        return self.rating*100/5