# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
import operator
from functools import wraps
from inspect import isfunction
from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, models
from django.contrib import messages
from django.shortcuts import redirect
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from jiango.shortcuts import render_to_string, HttpResponseException, get_or_create_referer_params, HttpReload
from jiango.utils.model import get_deleted_objects
from jiango.ui import Element, Link
from jiango.pagination import Paging
from jiango.bootstrap.ui import Grid
from .auth import login_redirect, logout_redirect, get_request_user
from .models import Permission, Log, LogTypes
from .ui import MainUI, links, AdminPagination
from . import config


SEARCH_VAR = 'q'


class Alert(Exception):
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    TAGS = {DEBUG: 'debug',
            INFO: 'info',
            SUCCESS: 'success',
            WARNING: 'warning',
            ERROR: 'error'}
    
    def __init__(self, level, message, buttons=None, back=True):
        self.level = level
        self.message = message
        self.buttons = buttons or {}
        self.back = back
    
    @property
    def tag(self):
        return self.TAGS[self.level]


def has_superuser(request):
    user = get_request_user(request)
    if user and user.is_active and user.is_superuser:
        return
    raise Alert(Alert.ERROR, u'只有超级用户才有权利操作')


def has_perm(request, codename):
    user = get_request_user(request)
    if user and user.has_perm(codename):
        return
    try:
        perm = Permission.objects.get(codename=codename)
        perm_name = perm.name
    except Permission.DoesNotExist:
        perm_name = codename
    raise Alert(Alert.ERROR, u'你没有 "%s" 权限' % perm_name)


