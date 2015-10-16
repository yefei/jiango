# -*- coding: utf-8 -*-
# Created on 2015-10-16
# @author: Yefei
from jiango.importlib import import_object
from jiango.cms.config import CONTENT_MODELS, CONTENT_ACTIONS


COLUMN_IMPORTED_OBJECTS = {}


# 取得模型相关对象 model, form, index_view, list_view, content_view
def get_model_object(model, key):
    if model in CONTENT_MODELS and key in CONTENT_MODELS[model]:
        cache_key = '-'.join((model, key))
        if cache_key not in COLUMN_IMPORTED_OBJECTS:
            COLUMN_IMPORTED_OBJECTS[cache_key] = import_object(CONTENT_MODELS[model][key])
        return COLUMN_IMPORTED_OBJECTS[cache_key]


# 取得指定扩展模型中的操作和系统内置操作
def get_model_actions(model):
    actions = CONTENT_ACTIONS
    model_actions = CONTENT_MODELS[model].get('actions')
    if model_actions:
        actions.update(model_actions)
    return actions


# 取得所有模型操作和内置操作
def get_all_actions():
    actions = CONTENT_ACTIONS
    for m in CONTENT_MODELS:
        model_actions = CONTENT_MODELS[m].get('actions')
        if model_actions:
            actions.update(model_actions)
    return actions
