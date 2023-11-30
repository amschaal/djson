from rest_framework import serializers
# from rest_framework.validators import UniqueValidator
from rest_framework.validators import ValidationError
import jsonschema

class JsonSchemaValidator:
    """
    Validator for validating JSONField against a schema.

    Should be applied to an individual field on the serializer.
    """

    def __init__(self, schema):
        self.schema = schema

    def set_context(self, serializer_field):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        self.field_name = serializer_field.source_attrs[-1]
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer_field.parent, 'instance', None)

    def __call__(self, value):
        schema = self.schema
        validator = jsonschema.Draft7Validator(schema)
        errors = validator.iter_errors(value)
        error_messages = [str(e) for e in errors]
        if error_messages:
            raise ValidationError(', '.join(error_messages), code='json_schema')

class JSONSchemaField(serializers.JSONField):
    # default_validators = [validate_json]
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema', False)
        validators = kwargs.pop('validators', [])
        validators.append(JsonSchemaValidator(self.schema))
        super().__init__(*args, validators=validators, **kwargs)