# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2018/12/19
import hashlib
from django.core.urlresolvers import reverse
from django.utils.crypto import constant_time_compare
from django.utils.encoding import smart_str
from django.conf import settings


def get_thumb_sign(path, width=0, height=0):
    return hashlib.md5('%s$%s$%d$%d' % (settings.SECRET_KEY, smart_str(path), width, height)).hexdigest()


def check_thumb_sign(sign, width=0, height=0):
    return constant_time_compare(sign, get_thumb_sign(width, height))


class ThumbUrl:
    def __init__(self, image):
        self.image = image

    def __unicode__(self):
        return self.image.url

    def size(self, width=0, height=0):
        if width == height == 0:
            return unicode(self)
        sign = get_thumb_sign(self.image, width, height)
        return reverse('thumb', kwargs={'width': width, 'height': height, 'sign': sign, 'path': self.image})

    def __getitem__(self, item):
        """
        通过属性名称取得尺寸 w100_h100
        :param item:
        :return:
        """
        width = 0
        height = 0
        for i in item.split('_'):
            t, v = i[:1], i[1:]
            if t == 'w':
                width = int(v)
            elif t == 'h':
                height = int(v)
        if width or height:
            return self.size(width, height)
        raise ValueError('unknown thumb rule')
