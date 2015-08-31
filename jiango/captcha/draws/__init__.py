# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib
from jiango.captcha.settings import CAPTCHA_DRAWS, CAPTCHA_DRAW


class InvalidCaptchaDrawError(ImproperlyConfigured):
    pass


def get_draw(draw_alias):
    mod_path = CAPTCHA_DRAWS[draw_alias]['DRAW']
    try:
        mod = importlib.import_module(mod_path)
        draw_cls = getattr(mod, 'CaptchaDraw')
    except (AttributeError, ImportError), e:
        raise InvalidCaptchaDrawError("Could not find backend '%s': %s" % (mod_path, e))
    return draw_cls(CAPTCHA_DRAWS[draw_alias]['OPTIONS'])


draw = get_draw(CAPTCHA_DRAW)
