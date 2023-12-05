from rest_framework import serializers
from rest_framework.validators import ValidationError
import jsonschema

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
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer_field.parent, 'instance', None)
        if self.get_schema_func:
            self.schema = self.get_schema_func(self.instance, self.field_name)

    def __call__(self, value, serializer_field):
        self.set_context(serializer_field=serializer_field)
        schema = self.schema
        if schema:
            validator = jsonschema.Draft7Validator(schema)
            errors = validator.iter_errors(value)
            error_messages = [str(e) for e in errors]
            if error_messages:
                raise ValidationError(', '.join(error_messages), code='json_schema')

class JSONSchemaField(serializers.JSONField):
    # default_validators = [validate_json]
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema', False)
        self.get_schema_func = kwargs.pop('get_schema_func', None)
        validators = kwargs.pop('validators', [])
        validators.append(JsonSchemaValidator(self.schema, get_schema_func=self.get_schema_func))
        super().__init__(*args, validators=validators, **kwargs)