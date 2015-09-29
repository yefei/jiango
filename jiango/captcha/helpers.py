# -*- coding: utf-8 -*-
from hashlib import md5
from django.core.cache import cache
from django.core.signing import b64_decode, b64_encode
from django.utils.encoding import smart_str
from django.utils.crypto import get_random_string
from jiango.crypto import crypto_data
from .settings import CAPTCHA_CHARS, CAPTCHA_LENGTH, CAPTCHA_AGE


def create_crypted_challenge():
    challenge = get_random_string(CAPTCHA_LENGTH, CAPTCHA_CHARS)
    return b64_encode(crypto_data.encrypt(challenge, CAPTCHA_AGE))


def decrypt_challenge(data):
    try:
        data = b64_decode(smart_str(data))
    except TypeError:
        return None
    return crypto_data.decrypt(data)


class CaptchaStore(object):
    def __init__(self, key):
        self.cache = cache
        self.key = 'captcha:' + md5(key).hexdigest()
    
    def create(self):
        self.cache.set(self.key, 1, CAPTCHA_AGE)
    
    def exists(self):
        return self.cache.has_key(self.key)

    def delete(self):
        self.cache.delete(self.key)
