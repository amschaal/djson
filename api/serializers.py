from rest_framework import serializers
from djson.models import ModelType
from django.contrib.contenttypes.models import ContentType

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        exclude = []

class ModelTypeSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()
    def get_model(self, instance):
        return instance.content_type.model if instance and instance.content_type else None
    class Meta:
        model = ModelType
        exclude = []
