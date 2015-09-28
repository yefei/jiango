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
    return b64_encode(crypto_data.encode(challenge, CAPTCHA_AGE))


def decrypt_challenge(data):
    try:
        data = b64_decode(smart_str(data))
    except TypeError:
        return None
    return crypto_data.decode(data)


class CaptchaStore(object):
    def __init__(self):
        self._cache = cache
    
    def _hash(self, key):
        return md5(key).hexdigest()
    
    def create(self, key):
        if self.exists(key):
            func = self._cache.set
        else:
            func = self._cache.add
        func(self._hash(key), None, CAPTCHA_AGE)
    
    def exists(self, key):
        return self._cache.has_key(self._hash(key))

    def delete(self, key):
        self._cache.delete(self._hash(key))
