# -*- coding: utf-8 -*-
"""
Created on 2017/1/20
@author: Fei Ye <316606233@qq.com>
"""
from django.db import models
from django.utils.encoding import smart_str, smart_unicode
from django.core.cache import cache
from django.conf import settings
from jiango.shortcuts import get_object_or_none


CACHE_KEY_PREFIX = 'CONFIGURATION_ITEM:'


TYPE_STR = 1
TYPE_UNICODE = 2
TYPE_INT = 3
TYPE_FLOAT = 4
TYPE_BOOL = 5


class Item(models.Model):
    key = models.CharField(max_length=30, primary_key=True)
    type = models.SmallIntegerField()
    value = models.TextField(null=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)


def get_value_type(value):
    if isinstance(value, bool):
        return TYPE_BOOL
    if isinstance(value, str):
        return TYPE_STR
    if isinstance(value, unicode):
        return TYPE_UNICODE
    if isinstance(value, int):
        return TYPE_INT
    if isinstance(value, float):
        return TYPE_FLOAT


def get_config_item(key):
    items = getattr(settings, 'CONFIGURATION_ITEMS')
    if items:
        for item in items:
            if item[0] == key:
                return item


def get_config_value(key):
    item = get_config_item(key)
    if not item:
        return

    value = cache.get(CACHE_KEY_PREFIX + key)
    if value:
        return value

    obj = get_object_or_none(Item, key=key)
    if obj:
        if obj.type == TYPE_STR:
            value = smart_str(obj.value)
        elif obj.type == TYPE_UNICODE:
            value = smart_unicode(obj.value)
        elif obj.type == TYPE_INT:
            value = int(obj.value)
        elif obj.type == TYPE_FLOAT:
            value = float(obj.value)
        elif obj.type == TYPE_BOOL:
            value = obj.value == 'True'

    if value is None:
        value = item[1]

    cache.set(CACHE_KEY_PREFIX + key, value)
    return value


def set_config_value(key, value):
    cache.set(CACHE_KEY_PREFIX + key, value)
    value_type = get_value_type(value)
    obj = get_object_or_none(Item, key=key)
    if obj:
        obj.value = value
        obj.type = value_type
        obj.save()
        return obj
    else:
        return Item.objects.create(key=key, value=value, type=value_type)


def delete_config(key):
    cache.delete(CACHE_KEY_PREFIX + key)
    obj = get_object_or_none(Item, key=key)
    if obj:
        obj.delete()
