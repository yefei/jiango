# -*- coding: utf-8 -*-
# Created on 2015-8-26
# @author: Yefei
from functools import wraps
import re
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.template.context import RequestContext
from jiango.serializers import get_serializer


MOBILE_MATCH = re.compile(r'iphone|ipod|android|blackberry|mini|windows\sce|palm', re.I)


def renderer(prefix=None, template_ext='html', content_type=settings.DEFAULT_CONTENT_TYPE, do_exception=None):
    """ return HttpResponse()
        return {'var': value ...}
        return 'template'
        return '/root_template'
        return ('temp1', 'temp2' ...),
        return 'template', {'var': value ...}
    """
    def do_renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # 移动设备判断
            request.is_mobile = MOBILE_MATCH.search(request.META.get('HTTP_USER_AGENT',''))
            
            response = HttpResponse(content_type=content_type)
            dictionary = None
            
            try:
                result = func(request, response, *args, **kwargs)
            except Exception, e:
                if do_exception:
                    result = do_exception(request, response, e)
                else:
                    raise
            
            if isinstance(result, HttpResponse):
                return result
            
            if isinstance(result, basestring):
                templates = result
            elif isinstance(result, tuple) and len(result) == 2:
                templates, dictionary = result
            else:
                templates = func.__name__
                dictionary = result
            
            if not isinstance(templates, (list, tuple)):
                templates = [templates]
            
            if request.is_mobile:
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
