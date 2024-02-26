from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework.validators import ValidationError
import jsonschema

from djson.validation import get_validator_error_tree

def get_validator(schema, data):
    if hasattr(settings, 'DJSON_GET_VALIDATOR'):
        return import_string(settings.DJSON_GET_VALIDATOR)(schema, data=data)
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
        self.schema = self.field.get_schema()
        # Determine the existing instance, if this is an update operation.
        # self.instance = getattr(serializer_field.parent, 'instance', None)
        # if self.get_schema_func:
        #     self.schema = self.get_schema_func(self)
        # serializer_field.parent._schema = self.schema


    def __call__(self, value, serializer_field):
        self.set_context(serializer_field=serializer_field)
        schema = self.schema
        if schema:
            validator = get_validator(schema, value)#jsonschema.Draft7Validator(schema)
            # errors = validator.iter_errors(value)
            tree = get_errors(validator, value)
            if tree:
                raise ValidationError(tree, code='json_schema')
            # error_messages = [str(e) for e in errors]
            # if error_messages:
            #     raise ValidationError(', '.join(error_messages), code='json_schema')