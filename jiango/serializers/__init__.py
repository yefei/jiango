"""
Interfaces for serializing objects.

Usage::

    from jiango import serializers
    json = serializers.serialize("json", some_object)
    objects = serializers.deserialize("json", json)

To add your own serializers, use the JIANGO_SERIALIZATION_MODULES setting::

    JIANGO_SERIALIZATION_MODULES = {
        "csv" : "path.to.csv",
        "txt" : "path.to.txt",
    }

"""

from django.conf import settings
from django.utils.importlib import import_module

# Built-in serializers
BUILTIN_SERIALIZERS = {
    "json": "jiango.serializers.json",
}

# Check for PyYaml and register the serializer if it's available.
try:
    import yaml
    BUILTIN_SERIALIZERS["yaml"] = "jiango.serializers.yaml"
except ImportError:
    pass


_serializers = {}


class Serializer:
    def __init__(self, serialize, deserialize, mimetypes=None):
        self.serialize = serialize
        self.deserialize = deserialize
        self.mimetypes = mimetypes
        self.mimetype = mimetypes[0] if mimetypes else None


def register_serializer(format_, serializer_module):
    m = import_module(serializer_module)
    _serializers[format_] = Serializer(serialize=m.serialize,
                                       deserialize=m.deserialize,
                                       mimetypes=getattr(m, 'MIME_TYPES', None))


def unregister_serializer(format_):
    if format_ in _serializers:
        del _serializers[format_]


def get_serializer_formats():
    return _serializers.keys()


def get_serializer_mimetypes():
    mimetypes = {}
    for f, m in _serializers.items():
        if not m.mimetypes:
            continue
        for t in m.mimetypes:
            mimetypes[t] = f
    return mimetypes


def get_serializer(format_):
    assert format_ in _serializers, 'Unknown serializer "%s"' % format_
    return _serializers[format_]


def serialize(format_, obj, **options):
    s = get_serializer(format_)
    return s.serialize(obj, **options)


def deserialize(format_, stream_or_string, **options):
    s = get_serializer(format_)
    return s.deserialize(stream_or_string, **options)


def _load_serializers():
    if _serializers:
        return
    for f, m in BUILTIN_SERIALIZERS.items():
        register_serializer(f, m)
    if hasattr(settings, "JIANGO_SERIALIZATION_MODULES"):
        for f, m in settings.JIANGO_SERIALIZATION_MODULES.items():
            register_serializer(f, m)

_load_serializers()
