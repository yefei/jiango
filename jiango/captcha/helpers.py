# -*- coding: utf-8 -*-
import random
import time
import hmac
import hashlib
import pyDes
from django.conf import settings
from django.core.cache import cache
from django.core.signing import b64_decode, b64_encode
from django.utils.encoding import smart_str
from django.utils.crypto import constant_time_compare
from .settings import CAPTCHA_CHARS, CAPTCHA_LENGTH, CAPTCHA_AGE


TIMESTAMP_LENGTH = 13
HMAC_LENGTH = 16


def random_char_challenge():
    return ''.join([random.choice(CAPTCHA_CHARS) for i in range(CAPTCHA_LENGTH)])

def create_crypted_challenge():
    timestamp = str(time.time()).zfill(TIMESTAMP_LENGTH)[:TIMESTAMP_LENGTH]
    hash_key = hashlib.md5('%s%s' % (timestamp, settings.SECRET_KEY)).digest()
    challenge = random_char_challenge()
    des = pyDes.triple_des(hash_key, pyDes.CBC, padmode=pyDes.PAD_PKCS5)
    crypted_challenge = des.encrypt(challenge)
    hash = hmac.new(hash_key, crypted_challenge).digest()
    return b64_encode(''.join((hash,timestamp,crypted_challenge)))

def decrypt_challenge(key):
    try:
        s = b64_decode(smart_str(key))
    except TypeError:
        return None
    hash, timestamp, crypted_challenge = s[:HMAC_LENGTH], \
        s[HMAC_LENGTH:HMAC_LENGTH+TIMESTAMP_LENGTH], s[HMAC_LENGTH+TIMESTAMP_LENGTH:]
    hash_key = hashlib.md5('%s%s' % (timestamp, settings.SECRET_KEY)).digest()
    expected_hash = hmac.new(hash_key, crypted_challenge).digest()
    if not constant_time_compare(hash, expected_hash):
        return None
    if (time.time() - float(timestamp)) > CAPTCHA_AGE:
        return None
    d = pyDes.triple_des(hash_key, pyDes.CBC, padmode=pyDes.PAD_PKCS5)
    return d.decrypt(crypted_challenge)

class CaptchaStore(object):
    def __init__(self):
        self._cache = cache
    
    def _hash(self, key):
        return hashlib.md5(key).hexdigest()
    
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