def renderer(prefix=None, default_extends_layout=True,
             template_ext='html', content_type=settings.DEFAULT_CONTENT_TYPE):
    def render(func=None, extends_layout=default_extends_layout,
               login=True, logout=False, perm=None, ref_param=None):
        def do_wrapper(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                response = HttpResponse(content_type=content_type)
                
                if logout:
                    if get_request_user(request):
                        return logout_redirect(request)
                elif login:
                    if not get_request_user(request):
                        return login_redirect(request)
                
                try:
                    if perm:
                        has_perm(request, perm)
                    if ref_param:
                        kwargs[ref_param] = get_or_create_referer_params(request, key=ref_param)
                    result = func(request, response, *args, **kwargs)
                except HttpResponseException as e:
                    return e.response(request, response)
                except (Alert, ObjectDoesNotExist) as e:
                    result = {}
                    if isinstance(e, Alert):
                        result = {'message': e.message, 'tag': e.tag, 'buttons': e.buttons}
                        if e.back and 'HTTP_REFERER' in request.META:
                            result['buttons'][u'返回'] = request.META['HTTP_REFERER']
                    elif isinstance(e, ObjectDoesNotExist):
                        result = {'message': u'所访问的对象不存在，可能已经被删除。\n%r' % e, 'tag':'error'}
                    content = render_to_string(request, result, '/admin/alert', prefix, template_ext)
                else:
                    if isinstance(result, HttpResponse):
                        return result
                    if isinstance(result, Element):
                        content = result.render()
                    else:
                        content = render_to_string(request, result, func.__name__.rstrip('_'), prefix, template_ext)
                    if not extends_layout:
                        response.content = content
                        return response
                
                from .loader import get_navigation
                user = get_request_user(request)
                navigation = None
                current_sub_menus = None
                if user:
                    navigation = get_navigation(request)
                    for i in navigation:
                        if i['is_active']:
                            current_sub_menus = i['sub_menus']
                            break

                # <head> 提取
                head_content = ''
                if content.startswith('<head>') and '</head>' in content:
                    head_end_pos = content.index('</head>')
                    head_content = content[len('<head>'):head_end_pos]
                    content = content[head_end_pos+len('</head>'):]

                base_dictionary = {'content': content,
                                   'head_content': head_content,
                                   'config': config,
                                   'navigation': navigation,
                                   'current_sub_menus': current_sub_menus,
                                   'sidebar_collapse': request.COOKIES.get('admin-sidebar-collapse') == '1',
                                   'user': user}
                response.content = render_to_string(request, base_dictionary, 'admin/layout')
                return response
            return wrapper
        
        # @render() 带参数
        if func is None:
            return do_wrapper
        
        # @render 不带参数
        return do_wrapper(func)
    return render


class Logger(LogTypes):
    def __init__(self, app_label):
        self.app_label = app_label
    
    def __call__(self, request, level, content, action=None, user=None, remote_ip=None,
                 view_name=None, view_args=None, view_kwargs=None, form=None):
        if form:
            content = '%s\n\n%s' % (content, form.errors.as_text())
        
        if action is None:
            action = LogTypes.NONE
        
        if remote_ip is None:
            remote_ip = request.META.get('REMOTE_ADDR')
        
        if user is None:
            user = get_request_user(request)
        
        return Log.write(level, self.app_label, content, action,
                         view_name, view_args, view_kwargs, remote_ip, user)
    
    def debug(self, request, content, *args, **kwargs):
        return self(request, LogTypes.DEBUG, content, *args, **kwargs)
    
    def info(self, request, content, *args, **kwargs):
        return self(request, LogTypes.INFO, content, *args, **kwargs)
    
    def success(self, request, content, *args, **kwargs):
        return self(request, LogTypes.SUCCESS, content, *args, **kwargs)
    
    def warning(self, request, content, *args, **kwargs):
        return self(request, LogTypes.WARNING, content, *args, **kwargs)
    
    def error(self, request, content, *args, **kwargs):
        return self(request, LogTypes.ERROR, content, *args, **kwargs)


class ModelLogger(object):
    def __init__(self, instance=None):
        self.instance = instance
        self.instance_values = self.get_instance_values(instance) if instance else []

    @staticmethod
    def get_instance_values(instance):
        return [(f.attname, unicode(getattr(instance, f.attname))) for f in instance._meta.local_fields]

    @staticmethod
    def get_instance_name(instance):
        return '{0}.{1}'.format(instance._meta.app_label, instance.__class__.__name__)
    
    def diff_values(self, new_instance):
        diff_values = []
        for attname, orig_value in self.instance_values:
            new_value = unicode(getattr(new_instance, attname))
            if new_value != orig_value:
                diff_values.append((attname, orig_value, new_value))
        return diff_values

    def message(self, new_instance=None):
        if self.instance:
            class_name = self.get_instance_name(self.instance)
        elif new_instance:
            class_name = self.get_instance_name(new_instance)
        else:
            return

        output = [u'模型: %s' % class_name]

        if new_instance is None:
            # 数据被删除
            output.append(u'删除之前的数据为:')
            for attname, orig_value in self.instance_values:
                output.append(attname + ': ' + orig_value)
        elif self.instance:
            # 数据被更新
            diff_values = self.diff_values(new_instance)
            if not diff_values:
                output.append(u'没有更新')
            else:
                output.append(u'更新字段:')
                for attname, orig_value, new_value in diff_values:
                    output.append(attname + ': ' + orig_value + ' > ' + new_value)
        return '\n'.join(output)

    def log(self, request, log, new_instance=None):
        message = self.message(new_instance)
        if not message:
            return
        out = []
        if new_instance is None:
            action = log.DELETE
            out.append(u'删除')
        elif self.instance is None:
            action = log.CREATE
            out.append(u'新增')
        else:
            action = log.UPDATE
            out.append(u'更新')
        verbose_name = new_instance._meta.verbose_name if new_instance else self.instance._meta.verbose_name
        out.append(u'%s: %s' % (verbose_name, unicode(new_instance) if new_instance else unicode(self.instance)))
        out_message = ''.join(out)
        log.success(request, u'%s\n\n%s' % (out_message, message), action=action)
        return out_message


def process_on_success(on_success, *args, **kwargs):
    if isinstance(on_success, HttpResponse):
        return on_success
    if isinstance(on_success, basestring):
        return redirect(on_success)
    if isfunction(on_success):
        return on_success(*args, **kwargs)


def delete_confirm_view(app_label, request, queryset, on_success=None, using=None,
                        template='/admin/shortcuts/delete_confirm', extras=None):
    log = Logger(app_label)
    to_delete, protected = get_deleted_objects(queryset, using)
    if not to_delete:
        raise Alert(Alert.ERROR, u'没有需要删除的项', back=True)
    if request.method == 'POST':
        delete_info = []

        def each(lists, level=0):
            for i in lists:
                if isinstance(i, (tuple, list)):
                    each(i, level+1)
                else:
                    delete_info.append(u'%s%s' % ('    ' * level, i))

        each(to_delete)
        log.success(request, u'删除数据:\n%s' % '\n'.join(delete_info), action=Logger.DELETE)
        with transaction.commit_on_success():
            queryset.delete()
        if on_success is not None:
            return process_on_success(on_success)
        raise Alert(Alert.SUCCESS, u'删除成功')
    template_vars = locals()
    if extras:
        template_vars.update(extras)
    return template, template_vars


def edit_view(app_label, request, form, on_success=None, template='/admin/shortcuts/edit', extras=None,
              title=None, delete_url=None, **kwargs):
    log = Logger(app_label)
    if title is None:
        title = u'编辑 / %s.%s' % (form.__module__, form.__class__.__name__)
    m_log = None
    if hasattr(form, 'instance'):
        m_log = ModelLogger(form.instance)
        title = u'创建 / %s' % form.instance._meta.verbose_name
        if form.instance.pk is not None:
            title = u'编辑 / %s' %  unicode(form.instance)
    if form.is_valid():
        instance = None
        if hasattr(form, 'save'):
            with transaction.commit_on_success():
                instance = form.save()
            if m_log:
                msg = m_log.log(request, log, instance)
            else:
                msg = title
                log.success(request, msg)
            messages.success(request, msg)
        if on_success is not None:
            return process_on_success(on_success, instance=instance)
        raise HttpReload()
    template_vars = locals()
    if extras:
        template_vars.update(extras)
    return template, template_vars


class CURDAdmin(object):
    def __init__(self, app_label, name, verbose_name, model_class,
                 display_fields=None, select_related=None, can_delete=True, search_fields=None):
        self.app_label = app_label
        self.name = name
        self.verbose_name = verbose_name
        self.model_class = model_class
        self.form_class = None
        self.form_valid_callback = None
        self.can_add = False
        self.can_delete = can_delete
        self.display_fields = display_fields
        self.select_related = select_related
        self.search_fields = search_fields
        self.other_links = []

        self.render = renderer('%s/admin/' % app_label)
        self.log = Logger(app_label)

        self.urlpatterns = []
        self.permissions = {}

        self._setup_list_view()

        if self.can_delete:
            self._setup_delete_view()

    def add_view(self, perm, view_func, view_verbose_name, url_regex_append='$', url_name_append=None):
        view_func = self.render(perm=perm)(view_func)
        view_url = url('^/%s%s' % (self.name, url_regex_append), view_func,
                       name=('%s-%s' % (self.name, url_name_append)) if url_name_append else self.name)
        self.urlpatterns.append(view_url)
        self.permissions['%s.%s' % (self.name, perm)] = u'%s|%s' % (self.verbose_name, view_verbose_name)

    def _setup_list_view(self):
        self.add_view('view', self.list_view, u'查看')

    def list_view(self, request, response):
        qs = self.model_class.objects.all()
        if self.select_related:
            qs = qs.select_related(*self.select_related)

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        search_query = request.GET.get(SEARCH_VAR, '')
        if self.search_fields and search_query:
            orm_lookups = [construct_search(str(search_field)) for search_field in self.search_fields]
            for bit in search_query.split():
                or_queries = [models.Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
                qs = qs.filter(reduce(operator.or_, or_queries))

        qs = Paging(qs, request).page()

        # 字符串类型则使用自定义模版渲染
        if isinstance(self.display_fields, basestring):
            return self.display_fields, {'qs': qs, 'search_query': search_query}

        ui = MainUI(request)

        # 头部
        header = Element(tag='div', attrs={'class': 'clearfix mb-10'})
        ui.append(header)

        header_left = Element(tag='div', attrs={'class': 'pull-left'})
        header_left.append(Element(self.verbose_name, tag='h3', attrs={'class': 'm-0'}))
        header.append(header_left)

        header_right = Element(tag='div', attrs={'class': 'pull-right'})
        header.append(header_right)

        # 搜索表单
        if self.search_fields:
            search_form = Element(tag='form', attrs={'class': 'pull-left form-inline ml-10'})
            _wrap = Element(tag='div', attrs={'class': 'input-group'})
            search_form.append(_wrap)
            _wrap.append(Element(tag='input', close_tag=False, attrs={
                'name': SEARCH_VAR,
                'placeholder': '输入关键词搜索',
                'class': 'form-control',
                'value': search_query,
            }))

            buttons = Element(tag='span', attrs={'class': 'input-group-btn'})
            _wrap.append(buttons)
            
            buttons.append(Element(content=u'搜索', tag='button', attrs={
                'type': 'submit',
                'class': 'btn btn-default',
            }))
            if search_query:
                buttons.append(Element(content=u'取消', tag='a', attrs={
                    'href': '?',
                    'class': 'btn btn-default',
                }))
            header_right.append(search_form)

        # 添加按钮
        if self.can_add:
            add_btn = Link(mark_safe(u'<i class="fa fa-plus"></i> 添加'),
                           'admin:%s:%s-add' % (self.app_label, self.name))
            add_btn.set_attr('class', 'btn btn-primary ml-10')
            header_right.append(add_btn)

        grid = Grid(qs.object_list, self.display_fields)
        ui.add_table(grid)

        _links = [] + self.other_links
        if self.form_class:
            _links.append((lambda i: reverse('admin:%s:%s-edit' % (self.app_label, self.name), args=[i.pk]), u"编辑"))
        if self.can_delete:
            _links.append((lambda i: reverse('admin:%s:%s-delete' % (self.app_label, self.name), args=[i.pk]), u"删除"))
        if _links:
            grid.add_column(None, links(_links))

        page = AdminPagination(qs)
        ui.append(page)
        return ui

    def setup_add_view(self, view):
        self.can_add = True
        self.add_view('add', view, u'添加', '/add$', 'add')

    def setup_edit_view(self, form_class, form_valid_callback=None, can_add=True):
        self.form_class = form_class
        self.form_valid_callback = form_valid_callback
        self.add_view('edit', self.edit_view, u'编辑', '/(?P<pk>\d+)/edit$', 'edit')
        if can_add:
            self.setup_add_view(self.edit_view)

    def edit_view(self, request, response, pk=None):
        instance = self.model_class.objects.get(pk=pk) if pk else None
        form = self.form_class(data=request.POST or None, files=request.FILES or None, instance=instance)

        def form_valid(**kwargs):
            if self.form_valid_callback:
                self.form_valid_callback(form, request, response)
            form.save()
            return redirect('admin:%s:%s' % (self.app_label, self.name))

        if self.can_delete:
            delete_url = reverse('admin:%s:%s-delete' % (self.app_label, self.name),
                                 args=[instance.pk]) if instance else None
        else:
            delete_url = None

        return edit_view(self.app_label, request, form, form_valid, delete_url=delete_url)

    def _setup_delete_view(self):
        self.add_view('delete', self.delete_view, u'删除', '/(?P<pk>\d+)/delete$', 'delete')

    def delete_view(self, request, response, pk):
        instance = self.model_class.objects.filter(pk=pk)

        def on_success():
            return redirect('admin:%s:%s' % (self.app_label, self.name))

        return delete_confirm_view(self.app_label, request, instance, on_success)
