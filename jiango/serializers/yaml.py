"""
YAML serializer.

Requires PyYaml (http://pyyaml.org/), but that's checked for in __init__.
"""
from __future__ import absolute_import

import yaml
from cStringIO import StringIO
from django.db.models.query import QuerySet, ValuesQuerySet, ValuesListQuerySet
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.pyyaml import DjangoSafeDumper as _DjangoSafeDumper

from .base import Serializer as BaseSerializer


class DjangoSafeDumper(_DjangoSafeDumper):
    def represent_values_queryset(self, data):
        return self.represent_sequence('tag:yaml.org,2002:seq', [v for v in data])
    
    def represent_queryset(self, data):
        s = PythonSerializer()
        s.serialize(data)
        return self.represent_sequence('tag:yaml.org,2002:seq', s.getvalue())

DjangoSafeDumper.add_representer(ValuesListQuerySet, DjangoSafeDumper.represent_values_queryset)
DjangoSafeDumper.add_representer(ValuesQuerySet, DjangoSafeDumper.represent_values_queryset)
DjangoSafeDumper.add_representer(QuerySet, DjangoSafeDumper.represent_queryset)


class Serializer(BaseSerializer):
    """
    Convert a objects to YAML.
    """
    content_type = 'application/yaml'

    def serialization(self):
        yaml.dump(self.objects, self.stream, Dumper=DjangoSafeDumper, **self.options)


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of YAML data.
    """
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    return yaml.load(stream)

