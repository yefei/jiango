# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2018/12/19
import os
import logging
from PIL import Image
from django.http import Http404
from django.conf import settings
from django.views.static import serve
from .helpers import check_thumb_sign, MODES
from .settings import THUMB_ROOT, THUMB_JPEG_QUALITY


logger = logging.getLogger(__name__)


def thumb(request, path, sign, width=0, height=0, mode=0):
    if not THUMB_ROOT:
        raise Http404('E.005')

    width, height, mode = int(width), int(height), int(mode)
    if not check_thumb_sign(sign, path, width, height, mode):
        raise Http404('E.004')

    thumb_filename = os.path.join(str(mode), '%dx%d' % (width, height), sign, path)
    thumb_full_path = os.path.join(THUMB_ROOT, thumb_filename)
    if not os.path.exists(thumb_full_path):
        source_full_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.isfile(source_full_path):
            raise Http404('E.001')

        try:
            im = Image.open(source_full_path)
        except IOError as e:
            logger.warning('upload thumb open image error: %s', e)
            raise Http404('E.002')

        # if im.mode not in ('RGB', 'RGBA'):
        #   im = im.convert(mode='RGB')

        mode_func = MODES.get(mode)
        if mode_func is None:
            raise Http404('E.006')

        try:
            im = mode_func(im, width, height)
        except Exception:
            raise Http404('E.007')

        directory = os.path.dirname(thumb_full_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                pass

        if not os.path.isdir(directory):
            logger.warning('upload thumb save image error: %s', "%s exists and is not a directory." % directory)
            raise Http404('E.003')

        params = {}
        if im.format == 'JPEG':
            params['quality'] = THUMB_JPEG_QUALITY

        im.save(thumb_full_path, **params)

    return serve(request, thumb_filename, document_root=THUMB_ROOT)
