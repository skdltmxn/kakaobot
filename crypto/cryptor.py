# -*- coding: utf-8 -*-

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import os


class Cryptor(object):
    def __init__(self):
        self._key = os.urandom(16)
        self._iv = os.urandom(16)
        self._public_key = '''-----BEGIN PUBLIC KEY-----
MIIBIDANBgkqhkiG9w0BAQEFAAOCAQ0AMIIBCAKCAQEAxdunvI9dqgKv1hRkBG/g
JRNULzYZfexJfCeINu0cGpvUlT8vEO2JDkQUNIHVk36JpwjO5A6vdrrETk+0jlkF
txI5rQtnJ1utBTliU+TZaK0vFmnIkuFZFalMsxeF0Yut4zeHhQXEBOOBM9getwLY
7vliNP7kdtNKX+O3MFUQBXEgwaMNc2qp1Cq5eHk5N26QRnwaTzbqy0mDnNxUc+Z7
TsDT/OK9vxNy/hfHtr0qlQ3sVqy2D/2xuR+7ouAR9HNj0kGLBdy/89O8KU1dZ6RA
4WQZpKGgFf1x2eEALpY1kBThpJ5JhjIsGhGCOkO7lys63gOhTBF7mTnDA8yV4cIk
HwIBAw==
-----END PUBLIC KEY-----'''

        print "Key: " + self._key.encode("hex")
        print "Iv: " + self._iv.encode("hex")

    def _pad(self, data):
        length = 16 - (len(data) % 16)
        data += chr(0) * length
        return data

    def _get_pem(self):
        return self._public_key

    def get_aes_key_iv(self):
        return self._key + self._iv

    def encrypt_aes(self, data):
        aes = AES.new(self._key, AES.MODE_CFB, IV=self._iv, segment_size=8 * AES.block_size)
        original_len = len(data)
        return aes.encrypt(self._pad(data))[:original_len]

    def decrypt_aes(self, data):
        aes = AES.new(self._key, AES.MODE_CFB, IV=self._iv, segment_size=8 * AES.block_size)
        original_len = len(data)
        return aes.decrypt(self._pad(data))[:original_len]

    def encrypt_rsa(self, data):
        key = RSA.importKey(self._get_pem())
        oaep = PKCS1_OAEP.new(key)
        return oaep.encrypt(data)
