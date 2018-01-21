# -*- coding: utf-8 -*-

from urllib import urlencode
import urllib2
import json
from gevent import monkey
monkey.patch_all()


class WebClient(object):
    def __init__(self, host):
        self._host = host
        self._headers = {}

    def add_header(self, key, value):
        self._headers[key] = value

    def get(self, path, is_json=True, **params):
        try:
            data = urlencode(params)
            url = "{0}{1}?{2}".format(self._host, path, data)
            req = urllib2.Request(url, headers=self._headers)
            data = urllib2.urlopen(req).read()
            if data == "":
                return data

            return json.loads(data) if is_json else data
        except urllib2.HTTPError as e:
            print e.code
            print e.read()

    def post(self, path, is_json=True, **params):
        try:
            data = urlencode(params)
            req = urllib2.Request(self._host + path, data=data, headers=self._headers)
            data = urllib2.urlopen(req).read()
            if data == "":
                return data

            return json.loads(data) if is_json else data
        except urllib2.HTTPError as e:
            print e.code
            print e.read()
