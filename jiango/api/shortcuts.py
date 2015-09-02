# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from jiango.serializers import get_serializer, deserialize, get_public_serializer_formats
from .utils import Param
from .exceptions import APIError


formats = get_public_serializer_formats()
content_types = dict([(get_serializer(f).content_type, f) for f in formats])


def render(func):
    @wraps(func)
    def wrapper(request, output_format, *args, **kwargs):
        status = 200
        serializer = get_serializer(output_format)()
        response = HttpResponse(content_type=serializer.content_type)
        
        try:
            request.param = Param(request.REQUEST)
            request.value = None
            content_type = request.META.get('CONTENT_TYPE')
            if content_type in content_types and request.body:
                try:
                    request.value = deserialize(content_types[content_type], request.body)
                except Exception, e:
                    raise APIError(e.message)
            
            value = func(request, response, *args, **kwargs)
            
        except (APIError, ObjectDoesNotExist), e:
            value = {'type':e.__class__.__name__, 'message':e.message}
            status = e.status_code if hasattr(e, 'status_code') else 422
        
        response.content = serializer.serialize(value)
        response.status_code = status
        return response
    return wrapper
