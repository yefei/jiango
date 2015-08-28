# -*- coding: utf-8 -*-
# Created on 2015-8-26
# @author: Yefei
from functools import wraps
import re
import json
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.template.context import RequestContext


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


def response_json(value, response=None):
    if isinstance(value, HttpResponse):
        return value
    response = response or HttpResponse()
    response.content = json.dumps(value)
    #response['Content-Type'] = 'text/json'
    return response


def render_json(func_or_format):
    """ return HttpResponse()
        return {'var': value ...} or [list] or 'string'
    """
    
    def do_renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            response = HttpResponse()
            result = func(request, response, *args, **kwargs)
            return response_json(result, response)
        return wrapper
    
    # @render_serialize
    return do_renderer(func_or_format)
