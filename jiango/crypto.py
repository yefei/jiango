# -*- coding: utf-8 -*-
# Created on 2015-9-28
# 简单数据加密，算法源自 discuz authcode 并加以改良
# @author: Yefei
import struct
from time import time
from hashlib import md5
from django.conf import settings
from django.utils.crypto import get_random_string


class CryptoData(object):
    INFO_FMT = '>I8s'
    FMT = INFO_FMT + '%ds'
    INFO_LEN = struct.calcsize(INFO_FMT)
    
    def __init__(self, key=None, ckey_len=4):
        self.key = key or settings.SECRET_KEY
        self.ckey_len = min(ckey_len, 16)
        self.key_digest = md5(self.key).digest()
        self.keya = md5(self.key_digest[:8]).digest()
        self.keyb = md5(self.key_digest[8:]).digest()
    
    def get_data_key(self, data):
        return md5(self.keyb + data).digest()[:8]
    
    def encrypt(self, data, expiry=0):
        ckey = ''
        if self.ckey_len > 0:
            ckey = md5(get_random_string(16)).digest()[:self.ckey_len]
        if expiry > 0:
            expiry += time()
        data = struct.pack(self.FMT % len(data), expiry, self.get_data_key(data), data)
        return ckey + self.xor(data, ckey)
    
    def decrypt(self, data):
        ckey = ''
        if self.ckey_len > 0:
            if len(data) < self.ckey_len + self.INFO_LEN:
                return False
            ckey = data[:self.ckey_len]
            data = data[self.ckey_len:]
        if data < self.INFO_LEN:
            return False
        data = self.xor(data, ckey)
        # len(data)-INFO_FMT 剩余长度的为数据长度
        expiry, data_key, data = struct.unpack(self.FMT % (len(data)-self.INFO_LEN), data)
        if (expiry == 0 or expiry-time() > 0) and data_key == self.get_data_key(data):
            return data
        return False
    
    def xor(self, data, ckey=''):
        cryptkey = md5(self.keya + ckey).digest()
        result = []
        box = range(0, 256)
        rndkey = [ord(cryptkey[i % 16]) for i in xrange(0, 256)]
        j = 0
        for i in xrange(0, 256):
            j = (j + box[i] + rndkey[i]) % 256
            box[i], box[j] = box[j], box[i]
        a = j = 0
        for i in xrange(0, len(data)):
            a = (a + 1) % 256
            j = (j + box[a]) % 256
            box[a], box[j] = box[j], box[a]
            result.append(chr(ord(data[i]) ^ (box[(box[a] + box[j]) % 256])))
        return ''.join(result)

crypto_data = CryptoData()
