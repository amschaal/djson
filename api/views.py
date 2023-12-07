from rest_framework import viewsets
from djson.models import ModelType
from .serializers import ModelTypeSerializer

class ModelTypeViewset(viewsets.ReadOnlyModelViewSet):
    queryset = ModelType.objects.distinct()
    serializer_class = ModelTypeSerializer
    filterset_fields = {
        'name':['icontains','exact'],
        'id':['icontains','exact'],
        'content_type': ['exact'],
        'content_type__model':['exact'],
        'description':['icontains']
        }
    search_fields = ('name', 'id')
