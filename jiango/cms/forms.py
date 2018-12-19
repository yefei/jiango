# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
from django import forms
from jiango.importlib import import_object
from jiango.admin.models import LogTypes
from .models import Path, Menu, get_all_menus, flat_all_menus, Collection
from .config import PATH_RE, FLAGS


class PathForm(forms.ModelForm):
    class Meta:
        model = Path
    
    def clean_path(self):
        path = self.cleaned_data['path'].strip(' /')
        paths = filter(lambda v: v != '', path.split('/'))
        for slug in paths:
            if slug.isdigit() or not PATH_RE.search(slug):
                raise forms.ValidationError(u"目录 '%s' 不符合规则" % slug)
        # 检查父路径是否存在
        if paths[:-1]:
            check = Path.objects.filter(path='/'.join(paths[:-1]))
            if self.instance.pk:
                check = check.exclude(pk=self.instance.pk)
            if not check.exists():
                raise forms.ValidationError(u"父栏目路径 '%s' 不存在" % '/'.join(paths[:-1]))
        return '/'.join(paths)


class PathDeleteForm(forms.Form):
    confirm = forms.BooleanField(label=u'我确定要删除以上数据')


class ActionForm(forms.Form):
    action = forms.CharField()
    back = forms.CharField(required=False)

    def __init__(self, actions, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self._actions = actions
        self._form_object = None

    def clean_action(self):
        action = self.cleaned_data['action']
        if action not in self._actions:
            raise forms.ValidationError(u'无效的操作项')
        self._form_object = import_object(self._actions[action]['form'])
        return action
    
    def get_form_object(self):
        return self._form_object
    
    def get_action_name(self):
        action = self.cleaned_data.get('action')
        if action:
            return self._actions[action].get('name')


class ActionBaseForm(forms.Form):
    log_action = LogTypes.NONE
    
    def __init__(self, qs, *args, **kwargs):
        super(ActionBaseForm, self).__init__(*args, **kwargs)
        self.qs = qs
    
    def execute(self):
        pass


class FlagAction(ActionBaseForm):
    log_action = LogTypes.UPDATE
    flag = forms.ChoiceField(required=False, label='标记为', choices=FLAGS)

    def execute(self):
        self.qs.update(flag=self.cleaned_data['flag'])


class HideAction(ActionBaseForm):
    log_action = LogTypes.UPDATE
    is_hidden = forms.BooleanField(required=False, label='隐藏 (在前台不显示)', initial=True)
    
    def execute(self):
        self.qs.update(is_hidden=self.cleaned_data['is_hidden'])


class DeleteAction(ActionBaseForm):
    log_action = LogTypes.DELETE
    
    def execute(self):
        self.qs.update(is_deleted=True)


class CollectionDeleteAction(ActionBaseForm):
    log_action = LogTypes.DELETE

    def execute(self):
        self.qs.delete()


########################################################################################################################


class MenuForm(forms.ModelForm):
    value = forms.RegexField(r'^[_\w]+\Z', label=u'句柄',
                             help_text=u'句柄用于菜单调用，同级中不可重复。只可使用字幕数字下划线。')

    class Meta:
        model = Menu
        fields = ['title', 'value', 'is_hidden']

    def clean_value(self):
        value = self.cleaned_data['value']
        # 冲突检查
        qs = Menu.objects.filter(parent=None, value=value)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(u'句柄名称冲突', 'name-conflict')
        return value


class MenuItemForm(forms.ModelForm):
    value = forms.CharField(label=u'链接', widget=forms.Textarea, help_text=u'请输入绝对路径，支持模版代码。')

    class Meta:
        model = Menu
        fields = ['title', 'value', 'parent', 'is_hidden', 'order']

    def __init__(self, request, *args, **kwargs):
        super(MenuItemForm, self).__init__(*args, **kwargs)
        self.request = request

        items = get_all_menus()
        # 父选择需要排除自己以及子项，防止无限嵌套
        if self.instance.pk:
            items = flat_all_menus(items, self.instance)
        else:
            items = flat_all_menus(items)
        self.fields['parent'].choices = ((i.pk, '%s%s%s' % (
            '+--' * i.level, ' ' if i.level else '', i.title)) for i in items)

    def clean_value(self):
        value = self.cleaned_data['value']
        # 清除本机 http://host 前缀
        scheme_host = '{}://{}'.format(self.request.is_secure() and 'https' or 'http', self.request.get_host())
        if value.startswith(scheme_host):
            value = value[len(scheme_host):]
        return value


########################################################################################################################


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
