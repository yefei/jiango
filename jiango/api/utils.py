# -*- coding: utf-8 -*-
# Created on 2012-9-20
# @author: Yefei
from .exceptions import ParamError


def intval(value, default=None, max_value=None, min_value=None):
    try:
        value = int(value)
        if max_value is not None and value > max_value:
            raise ParamError('Ensure this value %r is less than or equal to %d.' % (value, max_value))
        if min_value is not None and value < min_value:
            raise ParamError('Ensure this value %r is greater than or equal to %d.' % (value, min_value))
    except (ValueError, TypeError):
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
        if default is not None:
            return default
        raise ParamError('Key %r does not exist.' % key)
    
    def intlist(self, key, default=None, max_value=None, min_value=None):
        if self.has_key(key):
            values = []
            for i in self.data.getlist(key):
                values.append(intval(i, default, max_value, min_value))
            return values
        if default is not None:
            return [default]
        raise ParamError('Key %r does not exist.' % key)
