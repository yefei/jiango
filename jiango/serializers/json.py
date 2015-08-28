"""
Serialize data to/from JSON
"""
from __future__ import absolute_import
import json
from cStringIO import StringIO
from django.db.models.query import QuerySet, ValuesQuerySet
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.json import DjangoJSONEncoder

from .base import Serializer as BaseSerializer



class JSONEncoder(DjangoJSONEncoder):
    """
    DjangoJSONEncoder subclass that knows how to encode ValuesQuerySet and QuerySet types.
    """
    
    def default(self, o):
        if isinstance(o, ValuesQuerySet):
            return [v for v in o]
        elif isinstance(o, QuerySet):
            return PythonSerializer().serialize(o)
        else:
            return super(JSONEncoder, self).default(o)


class Serializer(BaseSerializer):
    """
    Convert a objects to JSON.
    """
    content_type = 'application/json'

    def serialization(self):
        json.dump(self.objects, self.stream, cls=JSONEncoder, **self.options)


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    return json.load(stream)
