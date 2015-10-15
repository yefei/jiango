# -*- coding: utf-8 -*-
# Created on 2015-10-15
# @author: Yefei
from django.db import models
from jiango.cms.models import ContentBase


class Article(ContentBase):
    title = models.CharField(u'标题', max_length=200)
    
    def __unicode__(self):
        return self.title


class Content(models.Model):
    article = models.OneToOneField(Article, primary_key=True, editable=False)
    content = models.TextField(u'内容')
