# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from jiango.serializers import deserialize, get_serializer, get_serializer_formats, get_serializer_mimetypes
from .utils import Param
from .exceptions import APIError


formats = get_serializer_formats()
mimetypes = get_serializer_mimetypes()


def default_exception_func(e):
    value = {'type': e.__class__.__name__, 'message': e.message}
    status = e.status_code if hasattr(e, 'status_code') else 422
    return value, status


def render(func, exception_func=None):
    if exception_func is None:
        exception_func = default_exception_func
    
    @wraps(func)
    def wrapper(request, output_format, *args, **kwargs):
        status = 200
        serializer = get_serializer(output_format)
        response = HttpResponse(content_type=serializer.mimetype)
        
        try:
            request.param = Param(request.REQUEST)
            request.value = None
            mimetype = request.META.get('CONTENT_TYPE')
            if mimetype in mimetypes and request.body:
                try:
                    request.value = deserialize(mimetypes[mimetype], request.body)
                except Exception, e:
                    raise APIError(e.message)
            
            value = func(request, response, *args, **kwargs)
            
        except (APIError, ObjectDoesNotExist), e:
            value, status = exception_func(e)

        if isinstance(value, HttpResponse):
            return value

        response.content = serializer.serialize(value)
        response.status_code = status
        return response
    return wrapper
