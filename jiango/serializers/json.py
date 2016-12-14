"""
Serialize data to/from JSON
"""
from __future__ import absolute_import
import json
import datetime
from django.db.models import Model
from django.db.models.query import QuerySet, ValuesQuerySet
from django.core.serializers.json import DjangoJSONEncoder
from .python import QuerySetSerializer


MIME_TYPES = ('text/json',
              'text/x-json',
              'application/json',
              'application/jsonrequest')


class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:19] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r

        if isinstance(o, ValuesQuerySet):
            return list(o)
        
        if isinstance(o, QuerySet):
            return QuerySetSerializer().serialize(o)
        
        if isinstance(o, Model):
            return QuerySetSerializer().serialize((o,))[0]
        
        return super(JSONEncoder, self).default(o)


def serialize(obj, stream=None, **options):
    if stream:
        json.dump(obj, stream, cls=JSONEncoder, **options)
    else:
        return json.dumps(obj, cls=JSONEncoder, **options)


def deserialize(stream_or_string, **options):
    if isinstance(stream_or_string, basestring):
        return json.loads(stream_or_string, **options)
    return json.load(stream_or_string, **options)
