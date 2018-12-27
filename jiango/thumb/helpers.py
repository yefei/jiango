# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2018/12/19
import hashlib
from PIL import Image
from django.utils.crypto import constant_time_compare
from django.utils.encoding import smart_str, filepath_to_uri
from django.conf import settings
from .settings import THUMB_URL


def get_thumb_sign(path, width=0, height=0, mode=0):
    return hashlib.md5('%s$%s$%d$%d$%d' % (settings.SECRET_KEY, smart_str(path), width, height, mode)).hexdigest()


def check_thumb_sign(sign, path, width=0, height=0, mode=0):
    return constant_time_compare(sign, get_thumb_sign(path, width, height, mode))


def model_0(im, width, height):
    u"""
    限定缩略图的长边最多为<width>，短边最多为<height>，进行等比缩放，不裁剪。
    如果只指定 w 参数则表示限定长边（短边自适应），只指定 h 参数则表示限定短边（长边自适应）。
    """
    im.thumbnail((width or im.size[0], height or im.size[1]), Image.ANTIALIAS)
    return im


def model_1(im, width, height):
    u"""
    限定缩略图的宽最少为<Width>，高最少为<Height>，进行等比缩放，居中裁剪。
    转后的缩略图通常恰好是 <Width>x<Height> 的大小（有一个边缩放的时候会因为超出矩形框而被裁剪掉多余部分）。
    如果只指定 w 参数或只指定 h 参数，代表限定为长宽相等的正方图。
    """
    if im.size == (width, height):
        return im

    _w = max(im.size[0] * height / im.size[1], 1)
    _h = height

    if _w < width:
        _w = width
        _h = max(im.size[1] * width / im.size[0], 1)
        center = (_h - height) / 2
        crop = 0, center, width, _h - center
    else:
        center = (_w - width) / 2
        crop = center, 0, _w - center, height

    return im.resize((_w, _h), Image.ANTIALIAS).crop(crop)


MODES = {
    0: model_0,
    1: model_1,
}


class ThumbUrl:
    def __init__(self, image, base_url=None):
        self.image = image
        self.base_url = base_url or THUMB_URL

    def __unicode__(self):
        return self.image.url

    def size(self, width=0, height=0, mode=0):
        u"""
        :param width: 宽度
        :param height: 高度
        :param mode: 模式
        :return: 缩略图访问地址
        """
        if width == height == 0:
            return unicode(self)
        if mode not in MODES:
            mode = 0
        sign = get_thumb_sign(self.image, width, height, mode)
        return '%s%d/%dx%d/%s/%s' % (self.base_url, mode, width, height, sign, filepath_to_uri(self.image))

    def __getitem__(self, item):
        u"""
        通过属性名称取得尺寸 w100_h100_m0
        :param item:
        :return:
        """
        width = 0
        height = 0
        mode = 0
        for i in item.split('_'):
            t, v = i[:1], i[1:]
            if t == 'w':
                width = int(v)
            elif t == 'h':
                height = int(v)
            elif t == 'm':
                mode = int(v)
        if width or height:
            return self.size(width, height, mode)
        raise ValueError('unknown thumb rule')
