# -*- coding: utf-8 -*-
# Created on 2015-8-26
# @author: Yefei
from functools import wraps
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.template.context import RequestContext
from jiango.serializers import get_serializer


def renderer(prefix=None, template_ext='html', content_type=settings.DEFAULT_CONTENT_TYPE, do_exception=None):
    """ return HttpResponse()
        return {'var': value ...}
        return 'template' or '/root_template'
        return 'template1', 'template2' ...
        return 'template', {'var': value ...}
        return 'template1', 'template2', ... {'var': value ...}
    """
    def do_renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            response = HttpResponse(content_type=content_type)
            
            try:
                result = func(request, response, *args, **kwargs)
            except Exception, e:
                if do_exception:
                    result = do_exception(request, response, e)
                else:
                    raise
            
            if isinstance(result, HttpResponse):
                return result
            
            templates = [func.__name__]
            dictionary = None
            
            # 参数解析
            # {'var': value ...}
            if isinstance(result, dict):
                dictionary = result
            
            # 'template' or '/root_template'
            elif isinstance(result, basestring):
                templates = [result]
            
            # 'template1', 'template2' ...
            # 'template', {'var': value ...}
            # 'template1', 'template2', ... {'var': value ...}
            elif isinstance(result, tuple):
                # 最后一项是否为字典
                if isinstance(result[-1], dict):
                    templates = list(result[:-1])
                    dictionary = result[-1]
                else:
                    templates = list(result)
            
            if getattr(request, 'is_mobile'):
                templates = [t + '.mobile' for t in templates] + templates
            
            for i in xrange(0, len(templates)):
                if templates[i].startswith('/'):
                    templates[i] = templates[i][1:]
                elif prefix:
                    templates[i] = prefix + templates[i]
                templates[i] += '.' + template_ext
            
            response.content = render_to_string(templates, dictionary, RequestContext(request))
            return response
        return wrapper
    return do_renderer


def response_serialize(value, output_format='json', options=None, response=None):
    if isinstance(value, HttpResponse):
        return value
    options = options if options else {}
    serializer = get_serializer(output_format)()
    response = response or HttpResponse()
    response.content = serializer.serialize(value, **options)
    response['Content-Type'] = serializer.content_type
    return response


def render_serialize(func_or_format):
    """ return HttpResponse()
        return {'var': value ...} or [list] or 'string'
        return 'json', {'var': value ...}
        return 'json', {'var': value ...}, {'options': opt ...}
    """
    
    default_format = 'json'
    
    def do_renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            _format = default_format
            value = None
            options = {}
            response = HttpResponse()
            
            result = func(request, response, *args, **kwargs)
            
            if isinstance(result, HttpResponse):
                return result
            
            if isinstance(result, tuple):
                len_tuple = len(result)
                if len_tuple == 2:
                    _format, value = result
                elif len_tuple == 3:
                    _format, value, options = result
            else:
                value = result
            
            return response_serialize(value, _format, options, response)
        return wrapper
    
    # @render_serialize('json')
    if isinstance(func_or_format, basestring):
        default_format = func_or_format
        return do_renderer
    
    # @render_serialize
    return do_renderer(func_or_format) 
