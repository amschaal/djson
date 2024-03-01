from rest_framework import serializers
from djson.fields import JSONSchemaField, ModelRelatedField
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

class ModelTypeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelType
        fields = ['id', 'name']

def get_schema_func(field):
    # raise Exception('get_schema_func', validator.serializer.initial_data)
    serializer = field.parent
    instance = serializer.instance
    if instance:
        if hasattr(instance, 'schema') and instance.schema:
            return instance.schema
        if getattr(instance, 'type'):
            return instance.type.schema
    else:
        type = serializer.initial_data.get('type')
        # Find a cleaner way to do this now that we accept serialized type as input thanks to ModelRelatedField
        try:
            type_id = type['id']
        except:
            type_id = type
        if type_id:
            model_type = ModelType.objects.filter(id=type_id).first()
            if model_type:
                return model_type.schema


class DjsonTypeModelSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('schema',)
    def __init__(self, instance=None, **kwargs):
        # self.fields['type'].queryset =  ModelType.get_model_queryset(self.Meta.model)#self.get_type_choices()#ModelType.objects.all()#.filter(content_type=ContentType.objects.get_for_model(self.Meta.model))
        # raise Exception('wtf', ModelType.objects.all(),  self.fields['type'].choices)
        # raise Exception(self.Meta.model, self.fields['type'].choices)
        super().__init__(instance, **kwargs)
        # raise Exception('initializing DjsonTypeModelSerializer')
    def to_internal_value(self, data):
        _data = super().to_internal_value(data)
        if getattr(self,'_schema') and (not self.instance or not self.instance.schema):
            _data['schema'] = self._schema
        return _data
    def validate_type(self, value):
        """
        Type should not be changed once set.
        """
        if self.instance and self.instance.type and value != self.instance.type:
            raise serializers.ValidationError("Types cannot be changed.")
        return value
    # data = JSONSchemaField(schema=TEST_SCHEMA, required=True)
    # type = serializers.ChoiceField(choices=[])
    # type = serializers.PrimaryKeyRelatedField(queryset=ModelType.objects.all())
    type = ModelRelatedField(model=ModelType, serializer=ModelTypeBasicSerializer)
    data = JSONSchemaField(required=True, get_schema_func=get_schema_func)
    # def get_type_choices(self):
    #      return [(mt.id, mt.name) for mt in ModelType.objects.filter(content_type=ContentType.objects.get_for_model(self.Meta.model))]
    # data = serializers.JSONField(required=False, validators=[JsonSchemaValidator(schema='sdflsdf')])
    # class Meta:
    #     model = Machine
    #     exclude = []