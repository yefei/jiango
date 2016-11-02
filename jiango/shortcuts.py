# -*- coding: utf-8 -*-
# Created on 2015-8-26
# @author: Yefei
from functools import wraps
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string as _render_to_string
from django.template.context import RequestContext
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from django.db.models.manager import Manager
from django.contrib.messages import add_message, constants as message_constants
from jiango.serializers import get_serializer


# 让客户端浏览器重新载入当前地址
class HttpReload(Exception):
    # remove_get_vars 是否需要清除指定的 GETs
    # 如果为列表参数则删除列表中指定的 GET 变量
    # 如果为 True 则删除所有 GET 变量
    # None 就什么都不做,直接重载当前地址
    def __init__(self, remove_get_vars=None):
        self.remove_get_vars = remove_get_vars
    
    def response(self, request, response=None):
        if response is None:
            response = HttpResponse()
        response.status_code = 302
        if request.GET and self.remove_get_vars is True:
            location = request.path
        elif request.GET and isinstance(self.remove_get_vars, (tuple, list)):
            get_vars = request.GET.copy()
            for k in self.remove_get_vars:
                del get_vars[k]
            location = '%s%s' % (request.path, get_vars and ('?' + get_vars.urlencode()) or '')
        else:
            location = request.get_full_path()
        response['Location'] = location
        return response


class AlertMessage(HttpReload):
    DEBUG = message_constants.DEBUG
    INFO = message_constants.INFO
    SUCCESS = message_constants.SUCCESS
    WARNING = message_constants.WARNING
    ERROR = message_constants.ERROR
    
    def __init__(self, level, message, extra_tags='', fail_silently=False, remove_get_vars=None):
        self.level = level
        self.message = message
        self.extra_tags = extra_tags
        self.fail_silently = fail_silently
        self.remove_get_vars = remove_get_vars
    
    def response(self, request, response=None):
        add_message(request, self.level, self.message, self.extra_tags, self.fail_silently)
        return super(AlertMessage, self).response(request, response)


def render_to_string(request, result, default_template, prefix=None, template_ext='html'):
    templates = [default_template]
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
    
    if getattr(request, 'is_mobile', False):
        templates = [t + '.mobile' for t in templates] + templates
    
    for i in xrange(0, len(templates)):
        if templates[i].startswith('/'):
            templates[i] = templates[i][1:]
        elif prefix:
            templates[i] = prefix + templates[i]
        templates[i] += '.' + template_ext
    
    return _render_to_string(templates, dictionary, RequestContext(request))


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
            except HttpReload as e:
                return e.response(request, response)
            except Exception as e:
                if do_exception:
                    result = do_exception(request, response, e)
                else:
                    raise
            if isinstance(result, HttpResponse):
                return result
            response.content = render_to_string(request, result, func.__name__.rstrip('_'), prefix, template_ext)
            return response
        return wrapper
    return do_renderer


def response_serialize(value, output_format='json', options=None, response=None):
    if isinstance(value, HttpResponse):
        return value
    options = options if options else {}
    serializer = get_serializer(output_format)
    response = response or HttpResponse()
    response.content = serializer.serialize(value, **options)
    response['Content-Type'] = serializer.mimetype
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


def _get_queryset(klass):
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, Manager):
        manager = klass
    else:
        manager = klass._default_manager
    return manager.all()


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def update_instance(instance, **fields):
    if not fields:
        return
    updates = {}
    for f, v in fields.items():
        setattr(instance, f, v)
        updates[f] = v
    instance._default_manager.filter(pk=instance.pk).update(**updates)


# 批量增加 model 实例中字段的数值并更新到数据库
def incr_and_update_instance(instance, **fields):
    if not fields:
        return
    updates = {}
    for f, v in fields.items():
        setattr(instance, f, getattr(instance, f) + v)
        updates[f] = F(f) + v
    instance._default_manager.filter(pk=instance.pk).update(**updates)
