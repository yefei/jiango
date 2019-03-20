# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from functools import wraps
from django.http import HttpResponse
from django.utils.log import logger
from jiango.serializers import deserialize, get_serializer, get_serializer_formats, get_serializer_mimetypes
from jiango.settings import get_setting
from .utils import Param
from .exceptions import LoginRequired, APIError
from .helpers import APIResult, api_result
from .errorcodes import LOGIN_AUTH_FAIL, UNKNOWN_ERROR


ACCESS_CONTROL_ALLOW_ORIGIN = get_setting('API_ACCESS_CONTROL_ALLOW_ORIGIN', '*')


formats = get_serializer_formats()
mimetypes = get_serializer_mimetypes()


def default_exception_func(e):
    if isinstance(e, LoginRequired):
        return api_result(*LOGIN_AUTH_FAIL), 200
    if isinstance(e, APIResult):
        return api_result(e.error_code, e.error_message, **e.params), 200
    logger.warning('API unknown error: %s', repr(e))
    return api_result(UNKNOWN_ERROR, 'unknown error'), 422


def render(func, exception_func=None):
    if exception_func is None:
        exception_func = default_exception_func

    @wraps(func)
    def wrapper(request, output_format, *args, **kwargs):
        status = 200
        serializer = get_serializer(output_format)
        response = HttpResponse(content_type=serializer.mimetype)

        if ACCESS_CONTROL_ALLOW_ORIGIN:
            response['Access-Control-Allow-Origin'] = ACCESS_CONTROL_ALLOW_ORIGIN

        try:
            request.value = None
            content_type = request.META.get('CONTENT_TYPE', '').split(';')
            if content_type and content_type[0] in mimetypes and request.body:
                encoding = None
                if len(content_type) == 2:
                    content_type_param = content_type[1].strip().lower()
                    if content_type_param.startswith('charset='):
                        encoding = content_type_param[8:]
                try:
                    request.value = deserialize(mimetypes[content_type[0]], request.body, encoding=encoding)
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
