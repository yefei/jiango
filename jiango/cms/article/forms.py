# -*- coding: utf-8 -*-
# Created on 2015-10-15
# @author: Yefei
from django import forms
from jiango.shortcuts import get_object_or_none
from .models import Article, Content


class ArticleForm(forms.ModelForm):
    content = forms.CharField(label=u'内容', widget=forms.Textarea)
    
    class Meta:
        model = Article
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            content_obj = get_object_or_none(Content, article=instance)
            if content_obj:
                kwargs['initial'] = {'content': content_obj.content}
        super(ArticleForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        obj = super(ArticleForm, self).save(commit)
        content = self.cleaned_data['content']
        content_obj = get_object_or_none(Content, article=obj)
        if content_obj:
            content_obj.content = content
            content_obj.save()
        else:
            Content.objects.create(article=obj, content=content)
        return obj
