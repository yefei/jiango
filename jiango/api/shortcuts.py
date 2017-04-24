# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from functools import wraps
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
            request.value = None
            content_type = request.META.get('CONTENT_TYPE', '').split(';')
            if content_type and content_type[0] in mimetypes and request.body:
                try:
                    request.value = deserialize(mimetypes[content_type[0]], request.body)
                except Exception, e:
                    raise APIError(e.message)
            request.param = Param(request.value or request.REQUEST)
            value = func(request, response, *args, **kwargs)

        except APIError as e:
            value, status = exception_func(e)

        if isinstance(value, HttpResponse):
            return value

        response.content = serializer.serialize(value)
        response.status_code = status
        return response
    return wrapper
