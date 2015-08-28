"""
Module for abstract serializer/unserializer base classes.
"""
from cStringIO import StringIO


class Serializer(object):
    """
    Abstract serializer base class.
    """
    
    # Indicates if the implemented serializer is only available for
    # internal Django use.
    internal_use_only = False
    
    # Serializer Mime-type
    content_type = None
    
    def serialize(self, objects, **options):
        self.objects = objects
        self.options = options
        self.stream = options.pop("stream", StringIO())
        self.serialization()
        return self.getvalue()
    
    def serialization(self):
        raise NotImplementedError
    
    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()

