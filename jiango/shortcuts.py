# -*- coding: utf-8 -*-
# Created on 2015-8-26
# @author: Yefei
from functools import wraps
from django.http import HttpResponse, QueryDict
from django.conf import settings
from django.template.loader import render_to_string as _render_to_string
from django.template.context import RequestContext
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from django.db.models.manager import Manager
from django.contrib.messages import add_message, constants as message_constants
from jiango.serializers import get_serializer


class HttpResponseException(Exception):
    def response(self, request, response=None):
        return response


# 让客户端浏览器重新载入当前地址
class HttpReload(HttpResponseException):
    # remove_get_vars 是否需要清除指定的 GETs
    # 如果为列表参数则删除列表中指定的 GET 变量
    # 如果为 True 则删除所有 GET 变量
    # None 就什么都不做,直接重载当前地址
    def __init__(self, remove_get_vars=None, add_get_vars_dict=None):
        self.remove_get_vars = remove_get_vars
        self.add_get_vars_dict = add_get_vars_dict

    def response(self, request, response=None):
        if response is None:
            response = HttpResponse()
        response.status_code = 302
        if self.remove_get_vars is True:
            get_vars = QueryDict(None)
        else:
            get_vars = request.GET.copy()
            if self.remove_get_vars:
                for k in self.remove_get_vars:
                    if k in get_vars:
                        del get_vars[k]
        if self.add_get_vars_dict:
            get_vars.update(self.add_get_vars_dict)
        response['Location'] = '%s%s' % (request.path, get_vars and ('?' + get_vars.urlencode()) or '')
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
        super(AlertMessage, self).__init__(remove_get_vars)

    def response(self, request, response=None):
        add_message(request, self.level, self.message, self.extra_tags, self.fail_silently)
        return super(AlertMessage, self).response(request, response)


def get_or_create_referer_params(request, default=None, key='ref'):
    ref = request.GET.get(key)
    if ref is None:
        ref = request.META.get('HTTP_REFERER', default)
        if ref:
            raise HttpReload(add_get_vars_dict={key: ref})
    return ref


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
    def render(func=None, template_ext=template_ext, content_type=content_type, do_exception=do_exception,
               ref_param=None):
        def do_wrapper(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                response = HttpResponse(content_type=content_type)
                try:
                    if ref_param:
                        kwargs[ref_param] = get_or_create_referer_params(request, key=ref_param)
                    result = func(request, response, *args, **kwargs)
                except HttpResponseException as e:
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

        # @render() 带参数
        if func is None:
            return do_wrapper

        # @render 不带参数
        return do_wrapper(func)

    return render


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


# 更新 M2M 字段中的值，存在的忽略，不存在的创建，已经存在的但更新时候不存在的则删除
def update_m2m(through, fk_a_name, fk_a_value, fk_b_name, fk_b_values, **creates):
    fk_a_qs = through.objects.filter(**{fk_a_name: fk_a_value})
    if not fk_b_values:
        fk_a_qs.delete()
    else:
        values_ids = (i.pk for i in fk_b_values)
        delete_ids = []
        exists_ids = []
        for t in fk_a_qs:
            fk_a_id = getattr(t, '%s_id' % fk_b_name)
            if fk_a_id not in values_ids:  # 不在需要创建的则需要删除
                delete_ids.append(t.pk)
            else:
                exists_ids.append(fk_a_id)
        # 删除已经不需要的
        if delete_ids:
            through.objects.filter(pk__in=delete_ids).delete()
        # 插入新的
        for i in fk_b_values:
            if i.pk in exists_ids:
                continue
            creates[fk_a_name] = fk_a_value
            creates[fk_b_name] = i
            through.objects.create(**creates)
