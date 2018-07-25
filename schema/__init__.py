
import os
import json
import datetime
import jsonschema

import format
import exceptions as ex

def type_draft4(validator, types, instance, schema):
    types = jsonschema._utils.ensure_list(types)

    # NOTE: A datetime object is not a string, but is still valid.
    if ('format' in schema and schema['format'] == 'datetime'
            and isinstance(instance, datetime.datetime)):
        return

    if not any(validator.is_type(instance, type) for type in types):
        yield jsonschema.ValidationError(
            jsonschema._utils.types_msg(instance, types))


Draft4Validator = jsonschema.validators.extend(
    jsonschema.validators.Draft4Validator,
    validators={
        "type": type_draft4,
    })


SCHEMA_DIR = './schema/'
def set_schema_dir(path):
    global SCHEMA_DIR

    # once set, don't support change
    if SCHEMA_DIR is None:
        SCHEMA_DIR = os.path.abspath(path)


def load_schema(name):
    if SCHEMA_DIR is None:
        raise ex.InternalServerError("API schema path wasn't set")

    schema_path = os.path.join(SCHEMA_DIR, "%s.json" % name)

    if not os.path.exists(schema_path):
        raise Exception("schema '%s' doesn't exist." % name)

    with open(schema_path) as f:
        raw_schema = f.read()

    return json.loads(raw_schema.decode('utf-8'))


class LocalResolver(jsonschema.RefResolver):
    def __init__(self, base_uri, referrer):
        super(LocalResolver, self).__init__(base_uri, referrer, (), True)

    @classmethod
    def from_schema(cls, schema, *args, **kwargs):
        resolver = cls(schema.get("id", ""), schema, *args, **kwargs)

        return resolver

    def resolve_remote(self, uri):
        return load_schema(uri)


class Schema(object):
    def __init__(self, name):
        self.raw_schema = load_schema(name)
        self.resolver = LocalResolver.from_schema(self.raw_schema)

        self.validator = Draft4Validator(
                self.raw_schema, resolver=self.resolver,
                format_checker=format.draft4_format_checker)

    @property
    def schema(self):
        return self.validator.schema

    @property
    def properties(self):
        return self.schema['properties']

    @property
    def raw(self):
        return self.raw_schema

    def validate(self, obj):
        errors = []
        try:
            for error in self.validator.iter_errors(obj):
                errors.append({
                    'path': ".".join([str(x) for x in error.path]),
                    'message': error.message,
                    'validator': error.validator
                })
        except Exception as e:
            raise e

        if len(errors) > 0:
            message = ['property ' + e['message'] for e in errors]
            message = '\n'.join(message)
            raise Exception(message)


    def filter(self, instance, properties=None):
        if not properties:
            properties = self.properties

        filtered = {}

        for name, subschema in list(properties.items()):
            if 'type' in subschema and subschema['type'] == 'array':
                subinstance = instance.get(name, None)
                filtered[name] = self._filter_array(subinstance, subschema)
            elif 'type' in subschema and subschema['type'] == 'object':
                subinstance = instance.get(name, None)
                properties = subschema['properties']
                filtered[name] = self.filter(subinstance, properties)
            else:
                filtered[name] = instance.get(name, None)

        return filtered

    def _filter_array(self, instance, schema):
        if 'items' in schema and isinstance(schema['items'], list):
            # NOTE: We currently don't make use of this.
            raise NotImplementedError()

        elif 'items' in schema:
            schema = schema['items']

            if '$ref' in schema:
                with self.resolver.resolving(schema['$ref']) as ischema:
                    schema = ischema

            properties = schema['properties']

            return [self.filter(i, properties) for i in instance]

        elif 'properties' in schema:
            schema = schema['properties']

            with self.resolver.resolving(schema['$ref']) as ischema:
                    schema = ischema

            return [self.filter(i, schema) for i in instance]

        else:
            raise NotImplementedError("Can't filter unknown array type")
