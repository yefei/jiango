# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2019/1/21
import os
from .settings import KEY_PREFIX, TEMP_PREFIX
from .models import File
from .client import get_stat, move_file, image_info, av_info, put_stream, get_stream_hash


# 通过上传的 key 创建文件
# 文件信息从存储服务器获取
def create_by_hash(hash_key, size, mime=None):
    save_key = KEY_PREFIX + hash_key
    width = 0
    height = 0
    if mime.startswith('image/'):
        info = image_info(save_key)
        width = int(info['width'])
        height = int(info['height'])
    elif mime.startswith('video/'):
        info = av_info(save_key)
        width = int(info['video']['width'])
        height = int(info['video']['height'])
    return File.objects.create(
        hash=hash_key,
        mime=mime,
        size=size,
        width=width,
        height=height,
    )


# 通过临时上传创建文件
def create_by_temp(hash_key):
    upload_key = TEMP_PREFIX + hash_key
    stat = get_stat(upload_key)
    # 移动文件
    move_file(upload_key, KEY_PREFIX + hash_key)
    # 获取信息
    mime = stat['mimeType']
    size = stat['fsize']
    return create_by_hash(hash_key, size, mime)


# 通过数据流创建文件
def create_by_stream(stream, mime=None, hash_key=None):
    if hash_key is None:
        hash_key = get_stream_hash(stream)
        stream.seek(0)
    if hasattr(stream, 'size'):
        size = stream.size
    else:
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0)
    put_stream(KEY_PREFIX + hash_key, stream, size, mime)
    return create_by_hash(hash_key, size, mime)


def get_file_by_hash(hash_key):
    try:
        return File.objects.get(hash=hash_key)
    except File.DoesNotExist:
        pass


def get_or_create_by_stream(stream, mime=None):
    hash_key = get_stream_hash(stream)
    obj = get_file_by_hash(hash_key)
    if obj is None:
        # 不存在则创建
        obj = create_by_stream(stream, mime, hash_key)
    return obj
