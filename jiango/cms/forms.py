# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
from django import forms
from jiango.shortcuts import get_object_or_none
from .models import Column, Article, ArticleContent
from .config import COLUMN_PATH_RE


class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
    
    def clean_path(self):
        path = self.cleaned_data['path'].strip(' /')
        paths = filter(lambda v: v!='', path.split('/'))
        for slug in paths:
            if slug.isdigit() or not COLUMN_PATH_RE.search(slug):
                raise forms.ValidationError(u"目录 '%s' 不符合规则" % slug)
        # 检查父路径是否存在
        if paths[:-1]:
            check = Column.objects.filter(path='/'.join(paths[:-1]))
            if self.instance.pk:
                check = check.exclude(pk=self.instance.pk)
            if not check.exists():
                raise forms.ValidationError(u"父栏目路径 '%s' 不存在" % '/'.join(paths[:-1]))
        return '/'.join(paths)


class ColumnEditForm(ColumnForm):
    class Meta:
        model = Column
        exclude = ('model',)


class ArticleForm(forms.ModelForm):
    content = forms.CharField(label=u'内容', widget=forms.Textarea)
    
    class Meta:
        model = Article
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            content_obj = get_object_or_none(ArticleContent, article=instance)
            if content_obj:
                kwargs['initial'] = {'content': content_obj.content}
        super(ArticleForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        obj = super(ArticleForm, self).save(commit)
        content = self.cleaned_data['content']
        content_obj = get_object_or_none(ArticleContent, article=obj)
        if content_obj:
            content_obj.content = content
            content_obj.save()
        else:
            ArticleContent.objects.create(article=obj, content=content)
        return obj
