# -*- coding: utf-8 -*-
# Created on 2012-9-20
# @author: Yefei
from django.db.models import Model
from django.db.models.query import QuerySet
from .exceptions import ParamError


def intval(value, default=None, max_value=None, min_value=None):
    try:
        value = int(value)
        if max_value != None and value > max_value:
            raise ParamError('Ensure this value %r is less than or equal to %d.' % (value, max_value))
        if min_value != None and value < min_value:
            raise ParamError('Ensure this value %r is greater than or equal to %d.' % (value, min_value))
    except ValueError:
        if default is None:
            raise ParamError('Value %r is not a number.' % value)
        value = default
    return value


class Param(object):
    def __init__(self, data):
        self.data = data
    
    def __call__(self, key):
        if self.has_key(key):
            return self.data[key]
        raise ParamError('Key %r does not exist.' % key)
    
    def has_key(self, key):
        return self.data.has_key(key)
    
    def int(self, key, default=None, max_value=None, min_value=None):
        if self.has_key(key):
            return intval(self.data[key], default, max_value, min_value)
        if default != None:
            return default
        raise ParamError('Key %r does not exist.' % key)
    
    def intlist(self, key, default=None, max_value=None, min_value=None):
        if self.has_key(key):
            values = []
            for i in self.data.getlist(key):
                values.append(intval(i, default, max_value, min_value))
            return values
        if default != None:
            return [default]
        raise ParamError('Key %r does not exist.' % key)


def model_serialize(model):
    if isinstance(model, QuerySet):
        return [model_serialize(m) for m in model]
    if isinstance(model, Model):
        d = {'type': model.__class__.__name__}
        if hasattr(model, 'export_fields'):
            for field_name in model.export_fields:
                if '@' in field_name:
                    field_name, field = field_name.split('@')
                    field = getattr(model, field)
                else:
                    field = getattr(model, field_name)
                if isinstance(field, Model):
                    d[field_name] = model_serialize(field)
                else:
                    if callable(field):
                        d[field_name] = field()
                    else:
                        d[field_name] = field
        else:
            for field in model._meta.local_fields:
                if field.serialize:
                    if field.rel:
                        d[field.name + '_id'] = getattr(model, field.name + '_id')
                    else:
                        d[field.name] = getattr(model, field.name)
        d['id'] = model._get_pk_val()
        return d
    return None

