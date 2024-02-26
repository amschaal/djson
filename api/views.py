from rest_framework import viewsets
from djson.models import ModelType
from djson.serializers import ContentTypeSerializer, ModelTypeSerializer
from django.contrib.contenttypes.models import ContentType

class ModelTypeViewset(viewsets.ModelViewSet):
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

class ContentTypeViewset(viewsets.ModelViewSet):
    queryset = ContentType.objects.distinct()
    serializer_class = ContentTypeSerializer
    filterset_fields = {
        'id':['icontains','exact'],
        'app_label': ['exact'],
        'model':['exact', 'in']
        }
