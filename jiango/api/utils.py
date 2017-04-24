# -*- coding: utf-8 -*-
# Created on 2012-9-20
# @author: Yefei
from .exceptions import ParamError


def number_value(value, default=None, max_value=None, min_value=None, convert=int):
    try:
        value = convert(value)
        if max_value is not None and value > max_value:
            raise ParamError('Ensure this value %r is less than or equal to %d.' % (value, max_value))
        if min_value is not None and value < min_value:
            raise ParamError('Ensure this value %r is greater than or equal to %d.' % (value, min_value))
    except (ValueError, TypeError):
        if default is None:
            raise ParamError('Value %r is not a number.' % value)
        value = default
    return value


intval = number_value


class Param(dict):
    def __call__(self, key):
        if key in self:
            return self[key]
        raise ParamError('Key %r does not exist.' % key)

    def int(self, key, default=None, max_value=None, min_value=None):
        if key in self:
            return number_value(self[key], default, max_value, min_value)
        if default is not None:
            return default
        raise ParamError('Key %r does not exist.' % key)

    def float(self, key, default=None, max_value=None, min_value=None):
        if key in self:
            return number_value(self[key], default, max_value, min_value, float)
        if default is not None:
            return default
        raise ParamError('Key %r does not exist.' % key)
