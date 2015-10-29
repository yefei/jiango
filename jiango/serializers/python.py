# -*- coding: utf-8 -*-
# Created on 2015-9-26
# @author: Yefei
from django.core.serializers.python import Serializer
from django.utils.encoding import smart_unicode


class QuerySetSerializer(Serializer):
    def end_object(self, obj):
        self._current['id'] = smart_unicode(obj._get_pk_val(), strings_only=True)
        self.objects.append(self._current)
        self._current = None
    
    def handle_fk_field(self, obj, field):
        if self.use_natural_keys and hasattr(field.rel.to, 'natural_key'):
            related = getattr(obj, field.name)
            if related:
                value = related.natural_key()
            else:
                value = None
        elif hasattr(obj, field.get_cache_name()):  # For select_related()
            value = getattr(obj, field.name)
        else:
            value = getattr(obj, field.get_attname())
        self._current[field.name] = value
