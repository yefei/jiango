"""
YAML serializer.

Requires PyYaml (http://pyyaml.org/), but that's checked for in __init__.
"""
from __future__ import absolute_import
import yaml
from cStringIO import StringIO
from django.db.models import Model
from django.db.models.query import QuerySet, ValuesQuerySet
from django.core.serializers.pyyaml import DjangoSafeDumper
from .python import QuerySetSerializer


MIME_TYPES = ('text/yaml',
              'text/x-yaml',
              'application/yaml',
              'application/x-yaml')


class SafeDumper(DjangoSafeDumper):
    def represent_data(self, data):
        if isinstance(data, ValuesQuerySet):
            data = list(data)
        
        elif isinstance(data, QuerySet):
            data = QuerySetSerializer().serialize(data)
        
        elif isinstance(data, Model):
            data = QuerySetSerializer().serialize((data,))[0]
        
        return super(SafeDumper, self).represent_data(data)


def serialize(obj, stream=None, **options):
    return yaml.dump(obj, stream, Dumper=SafeDumper, **options)


def deserialize(stream_or_string, **options):
    if isinstance(stream_or_string, basestring):
        stream_or_string = StringIO(stream_or_string)
    return yaml.load(stream_or_string)
