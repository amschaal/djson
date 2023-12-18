from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.validators import ValidationError
import jsonschema
from django.contrib.contenttypes.models import ContentType
from djson.models import ModelType
from djson.validation import get_validator_error_tree

def get_validator(schema):
    if hasattr(settings, 'DJSON_GET_VALIDATOR'):
        return import_string(settings.DJSON_GET_VALIDATOR)(schema)
    else:
        return jsonschema.Draft7Validator(schema)

def get_errors(validator, data):
    if hasattr(settings, 'DJSON_GET_ERRORS'):
        return import_string(settings.DJSON_GET_ERRORS)(validator, data)
    else:
        return get_validator_error_tree(validator, data)

class JsonSchemaValidator:
    """
    Validator for validating JSONField against a schema.

    Should be applied to an individual field on the serializer.
    """
    requires_context = True
    def __init__(self, schema, get_schema_func=None):
        self.schema = schema
        self.get_schema_func = get_schema_func

    def set_context(self, serializer_field):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        self.field_name = serializer_field.source_attrs[-1]
        self.field = serializer_field
        self.serializer = serializer_field.parent
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer_field.parent, 'instance', None)
        if self.get_schema_func:
            self.schema = self.get_schema_func(self)

    def __call__(self, value, serializer_field):
        self.set_context(serializer_field=serializer_field)
        schema = self.schema
        if schema:
            validator = get_validator(schema)#jsonschema.Draft7Validator(schema)
            # errors = validator.iter_errors(value)
            tree = get_errors(validator, value)
            if tree:
                raise ValidationError(tree, code='json_schema')
            # error_messages = [str(e) for e in errors]
            # if error_messages:
            #     raise ValidationError(', '.join(error_messages), code='json_schema')

class JSONSchemaField(serializers.JSONField):
    # default_validators = [validate_json]
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema', False)
        self.get_schema_func = kwargs.pop('get_schema_func', None)
        validators = kwargs.pop('validators', [])
        validators.append(JsonSchemaValidator(self.schema, get_schema_func=self.get_schema_func))
        super().__init__(*args, validators=validators, **kwargs)

def get_schema_func(validator):
    # raise Exception('get_schema_func', validator.serializer.initial_data)
    if validator.instance:
        return validator.instance.type.schema
    type_id = validator.serializer.initial_data.get('type')
    if type_id:
        model_type = ModelType.objects.filter(id=type_id).first()
        if model_type:
            return model_type.schema

class DjsonTypeModelSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, **kwargs):
        # self.fields['type'].queryset =  ModelType.get_model_queryset(self.Meta.model)#self.get_type_choices()#ModelType.objects.all()#.filter(content_type=ContentType.objects.get_for_model(self.Meta.model))
        # raise Exception('wtf', ModelType.objects.all(),  self.fields['type'].choices)
        # raise Exception(self.Meta.model, self.fields['type'].choices)
        super().__init__(instance, **kwargs)
    # data = JSONSchemaField(schema=TEST_SCHEMA, required=True)
    # type = serializers.ChoiceField(choices=[])
    type = serializers.PrimaryKeyRelatedField(queryset=ModelType.objects.all())
    data = JSONSchemaField(required=True, get_schema_func=get_schema_func)
    # def get_type_choices(self):
    #      return [(mt.id, mt.name) for mt in ModelType.objects.filter(content_type=ContentType.objects.get_for_model(self.Meta.model))]
    # data = serializers.JSONField(required=False, validators=[JsonSchemaValidator(schema='sdflsdf')])
    # class Meta:
    #     model = Machine
    #     exclude = []