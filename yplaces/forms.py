import logging
from django import forms

from models import Place

# Instantiate logger.
logger = logging.getLogger(__name__)


class PlaceForm(forms.ModelForm):
    """
    Fields required to create/update Places.
    """
    class Meta:
        model = Place