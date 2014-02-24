import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseForbidden
from yapi.authentication import ApiKeyAuthentication, SessionAuthentication
from yapi.decorators import authentication_classes, permission_classes
from yapi.permissions import IsStaff
from yapi.resource import Resource
from yapi.response import HTTPStatus, Response

from serializers import PlaceSerializer, PhotoSerializer, ReviewSerializer
from yplaces.forms import PlaceForm, PhotoForm, ReviewForm
from yplaces.models import Place, Photo, Review

# Instantiate logger.
logger = logging.getLogger(__name__)


class PlacesHandler(Resource):
    """
    API endpoint handler.
    """
    # HTTP methods allowed.
    allowed_methods = ['POST', 'GET']
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def post(self, request):
        """
        Process POST request.
        """
        # Populate form with provided data.
        form = PlaceForm(request.data)
        
        # Create new instance.
        try:
            new_instance = form.save()
            return Response(request=request,
                            data=new_instance,
                            serializer=PlaceSerializer,
                            status=HTTPStatus.SUCCESS_201_CREATED)
            
        # Form didn't validate!
        except ValueError:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Process GET request.
        """
        # Lets start with all.
        results = Place.objects.all()
        
        #
        # Filters
        #
        filters = {}
        
        # **************** IMPORTANT ***************
        # Only show full listing (i.e. inactive places) to staff users.
        # ******************************************
        if request.user and not request.user.is_staff:
            results = results.filter(active=True)
        # If staff, can filter by active status.
        elif request.user and request.user.is_staff:
            try:
                active = request.GET['active']
                if active != '':
                    ['true', 'false'].index(active)
                    active = (active.lower() == 'true')
                    results = results.filter(active=active)
                    filters['active'] = active
            except KeyError:
                pass
            except ValueError:
                return Response(request=request,
                                data={ 'message': 'Invalid parameters', 'parameters': { 'active': ['Invalid value'] } },
                                serializer=None,
                                status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
        
        # Name.
        try:
            name = request.GET['name']
            if name != '':
                results = results.filter(Q(name__icontains=name))
                filters['name'] = name
        except KeyError:
            pass
        
        #
        # Return.
        #
        return Response(request=request,
                        data=results,
                        filters=filters,
                        serializer=PlaceSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
        
        
class PlaceIdHandler(Resource):
    """
    API endpoint handler.
    """
    
    # HTTP methods allowed.
    allowed_methods = ['GET', 'PUT']
    
    def get(self, request, pk):
        """
        Process GET request.
        """
        # Check if instance with given ID exists.
        try:
            instance = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only show inactive places to _staff_ users.
        # ******************************************
        if not instance.active and (request.user and not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Return.
        return Response(request=request,
                        data=instance,
                        serializer=PlaceSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
    
    @permission_classes([IsStaff])
    def put(self, request, pk):
        """
        Process PUT request.
        """
        # Check if instance with given ID exists.
        try:
            instance = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Populate form with provided data, for given instance.
        form = PlaceForm(request.data, instance=instance)
        
        # Update.
        try:
            form.save()
            return Response(request=request,
                            data=instance,
                            serializer=PlaceSerializer,
                            status=HTTPStatus.SUCCESS_200_OK)
            
        # Form didn't validate!
        except ValueError:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
            
            
class ReviewsHandler(Resource):
    """
    API endpoint handler.
    """
    # HTTP methods allowed.
    allowed_methods = ['POST', 'GET']
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def post(self, request, pk):
        """
        Process POST request.
        """
        # Check if (active) Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk, active=True)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Add user and place IDs to data.
        request.data['user'] = request.auth['user'].pk
        request.data['place'] = place.pk
        
        # Populate form with provided data.
        form = ReviewForm(request.data)
        
        # Create new instance.
        try:
            new_instance = form.save()
            return Response(request=request,
                            data=new_instance,
                            serializer=ReviewSerializer,
                            status=HTTPStatus.SUCCESS_201_CREATED)
            
        # Form didn't validate!
        except ValueError:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
    
    def get(self, request, pk):
        """
        Process GET request.
        """
        # Check if Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (request.user and not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Lets start with all.
        results = place.review_set.all()
        
        #
        # Return.
        #
        return Response(request=request,
                        data=results,
                        serializer=ReviewSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
        
        
class ReviewIdHandler(Resource):
    """
    API endpoint handler.
    """
    
    # HTTP methods allowed.
    allowed_methods = ['GET', 'DELETE']
    
    def get(self, request, pk, review_pk):
        """
        Process GET request.
        """
        # Check if instance with given ID for given Place ID exists. 
        try:
            place = Place.objects.get(pk=pk)
            instance = Review.objects.get(pk=review_pk, place=place)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (request.user and not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Return.
        return Response(request=request,
                        data=instance,
                        serializer=ReviewSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def delete(self, request, pk, review_pk):
        """
        Process DELETE request.
        """
        # Check if instance with given ID for given Place ID exists.
        try:
            place = Place.objects.get(pk=pk)
            instance = Review.objects.get(pk=review_pk, place=place)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (request.user and not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Check if Review belongs to user.
        elif instance.user != request.auth['user']:
            return HttpResponseForbidden()
        
        # Proceed...
        else:
            instance.destroy()
            return HttpResponse(status=HTTPStatus.SUCCESS_204_NO_CONTENT)
        

class PhotosHandler(Resource):
    """
    API endpoint handler.
    """
    # HTTP methods allowed.
    allowed_methods = ['POST', 'GET']
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def post(self, request, pk):
        """
        Process POST request.
        """
        # Check if (active) Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk, active=True)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Add user and place IDs to data.
        request.data['added_by'] = request.auth['user'].pk
        request.data['place'] = place.pk
        
        # Populate form with provided data.
        form = PhotoForm(request.POST, request.FILES)
        
        # Provided data is valid.
        if form.is_valid():
            raise Exception('Implement meh!')
        
        # Form didn't validate!
        else:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
    
    def get(self, request, pk):
        """
        Process GET request.
        """
        # Check if Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (request.user and not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Lets start with all.
        results = place.photo_set.all()
        
        #
        # Return.
        #
        return Response(request=request,
                        data=results,
                        serializer=PhotoSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
        
        
class PhotoIdHandler(Resource):
    """
    API endpoint handler.
    """
    
    # HTTP methods allowed.
    allowed_methods = ['GET']
    
    def get(self, request, pk, photo_pk):
        """
        Process GET request.
        """
        # Check if instance with given ID for given Place ID exists. 
        try:
            place = Place.objects.get(pk=pk)
            instance = Photo.objects.get(pk=photo_pk, place=place)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (request.user and not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Return.
        return Response(request=request,
                        data=instance,
                        serializer=PhotoSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)