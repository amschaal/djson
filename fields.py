from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from djson.validators import JsonSchemaValidator

#Allows Creation/Updating of related model fields with OBJECT instead of just id
#usage field_name = ModelRelatedField(model=Sample,serializer=SampleSerializer)
class ModelRelatedField(serializers.RelatedField):
    model = None
    pk = 'id'
    serializer = None
    def __init__(self, **kwargs):
        self.model = kwargs.pop('model', self.model)
        self.pk = kwargs.pop('pk', self.pk)
        self.serializer = kwargs.pop('serializer', self.serializer)
        assert self.model is not None, (
            'Must set model for ModelRelatedField'
        )
        assert self.serializer is not None, (
            'Must set serializer for ModelRelatedField'
        )
        self.queryset = kwargs.pop('queryset', self.model.objects.all())
        super(ModelRelatedField, self).__init__(**kwargs)
    def to_internal_value(self, data):
        if isinstance(data, int) or isinstance(data, str):
            kwargs = {self.pk:data}
            return self.model.objects.get(**kwargs)
        if data.get(self.pk,None):
            kwargs = {self.pk:data.get(self.pk)}
            return self.model.objects.get(**kwargs)
        return None
    def to_representation(self, value):
        return self.serializer(value).data

class JSONSchemaField(serializers.JSONField):
    # default_validators = [validate_json]
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema', False)
        self.get_schema_func = kwargs.pop('get_schema_func', None)
        validators = kwargs.pop('validators', [])
        validators.append(JsonSchemaValidator(self.schema, get_schema_func=self.get_schema_func))
        super().__init__(*args, validators=validators, **kwargs)
    def get_schema(self):
        if not hasattr(self,'_schema'):
            if self.schema:
                self._schema = self.schema
                return self.schema
            if self.get_schema_func:
                self._schema = self.get_schema_func(self)
        self.parent._schema = self._schema
        return self._schema