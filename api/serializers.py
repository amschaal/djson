from rest_framework import serializers
from djson.models import ModelType
from django.contrib.contenttypes.models import ContentType

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        exclude = []

class ModelTypeSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer()
    class Meta:
        model = ModelType
        exclude = []
